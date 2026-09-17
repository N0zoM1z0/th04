#pragma option -zCTILE_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "src/shared/hardware/v_colors.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/phase.hpp"
#include "th04/main/midboss/midboss.hpp"

static const int MIDBOSS3_PAT_BASE = 144;

void pascal near midboss3_render(void)
{
    if(
        (midboss.pos.cur.y.v <= 0) ||
        (midboss.pos.cur.y.v >= TO_SP(368)) ||
        (midboss.pos.cur.x.v <= 0) ||
        (midboss.pos.cur.x.v >= TO_SP(384))
    ) {
        return;
    }

    register screen_x_t left = midboss.pos.cur.x.to_pixel();
    vram_y_t top = scroll_subpixel_y_to_vram_seg1(
        midboss.pos.cur.y.v - TO_SP(16)
    );

    if(midboss.phase == PHASE_EXPLODE_BIG) {
        midboss_defeat_render();
        return;
    }
    if(midboss.phase > 2) {
        return;
    }

    register int patnum = MIDBOSS3_PAT_BASE;
    if(midboss.sprite == 1) {
        if((midboss.phase_frame % 32) < 16) {
            patnum += ((midboss.phase_frame % 16) / 4);
        } else {
            patnum += (3 - ((midboss.phase_frame % 16) / 4));
        }
    }
    midboss_put_generic(left, top, patnum);
}
