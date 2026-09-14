#pragma option -zCTILE_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/main/frames.h"
#include "th04/main/scroll.hpp"
#include "th04/main/phase.hpp"
#include "th04/main/midboss/midboss.hpp"

static const int MIDBOSSX_PAT_BASE = 148;

void pascal near midbossx_render(void)
{
    if(
        (midboss.pos.cur.y.v <= -TO_SP(16)) ||
        (midboss.pos.cur.x.v <= -TO_SP(16)) ||
        (midboss.pos.cur.x.v >= TO_SP(392))
    ) {
        return;
    }

    screen_x_t left = (midboss.pos.cur.x.to_pixel() + 16);
    vram_y_t top = scroll_subpixel_y_to_vram_seg1(midboss.pos.cur.y.v);
    int patnum = ((stage_frame_mod16 / 4) + MIDBOSSX_PAT_BASE);
    super_roll_put(left, top, patnum);
}
