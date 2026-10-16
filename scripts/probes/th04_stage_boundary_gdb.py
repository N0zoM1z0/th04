"""Read-only code-fetch checkpoints across the actual next-stage lifecycle."""

import gzip, hashlib, json, os, struct
from pathlib import Path
import gdb
from th04_demo_video import VideoRam, LAYOUT, SYMBOL_SIZES, BLOCK_SIZE

sha = lambda b: hashlib.sha256(b).hexdigest()


class Entry(gdb.Breakpoint):
    def __init__(self, b, label):
        self.b = b
        self.label = label
        point = b.profile["entries"][label]
        self.segment = point["segment"]
        self.offset = point["offset"]
        self.linear = (b.m.current.load + self.segment) * 16 + self.offset
        self.host = b.m.ram.state()[0] + b.m.ram.physical(self.linear)
        super().__init__(
            "*(unsigned char *)%d" % self.host,
            type=gdb.BP_WATCHPOINT,
            wp_class=gdb.WP_READ,
            internal=True,
        )

    def stop(self):
        b = self.b
        try:
            regs = bytes(
                gdb.selected_inferior().read_memory(b.m.address("cpu_regs"), 48)
            )
            segs = bytes(gdb.selected_inferior().read_memory(b.m.address("Segs"), 136))
            cs = int.from_bytes(segs[8:16], "little")
            ip = int.from_bytes(regs[32:36], "little") & 65535
            if (cs, ip) != (b.m.current.load + self.segment, self.offset):
                b.ignored += 1
                return False
            self.enabled = False
            return b.reached(self.label)
        except Exception as error:
            b.m.error = "stage boundary: " + repr(error)
            return True


