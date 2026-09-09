#pragma option -zCMAIN_012_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"

static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

extern unsigned char elly_scythe_flag;
extern PlayfieldMotion elly_scythe_motion;

void pascal near elly_fg_render(void)
{
    int patnum;
    #define left _SI
    #define top _DI

    left = (boss.pos.cur.x.v >> 4);
    top = ((boss.pos.cur.y.v >> 4) - 16);

    if(boss.phase < PHASE_EXPLODE_BIG) {
        if(boss.damage_this_frame == 0) {
            super_put(left, _AX, boss.sprite);
        } else {
            super_put_1plane(
                left, top, boss.sprite, PATTERN_ERASE, PLANE_ALL_PUT
            );
        }
    } else if(boss.phase == PHASE_EXPLODE_BIG) {
        super_large_put(left, top, boss.sprite);
    }

    if(
        (elly_scythe_flag == 1) &&
        (elly_scythe_motion.cur.x.v >= 0) &&
        (elly_scythe_motion.cur.x.v < TO_SP(384)) &&
        (elly_scythe_motion.cur.y.v >= 0) &&
        (elly_scythe_motion.cur.y.v < TO_SP(368))
    ) {
        left = (elly_scythe_motion.cur.x.v >> 4);
        top = ((elly_scythe_motion.cur.y.v >> 4) - 16);
        patnum = (142 + (stage_frame_mod8 / 2));
        super_put(left, top, patnum);
    }

    explosions_small_update_and_render();
    explosions_big_update_and_render();

    #undef top
    #undef left
}
