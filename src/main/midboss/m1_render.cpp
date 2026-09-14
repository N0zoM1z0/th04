#pragma option -zCTILE_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/main/frames.h"
#include "th04/main/scroll.hpp"
#include "th04/main/phase.hpp"
#include "th04/main/midboss/midboss.hpp"

void pascal near midboss1_render(void)
{
    register screen_x_t left;
    register vram_y_t top;

    if(midboss.phase == 1) {
        left = (midboss.pos.cur.x.to_pixel() + 16);
        top = scroll_subpixel_y_to_vram_seg1(midboss.pos.cur.y.v);
        super_roll_put(left, top, midboss.sprite);
    } else if(midboss.phase == 2) {
        left = midboss.pos.cur.x.to_pixel();
        top = scroll_subpixel_y_to_vram_seg1(midboss.pos.cur.y.v - TO_SP(16));
        super_roll_put(left, top, midboss.sprite);
        top = scroll_subpixel_y_to_vram_seg1(midboss.pos.cur.y.v + TO_SP(16));
        super_roll_put(left, top, (midboss.sprite + 1));
    } else if(midboss.phase == 3) {
        left = midboss.pos.cur.x.to_pixel();
        top = scroll_subpixel_y_to_vram_seg1(midboss.pos.cur.y.v - TO_SP(16));
        if(midboss.damage_this_frame == 0) {
            super_roll_put(left, top, (((stage_frame >> 3) % 5) + 147));
            top = scroll_subpixel_y_to_vram_seg1(midboss.pos.cur.y.v + TO_SP(16));
            super_roll_put(left, top, 146);
        } else {
            super_roll_put_1plane(
                left, top, (((stage_frame >> 3) % 5) + 147),
                0, super_plane(V_WHITE)
            );
            top = scroll_subpixel_y_to_vram_seg1(midboss.pos.cur.y.v + TO_SP(16));
            super_roll_put_1plane(
                left, top, 146, 0, super_plane(V_WHITE)
            );
            midboss.damage_this_frame = 0;
        }
    } else if(midboss.phase == PHASE_EXPLODE_BIG) {
        midboss_defeat_render();
    }
}
