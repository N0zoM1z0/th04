#ifndef TH04_BOSS_BG_MAIN01_COMBINED
#pragma option -zCBOSS_BG_TEXT -zPmain_01

#include "compat/rec98/th01/hardware/grcg.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/math/randring.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/tile/bb.hpp"

static const int YUUKA6_BG_SHAPE_COUNT = 56;

struct yuuka6_bg_shape_t {
    SPPoint pos;
    unsigned char angle;
    SubpixelLength8 speed;
};

extern yuuka6_bg_shape_t bg_shapes[YUUKA6_BG_SHAPE_COUNT + 1];
extern main_patnum_t bg_shape_patnum;
extern Subpixel bg_shape_flyout_speed;
extern unsigned char yuuka6_bg_state;
extern unsigned char yuuka6_bg_fade;

extern "C" void near playfield_fill(void);
extern "C" void near yuuka6_bg_update_render(void);
void near playfield_checkerboard_grcg_tdw_(void);

#endif

void pascal near yuuka6_bg_render(void)
{
    unsigned char entrance_cel;
    register yuuka6_bg_shape_t near *shape;
    register int i;

    grcg_setmode_tdw();

    if(boss.phase == PHASE_HP_FILL) {
        grcg_setcolor_direct(1);
        playfield_fill();
        grcg_off();
        if(boss.phase_frame != 2) {
            return;
        }

        shape = bg_shapes;
        i = 0;
        for(; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
            shape->pos.x.v = randring1_next16_mod(TO_SP(PLAYFIELD_W));
            shape->pos.y.v = randring1_next16_mod(TO_SP(PLAYFIELD_H));
            shape->angle = 0x60;
            shape->speed.v = TO_SP(1);
        }
        bg_shape_flyout_speed.v = TO_SP(1);
        bg_shape_patnum = static_cast<main_patnum_t>(120);
        yuuka6_bg_state = 0;
        yuuka6_bg_fade = 0;
        return;
    }

    if(boss.phase == PHASE_BOSS_ENTRANCE_BB) {
        entrance_cel = (boss.phase_frame / 4);
        grcg_setcolor_direct(1);
        if(entrance_cel < 8) {
            playfield_fill();
        } else {
            playfield_checkerboard_grcg_tdw_();
        }
        tiles_bb_put(bb_boss_seg, entrance_cel);
        return;
    }

    if(boss.phase < PHASE_EXPLODE_BIG) {
        playfield_checkerboard_grcg_tdw_();
    } else {
        grcg_setcolor_direct(1);
        playfield_fill();
        grcg_off();
    }
    yuuka6_bg_update_render();
}
