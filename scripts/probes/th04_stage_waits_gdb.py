"""Read-only own-file Stage2 blocking call/return/player checkpoints."""

import gzip, hashlib, json, struct
import gdb

sha = lambda b: hashlib.sha256(b).hexdigest()


class Point(gdb.Breakpoint):
    def __init__(self, owner, label):
        self.owner = owner
        self.label = label
        p = owner.profile["entries"][label]
        self.segment = p["segment"]
        self.offset = p["offset"]
        b = owner.boundary
        self.linear = (b.m.current.load + self.segment) * 16 + self.offset
        host = b.m.ram.state()[0] + b.m.ram.physical(self.linear)
        super().__init__(
            "*(unsigned char *)%d" % host,
            type=gdb.BP_WATCHPOINT,
            wp_class=gdb.WP_READ,
            internal=True,
        )
        self.enabled = False

    def stop(self):
        d = self.owner
        b = d.boundary
        m = b.m
        try:
            regs = bytes(gdb.selected_inferior().read_memory(m.address("cpu_regs"), 48))
            segs = bytes(gdb.selected_inferior().read_memory(m.address("Segs"), 136))
            cs = int.from_bytes(segs[8:16], "little")
            ip = int.from_bytes(regs[32:36], "little") & 65535
            if (cs, ip) != (m.current.load + self.segment, self.offset):
                d.ignored += 1
                return False
            self.enabled = False
            d.record(self.label, regs, segs)
            return False
        except Exception as error:
            # Preserve the actual failing owner before the batch debugger exits.
            # A semantic assertion must not erase its CPU/frame evidence.
            try:
                memory = m.ram.read_range(0, 655360)[0]
                path = m.output / "stage-wait-error-memory.bin.gz"
                path.write_bytes(gzip.compress(memory, mtime=0, compresslevel=1))
                (m.output / "stage-wait-error.json").write_text(
                    json.dumps(dict(label=self.label, cue=d.current, frame=d.frame(),
                        cpu_regs=regs.hex(), segments=segs.hex(),
                        memory=path.name, memory_sha256=sha(memory), error=repr(error)), indent=2) + "\n"
                )
            except Exception as evidence_error:
                gdb.write("TH04_WAIT_ERROR_EVIDENCE " + repr(evidence_error) + "\n")
            m.error = "stage wait: " + repr(error)
            return True


