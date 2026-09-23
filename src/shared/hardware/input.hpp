#ifndef TH04_SHARED_HARDWARE_INPUT_HPP
#define TH04_SHARED_HARDWARE_INPUT_HPP

extern unsigned short key_det;

void input_reset_sense(void);
void input_sense(void);
void pascal input_wait_for_change(int frames);

enum {
    INPUT_NONE = 0
};

#endif
