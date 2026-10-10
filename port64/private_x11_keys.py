"""Persistent ordinary XTest keys, restricted to a checked private Xvfb.

This is an external OS input controller. It neither opens the host display nor
calls game code. A round trip completes each key-set change on the X server;
the game still receives and samples the resulting SDL keyboard events itself.
"""
import ctypes as C
import os

from private_x11 import require_private_xvfb


class PrivateKeys:
    NAMES = ('Up', 'Down', 'Left', 'Right', 'z', 'x', 'Shift_L',
             'Return', 'KP_Enter', 'Escape')

    def __init__(self):
        self.identity = require_private_xvfb()
        self.held = set()
        self.display = None
        self.xlib = C.CDLL('libX11.so.6')
        self.xtest = C.CDLL('libXtst.so.6')
        self.xlib.XOpenDisplay.argtypes = [C.c_char_p]
        self.xlib.XOpenDisplay.restype = C.c_void_p
        self.xlib.XCloseDisplay.argtypes = [C.c_void_p]
        self.xlib.XCloseDisplay.restype = C.c_int
        self.xlib.XStringToKeysym.argtypes = [C.c_char_p]
        self.xlib.XStringToKeysym.restype = C.c_ulong
        self.xlib.XKeysymToKeycode.argtypes = [C.c_void_p, C.c_ulong]
        self.xlib.XKeysymToKeycode.restype = C.c_ubyte
        self.xlib.XSync.argtypes = [C.c_void_p, C.c_int]
        self.xlib.XSync.restype = C.c_int
        self.xlib.XQueryKeymap.argtypes = [C.c_void_p, C.POINTER(C.c_char)]
        self.xlib.XQueryKeymap.restype = C.c_int
        self.xtest.XTestQueryExtension.argtypes = [C.c_void_p] + [C.POINTER(C.c_int)] * 4
        self.xtest.XTestQueryExtension.restype = C.c_int
        self.xtest.XTestFakeKeyEvent.argtypes = [C.c_void_p, C.c_uint, C.c_int, C.c_ulong]
        self.xtest.XTestFakeKeyEvent.restype = C.c_int
        try:
            self.display = self.xlib.XOpenDisplay(self.identity['display'].encode())
            if not self.display:
                raise RuntimeError('cannot connect to the checked private Xvfb')
            values = [C.c_int() for _ in range(4)]
            if not self.xtest.XTestQueryExtension(self.display, *[C.byref(v) for v in values]):
                raise RuntimeError('private Xvfb has no XTest extension')
            self.codes = {name: int(self.xlib.XKeysymToKeycode(
                self.display, self.xlib.XStringToKeysym(name.encode()))) for name in self.NAMES}
            if not all(self.codes.values()) or len(set(self.codes.values())) != len(self.codes):
                raise RuntimeError('missing or aliased private keycodes')
        except Exception:
            self.close()
            raise

    def set(self, desired):
        desired = set(desired)
        if not self.display:
            raise RuntimeError('private keyboard is closed')
        if desired - self.codes.keys():
            raise ValueError('unsupported private controller key')
        if os.environ.get('DISPLAY') != self.identity['display']:
            raise RuntimeError('DISPLAY changed during private input')
        # Keep release-before-press ordering, with one connection and round trip.
        for pressed, names in ((0, self.held - desired), (1, desired - self.held)):
            for name in sorted(names):
                if not self.xtest.XTestFakeKeyEvent(self.display, self.codes[name], pressed, 0):
                    raise RuntimeError('private XTest key request failed')
                if pressed:
                    self.held.add(name)
                else:
                    self.held.discard(name)
        self.xlib.XSync(self.display, 0)

    def observed(self):
        """Read server key bits for isolated controller checks, not game state."""
        state = C.create_string_buffer(32)
        self.xlib.XQueryKeymap(self.display, state)
        return {name for name, code in self.codes.items()
                if state.raw[code // 8] & (1 << (code % 8))}

    def close(self):
        if self.display:
            for name in sorted(self.held):
                self.xtest.XTestFakeKeyEvent(self.display, self.codes[name], 0, 0)
            self.xlib.XSync(self.display, 0)
            self.xlib.XCloseDisplay(self.display)
            self.display = None
            self.held.clear()
