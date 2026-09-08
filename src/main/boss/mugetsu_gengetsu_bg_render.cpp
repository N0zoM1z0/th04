#pragma option -zCBOSS_BG_TEXT -zPmain_01

#include "compat/rec98/th01/hardware/grcg.hpp"
#include "compat/rec98/th03/formats/cdg.h"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/formats/bb.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/boss/backdrop.hpp"
#include "th04/main/boss/bosses.hpp"
#include "th04/main/null.hpp"
#include "th04/main/stage/stage.hpp"
#include "th04/main/tile/bb.hpp"
#include "th04/main/tile/tile.hpp"
#include "th04/sprites/main_cdg.h"

void pascal near mugetsu_gengetsu_bg_render(void)
{
    unsigned char entrance_cel;

    if(boss.phase == PHASE_HP_FILL) {
        if(boss.phase_frame <= 2) {
            stage_render = nullfunc_near;
            tiles_render_all();
            return;
        }
        tiles_render();
        return;
    }

    if(boss.phase == PHASE_BOSS_ENTRANCE_BB) {
        entrance_cel = (boss.phase_frame / 4);
        if(entrance_cel < 8) {
            tiles_render_all();
        } else {
            grcg_setmode_tdw();
            grcg_setcolor_direct(1);
            mugetsu_gengetsu_backdrop_colorfill();
            grcg_off();
            cdg_put_noalpha_8(32, 16, CDG_BG_BOSS);
        }
        tiles_bb_put(bb_boss_seg, entrance_cel);
        return;
    }

    if(boss.phase < PHASE_EXPLODE_BIG) {
        boss_backdrop_render(32, 16, 1);
        return;
    }

    if(boss.phase == PHASE_EXPLODE_BIG) {
        tiles_render_all();
        return;
    }

    if(boss.phase_frame <= 2) {
        tiles_render_all();
        return;
    }
    tiles_render();
}
