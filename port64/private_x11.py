"""Reject host-desktop input; these controllers require a private Xvfb server."""
import os
from pathlib import Path
import re

# TH04 player_motion.hpp and host_window::input use the same held-key ABI.
HELD_KEYS = ((1, "Up"), (2, "Down"), (4, "Left"), (8, "Right"),
             (32, "z"), (2048, "x"))

def key_names(held, shift):
    if held & ~0x82f:
        raise ValueError("unsupported route input bits")
    result = {key for bit, key in HELD_KEYS if held & bit}
    if shift:
        result.add("Shift_L")
    return result

def require_private_xvfb():
    display = os.environ.get("DISPLAY", "")
    match = re.fullmatch(r":([0-9]+)(?:\.[0-9]+)?", display)
    if not match:
        raise RuntimeError("controller requires a local private Xvfb DISPLAY")
    number = match.group(1)
    lock = Path("/tmp/.X" + number + "-lock")
    pid = int(lock.read_text().strip())
    proc = Path("/proc") / str(pid)
    argv = [part.decode() for part in (proc / "cmdline").read_bytes().split(b"\0") if part]
    if (proc.stat().st_uid != os.getuid() or not argv or
            Path(argv[0]).name != "Xvfb" or ":" + number not in argv or
            not any(argv[i:i+2] == ["-nolisten", "tcp"] for i in range(len(argv)-1))):
        raise RuntimeError("input is allowed only on our local Xvfb with TCP disabled")
    return dict(display=display, server_pid=pid, server_argv=argv)
