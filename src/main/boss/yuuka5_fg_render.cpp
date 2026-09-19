#pragma option -zCMAIN_TEXT -zPmain_01

#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/v_colors.hpp"
#include "src/main/hardware/grcg.hpp"
#include "th04/main/frames.h"
#include "src/main/boss/boss.hpp"

static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

extern unsigned char yuuka5_move_state;
extern "C" void near thicklasers_render(void);

void pascal near yuuka5_fg_render(void)
{
    int patnum;
    register int left;
    register int top;

    left = ((boss.pos.cur.x.v >> 4) - 16);
    top = ((boss.pos.cur.y.v >> 4) - 32);

    if(boss.phase == PHASE_EXPLODE_BIG) {
        super_zoom(left, top, boss.sprite, 3);
    } else if(boss.phase <= PHASE_BOSS_ENTRANCE_BB) {
        left = (boss.pos.cur.x.v >> 4);
        top = ((boss.pos.cur.y.v >> 4) - 16);
        if(boss.damage_this_frame == 0) {
            super_put(left, top, 128);
        } else {
            super_put_1plane(
                left, top, 128, PATTERN_ERASE, PLANE_ALL_PUT
            );
            boss.damage_this_frame = 0;
        }
    } else if(boss.phase < PHASE_EXPLODE_BIG) {
        if(yuuka5_move_state == 0) {
            patnum = (((stage_frame_mod16 / 4) * 2) + 129);
            if(boss.damage_this_frame == 0) {
                super_put(left, top, patnum);
                super_put((left + 48), top, (patnum + 1));
            } else {
                super_put_1plane(
                    left, top, patnum, PATTERN_ERASE, PLANE_ALL_PUT
                );
                super_put_1plane(
                    (left + 48),
                    top,
                    (patnum + 1),
                    PATTERN_ERASE,
                    PLANE_ALL_PUT
                );
                boss.damage_this_frame = 0;
            }
        } else if(yuuka5_move_state == 1) {
            left = (boss.pos.cur.x.v >> 4);
            top = ((boss.pos.cur.y.v >> 4) - 16);
            grcg_setmode_rmw();
            _AH = V_WHITE;
            grcg_setcolor_direct_raw();
            patnum = (80 - (boss.phase_frame * 2));
            grcg_circlefill((left + 32), (top + 32), patnum);
            _DX = 0x7C;
            _AL = 0;
            outportb(_DX, _AL);
            super_put(left, top, 128);
        } else if(yuuka5_move_state == 2) {
            left = ((boss.pos.cur.x.v >> 4) + 32);
            top = ((boss.pos.cur.y.v >> 4) + 16);
            grcg_setmode_rmw();
            _AH = V_WHITE;
            grcg_setcolor_direct_raw();
            grcg_circlefill(left, top, 16);
            _DX = 0x7C;
            _AL = 0;
            outportb(_DX, _AL);
        } else if(yuuka5_move_state == 3) {
            left = (boss.pos.cur.x.v >> 4);
            top = ((boss.pos.cur.y.v >> 4) - 16);
            grcg_setmode_rmw();
            _AH = V_WHITE;
            grcg_setcolor_direct_raw();
            patnum = ((boss.phase_frame * 8) + 16);
            grcg_circlefill((left + 32), (top + 32), patnum);
            super_put(left, top, 128);
            _DX = 0x7C;
            _AL = 0;
            outportb(_DX, _AL);
        }
    }

    explosions_small_update_and_render();
    explosions_big_update_and_render();
    if(boss.phase < PHASE_NONE) {
        thicklasers_render();
    }

}
