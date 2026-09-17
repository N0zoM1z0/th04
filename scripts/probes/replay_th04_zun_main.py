#!/usr/bin/env python3
"""Diagnose maintained ZUN resident main source in two isolated TC4J builds.

The combined object still uses ReC98 headers and link inputs. This script
records a source-present comparison; it does not accept an exact unit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import tomllib

from replay_th04_zun_cfg_init import (
    ROOT, SNAPSHOT, SOURCE as CFG_SOURCE, UPSTREAM_SOURCE_SHA,
    BASELINE_COM_SHA, BASELINE_FLAT_SHA, RESIDENT_HEADER, CFG_HEADER,
    DEFAULTS_HEADER, API_HEADER, materialize_local_headers,
    localize_wrapper_includes,
    code, run, sha, wine_cmd, wine_env,
)

MAIN_SOURCE = ROOT / "src/zun/resident/main.cpp"
PAYLOAD = ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin"
PAYLOAD_SHA = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
TARGET_MAIN_SHA = "db04398b52ca5780c734f839e2cf3768718f7f7c65705a9cdb9e88e34aa64871"
CFG_CODE_SHA = "4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4"


def main_text(comma_return: bool) -> str:
    text = MAIN_SOURCE.read_text()
    if comma_return:
        replacements = (
            ('            dos_puts2("そんなオプション付けられても、困るんですけど\\n\\n");\n'
             '            return 1;',
             '            return (dos_puts2("そんなオプション付けられても、困るんですけど\\n\\n"), 1);'),
            ('        dos_puts2("わたし、すでにいますよぉ\\n\\n");\n'
             '        return 1;',
             '        return (dos_puts2("わたし、すでにいますよぉ\\n\\n"), 1);'),
        )
        for before, after in replacements:
            if text.count(before) != 1:
                raise ValueError("comma-return control no longer matches maintained source")
            text = text.replace(before, after)
    return text


def build(label: str, snapshot: Path, output: Path, source_text: str) -> dict[str, object]:
    if sha((snapshot / "th04/res_huma.cpp").read_bytes()) != UPSTREAM_SOURCE_SHA:
        raise ValueError(f"{label}: unexpected ReC98 C++ source")
    if sha((snapshot / "bin/th04/res_huma.com").read_bytes()) != BASELINE_COM_SHA:
        raise ValueError(f"{label}: unexpected ReC98 component")
    if sha((snapshot / "bin/th04/zun.com").read_bytes()) != BASELINE_FLAT_SHA:
        raise ValueError(f"{label}: unexpected ReC98 flat composite")

    work = output / "work" / label / "source"
    shutil.copytree(snapshot, work, symlinks=True)
    saved = output / "outputs" / label
    saved.mkdir(parents=True)
    cfg = work / "th04/zun/config/cfg_init.cpp"
    main = work / "th04/zun/resident/main.cpp"
    cfg.parent.mkdir(parents=True)
    main.parent.mkdir(parents=True)
    cfg.write_bytes(CFG_SOURCE.read_text().encode("cp932"))
    main.write_bytes(source_text.encode("cp932"))
    materialize_local_headers(work)

    upstream = localize_wrapper_includes(
        (work / "th04/res_huma.cpp").read_bytes().decode("cp932")
    )
    marker = "char debug = 0;"
    if upstream.count(marker) != 1:
        raise ValueError(f"{label}: unrecognized ReC98 source boundary")
    wrapper = (
        upstream[:upstream.index(marker)]
        + '#include "th04/zun/config/cfg_init.cpp"\n'
        + '#include "th04/zun/resident/main.cpp"\n'
    )
    (work / "th04/res_huma.cpp").write_bytes(wrapper.encode("cp932"))
    (saved / "wrapper.cpp").write_bytes(wrapper.encode("cp932"))

    object_path = work / "obj/th04/res_huma.obj"
    object_path.unlink(missing_ok=True)
    run(
        wine_cmd("tcc", "-c", "-I.", "-O", "-b-", "-3", "-Z", "-d",
                 "-DGAME=4", "-mt", "-nobj/th04/", "th04/res_huma.cpp"),
        work, saved / "compile.log", wine_env(),
    )
    if not object_path.is_file():
        raise ValueError(f"{label}: no compiled OMF")
    obj = object_path.read_bytes()
    (saved / "res_huma.obj").write_bytes(obj)
    compiled = code(saved / "res_huma.obj")
    if len(compiled) != 398 or sha(compiled[:0x98]) != CFG_CODE_SHA:
        raise ValueError(f"{label}: unexpected compiled CODE extents")
    (saved / "main.code").write_bytes(compiled[0x98:])

    standalone_path = work / "obj/th04/main.obj"
    standalone_path.unlink(missing_ok=True)
    run(
        wine_cmd("tcc", "-c", "-I.", "-O", "-b-", "-3", "-Z", "-d",
                 "-DGAME=4", "-mt", "-nobj/th04/", "th04/zun/resident/main.cpp"),
        work, saved / "standalone-main.log", wine_env(),
    )
    if not standalone_path.is_file():
        raise ValueError(f"{label}: no standalone main OMF")
    (saved / "main.obj").write_bytes(standalone_path.read_bytes())
    standalone_code = code(saved / "main.obj")
    if len(standalone_code) != 246:
        raise ValueError(f"{label}: unexpected standalone main CODE extent")

    component_path = work / "bin/th04/res_huma.com"
    component_path.unlink(missing_ok=True)
    run(wine_cmd("tlink", r"@obj\th04\res_huma.@l"),
        work, saved / "link.log", wine_env())
    if not component_path.is_file():
        raise ValueError(f"{label}: no linked component")
    (saved / "res_huma.com").write_bytes(component_path.read_bytes())
    (saved / "res_huma.map").write_bytes((work / "obj/th04/res_huma.map").read_bytes())
    return {
        "omf_sha256": sha(obj),
        "code_sha256": sha(compiled),
        "cfg_code_sha256": sha(compiled[:0x98]),
        "main_code_size": len(compiled[0x98:]),
        "main_code_sha256": sha(compiled[0x98:]),
        "standalone_main_omf_sha256": sha(standalone_path.read_bytes()),
        "standalone_main_code_sha256": sha(standalone_code),
        "component_sha256": sha(component_path.read_bytes()),
        "map_sha256": sha((saved / "res_huma.map").read_bytes()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-a", type=Path, default=SNAPSHOT / "a/source")
    parser.add_argument("--snapshot-b", type=Path, default=SNAPSHOT / "b/source")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--keep-workdirs", action="store_true")
    parser.add_argument("--comma-return-control", action="store_true",
                        help="test whether two comma-return branches retain target call placement")
    args = parser.parse_args()
    private_root = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        probe_root = private_root / "reconstruction/probes"
        probe_root.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="zun-main-replay-", dir=probe_root))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private_root):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    targets = tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
    target = next(t for t in targets if t["id"] == "th04-zun")
    if sha((ROOT / target["private_path"]).read_bytes()) != target["sha256"]:
        raise ValueError("pinned packed target identity failed")
    payload = PAYLOAD.read_bytes()
    target_main = payload[0xE67:0xF63]
    if sha(payload) != PAYLOAD_SHA or sha(target_main) != TARGET_MAIN_SHA:
        raise ValueError("independently decoded target payload identity failed")
    source_text = main_text(args.comma_return_control)
    results = {
        "a": build("a", args.snapshot_a.resolve(), output, source_text),
        "b": build("b", args.snapshot_b.resolve(), output, source_text),
    }
    for field in ("code_sha256", "main_code_sha256", "standalone_main_code_sha256",
                  "component_sha256", "map_sha256"):
        if results["a"][field] != results["b"][field]:
            raise ValueError(f"A/B {field} differs")
    receipt = {
        "schema_version": 1,
        "claim_scope": "source-present ZUN _main; diagnostic ReC98 composite; no exact promotion",
        "artifact": "th04-zun",
        "target_sha256": target["sha256"],
        "target_payload_sha256": PAYLOAD_SHA,
        "target_main_load_extent": "com-payload/_TEXT 0xE67..0xF62",
        "target_main_size": len(target_main),
        "target_main_sha256": sha(target_main),
        "product_main_source_sha256": sha(MAIN_SOURCE.read_bytes()),
        "compiled_main_source_sha256": sha(source_text.encode("cp932")),
        "comma_return_control": args.comma_return_control,
        "product_cfg_source_sha256": sha(CFG_SOURCE.read_bytes()),
        "resident_header_sha256": sha(RESIDENT_HEADER.read_bytes()),
        "cfg_header_sha256": sha(CFG_HEADER.read_bytes()),
        "defaults_header_sha256": sha(DEFAULTS_HEADER.read_bytes()),
        "runtime_api_header_sha256": sha(API_HEADER.read_bytes()),
        "builds": results,
        "main_code_size_difference": len(target_main) - results["a"]["main_code_size"],
        "exact": False,
        "limitations": "The natural source omits three inert ReC98 statements and compiles six bytes shorter. ReC98 headers, support objects, and link inputs remain external.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if not args.keep_workdirs:
        shutil.rmtree(output / "work")
    print(json.dumps({"receipt": str(output / "receipt.json"), "exact": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
