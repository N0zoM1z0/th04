#pragma option -G
#pragma option -zCMAIN_TEXT -zPmain_01

#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/v_colors.hpp"
#include "th04/main/playfld.hpp"
#include "src/main/bullet/laser_t.hpp"

extern "C" void near thicklasers_render(void)
{
    register thicklaser_t near *laser = thicklasers;
    int i;
    int screen_center_x;
    int screen_circle_center_y;
    int screen_left;
    int screen_right;
    register int quarter_radius;

    for(i = 0; i < THICKLASER_COUNT; (i++, laser++)) {
        if(laser->flag == TF_FREE) {
            continue;
        }
        if(laser->flag == TF_LINE) {
            screen_center_x = ((laser->origin.x.v >> 4) + PLAYFIELD_LEFT);
            screen_circle_center_y = ((laser->origin.y.v >> 4) + PLAYFIELD_TOP);
            grcg_setcolor(GC_RMW, V_WHITE);
            grcg_vline(
                screen_center_x,
                screen_circle_center_y,
                (PLAYFIELD_BOTTOM - 1)
            );
            continue;
        }

        screen_center_x = ((laser->origin.x.v >> 4) + PLAYFIELD_LEFT);
        screen_circle_center_y = (
            (laser->origin.y.v >> 4) + laser->radius_cur + PLAYFIELD_TOP
        );
        screen_left = (screen_center_x - laser->radius_cur);
        screen_right = (screen_center_x + laser->radius_cur);
        quarter_radius = (laser->radius_cur / 4);
        if(quarter_radius > 16) {
            quarter_radius = 16;
        }

        if((quarter_radius / 2) != 0) {
            grcg_setcolor(GC_RMW, laser->col_outline);
            grcg_circlefill(
                screen_center_x,
                screen_circle_center_y,
                laser->radius_cur
            );
            grcg_boxfill(
                screen_left,
                screen_circle_center_y,
                (screen_left + (quarter_radius / 2)),
                (PLAYFIELD_BOTTOM - 1)
            );
            grcg_boxfill(
                (screen_right - (quarter_radius / 2)),
                screen_circle_center_y,
                screen_right,
                (PLAYFIELD_BOTTOM - 1)
            );
        }

        if(quarter_radius != 0) {
            grcg_setcolor(GC_RMW, (laser->col_outline + 1));
            grcg_circlefill(
                screen_center_x,
                screen_circle_center_y,
                (laser->radius_cur - (quarter_radius / 2))
            );
            grcg_boxfill(
                (screen_left + (quarter_radius / 2)),
                screen_circle_center_y,
                (screen_left + quarter_radius),
                (PLAYFIELD_BOTTOM - 1)
            );
            grcg_boxfill(
                (screen_right - quarter_radius),
                screen_circle_center_y,
                (screen_right - (quarter_radius / 2)),
                (PLAYFIELD_BOTTOM - 1)
            );
        }

        screen_left += quarter_radius;
        screen_right -= quarter_radius;
        grcg_setcolor(GC_RMW, V_WHITE);
        grcg_circlefill(
            screen_center_x,
            screen_circle_center_y,
            (laser->radius_cur - quarter_radius)
        );
        grcg_boxfill(
            screen_left,
            screen_circle_center_y,
            screen_right,
            (PLAYFIELD_BOTTOM - 1)
        );
    }

    _DX = 0x7C;
    _AL = 0;
    outportb(_DX, _AL);
}
