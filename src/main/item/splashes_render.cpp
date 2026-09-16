#pragma option -zCCIRCLE_TEXT -zPmain_01

#include "x86real.h"
#include "th04/hardware/grcg.hpp"
#include "th04/main/item/splash.hpp"
#include "th04/main/drawp.hpp"
#include "th04/math/vector.hpp"

extern "C" void pascal near item_splashes_render(void)
{
    int i;
    subpixel_t radius;
    register item_splash_t near *splash;
    register int angle;

    grcg_setcolor_direct(15);
    splash = item_splashes;
    i = 0;
    for(; i < ITEM_SPLASH_COUNT; (i++, splash++)) {
        if(splash->flag != F_ALIVE) {
            continue;
        }
        angle = 0;
        for(; angle < 256; angle += (256 / ITEM_SPLASH_DOTS)) {
            radius = splash->radius_cur.v;
            vector2_at(
                drawpoint,
                splash->center.x.v,
                splash->center.y.v,
                radius,
                angle
            );
            if(drawpoint.y.v < 0) {
                continue;
            }
            if(drawpoint.y.v >= TO_SP(PLAYFIELD_H)) {
                continue;
            }
            if(drawpoint.x.v < 0) {
                continue;
            }
            if(drawpoint.x.v >= TO_SP(PLAYFIELD_W)) {
                continue;
            }
            _DX = scroll_subpixel_y_to_vram_seg1(
                drawpoint.y.v + TO_SP(PLAYFIELD_TOP)
            );
            _AX = TO_PIXEL(drawpoint.x.v) + PLAYFIELD_LEFT;
            item_splash_dot_render(_AX, _DX);
        }
    }
}
