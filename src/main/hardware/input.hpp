#ifndef TH04_MAIN_HARDWARE_INPUT_HPP
#define TH04_MAIN_HARDWARE_INPUT_HPP

#include "src/shared/platform/types.hpp"

// Keep the declaration order of the historical inputvar.h/input.h pair:
// globals precede the entry points so TC4J emits the same EXTDEF ordering.
typedef uint16_t input_t;
// Replay stores only the low-byte actions. Live input also carries keypad
// diagonals and menu/Q bits in the high byte; do not widen replay storage.
typedef uint8_t input_replay_t;

static const input_replay_t INPUT_NONE = 0x0000;
static const input_replay_t INPUT_UP = 0x0001;
static const input_replay_t INPUT_DOWN = 0x0002;
static const input_replay_t INPUT_LEFT = 0x0004;
static const input_replay_t INPUT_RIGHT = 0x0008;
static const input_replay_t INPUT_BOMB = 0x0010;
static const input_replay_t INPUT_SHOT = 0x0020;
static const input_t INPUT_UP_LEFT = 0x0100;
static const input_t INPUT_UP_RIGHT = 0x0200;
static const input_t INPUT_DOWN_LEFT = 0x0400;
static const input_t INPUT_DOWN_RIGHT = 0x0800;
static const input_t INPUT_CANCEL = 0x1000;
static const input_t INPUT_OK = 0x2000;
static const input_t INPUT_Q = 0x4000;

static const input_t INPUT_MOVEMENT = (
	INPUT_UP | INPUT_DOWN | INPUT_LEFT | INPUT_RIGHT |
	INPUT_UP_LEFT | INPUT_UP_RIGHT | INPUT_DOWN_LEFT | INPUT_DOWN_RIGHT
);

extern input_t key_det;
// BIOS modifier state is sampled separately from the latched action word.
extern bool shiftkey;

// Reset clears keyboard/joystick action latches, then falls through to sense.
// Plain sense ORs new actions into key_det, preserving earlier samples.
void input_reset_sense(void);
void input_sense(void);
// Release is unbounded. Press timeout 0 or 9999 repeats; negatives skip press.
void pascal input_wait_for_change(int press_timeout_frames);

// The interface alias is part of the historical TH04 header and is used by
// UI code that intentionally ignores held-key distinctions.
#define input_reset_sense_interface input_reset_sense

#endif
