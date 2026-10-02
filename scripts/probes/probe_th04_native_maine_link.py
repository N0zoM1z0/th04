#!/usr/bin/env python3
"""Compile TH04-owned OP or MAINE sources and report the native link frontier.

The optional external masters.lib is a pinned calibration input. A complete
TH04-only MZ is a build candidate; runtime acceptance requires separate gates.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402

RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
SUPPORT_LIB = ROOT / "_reference/ReC98/bin/masters.lib"
SUPPORT_SHA256 = "6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6"
SOURCE_MANIFESTS = {
    "op": ROOT / "config/native_op_sources.toml",
    "maine": ROOT / "config/native_maine_sources.toml",
}
SOURCE_EXCLUSIONS = {
    # OP owns its release-specific implementation. MAINE uses the shared one.
    "op": {"src/shared/sound/se_update.cpp", "src/shared/dos/dos_puts2.asm"},
    "maine": set(),
}
# The MS-DOS command tail is bounded. A longer product define makes TC4J
# misread the longest MAINE source path's extension before compilation.
# TH04P selects C++ code grouping; ASM still uses TH04_LARGE_PRODUCT.
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-DTH04P", "-ml")


def load_sources(artifact: str = "maine") -> tuple[list[Path], list[Path]]:
    data = tomllib.loads(SOURCE_MANIFESTS[artifact].read_text(encoding="utf-8"))
    if (set(data) != {"schema_version", "artifact", "c_sources", "asm_sources"}
            or data["schema_version"] != 1 or data["artifact"] != f"th04-{artifact}"):
        raise ValueError(f"invalid {artifact.upper()} native source manifest")

    result: list[list[Path]] = []
    for key, suffixes in (("c_sources", {".c", ".cpp"}), ("asm_sources", {".asm"})):
        listed = data[key]
        if not isinstance(listed, list) or not listed or not all(isinstance(s, str) for s in listed):
            raise ValueError(f"invalid {key} source list")
        if len(set(listed)) != len(listed):
            raise ValueError(f"duplicate source in {key}")
        paths = [Path(s) for s in listed]
        for name, path in zip(listed, paths):
            if (path.is_absolute() or ".." in path.parts or name != path.as_posix()
                    or path.parts[:2] not in (("src", artifact), ("src", "shared"))
                    or path.suffix not in suffixes or not (ROOT / path).is_file()):
                raise ValueError(f"invalid or missing {artifact.upper()} source: {name}")
        discovered = {
            path.relative_to(ROOT).as_posix()
            for group in (artifact, "shared")
            for path in (ROOT / "src" / group).rglob("*")
            if path.suffix in suffixes
        }
        expected = discovered - SOURCE_EXCLUSIONS[artifact]
        if set(listed) != expected:
            raise ValueError(f"{key} source graph drift: missing={sorted(expected - set(listed))}, "
                             f"stale={sorted(set(listed) - expected)}")
        result.append(paths)
    return result[0], result[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maine_handoff_trace_overlay(work: Path) -> dict:
    """Attest MAINE startup/score checkpoints in a private copied source tree."""
    modified = {}
    entry = work / "src/maine/end/entry.cpp"
    before = entry.read_text()
    helper = r'''
extern "C" void far maine_handoff_trace(unsigned marker, unsigned detail)
{
    const char hex[] = "0123456789ABCDEF";
    char name[] = "ME00.BIN";
    name[2] = hex[marker >> 4]; name[3] = hex[marker & 15];
    unsigned sample[4] = {marker, detail, _psp,
        *(unsigned far *)MK_FP(_psp - 1, 3)};
    int handle; unsigned written;
    if(!_dos_creat(name, 0, &handle)) {
        _dos_write(handle, sample, sizeof(sample), &written);
        _dos_close(handle);
    }
}
'''
    anchor = '#include "src/maine/end/main.inl"'
    if before.count(anchor) != 1:
        raise ValueError("MAINE handoff helper anchor changed")
    after = ('#include <dos.h>\nextern "C" void far maine_handoff_trace(unsigned, unsigned);\n'
             + before.replace(anchor, helper + '\n' + anchor))
    after = after.replace("    frame_delay(100);", "    maine_handoff_trace(0x90, 0);\n    frame_delay(100);\n    maine_handoff_trace(0x91, 0);")
    after = after.replace("    regist_menu();", "    regist_menu();\n    maine_handoff_trace(0x92, 0);")
    entry.write_text(after)
    modified[str(entry.relative_to(work))] = {"original_sha256": hashlib.sha256(before.encode()).hexdigest(),
                                            "overlay_sha256": sha(entry)}
    path = work / "src/maine/end/main.inl"
    before = path.read_text()
    after = before.replace("void main(void)\n{", "void main(void)\n{\n\tmaine_handoff_trace(0, 0);", 1)
    calls = ["mem_assign_paras = (336000 >> 4);", "game_init_main(OP_AND_END_PF_FN);",
             "gaiji_backup();", "gaiji_entry_bfnt(GAIJI_FN);",
             "snd_determine_modes(resident->bgm_mode, resident->se_mode);", "graph_show();"]
    for marker, call in enumerate(calls, 1):
        after = after.replace("\t" + call, "\t" + call + f"\n\tmaine_handoff_trace({marker}, resident->end_sequence);", 1)
    path.write_text(after)
    modified[str(path.relative_to(work))] = {"original_sha256": hashlib.sha256(before.encode()).hexdigest(),
                                           "overlay_sha256": sha(path)}
    path = work / "src/shared/core/game_init_main.cpp"
    before = path.read_text()
    after = before.replace('#include <stddef.h>', '#include <stddef.h>\nextern "C" void far maine_handoff_trace(unsigned, unsigned);', 1)
    anchor = "\tif(mem_assign_dos(mem_assign_paras)) {"
    if after.count(anchor) != 1:
        raise ValueError("MAINE memory assignment trace anchor changed")
    after = after.replace(anchor, "\tmaine_handoff_trace(0x20, mem_assign_paras);\n"
                          "\tint assigned = mem_assign_dos(mem_assign_paras);\n"
                          "\tmaine_handoff_trace(0x21, assigned);\n\tif(assigned) {", 1)
    for marker, call in enumerate(["pfsetbufsiz(4096);", "vram_planes_set();",
                                   "vsync_start();", "egc_start();", "graph_400line();",
                                   "js_start();", "pfstart(pf_fn);", "bgm_init(2048);"], 0x22):
        anchor = "\t" + call
        if after.count(anchor) != 1:
            raise ValueError(f"MAINE initialization trace anchor changed: {call}")
        after = after.replace(anchor, anchor + f"\n\tmaine_handoff_trace({marker}, 0);", 1)
    path.write_text(after)
    modified[str(path.relative_to(work))] = {"original_sha256": hashlib.sha256(before.encode()).hexdigest(),
                                           "overlay_sha256": sha(path)}
    return modified


def handoff_trace_overlay(work: Path) -> dict:
    """Record OP menu/cleanup/exec checkpoints only in the private build tree."""
    modified = {}
    entry = work / "src/op/main/entry.cpp"
    before = entry.read_text()
    helper = r'''
extern "C" void far op_handoff_trace(unsigned marker, int detail)
{
    static const char hex[] = "0123456789ABCDEF";
    char filename[] = "OPH00.BIN";
    unsigned sample[8];
    int handle;
    unsigned done;
    filename[3] = hex[(marker >> 4) & 15];
    filename[4] = hex[marker & 15];
    sample[0] = marker;
    sample[1] = detail;
    unsigned largest = 0;
    _dos_allocmem(0xFFFFu, &largest);
    sample[2] = largest;
    sample[3] = _psp;
    sample[4] = *reinterpret_cast<unsigned far *>(MK_FP(_psp - 1u, 3));
    unsigned next_mcb = _psp + sample[4];
    sample[5] = *reinterpret_cast<unsigned far *>(MK_FP(next_mcb, 1));
    sample[6] = *reinterpret_cast<unsigned far *>(MK_FP(next_mcb, 3));
    sample[7] = *reinterpret_cast<unsigned char far *>(MK_FP(next_mcb, 0));
    if(_dos_creat(filename, 0, &handle) == 0) {
        _dos_write(handle, sample, sizeof(sample), &done);
        _dos_close(handle);
    }
}
'''
    anchor = '#include "src/op/main/main.inl"'
    if before.count(anchor) != 1:
        raise ValueError("OP handoff helper anchor changed")
    after = '#include <dos.h>\n' + before.replace(anchor, helper + '\n' + anchor)
    entry.write_text(after)
    modified[str(entry.relative_to(work))] = {"original_sha256": hashlib.sha256(before.encode()).hexdigest(),
                                            "overlay_sha256": sha(entry)}
    for source in ("src/op/start/start_demo.cpp", "src/op/start/start_game.cpp",
                   "src/op/start/start_extra.cpp"):
        path = work / source
        before = path.read_text()
        after = '#include <errno.h>\nextern "C" void far op_handoff_trace(unsigned, int);\n' + before
        if source.endswith("start_demo.cpp"):
            after = after.replace('    main_cdg_free();', '    op_handoff_trace(0x10, 0);\n    main_cdg_free();\n    op_handoff_trace(0x11, 0);')
            after = after.replace('    cfg_save();', '    cfg_save();\n    op_handoff_trace(0x12, 0);')
            after = after.replace('    gaiji_restore();', '    gaiji_restore();\n    op_handoff_trace(0x13, 0);')
            after = after.replace('    game_exit();', '    op_handoff_trace(0x14, 0);\n    game_exit();\n    op_handoff_trace(0x15, 0);')
            for binary in ("BINARY_MAIN", "BINARY_DEB"):
                statement = f'execl({binary}, {binary}, nullptr);'
                after = after.replace(statement, 'op_handoff_trace(0x16, 0);\n        ' + statement
                                      + '\n        op_handoff_trace(0x17, errno);')
        path.write_text(after)
        modified[source] = {"original_sha256": hashlib.sha256(before.encode()).hexdigest(),
                            "overlay_sha256": sha(path)}
    for source in ("src/op/start/start_game.inl", "src/op/start/start_extra.inl"):
        path = work / source
        before = path.read_text()
        after = before.replace('{\n', '{\n\top_handoff_trace(0x20, 0);\n', 1)
        after = after.replace('\tmain_cdg_free();', '\top_handoff_trace(0x21, 0);\n\tmain_cdg_free();\n\top_handoff_trace(0x22, 0);')
        for marker, statement in ((0x23, 'cfg_save();'), (0x24, 'gaiji_restore();'), (0x25, 'game_exit();')):
            after = after.replace(statement, statement + f'\n\top_handoff_trace(0x{marker:02X}, 0);')
        for binary in ("BINARY_MAIN", "BINARY_DEB"):
            statement = f'execl({binary}, {binary}, nullptr);'
            after = after.replace(statement, 'op_handoff_trace(0x26, 0);\n\t\t' + statement
                                  + '\n\t\top_handoff_trace(0x27, errno);')
        path.write_text(after)
        modified[source] = {"original_sha256": hashlib.sha256(before.encode()).hexdigest(),
                            "overlay_sha256": sha(path)}
    return modified


def link_relevant_sha(path: Path) -> str:
    digest = hashlib.sha256()
    for record in parse_omf(path.read_bytes()):
        if record.record_type != 0x88:  # COMENT is not a linker input.
            digest.update(bytes([record.record_type]))
            digest.update(len(record.data).to_bytes(2, "little"))
            digest.update(record.data)
    return digest.hexdigest()


def run(command: list[str], work: Path, env: dict[str, str], log: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=work, env=env, capture_output=True,
                            text=True, timeout=240)
    log.write_text(json.dumps(command) + f"\nexit={result.returncode}\n"
                   + result.stdout + result.stderr, encoding="utf-8")
    return result


def assemble(source: Path, obj: Path, work: Path, env: dict[str, str], log: Path) -> None:
    src = str(source.relative_to(work)).replace("/", "\\")
    dst = str(obj.relative_to(work)).replace("/", "\\")
    command = ["wine", "cmd", "/d", "/c",
               "set PATH=C:\\TASM50\\BIN;C:\\TC4\\BIN;%PATH%&&"
               f"tasm32 /m /mx /kh32768 /t /dGAME=4 /dTH04_LARGE_PRODUCT=1 {src} {dst}"]
    if run(command, work, env, log).returncode:
        raise RuntimeError(f"TASM failed: {log}")


def main(artifact: str = "maine") -> int:
    if artifact not in SOURCE_MANIFESTS:
        raise ValueError(f"unsupported native artifact: {artifact}")
    source_manifest = SOURCE_MANIFESTS[artifact]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check-manifest", action="store_true",
                        help="check the TH04 source graph without running Wine")
    parser.add_argument("--without-support", action="store_true",
                        help="link only TH04 source plus pinned Borland system libraries")
    parser.add_argument("--reuse-from", type=Path,
                        help="reuse verified objects with unchanged source and recorded dependencies")
    parser.add_argument("--handoff-trace", action="store_true",
                        help="private OP cleanup/exec or MAINE startup/score checkpoints")
    args = parser.parse_args()
    if args.check_manifest:
        if args.output_dir or args.without_support or args.reuse_from or args.handoff_trace:
            parser.error("--check-manifest cannot be combined with build options")
        sources, asm_sources = load_sources(artifact)
        print(json.dumps({"artifact": f"th04-{artifact}", "c_sources": len(sources),
                          "asm_sources": len(asm_sources),
                          "manifest_sha256": sha(source_manifest)}, sort_keys=True))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for a native link probe")
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or not output.is_relative_to(private):
        parser.error("output must be a new directory below .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    identities = [(RUNNER, RUNNER_SHA256)]
    if not args.without_support:
        identities.append((SUPPORT_LIB, SUPPORT_SHA256))
    for path, expected in identities:
        if sha(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")
    sources, asm_sources = load_sources(artifact)

    output.mkdir(parents=True)
    work = output / "source"
    shutil.copytree(ROOT / "src", work / "src")
    source_hashes = {source.as_posix(): sha(work / source) for source in sources + asm_sources}
    handoff_trace = ((handoff_trace_overlay(work) if artifact == "op"
                      else maine_handoff_trace_overlay(work)) if args.handoff_trace else None)
    (work / "bin").mkdir()
    if not args.without_support:
        shutil.copy2(SUPPORT_LIB, work / "bin/masters.lib")
    (work / "obj/product").mkdir(parents=True)
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")

    cache = {}
    if args.reuse_from:
        previous = args.reuse_from.resolve()
        if not previous.is_relative_to(private) or previous == output:
            parser.error("use an earlier private build as the object cache")
        prior = json.loads((previous / "receipt.json").read_text())
        if (prior["artifact"] != f"th04-{artifact}" or prior["compiler_flags"] != list(FLAGS)
                or prior["runner_sha256"] != RUNNER_SHA256
                or prior["support_lib_sha256"] != (None if args.without_support else SUPPORT_SHA256)):
            raise RuntimeError("object cache artifact/toolchain/options differ")
        for record in prior["objects"]:
            current = work / record["source"]
            # Generated BGIMAGE assembly records cannot attest its C++ headers.
            if (record["source"] == "src/shared/hardware/bgimage.cpp"
                    or not current.is_file() or sha(current) != record["source_sha256"]):
                continue
            obj = previous / "source" / record["object"]
            if sha(obj) != record["object_sha256"]:
                raise RuntimeError("object cache identity drift")
            description = describe_omf(obj.read_bytes())
            dependencies = description["dependency_paths"]
            unchanged = bool(dependencies)
            for dependency in dependencies:
                dependency = re.sub(r"/+", "/", dependency.replace("\\", "/"))
                if dependency.upper().startswith("C:/TC4/"):
                    continue  # Vendor headers are covered by toolchain attestation.
                old = previous / "source" / dependency
                new = work / dependency
                # The pinned DOS runner gives long compilation roots an 8.3
                # alias. The recorded compiler input and its hash already
                # bind that module to the logical source. Resolve only that
                # module's own dependency; every included file still needs
                # a real, hash-equal path in both staged trees.
                logical = Path(record["source"])
                module = (description["module_name"] or "").replace("\\", "/")
                alias = Path(dependency)
                if (not old.is_file() and dependency == module
                        and alias.parent == logical.parent
                        and alias.suffix == logical.suffix
                        and re.fullmatch(re.escape(logical.stem[:4]) + r"~[a-z0-9]{3}", alias.stem)):
                    old = previous / "source" / logical
                    new = work / logical
                if not old.is_file() or not new.is_file() or sha(old) != sha(new):
                    unchanged = False
                    break
            if unchanged:
                cache[record["source"]] = (record, obj)

    object_paths: list[Path] = []
    records: list[dict[str, str]] = []
    def checkpoint() -> None:
        # Preserve independently validated objects if a later source fails.
        # This incomplete receipt is a cache input, never a publishable build.
        (output / "receipt.json").write_text(json.dumps({
            "artifact": f"th04-{artifact}", "runner_sha256": RUNNER_SHA256,
            "compiler_flags": list(FLAGS),
            "support_lib_sha256": None if args.without_support else SUPPORT_SHA256,
            "scope": "incomplete compiler/assembler checkpoint",
            "objects": records, "link_complete": False, "link_exit": None,
            "link_errors": ["build incomplete"], "mz_header": None,
        }, indent=2) + "\n")
    checkpoint()
    for index, source in enumerate(sources):
        group = source.parts[1]
        obj_dir = work / "obj" / group / f"{index:03d}"
        obj_dir.mkdir(parents=True)
        if source.as_posix() in cache:
            prior_record, previous_obj = cache[source.as_posix()]
            obj = obj_dir / previous_obj.name
            shutil.copy2(previous_obj, obj)
            object_paths.append(obj)
            records.append(dict(prior_record, object=obj.relative_to(work).as_posix(),
                                reused_from=str(args.reuse_from)))
            checkpoint()
            continue
        extra = ["-B"] if source.as_posix() == "src/shared/hardware/bgimage.cpp" else []
        if group == artifact:
            extra.append(f"-DBINARY='{'E' if artifact == 'maine' else 'O'}'")
        command = ["wine", str(RUNNER), "-e", "-x", "tcc", *extra, *FLAGS,
                   f"-nobj/{group}/{index:03d}/", source.as_posix()]
        log = output / f"compile-{index:03d}.log"
        result = run(command, work, env, log)
        if extra[:1] == ["-B"]:
            generated = list(obj_dir.glob("*.asm"))
            if len(generated) != 1 or "Unable to execute command 'tasm.exe'" not in result.stdout + result.stderr:
                raise RuntimeError(f"BGIMAGE ASM generation failed: {log}")
            obj = generated[0].with_suffix(".obj")
            assemble(generated[0], obj, work, env, output / f"assemble-generated-{index:03d}.log")
        elif result.returncode:
            raise RuntimeError(f"TC4J failed: {log}")
        objects = list(obj_dir.glob("*.obj"))
        if len(objects) != 1:
            raise RuntimeError(f"expected one object: {log}")
        obj = objects[0]
        omf = describe_omf(obj.read_bytes())
        producer = "Turbo Assembler  Version 5.0" if extra[:1] == ["-B"] else "TC86 Borland C++ 4.02"
        if not any(producer in comment for comment in omf["translator_comments"]):
            raise RuntimeError(f"unexpected OMF producer: {source}")
        object_paths.append(obj)
        records.append({"source": source.as_posix(), "source_sha256": source_hashes[source.as_posix()],
                        "object": obj.relative_to(work).as_posix(), "object_sha256": sha(obj),
                        "link_relevant_sha256": link_relevant_sha(obj)})
        checkpoint()

    for index, source in enumerate(asm_sources):
        obj_dir = work / "obj/asm" / f"{index:03d}"
        obj_dir.mkdir(parents=True)
        obj = obj_dir / "unit.obj"
        if source.as_posix() in cache:
            prior_record, previous_obj = cache[source.as_posix()]
            shutil.copy2(previous_obj, obj)
            object_paths.append(obj)
            records.append(dict(prior_record, object=obj.relative_to(work).as_posix(),
                                reused_from=str(args.reuse_from)))
            checkpoint()
            continue
        assemble(work / source, obj, work, env, output / f"assemble-{index:03d}.log")
        omf = describe_omf(obj.read_bytes())
        if not any("Turbo Assembler  Version 5.0" in comment for comment in omf["translator_comments"]):
            raise RuntimeError(f"unexpected ASM OMF producer: {source}")
        object_paths.append(obj)
        records.append({"source": source.as_posix(), "source_sha256": source_hashes[source.as_posix()],
                        "object": obj.relative_to(work).as_posix(), "object_sha256": sha(obj),
                        "link_relevant_sha256": link_relevant_sha(obj)})
        checkpoint()

    objlist = " ".join(str(path.relative_to(work)).replace("/", "\\") for path in object_paths)
    response = work / f"obj/product/{artifact}.@l"
    libraries = ("emu.lib mathl.lib cl.lib" if args.without_support else
                 "bin\\masters.lib emu.lib mathl.lib cl.lib")
    response.write_text("-c -s -E c0l.obj " + objlist
                        + f", bin\\{artifact}-native.exe, obj\\product\\{artifact}-native.map, "
                        + libraries + "\n", encoding="ascii")
    command = ["wine", str(RUNNER), "-e", "-x", "tlink",
               f"@obj\\product\\{artifact}.@l"]
    link_log = output / "link.log"
    link = run(command, work, env, link_log)
    errors = re.findall(r"^Error: Undefined symbol (.+)$", link.stdout, re.M)
    link_errors = re.findall(r"^(?:Error|Fatal): (.+)$", link.stdout, re.M)
    warnings = re.findall(r"^Warning: (.+)$", link.stdout, re.M)
    exe = work / f"bin/{artifact}-native.exe"
    mz = parse_mz(exe.read_bytes()) if exe.exists() else None
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": (f"TH04-owned {artifact.upper()} source graph without historical support library"
                  if args.without_support else
                  f"TH04-owned {artifact.upper()} source graph and diagnostic support-library link"),
        "artifact": f"th04-{artifact}",
        "handoff_trace": handoff_trace,
        "runner_sha256": RUNNER_SHA256,
        "support_lib_sha256": None if args.without_support else SUPPORT_SHA256,
        "source_manifest_sha256": sha(source_manifest),
        "compiler_flags": list(FLAGS),
        "assembler_flags": ["/m", "/mx", "/kh32768", "/t", "/dGAME=4",
                            "/dTH04_LARGE_PRODUCT=1"],
        "objects": records,
        "reused_object_count": sum("reused_from" in record for record in records),
        "response_sha256": sha(response),
        "link_log_sha256": sha(link_log),
        "link_exit": link.returncode,
        "unresolved": errors,
        "link_errors": link_errors,
        "warnings": warnings,
        "mz_header": ({"sha256": sha(exe), "valid": mz.valid,
                "relocations": len(mz.relocations)} if mz else None),
        "link_complete": link.returncode == 0 and not link_errors and bool(mz and mz.valid),
        "limit": (
            "Historical-library calibration only; not a TH04-only product or runtime acceptance."
            if not args.without_support else
            f"TH04-only {artifact.upper()} build candidate; audit every relocation and ABI edge, then validate PC-98 runtime and packaging."
        ),
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"c_sources": len(sources), "asm_sources": len(asm_sources),
                      "objects": len(records), "link_exit": link.returncode,
                      "unresolved": len(errors), "warnings": len(warnings),
                      "link_errors": len(link_errors),
                      "mz_header_valid": mz.valid if mz else None,
                      "link_complete": receipt["link_complete"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
