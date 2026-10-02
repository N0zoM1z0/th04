#!/usr/bin/env python3
"""Replay a private OP or MAINE HDI probe under pinned DOSBox-X.

Run under ``xvfb-run -a``. A frame and a DOS boot log are diagnostics only;
the OP-to-MAINE transition must be observed before claiming MAINE execution.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
import tomllib

from prepare_th04_maine_diagnostic_hdi import Fat12, sha, u16, u32


ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis/runtime/candidates").resolve()


def scenario_defaults(path: Path) -> dict:
    settings = json.loads(path.read_text())["settings"]
    types = {"frame_second": int, "time_limit": int, "key_delay_ms": int,
             "audio": bool, "stop_after_frame": bool,
             "checkpoint_second": list, "input_event": list}
    if not isinstance(settings, dict) or any(
            key not in types or type(value) is not types[key]
            for key, value in settings.items()):
        raise ValueError("invalid runtime scenario settings")
    if (any(type(value) is not int for value in settings.get("checkpoint_second", []))
            or any(type(value) is not str for value in settings.get("input_event", []))):
        raise ValueError("invalid runtime scenario timeline")
    return settings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path,
                        help="JSON defaults; CLI scalars override and input/checkpoint lists append")
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--frame-second", type=int, default=10)
    parser.add_argument("--checkpoint-second", type=int, action="append", default=[],
                        help="capture an additional frame before the final frame; repeatable")
    parser.add_argument("--audio", action="store_true",
                        help="enable the mixer; host-key+W input events toggle WAV capture")
    parser.add_argument("--debug-port-e9", action="store_true",
                        help="record private guest checkpoints emitted through Bochs port E9")
    observer = parser.add_mutually_exclusive_group()
    observer.add_argument("--emulator-receipt", type=Path,
                        help="explicit private CPU-observer emulator attestation")
    observer.add_argument("--cpu-debugger-receipt", type=Path,
                         help="attested exception debugger for the unchanged primary emulator")
    parser.add_argument("--stop-after-frame", action="store_true",
                        help="close DOSBox-X through Ctrl+F9 after the final checkpoint")
    parser.add_argument("--time-limit", type=int, default=20)
    parser.add_argument(
        "--input-key",
        help="send one xdotool key to the DOSBox-X window before the frame",
    )
    parser.add_argument(
        "--input-second",
        type=float,
        help="host-second offset for --input-key (requires --input-key)",
    )
    parser.add_argument(
        "--input-event",
        action="append",
        default=[],
        metavar="KEY@SECOND",
        help="KEY@SECOND, down:KEY@SECOND or up:KEY@SECOND; repeat for a timeline",
    )
    parser.add_argument("--key-delay-ms", type=int, default=150,
                        help="xdotool tap duration; held down/up events are unchanged")
    scenario_parser = argparse.ArgumentParser(add_help=False)
    scenario_parser.add_argument("--scenario", type=Path)
    scenario_path = scenario_parser.parse_known_args()[0].scenario
    if scenario_path is not None:
        parser.set_defaults(**scenario_defaults(scenario_path))
    args = parser.parse_args()
    if not 1 <= args.key_delay_ms <= 1000:
        parser.error("key delay must be between 1 and 1000 milliseconds")
    input_specs = list(args.input_event)
    if (args.input_key is not None) != (args.input_second is not None):
        parser.error("--input-key and --input-second must be supplied together")
    if args.input_key is not None:
        input_specs.append(f"{args.input_key}@{args.input_second}")
    parsed_inputs = []
    for raw in input_specs:
        if "@" not in raw:
            parser.error("input events must use KEY@SECOND")
        key, second_text = raw.rsplit("@", 1)
        try:
            second = float(second_text)
        except ValueError:
            parser.error(f"invalid input-event offset: {raw}")
        if not key or second < 0 or second >= args.frame_second:
            parser.error("input events must be nonempty and before the frame")
        parsed_inputs.append((second, key))
    parsed_inputs.sort()
    checkpoints = sorted(set(args.checkpoint_second))
    if any(second < 1 or second >= args.frame_second for second in checkpoints):
        parser.error("checkpoints must be positive and before the final frame")
    prepared = args.prepared_dir.resolve()
    output = args.output_dir.resolve()
    if (not prepared.is_relative_to(PRIVATE) or not output.is_relative_to(PRIVATE)
            or output.exists() or args.frame_second < 1
            or args.time_limit <= args.frame_second + 2
            or any(second >= args.frame_second for second, _ in parsed_inputs)):
        parser.error("use private dirs and a frame before the time limit")
    prep_receipt_path = prepared / "receipt.json"
    prep = json.loads(prep_receipt_path.read_text(encoding="utf-8"))
    artifact = prep.get("artifact", "th04-maine")
    if artifact not in {"th04-main", "th04-maine", "th04-op", "th04-zun", "th04-game"}:
        raise ValueError(f"unsupported prepared artifact: {artifact}")
    source_image = prepared / "diagnostic.hdi"
    if sha(source_image.read_bytes()) != prep["diagnostic_hdi_sha256"]:
        raise ValueError("prepared HDI identity drift")

    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text(encoding="utf-8"))
    emulator_override = None
    cpu_debugger = None
    emulator_command = runtime["primary"]["command"]
    expected_emulator_sha = runtime["primary"]["binary_sha256"]
    if args.emulator_receipt is not None:
        from build_th04_cpu_fault_emulator import attest
        attestation = args.emulator_receipt.resolve()
        if not attestation.is_relative_to(ROOT / ".analysis/runtime/emulators"):
            parser.error("emulator attestation must be private")
        record_bytes = attestation.read_bytes()
        record = attest(attestation)
        private_binary = Path(record["binary"]).resolve()
        emulator_command = str(private_binary)
        expected_emulator_sha = record["binary_sha256"]
        emulator_override = dict(receipt=str(attestation), receipt_sha256=sha(record_bytes),
                                 scope=record["scope"], source_commit=record["source_commit"])
    executable_name = shutil.which(emulator_command)
    if executable_name is None:
        raise ValueError("pinned DOSBox-X is unavailable")
    executable = Path(executable_name).resolve()
    if not executable.is_file() or sha(executable.read_bytes()) != expected_emulator_sha:
        raise ValueError("DOSBox-X binary identity drift")
    if args.cpu_debugger_receipt is not None:
        from prepare_th04_primary_cpu_debugger import attest_debugger, command_prefix
        debugger_path = args.cpu_debugger_receipt.resolve()
        debugger_record = attest_debugger(debugger_path)
        if debugger_record["binary_sha256"] != expected_emulator_sha:
            raise ValueError("CPU debugger does not attest the active emulator")
        cpu_debugger = dict(receipt=str(debugger_path), receipt_sha256=sha(debugger_path.read_bytes()),
                            scope=debugger_record["scope"])
    source_conf = ROOT / runtime["primary"]["config"]
    conf_bytes = source_conf.read_bytes()
    if sha(conf_bytes) != runtime["primary"]["config_sha256"]:
        raise ValueError("pinned headless configuration identity drift")
    old = b"videodriver       = dummy"
    if conf_bytes.count(old) != 1:
        raise ValueError("expected one pinned video driver setting")

    output.mkdir(parents=True)
    image = output / "execution.hdi"
    shutil.copyfile(source_image, image)
    config = output / "dosbox-x-x11.conf"
    runtime_conf = conf_bytes.replace(old, b"videodriver       = x11")
    runtime_conf = runtime_conf.replace(b"[dosbox]\n", b"[dosbox]\nquit warning = false\n")
    if args.debug_port_e9:
        runtime_conf = runtime_conf.replace(
            b"[dosbox]\n", b"[dosbox]\nbochs debug port e9 = true\n")
    if args.audio:
        runtime_conf = runtime_conf.replace(b"nosound = true", b"nosound = false")
        runtime_conf = runtime_conf.replace(b"[dosbox]\n", b"[dosbox]\ncaptures = "
                                           + str(output / "captures").encode() + b"\n")
        (output / "captures").mkdir()
    config.write_bytes(runtime_conf)
    command = [
        str(executable), "-defaultconf", "-defaultmapper", "-conf", str(config),
        "-fastlaunch", "-nogui", "-nomenu", "-exit", "-time-limit",
        str(args.time_limit), "-c", f'imgmount 2 "{image}" -t hdd -fs none',
        "-c", "boot -l c",
    ]
    debug_log = output / "debug-port-e9.log"
    if args.debug_port_e9:
        command.extend(["-set", f"log logfile={debug_log}"])
    env = os.environ.copy()
    env.update({
        "SDL_VIDEODRIVER": "x11", "SDL_AUDIODRIVER": "dummy",
        "XDG_CACHE_HOME": str(output / "cache"),
        "XDG_CONFIG_HOME": str(output / "config"),
        "XDG_DATA_HOME": str(output / "data"),
    })
    if emulator_override is not None:
        env["TH04_CPU_FAULT_DIR"] = str(output)
    if cpu_debugger is not None:
        command = command_prefix(debugger_record) + command
        env.update(TH04_CPU_FAULT_DIR=str(output), TH04_CPU_DEBUG_FILE=debugger_record["debug_file"])
    # Font-ROM diagnostics can fill a pipe while we collect timed frames.
    # Stream directly to disk so observation cannot suspend the emulator.
    boot_log = output / "boot.log"
    log_stream = boot_log.open("w", encoding="utf-8")
    process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log_stream,
                               stderr=subprocess.STDOUT, text=True,
                               start_new_session=True)
    screenshot = output / "frame.png"
    host_timeout = False
    input_events = []
    input_failure = None
    early_exit_second = None
    next_input = 0
    checkpoint_frames = []
    next_checkpoint = 0
    try:
        started = time.monotonic()
        while True:
            elapsed = time.monotonic() - started
            if process.poll() is not None:
                early_exit_second = elapsed
                break
            if (next_input < len(parsed_inputs)
                    and elapsed >= parsed_inputs[next_input][0]):
                requested_second, input_key = parsed_inputs[next_input]
                action = "key"
                key = input_key
                if input_key.startswith(("down:", "up:")):
                    prefix, key = input_key.split(":", 1)
                    action = "keydown" if prefix == "down" else "keyup"
                    if not key:
                        raise ValueError("input event has no key")
                xdotool = shutil.which("xdotool")
                if xdotool is None:
                    raise ValueError("input events require xdotool")
                windows = subprocess.run(
                    [xdotool, "search", "--onlyvisible", "--name", "DOSBox-X"],
                    check=False, capture_output=True, text=True,
                ).stdout.split()
                if not windows:
                    input_failure = f"DOSBox-X window missing at input {input_key}@{requested_second}"
                    break
                for window in windows:
                    delay = ["--delay", str(args.key_delay_ms)] if action == "key" else []
                    subprocess.run(
                        [xdotool, action, *delay, "--window", window, key],
                        check=True, capture_output=True, text=True,
                    )
                input_events.append({
                    "key": input_key,
                    "action": action,
                    "requested_second": requested_second,
                    "observed_second": elapsed,
                    "window_ids": windows,
                })
                next_input += 1
            if (next_checkpoint < len(checkpoints)
                    and elapsed >= checkpoints[next_checkpoint]):
                second = checkpoints[next_checkpoint]
                frame = output / f"frame-{second:03d}s.png"
                subprocess.run(["import", "-window", "root", str(frame)], check=True,
                               timeout=10, capture_output=True)
                checkpoint_frames.append({"requested_second": second,
                    "observed_second": time.monotonic() - started,
                    "file": frame.name, "sha256": sha(frame.read_bytes())})
                next_checkpoint += 1
            remaining = args.frame_second - elapsed
            if remaining <= 0:
                break
            time.sleep(min(0.05, remaining))
        subprocess.run(["import", "-window", "root", str(screenshot)], check=True,
                       timeout=10, capture_output=True)
        if args.stop_after_frame and process.poll() is None:
            windows = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", "DOSBox-X"],
                                     capture_output=True, text=True).stdout.split()
            for window in windows:
                subprocess.run(["xdotool", "key", "--window", window, "ctrl+F9"], check=False,
                               capture_output=True)
        try:
            log, _ = process.communicate(
                timeout=(10 if args.stop_after_frame else
                         max(10, args.time_limit - args.frame_second + 10))
            )
        except subprocess.TimeoutExpired:
            host_timeout = True
            os.killpg(process.pid, signal.SIGKILL)
            log, _ = process.communicate(timeout=10)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate(timeout=10)
        log_stream.close()
    log = boot_log.read_text(encoding="utf-8", errors="replace")
    if args.debug_port_e9:
        if not debug_log.is_file():
            raise ValueError("Bochs debug port logging did not produce a log")
        log += debug_log.read_text(encoding="utf-8", errors="replace")
        boot_log.write_text(log, encoding="utf-8")
    if sha(source_image.read_bytes()) != prep["diagnostic_hdi_sha256"]:
        raise ValueError("prepared source HDI was modified")
    fs = Fat12(bytearray(image.read_bytes()))
    try:
        entry = fs.find_entry([fs.root], b"DIAG    TXT")
        marker = fs.file_bytes(u16(fs.image, entry + 26), u32(fs.image, entry + 28))
    except ValueError:
        marker = None
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        trace_entry = fs.find_entry(game_offsets, b"OPMARK  TXT")
        op_trace = fs.file_bytes(u16(fs.image, trace_entry + 26),
                                 u32(fs.image, trace_entry + 28))
    except ValueError:
        op_trace = None
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        cdg_entry = fs.find_entry(game_offsets, b"OPCDG   BIN")
        cdg_slots = fs.file_bytes(u16(fs.image, cdg_entry + 26),
                                  u32(fs.image, cdg_entry + 28))
    except ValueError:
        cdg_slots = None
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        mainhit_entry = fs.find_entry(game_offsets, b"MAINHIT TXT")
        mainhit = fs.file_bytes(u16(fs.image, mainhit_entry + 26),
                                u32(fs.image, mainhit_entry + 28))
    except ValueError:
        mainhit = None
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        input_entry = fs.find_entry(game_offsets, b"INPUT   BIN")
        input_trace = fs.file_bytes(u16(fs.image, input_entry + 26),
                                    u32(fs.image, input_entry + 28))
    except ValueError:
        input_trace = None
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        main_trace_entry = fs.find_entry(game_offsets, b"MAIN    BIN")
        main_trace = fs.file_bytes(u16(fs.image, main_trace_entry + 26),
                                   u32(fs.image, main_trace_entry + 28))
    except ValueError:
        main_trace = None
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        ems_trace_entry = fs.find_entry(game_offsets, b"EMS     BIN")
        ems_trace = fs.file_bytes(u16(fs.image, ems_trace_entry + 26),
                                  u32(fs.image, ems_trace_entry + 28))
    except ValueError:
        ems_trace = None
    stage_trace_files = {}
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        for stage_marker in range(256):
            name = (f"STG{stage_marker:02X}".ljust(8) + "BIN").encode("ascii")
            try:
                stage_entry = fs.find_entry(game_offsets, name)
            except ValueError:
                continue
            stage_trace_files[f"{stage_marker:02X}"] = fs.file_bytes(
                u16(fs.image, stage_entry + 26),
                u32(fs.image, stage_entry + 28),
            ).hex()
    except ValueError:
        stage_trace_files = {}
    game_trace_files = {}
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        for game_marker in range(256):
            name = (f"GAM{game_marker:02X}".ljust(8) + "BIN").encode("ascii")
            try:
                game_entry = fs.find_entry(game_offsets, name)
            except ValueError:
                continue
            game_trace_files[f"{game_marker:02X}"] = fs.file_bytes(
                u16(fs.image, game_entry + 26),
                u32(fs.image, game_entry + 28),
            ).hex()
    except ValueError:
        game_trace_files = {}
    player_trace_files = {}
    try:
        game_dir = fs.find_entry([fs.root], b"GENSO      ")
        game_offsets = [fs.cluster_offset(cluster) for cluster in
                        fs.chain(u16(fs.image, game_dir + 26))]
        for player_marker in range(256):
            name = (f"PLY{player_marker:02X}".ljust(8) + "BIN").encode("ascii")
            try:
                player_entry = fs.find_entry(game_offsets, name)
            except ValueError:
                continue
            player_trace_files[f"{player_marker:02X}"] = fs.file_bytes(
                u16(fs.image, player_entry + 26),
                u32(fs.image, player_entry + 28),
            ).hex()
    except ValueError:
        player_trace_files = {}
    expected_boot = runtime["primary"]["execution"]["boot_required_log_markers"]
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "diagnostic PC-98 boot frame; product execution needs a separate checkpoint",
        "scenario": ({"file": str(scenario_path.resolve()),
                      "sha256": sha(scenario_path.read_bytes())} if scenario_path else None),
        "artifact": artifact,
        "prepared_receipt_sha256": sha(prep_receipt_path.read_bytes()),
        "prepared_hdi_sha256": prep["diagnostic_hdi_sha256"],
        "executed_hdi_sha256": sha(image.read_bytes()),
        "artifact_source": prep.get("artifact_source", prep.get("maine_source")),
        "startup": prep["startup"],
        "emulator_sha256": expected_emulator_sha,
        "emulator_override": emulator_override,
        "cpu_debugger": cpu_debugger,
        "x11_config_sha256": sha(config.read_bytes()),
        "audio_enabled": args.audio,
        "audio_captures": [{"file": str(path.relative_to(output)), "size": path.stat().st_size,
                            "sha256": sha(path.read_bytes())}
                           for path in sorted((output / "captures").glob("*.wav"))],
        "command": command,
        "frame_second": args.frame_second,
        "input_events": input_events,
        "input_failure": input_failure,
        "key_delay_ms": args.key_delay_ms,
        "early_exit_second": early_exit_second,
        "stop_after_frame": args.stop_after_frame,
        "checkpoint_frames": checkpoint_frames,
        "host_timeout": host_timeout,
        "returncode": process.returncode,
        "missing_boot_markers": [item for item in expected_boot if item not in log],
        "diagnostic_marker_hex": marker.hex() if marker is not None else None,
        "op_trace_marker_hex": op_trace.hex() if op_trace is not None else None,
        "op_cdg_slots_hex": cdg_slots.hex() if cdg_slots is not None else None,
        "mainhit_marker_hex": mainhit.hex() if mainhit is not None else None,
        "input_trace_hex": input_trace.hex() if input_trace is not None else None,
        "main_trace_hex": main_trace.hex() if main_trace is not None else None,
        "ems_trace_hex": ems_trace.hex() if ems_trace is not None else None,
        "stage_trace_files_hex": stage_trace_files,
        "game_trace_files_hex": game_trace_files,
        "player_trace_files_hex": player_trace_files,
        "boot_log_sha256": sha(log.encode()),
        "debug_port_e9": args.debug_port_e9,
        "frame_sha256": sha(screenshot.read_bytes()),
    }
    if artifact == "th04-maine":
        receipt["maine_source"] = receipt["artifact_source"]
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(output / "receipt.json"),
                      "returncode": process.returncode,
                      "marker_hex": receipt["diagnostic_marker_hex"]}, sort_keys=True))
    # A frame probe may stop the emulator after its checkpoint. The receipt
    # records this separately from an emulator crash or missing boot marker.
    if (input_failure or early_exit_second is not None
            or (process.returncode and not host_timeout) or receipt["missing_boot_markers"]):
        raise ValueError("diagnostic boot did not pass host smoke markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