class StageWaits:
    def __init__(self, scope):
        self.scope = scope
        self.active = False
        self.complete = False
        self.index = 0
        self.points = {}
        self.ignored = 0

    def begin(self, b):
        self.boundary = b
        self.profile = b.profile.get("stage2_waits")
        if self.profile is None:
            return
        self.cues = self.profile["cues"]
        assert self.cues and all(
            0 < c["frame"] < b.profile["stage2_updates"]
            and c["kind"] in ["continue", "dialogue"]
            for c in self.cues
        )
        assert [c["frame"] for c in self.cues] == sorted(
            set(c["frame"] for c in self.cues)
        )
        self.cue_index = 0
        self.current = None
        self.labels = []
        assert set(self.profile["entries"]) == {
            "dialog_run",
            "dialog_return",
            "player_update",
            "continue_menu",
            "continue_return",
        }
        self.prefix = (b.m.output / "clock-input.json").read_bytes()
        self.prefix_actions = len(self.scope["actions"])
        self.prefix_waits = len(self.scope["waits"])
        self.directory = b.m.output / "stage2-waits"
        self.directory.mkdir()
        self.rows = []
        self.points = {name: Point(self, name) for name in self.profile["entries"]}
        self.active = True

    def frame(self):
        m = self.boundary.m
        p = m.profile
        off = next(at for name, at, size in p["fields"] if name == "frame")
        return int.from_bytes(m.ram.read_range(m.current.linear + off, 2)[0], "little")

    def cue(self, row):
        if (
            not self.active
            or self.cue_index >= len(self.cues)
            or row["frame"] != self.cues[self.cue_index]["frame"]
        ):
            return False
        assert self.current is None and not any(p.enabled for p in self.points.values())
        self.current = self.cues[self.cue_index]
        self.index = 0
        kind = self.current["kind"]
        self.labels = (
            ["player_update", "continue_menu", "continue_return"]
            if kind == "continue"
            else ["player_update", "dialog_run", "dialog_return"]
            if self.current.get("player_first", False)
            else ["dialog_run", "dialog_return", "player_update"]
        )
        m = self.boundary.m
        if kind == "continue":
            self.scope["continue_frame"] = row["frame"]
            m.continue_frame = row["frame"]
            m.continue_observed = True
            m.continue_requested = True
        else:
            self.scope["dialog_frame"] = row["frame"]
            m.dialog_frame = row["frame"]
            m.dialog_observed = True
            m.dialog_requested = True
        self.points[self.labels[0]].enabled = True
        return True

    def record(self, label, regs, segs):
        b = self.boundary
        m = b.m
        assert label == self.labels[self.index]
        group = m.ram.read_range(m.current.linear, 65536)[0]
        fields = {
            name: group[at : at + size].hex() for name, at, size in b.profile["fields"]
        }
        assert int(fields["stage"], 16) == 1 and self.frame() == self.current["frame"]
        memory = m.ram.read_range(0, 655360)[0]
        video, mapping = b.video.capture(1)
        ss = int.from_bytes(segs[16:24], "little")
        sp = int.from_bytes(regs[16:20], "little") & 65535
        stack = m.ram.read_range(ss * 16 + sp, 64)[0]
        p = self.profile["entries"][label]
        cs = int.from_bytes(segs[8:16], "little")
        ip = int.from_bytes(regs[32:36], "little") & 65535
        if label in ["dialog_run", "continue_menu"]:
            assert (
                int.from_bytes(stack[:2], "little")
                == self.profile["entries"][
                    "dialog_return" if label == "dialog_run" else "continue_return"
                ]["offset"]
            )
        names = {
            kind: f"{len(self.rows)}-{label}-{kind}.bin.gz"
            for kind in ["memory", "dgroup", "video"]
        }
        for kind, data in [("memory", memory), ("dgroup", group), ("video", video)]:
            (self.directory / names[kind]).write_bytes(
                gzip.compress(data, mtime=0, compresslevel=1)
            )
        assert (
            regs
            == bytes(gdb.selected_inferior().read_memory(m.address("cpu_regs"), 48))
            and segs
            == bytes(gdb.selected_inferior().read_memory(m.address("Segs"), 136))
            and memory == m.ram.read_range(0, 655360)[0]
        )
        row = dict(
            ordinal=len(self.rows),
            cue_index=self.cue_index,
            cue_kind=self.current["kind"],
            cue_ordinal=self.index,
            label=label,
            frame=self.frame(),
            stage=1,
            load_segment=m.current.load,
            dgroup_segment=m.current.dgroup,
            cs=cs,
            ip=ip,
            ss=ss,
            sp=sp,
            stack=stack.hex(),
            cpu_regs=regs.hex(),
            segments=segs.hex(),
            fields=fields,
            opcode=m.ram.read_range(cs * 16 + ip, 16)[0].hex(),
            memory=names["memory"],
            memory_sha256=sha(memory),
            dgroup=names["dgroup"],
            dgroup_sha256=sha(group),
            video=names["video"],
            video_sha256=sha(video),
            video_mapping=mapping,
            lcg_calls=m.ram.integer(m.address("th04_demo_observer::lcg_count"), 8),
            ring_calls=m.ram.integer(m.address("th04_demo_observer::ring_count"), 8),
            registered_breakpoints=len(gdb.breakpoints() or ()),
            unchanged_context=True,
        )
        self.rows.append(row)
        self.index += 1
        if self.index < len(self.labels):
            self.points[self.labels[self.index]].enabled = True
        else:
            self.cue_index += 1
            self.current = None
            self.complete = self.cue_index == len(self.cues)
        self.save()
        gdb.write("TH04_STAGE2_WAIT " + label + " frame" + str(row["frame"]) + "\n")

    def save(self):
        if not self.active:
            return
        out = self.boundary.m.output
        assert (out / "clock-input.json").read_bytes() == self.prefix
        report = dict(
            complete=self.complete,
            profile=self.profile,
            rows=self.rows,
            ignored_fetch_contexts=self.ignored,
            auxiliary_registered_watchpoints=len(self.points),
            prefix_clock_sha256=sha(self.prefix),
            prefix_action_count=self.prefix_actions,
            prefix_wait_count=self.prefix_waits,
            actions=self.scope["actions"][self.prefix_actions :],
            waits=self.scope["waits"][self.prefix_waits :],
            remaining=self.scope["schedule"],
            scope="Own-MZ read-only blocking call/return/player checkpoints and separate real keyboard actions. Firststage keyboard receipt stays byte-identical;guest RNG/gameplay/clock/code is never assigned. These observations do not accept pictures or physical timing.",
        )
        (out / "stage2-waits.json").write_text(json.dumps(report, indent=2) + "\n")
