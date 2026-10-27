"""Reject host-desktop input; these controllers require a private Xvfb server."""
import os
import ctypes
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


def request_window_close(window):
    """Send WM_DELETE_WINDOW on our private server, preserving MAIN Esc/pause."""
    require_private_xvfb()
    class Data(ctypes.Union):
        _fields_ = [('b', ctypes.c_char * 20), ('l', ctypes.c_long * 5)]
    class Client(ctypes.Structure):
        _fields_ = [('type', ctypes.c_int), ('serial', ctypes.c_ulong),
                    ('send_event', ctypes.c_int), ('display', ctypes.c_void_p),
                    ('window', ctypes.c_ulong), ('message_type', ctypes.c_ulong),
                    ('format', ctypes.c_int), ('data', Data)]
    class Event(ctypes.Union):
        _fields_ = [('client', Client), ('pad', ctypes.c_long * 24)]
    x = ctypes.CDLL('libX11.so.6')
    x.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x.XOpenDisplay.restype = ctypes.c_void_p
    x.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    x.XInternAtom.restype = ctypes.c_ulong
    x.XSendEvent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int,
                            ctypes.c_long, ctypes.POINTER(Event)]
    x.XCloseDisplay.argtypes = [ctypes.c_void_p]
    display = x.XOpenDisplay(None)
    if not display:
        raise RuntimeError('cannot open private Xvfb for owned window close')
    try:
        event = Event()
        event.client.type = 33
        event.client.display = display
        event.client.window = int(window, 0)
        event.client.message_type = x.XInternAtom(display, b'WM_PROTOCOLS', False)
        event.client.format = 32
        event.client.data.l[0] = x.XInternAtom(display, b'WM_DELETE_WINDOW', False)
        if not x.XSendEvent(display, event.client.window, False, 0, ctypes.byref(event)):
            raise RuntimeError('private WM_DELETE_WINDOW send failed')
    finally:
        x.XCloseDisplay(display)
