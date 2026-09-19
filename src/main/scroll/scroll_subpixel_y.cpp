#pragma option -zCCIRCLE_TEXT -zPmain_01 -k- -G

#include "x86real.h"
#include "src/main/math/subpixel.hpp"

extern vram_y_t scroll_line;
extern bool scroll_active;

extern "C" vram_y_t pascal near scroll_subpixel_y_to_vram_seg1(subpixel_t y)
{
    #define ret static_cast<vram_y_t>(_AX)

    _BX = _SP;
    ret = peek(_SS, (_BX + 2));
    ret = TO_PIXEL(ret);
    if(scroll_active) {
        ret += scroll_line;
    }
    if(ret < 0) {
        ret += RES_Y;
    } else if(ret >= RES_Y) {
        ret -= RES_Y;
    }
    return ret;

    #undef ret
}

#pragma option -k.
