#pragma option -zCMAIN_012_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"

static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

void pascal near orange_fg_render(void)
{
    int patnum;
    #define left _SI
    #define top _DI

    if(boss.phase < 2) {
        left = ((boss.pos.cur.x.v >> 4) + 16);
        top = ((boss.pos.cur.y.v >> 4) - 8);
        patnum = (boss.sprite + (stage_frame_mod8 / 4));
        super_put(left, top, patnum);

        if((boss.phase == PHASE_HP_FILL) && (boss.phase_frame >= 192)) {
            patnum = ((352 - boss.phase_frame) * 2);
            left += 24;
            top += 8;

            grcg_setmode_rmw();
            _AH = V_WHITE;
            grcg_setcolor_direct_raw();
            grcg_circle(left, top, patnum);
            _AH = 9;
            grcg_setcolor_direct_raw();
            grcg_circle(left, top, (patnum + 6));
            grcg_circle(left, top, (patnum + 12));
            _DX = 0x7C;
            _AL = 0;
            outportb(_DX, _AL);
        }
    } else if(boss.phase < PHASE_EXPLODE_BIG) {
        left = (boss.pos.cur.x.v >> 4);
        top = ((boss.pos.cur.y.v >> 4) - 24);
        patnum = (boss.sprite + (stage_frame_mod16 / 4));
        if(boss.damage_this_frame == 0) {
            super_put(left, top, patnum);
        } else {
            super_put_1plane(
                left, top, patnum, PATTERN_ERASE, PLANE_ALL_PUT
            );
        }
    } else if(boss.phase == PHASE_EXPLODE_BIG) {
        left = (boss.pos.cur.x.v >> 4);
        top = ((boss.pos.cur.y.v >> 4) - 16);
        super_large_put(left, _AX, boss.sprite);
    }

    explosions_small_update_and_render();
    explosions_big_update_and_render();

    #undef top
    #undef left
}
