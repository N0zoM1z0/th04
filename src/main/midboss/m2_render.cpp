#pragma option -zCMAI_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/main/frames.h"
#include "th04/main/scroll.hpp"
#include "th04/main/midboss/midboss.hpp"

void pascal near midboss2_render(void)
{
    register screen_x_t left;
    vram_y_t top;
    register int patnum;

    if(midboss.pos.cur.y.v <= 0) {
        return;
    }
    left = midboss.pos.cur.x.to_pixel();
    top = scroll_subpixel_y_to_vram_seg1(midboss.pos.cur.y.v - TO_SP(16));
    if(midboss.phase > 2) {
        return;
    }
    if(midboss.sprite == 0) {
        patnum = ((stage_frame_mod16 / 4) + 146);
    } else if(midboss.sprite == 1) {
        patnum = ((stage_frame_mod8 / 4) + 150);
    } else if(midboss.sprite == 2) {
        patnum = ((stage_frame_mod8 / 4) + 152);
    }
    midboss_put_generic(left, top, patnum);
}
