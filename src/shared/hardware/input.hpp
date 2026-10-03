#ifndef TH04_SHARED_HARDWARE_INPUT_HPP
#define TH04_SHARED_HARDWARE_INPUT_HPP

typedef unsigned short input_t;

// Latched action bits, rather than BIOS scan codes. input_sense() accumulates
// them; input_reset_sense() clears the word and immediately takes a new sample.
extern input_t key_det;

void input_reset_sense(void);
void input_sense(void);
// Wait for release, then press. Only the press phase has a finite timeout;
// zero or 9999 repeats indefinitely, while a negative value skips that phase.
void pascal input_wait_for_change(int press_timeout_frames);

enum {
    INPUT_NONE = 0,
    INPUT_UP = 0x0001,
    INPUT_DOWN = 0x0002,
    INPUT_LEFT = 0x0004,
    INPUT_RIGHT = 0x0008,
    INPUT_BOMB = 0x0010,
    INPUT_SHOT = 0x0020,
    INPUT_CANCEL = 0x1000,
    INPUT_OK = 0x2000,
};

#endif
