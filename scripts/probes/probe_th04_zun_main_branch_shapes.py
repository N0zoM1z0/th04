#!/usr/bin/env python3
"""Test semantic C++ branch shapes against the pinned ZUN _main CODE extent."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

from replay_th04_zun_cfg_init import code
from replay_th04_zun_source_only import (
    FLAGS, HEADERS, PAYLOAD, PAYLOAD_SHA256, ROOT, RUNNER, sha,
)

SOURCE = ROOT / "src/zun/resident/main.cpp"
TARGET_MAIN_SHA256 = "db04398b52ca5780c734f839e2cf3768718f7f7c65705a9cdb9e88e34aa64871"
BAD = '            dos_puts2("そんなオプション付けられても、困るんですけど\\n\\n");\n            return 1;'
ALREADY = '        dos_puts2("わたし、すでにいますよぉ\\n\\n");\n        return 1;'
NO_SPACE = '        dos_puts2("作れません、わたしの居場所がないの！\\n\\n");\n        return 1;'


def replace_once(source: str, before: str, after: str) -> str:
    if source.count(before) != 1:
        raise ValueError("maintained _main branch changed")
    return source.replace(before, after)


def variants(source: str) -> dict[str, str]:
    goto_both = source
    for branch in (BAD, ALREADY):
        goto_both = replace_once(goto_both, branch, branch.replace("return 1;", "goto failure;"))
    goto_all = replace_once(goto_both, NO_SPACE, NO_SPACE.replace("return 1;", "goto failure;"))
    ending = "    return 0;\n}\n"
    result = {
        "goto_bad_already": replace_once(goto_both, ending, "    return 0;\nfailure:\n    return 1;\n}\n"),
        "goto_all": replace_once(goto_all, ending, "    return 0;\nfailure:\n    return 1;\n}\n"),
        "local_message": replace_once(
            source, BAD,
            '            const char *message = "そんなオプション付けられても、困るんですけど\\n\\n";\n'
            '            dos_puts2(message);\n            return 1;',
        ),
        "const_local_result": replace_once(
            source, BAD,
            '            const int result = 1;\n'
            '            dos_puts2("そんなオプション付けられても、困るんですけど\\n\\n");\n'
            '            return result;',
        ),
        "local_result": replace_once(
            source, BAD,
            '            int result = 1;\n'
            '            dos_puts2("そんなオプション付けられても、困るんですけど\\n\\n");\n'
            '            return result;',
        ),
    }
    return result


def compile_one(name: str, label: str, source: str, output: Path) -> dict[str, object]:
    saved = output / name / label
    saved.mkdir(parents=True)
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    with tempfile.TemporaryDirectory(prefix=f"zun-main-{name}-{label}-", dir=output) as temporary:
        work = Path(temporary)
        (work / "obj/th04").mkdir(parents=True)
        for relative in HEADERS:
            destination = work / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
            os.utime(destination, (946684800, 946684800))
        relative = "src/zun/resident/main.cpp"
        destination = work / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.encode("cp932"))
        os.utime(destination, (946684800, 946684800))
        command = ["wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS, relative]
        completed = subprocess.run(
            command, cwd=work, env=environment, capture_output=True, text=True, timeout=120,
        )
        (saved / "compile.log").write_text(
            json.dumps(command) + f"\nexit={completed.returncode}\n"
            + completed.stdout + completed.stderr,
            encoding="utf-8",
        )
        object_path = work / "obj/th04/main.obj"
        if completed.returncode or not object_path.is_file():
            raise RuntimeError(f"{name}/{label}: TC4J failed: {saved / 'compile.log'}")
        object_data = object_path.read_bytes()
        (saved / "main.obj").write_bytes(object_data)
        compiled = code(object_path)
        (saved / "main.code").write_bytes(compiled)
        return {
            "object_sha256": sha(object_data),
            "code_size": len(compiled),
            "code_sha256": sha(compiled),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(x for x in manifest["artifacts"] if x["id"] == "th04-zun")
    target = (ROOT / target_info["private_path"]).read_bytes()
    payload = PAYLOAD.read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed target identity failed")
    target_main = payload[0xE67:0xF63]
    if sha(payload) != PAYLOAD_SHA256 or sha(target_main) != TARGET_MAIN_SHA256:
        raise RuntimeError("decoded target _main identity failed")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT, check=True,
                   capture_output=True, text=True)

    candidates = variants(SOURCE.read_text(encoding="utf-8"))
    output.mkdir(parents=True)
    results = {}
    for name, source in candidates.items():
        a = compile_one(name, "a", source, output)
        b = compile_one(name, "b", source, output)
        if a != b:
            raise RuntimeError(f"{name}: cold OMF/CODE results differ")
        results[name] = {"source_sha256": sha(source.encode("cp932")), **a}
        print(f"{name}: {a['code_size']} CODE bytes {a['code_sha256']}")
    receipt = {
        "schema_version": 1,
        "claim_scope": "semantic source-shape negatives for ZUN _main; no exact promotion",
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_main_extent": "ZUN.COM decoded _TEXT 0xE67..0xF62",
        "target_main_size": len(target_main),
        "target_main_sha256": sha(target_main),
        "maintained_source_sha256": sha(SOURCE.read_bytes()),
        "header_sha256": {path: sha((ROOT / path).read_bytes()) for path in HEADERS},
        "flags": list(FLAGS),
        "results": results,
        "all_fail_size_gate": all(r["code_size"] != len(target_main) for r in results.values()),
    }
    if not receipt["all_fail_size_gate"]:
        raise RuntimeError("a variant reached target size; inspect raw CODE before recording a negative")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