class Boundary:
    def __init__(self, scope):
        self.scope = scope
        self.complete = False
        self.m = None
        self.count = 0
        self.ignored = 0
        self.loop = 0
        self.previous_group = 0
        self.previous_video = 0
        self.watch = None
        self.watchers = {}
        self.base_registered = 0
        self.maximum_registered = 0
        self.bridge = [
            "score",
            "gameplay_return",
            "stage_free",
            "stage_init",
            "init_return",
        ]
        self.bridge_index = 0

    def arm(self, label):
        if label not in self.watchers:
            self.watchers[label] = Entry(self, label)
        else:
            self.watchers[label].enabled = True
        self.watch = self.watchers[label]
        assert sum(w.enabled for w in self.watchers.values()) == 1, (
            "exactly one active boundary watchpoint"
        )

    def begin(self, m):
        self.m = m
        m.current.enabled = False
        m.loader.enabled = False
        profiles = json.loads(
            Path(os.environ["TH04_STAGE_BOUNDARY_PROFILES"]).read_text()
        )
        matches = [
            p
            for p in profiles.values()
            if p["dgroup"] == m.profile["dgroup"]
            and p["signature"] == m.profile["signature"]
        ]
        assert len(matches) == 1
        self.profile = matches[0]
        self.waits = self.scope.get("stage_waits")
        if self.waits is not None:
            self.waits.begin(self)
        self.output = m.output
        self.checkpoints = self.output / "stage-boundary"
        self.checkpoints.mkdir()
        self.prefix = (self.output / "raw.txt").read_bytes()
        self.stream = (self.output / "stage-boundary.jsonl").open("x")
        self.raw = (self.output / "stage-boundary.bin.gz").open("xb")
        self.wire = gzip.GzipFile(
            filename="", mode="wb", fileobj=self.raw, mtime=0, compresslevel=1
        )
        self.wire.write(b"TH04SB1\n")
        layout_path = Path(self.profile["layout_path"])
        assert sha(layout_path.read_bytes()) == self.profile["layout_sha256"]
        layout = json.loads(layout_path.read_text())
        assert layout["passed"] and layout["layout"] == LAYOUT
        symbols = {name: m.address(name) for name in SYMBOL_SIZES}
        assert (
            len(
                {
                    symbols[name] - layout["symbols"][name]["address"]
                    for name in SYMBOL_SIZES
                }
            )
            == 1
        )
        self.video = VideoRam(gdb.selected_inferior().read_memory, symbols)
        self.base_registered = len(gdb.breakpoints() or ())
        self.record("stage1-actor")
        self.arm("score")

    def record(self, label):
        m = self.m
        reader = gdb.selected_inferior().read_memory
        regs = bytes(reader(m.address("cpu_regs"), 48))
        segs = bytes(reader(m.address("Segs"), 136))
        group, pages, state = m.ram.read_range(m.current.linear, 65536)
        fields = {
            name: group[at : at + size].hex() for name, at, size in m.profile["fields"]
        }
        frame = int.from_bytes(bytes.fromhex(fields["frame"]), "little")
        stage = int.from_bytes(bytes.fromhex(fields["stage"]), "little")
        pointer = bytes.fromhex(fields["resident_pointer"])
        resident_linear = (
            int.from_bytes(pointer[:2], "little")
            + int.from_bytes(pointer[2:], "little") * 16
        )
        resident = m.ram.read_range(resident_linear, 256)[0]
        video, mapping = self.video.capture(stage)
        cs = int.from_bytes(segs[8:16], "little")
        ip = int.from_bytes(regs[32:36], "little") & 65535
        ss = int.from_bytes(segs[16:24], "little")
        sp = int.from_bytes(regs[16:20], "little") & 65535
        stack = m.ram.read_range(ss * 16 + sp, 64)[0]
        memory_name = None
        if (
            label.startswith("stage1")
            or label in ["gameplay_return", "stage_free", "stage_init", "init_return"]
            or frame
            in [
                0,
                1,
                2,
                8,
                64,
                128,
                256,
                600,
                2599,
                2600,
                2601,
                2602,
                2604,
                2616,
                2700,
                2800,
                3000,
                self.profile["stage2_updates"],
            ]
            or frame in self.profile.get("extra_memory_frames", [])
        ):
            memory = m.ram.read_range(0, 655360)[0]
            memory_name = f"{self.count}-memory.bin.gz"
            (self.checkpoints / memory_name).write_bytes(
                gzip.compress(memory, mtime=0, compresslevel=1)
            )
        self.wire.write(struct.pack("<I", self.count))
        value = int.from_bytes(group, "little")
        self.wire.write((value ^ self.previous_group).to_bytes(65536, "little"))
        self.previous_group = value
        value = int.from_bytes(video, "little")
        self.wire.write((value ^ self.previous_video).to_bytes(BLOCK_SIZE, "little"))
        self.previous_video = value
        assert (
            regs == bytes(reader(m.address("cpu_regs"), 48))
            and segs == bytes(reader(m.address("Segs"), 136))
            and group == m.ram.read_range(m.current.linear, 65536)[0]
        ), "read-only stage checkpoint context drift"
        registered = len(gdb.breakpoints() or ())
        self.maximum_registered = max(self.maximum_registered, registered)
        assert registered <= self.base_registered + len(
            self.profile["entries"]
        ) and len(self.watchers) <= len(self.profile["entries"]), (
            "bounded registered boundary watchpoints"
        )
        assert not any(w.enabled for w in self.watchers.values()), (
            "checkpoint entered with another boundary watcher active"
        )
        row = dict(
            watchpoint_cache_slots=len(self.watchers),
            registered_breakpoints=registered,
            baseline_registered_breakpoints=self.base_registered,
            ordinal=self.count,
            label=label,
            frame=frame,
            stage=stage,
            load_segment=m.current.load,
            dgroup_segment=m.current.dgroup,
            cpu_regs=regs.hex(),
            segments=segs.hex(),
            cs=cs,
            ip=ip,
            ss=ss,
            sp=sp,
            stack=stack.hex(),
            resident_linear=resident_linear,
            resident=resident.hex(),
            fields=fields,
            quit=group[self.profile["quit_offset"]],
            lcg_calls=m.ram.integer(m.address("th04_demo_observer::lcg_count"), 8),
            ring_calls=m.ram.integer(m.address("th04_demo_observer::ring_count"), 8),
            dgroup_sha256=sha(group),
            video_sha256=sha(video),
            memory=memory_name,
            memory_sha256=sha(memory) if memory_name else None,
            opcode=m.ram.read_range(cs * 16 + ip, 16)[0].hex(),
            mapping=mapping,
            pages=pages,
            cr0=state[1],
            cr4=state[2],
            cr3=state[3],
            unchanged_context=True,
        )
        self.stream.write(json.dumps(row, separators=(",", ":")) + "\n")
        self.stream.flush()
        self.count += 1
        return row

    def reached(self, label):
        if self.bridge_index < len(self.bridge):
            assert label == self.bridge[self.bridge_index]
            row = self.record("stage1-score" if label == "score" else label)
            self.bridge_index += 1
            if self.bridge_index < len(self.bridge):
                self.arm(self.bridge[self.bridge_index])
            else:
                self.loop = 0
                self.arm("loop")
        elif label == "loop":
            row = self.record("stage2-loop")
            assert row["stage"] == 1 and row["frame"] == self.loop, (
                row["stage"],
                row["frame"],
                self.loop,
            )
            if self.loop == self.profile["stage2_updates"]:
                self.complete = True
                return True
            self.arm("actor")
        elif label == "actor":
            row = self.record("stage2-actor")
            assert row["stage"] == 1 and row["frame"] == self.loop + 1
            self.arm("score")
            if self.waits is not None and self.waits.cue(row):
                return True
        else:
            assert label == "score"
            row = self.record("stage2-score")
            assert row["stage"] == 1 and row["frame"] == self.loop + 1
            self.loop += 1
            self.arm("loop")
        if self.count % 300 == 0:
            gdb.write("TH04_STAGE_BOUNDARY %d frame%d\n" % (self.count, row["frame"]))
        return False

    def finish(self):
        assert self.complete and self.loop == self.profile["stage2_updates"]
        if self.waits is not None and self.waits.active:
            assert self.waits.complete
            waits = self.waits.scope["waits"][self.waits.prefix_waits :]
            assert len(waits) == len(self.waits.cues) and all(
                "action_end" in row for row in waits
            )
            self.waits.save()
        self.wire.close()
        self.raw.close()
        self.stream.close()
        path = self.output / "raw.txt"
        whole = path.read_bytes()
        assert whole.startswith(self.prefix)
        path.rename(self.output / "stage-all-raw.txt")
        path.write_bytes(self.prefix)
        (self.output / "stage2-raw-suffix.txt").write_bytes(whole[len(self.prefix) :])
        summary = dict(
            watchpoint_cache_limit=len(self.profile["entries"]),
            watchpoint_cache_slots=len(self.watchers),
            baseline_registered_breakpoints=self.base_registered,
            maximum_registered_breakpoints=self.maximum_registered,
            complete=True,
            records=self.count,
            stage2_complete_updates=self.loop,
            first_stage_prefix_bytes=len(self.prefix),
            first_stage_prefix_sha256=sha(self.prefix),
            extended_raw_sha256=sha(whole),
            trace_sha256=sha((self.output / "stage-boundary.jsonl").read_bytes()),
            wire_sha256=sha((self.output / "stage-boundary.bin.gz").read_bytes()),
            ignored_fetch_contexts=self.ignored,
            profile=self.profile,
            reader_sha256=sha(Path(__file__).read_bytes()),
            scope=f"Own-file read-only instruction-fetch observations after actualactor9836 andthrough{self.loop}completedStage2updates. Prefixraw/DGROUP remainsits original bounded extent;complete extendedraw andbridge/Stage2 wire/CPU/memory/video remainseparate. Exactlyone boundarywatcher isenabled atatime;thesevenfixedown-fileaddresses reusepersistenthardwarewatchpoints;no guest-state/clock/code writes orhost function calls bythisreader. Keyboard andtraceflush remainexplicit baseadapteroperations. No physicalscanout/campaign/exactclaim.",
        )
        if self.waits is not None and self.waits.active:
            summary["stage2_waits_sha256"] = sha(
                (self.output / "stage2-waits.json").read_bytes()
            )
        (self.output / "stage-boundary-summary.json").write_text(
            json.dumps(summary, indent=2) + "\n"
        )
        gdb.write("TH04_STAGE_BOUNDARY_COMPLETE\n")
