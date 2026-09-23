#pragma option -zCSHARED

#include "src/shared/hardware/frame_delay.hpp"
#include "src/shared/hardware/input.hpp"

void pascal input_wait_for_change(int frames_to_wait)
{
    int frame = 0;

    do {
        input_reset_sense();
        frame_delay(1);
        input_sense();
    } while(key_det != INPUT_NONE);

    if(!frames_to_wait) {
        frames_to_wait = 9999;
    }

    while(frame < frames_to_wait) {
        input_reset_sense();
        frame_delay(1);
        input_sense();
        if(key_det != INPUT_NONE) {
            break;
        }
        frame++;
        if(frames_to_wait == 9999) {
            frame = 0;
        }
    }
}
