#!/usr/bin/env python3
"""Ordinary private X11 early/closed miss-window Bomb trials; no game-state writes."""

import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path

NATIVE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NATIVE / "port64"))
from verify_host_window import latest, row
from verify_window_route import rescue_bomb
from private_x11 import require_private_xvfb
from private_x11_keys import PrivateKeys
from reduce_window_route import reduce
from verify import require_elf_x86_64

SHA = "dbe172259122af8675c1f995933eefd75234f50b72f3459fdeeded49e5ff46e7"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def trial(exe, hdi, font, out, mode):
    display = require_private_xvfb()
    require_elf_x86_64(exe)
    assert sha(exe) == SHA
    assert (
        sha(hdi) == "0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd"
    )
    assert (
        sha(font) == "41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6"
    )
    pins = {
        str(p): sha(p)
        for p in (
            exe,
            hdi,
            font,
            Path(__file__),
            NATIVE / "port64/verify_window_route.py",
            NATIVE / "port64/private_x11.py",
            NATIVE / "port64/private_x11_keys.py",
            NATIVE / "port64/verify_host_window.py",
            NATIVE / "port64/reduce_window_route.py",
        )
    }
    out.mkdir(exist_ok=False)
    save = out / "saves"
    save.mkdir()
    cfg = bytes([3, 2, 2, 2, 1, 0, 0, 0, 0, 10])
    (save / "MIKO.CFG").write_bytes(cfg)
    trace = out / "trace/window.tsv"
    command = [
        str(exe),
        "--hdi",
        str(hdi),
        "--font-bmp",
        str(font),
        "--save-dir",
        str(save),
        "--title",
        "--mute",
        "--window-trace",
        str(trace.parent),
    ]
    actions = []
    log = (out / "window.log").open("wb")
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
    keyboard = None
    passed = False
    error = None
    observations = {}

    def wait(predicate, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("owned game exited before checkpoint")
            r = latest(trace)
            if r:
                assert r["audio_opens"] == r["audio_failed"] == 0
                if predicate(r):
                    return r
            time.sleep(0.001)
        raise RuntimeError("bounded checkpoint timeout; no automatic restart")

    def keys(desired, r):
        desired = set(desired)
        if desired == keyboard.held:
            return
        start = time.monotonic_ns()
        keyboard.set(desired)
        actions.append(
            dict(
                seq=r["seq"],
                stage=r["stage"],
                frame=r["frame"],
                scene=r["scene"],
                keys=sorted(desired),
                input_started_ns=start,
                issued_ns=time.monotonic_ns(),
            )
        )

    def press(key):
        r = wait(lambda _: True)
        keys([key], r)
        time.sleep(0.12)
        r = wait(lambda _: True)
        keys([], r)
        time.sleep(0.04)

    try:
        keyboard = PrivateKeys()
        wait(lambda _: True)
        windows = subprocess.run(
            ["xdotool", "search", "--onlyvisible", "--pid", str(process.pid)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        assert len(windows) == 1
        subprocess.run(["xdotool", "windowfocus", "--sync", windows[0]], check=True)
        wait(lambda r: r["scene"] == "menu")
        press("Return")
        wait(lambda r: r["scene"] == "character")
        press("Return")
        wait(lambda r: r["scene"] == "shot")
        press("Return")
        r = wait(lambda r: r["scene"] == "main")
        assert (
            r["rank"],
            r["character"],
            r["shot"],
            r["stage"],
            r["lives"],
            r["bombs"],
            r["credits"],
        ) == (3, 0, 0, 0, 2, 2, 0)
        keys(["z"], r)
        first = wait(
            lambda r: r["scene"] == "main" and 65 <= r["respawn"] <= 71, timeout=120
        )
        assert first["bombs"] == 2 and not first["bombing"] and first["misses"] == 0
        observations["first_hit"] = first
        if mode == "early":
            held, reason = rescue_bomb(first, 32)
            assert held == 32 | 0x800 and reason == "early-hit-window"
            keys(["z", "x"], first)
            after = wait(
                lambda r: (
                    r["scene"] == "main"
                    and r["seq"] > first["seq"]
                    and r["bombs"] == 1
                    and r["bombing"]
                    and not r["respawn"]
                )
            )
            assert after["misses"] == 0 and after["invincibility"] >= 240
            keys(["z"], after)
            observations["after_X"] = after
        else:
            closed = wait(lambda r: r["scene"] == "main" and 60 <= r["respawn"] <= 64)
            assert closed["bombs"] == 2 and closed["misses"] == 1
            assert rescue_bomb(closed, 32) == (32, None)
            keys(["z", "x"], closed)
            after = wait(
                lambda r: r["scene"] == "main" and r["frame"] >= closed["frame"] + 3
            )
            keys(["z"], after)
            assert (
                after["bombs"] == 2
                and after["bombing"] == 0
                and after["misses"] == 1
                and 0 < after["respawn"] < closed["respawn"]
            )
            observations.update(closed=closed, after_X=after)
        # Ordinary host Escape closes MAIN; this bounded probe does not accept a route.
        r = wait(lambda _: True)
        keys(["Escape"], r)
        process.wait(timeout=15)
        assert process.returncode == 0
        keyboard.close()
        keyboard = None
        log.close()
        assert (save / "MIKO.CFG").read_bytes() == cfg
        schedule = reduce(trace)
        rows = [row(l) for l in trace.read_text().splitlines() if l.startswith("R ")]
        main = [r for r in rows if r["scene"] == "main"]
        assert all(
            (
                r["rank"],
                r["character"],
                r["shot"],
                r["credits"],
                r["program"],
                r["generation"],
            )
            == (3, 0, 0, 0, 1, 2)
            for r in main
        )
        assert all(r["audio_opens"] == r["audio_failed"] == 0 for r in rows)
        transitions = []
        for a, b in zip(rows, rows[1:]):
            if (
                a["scene"] == b["scene"] == "main"
                and a["stage"] == b["stage"]
                and b["frame"] == a["frame"] + 1
                and 65 <= a["respawn"] <= 71
                and b["held"] & 0x800
                and b["bombs"] == a["bombs"] - 1
                and b["bombing"]
                and not b["respawn"]
                and b["invincibility"] == 255
                and b["misses"] == a["misses"]
            ):
                transitions.append(dict(before=a, after=b))
        if mode == "early":
            assert transitions, "no actual held X/stock/miss cancellation transition"
        else:
            assert not transitions and any(
                r["held"] & 0x800
                and r["bombs"] == 2
                and r["misses"] == 1
                and 0 < r["respawn"] <= 64
                and not r["bombing"]
                for r in main
            )
        for p, h in pins.items():
            assert sha(p) == h
        result = dict(
            passed=True,
            mode=mode,
            private_display=display,
            command=command,
            pins=pins,
            cfg=list(cfg),
            observations=observations,
            transitions=transitions,
            actions=actions,
            trace_sha256=sha(trace),
            schedule=schedule,
            files={p.name: sha(p) for p in save.iterdir()},
            scope=__doc__,
        )
        (out / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
        passed = True
        print(mode, "actual OS Bomb window PASS", len(rows), flush=True)
    except Exception as e:
        error = str(e)
        raise
    finally:
        if keyboard is not None:
            keyboard.close()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        log.close()
        (out / "actions.json").write_text(json.dumps(actions, indent=2) + "\n")
        (out / "terminal.json").write_text(
            json.dumps(
                dict(
                    passed=passed,
                    error=error,
                    mode=mode,
                    command=command,
                    pins=pins,
                    observations=observations,
                ),
                indent=2,
            )
            + "\n"
        )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("exe", "hdi", "font", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--mode", choices=("early", "late"), required=True)
    a = p.parse_args()
    trial(
        a.exe.resolve(), a.hdi.resolve(), a.font.resolve(), a.output.resolve(), a.mode
    )


if __name__ == "__main__":
    main()
