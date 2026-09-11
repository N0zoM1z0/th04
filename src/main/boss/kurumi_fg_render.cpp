#pragma option -zCMAIN_012_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/custom.hpp"

static const int KURUMI_SPAWNRAY_COUNT = 6;
static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

enum kurumi_spawnray_flag_t {
    B2SF_FREE = 0,
    B2SF_GROW = 1,
    B2SF_SHRINK = 2,
};

struct kurumi_spawnray_t {
    kurumi_spawnray_flag_t flag;
    signed char unused;
    PlayfieldPoint target;
    PlayfieldPoint origin;
    PlayfieldPoint velocity;
    signed char padding[12];
};

#define kurumi_spawnrays ( \
    reinterpret_cast<kurumi_spawnray_t near *>(custom_entities) \
)

void pascal near kurumi_fg_render(void)
{
    int patnum;
    int spawnray_i;
    int origin_left;
    int origin_top;
    kurumi_spawnray_t near *spawnray;
    #define left _SI
    #define top _DI

    if(boss.phase < 2) {
        left = (boss.pos.cur.x.v >> 4);
        top = ((boss.pos.cur.y.v >> 4) - 16);
        patnum = (146 + boss.sprite + (stage_frame_mod16 / 4));
        super_put(left, top, patnum);

        if((boss.phase == PHASE_HP_FILL) && (boss.phase_frame > 128)) {
            patnum = ((320 - boss.phase_frame) * 2);
            left += 32;
            top += 24;

            grcg_setmode_rmw();
            _AH = 7;
            grcg_setcolor_direct_raw();
            grcg_circle(left, top, patnum);
            _AH = 6;
            grcg_setcolor_direct_raw();
            grcg_circle(left, top, (patnum + 6));
            grcg_circle(left, top, (patnum + 12));
            _DX = 0x7C;
            _AL = 0;
            outportb(_DX, _AL);
        }
    } else if(boss.phase < PHASE_EXPLODE_BIG) {
        left = (boss.pos.cur.x.v >> 4);
        top = ((boss.pos.cur.y.v >> 4) - 16);
        patnum = (boss.sprite + 146);
        if((boss.sprite == 0) || (boss.sprite == 12)) {
            patnum += (stage_frame_mod16 / 4);
        }
        if((boss.sprite == 4) || (boss.sprite == 6)) {
            patnum += (stage_frame_mod8 / 4);
        }

        if(boss.damage_this_frame == 0) {
            super_put(left, top, patnum);
        } else {
            super_put_1plane(
                left, top, patnum, PATTERN_ERASE, PLANE_ALL_PUT
            );
        }

        grcg_setmode_rmw();
        _AH = 9;
        grcg_setcolor_direct_raw();
        spawnray = kurumi_spawnrays;
        for(
            spawnray_i = 0;
            spawnray_i < KURUMI_SPAWNRAY_COUNT;
            (spawnray_i++, spawnray++)
        ) {
            if(spawnray->flag == B2SF_FREE) {
                continue;
            }
            left = ((spawnray->target.x.v / 16) + PLAYFIELD_LEFT);
            top = ((spawnray->target.y.v / 16) + PLAYFIELD_TOP);
            origin_left = ((spawnray->origin.x.v / 16) + PLAYFIELD_LEFT);
            origin_top = ((spawnray->origin.y.v / 16) + PLAYFIELD_TOP);
            grcg_line(left, top, origin_left, origin_top);
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
