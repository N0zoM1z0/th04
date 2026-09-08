#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"

extern signed char reimu_bg_pulse_direction;
extern bool palette_changed;

extern "C" void near reimu_bg_pulse(void)
{
    if(reimu_bg_pulse_direction == 0) {
        Palettes[0].c.r++;
        if(Palettes[0].c.r >= 240) {
            reimu_bg_pulse_direction = 1;
        }
    } else {
        Palettes[0].c.r--;
        if(Palettes[0].c.r <= 64) {
            reimu_bg_pulse_direction = 0;
        }
    }
    palette_changed = true;
}
