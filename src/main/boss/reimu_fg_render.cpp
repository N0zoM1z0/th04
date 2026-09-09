#pragma option -zCBOSS_FG_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"

static const unsigned PLANE_BI_PUT = (0xFF00 | GC_RMW | GC_BI);
static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

extern unsigned char reimu_trail_visible;
extern "C" void near reimu_orbs_render(void);

void pascal near reimu_fg_render(void)
{
    int patnum;
    #define left _SI
    #define top _DI

    if(boss.phase < PHASE_EXPLODE_BIG) {
        if(reimu_trail_visible != 0) {
            left = (boss.pos.prev.x.v >> 4);
            top = ((boss.pos.prev.y.v >> 4) - 16);
            super_put_1plane(
                left, _AX, boss.sprite, PATTERN_ERASE, PLANE_BI_PUT
            );
        }

        left = (boss.pos.cur.x.v >> 4);
        top = ((boss.pos.cur.y.v >> 4) - 16);
        if(boss.sprite == 136) {
            patnum = (136 + (stage_frame_mod16 / 4));
        } else {
            patnum = boss.sprite;
        }

        if(boss.damage_this_frame == 0) {
            super_put(left, top, patnum);
        } else {
            super_put_1plane(
                left, top, patnum, PATTERN_ERASE, PLANE_ALL_PUT
            );
            boss.damage_this_frame = 0;
        }
        reimu_orbs_render();
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
