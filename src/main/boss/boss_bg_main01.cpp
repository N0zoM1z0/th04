#pragma option -zCBOSS_BG_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th01/hardware/grcg.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "compat/rec98/th03/formats/cdg.h"
#include "th04/math/randring.hpp"
#include "th04/math/vector.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/boss/backdrop.hpp"
#include "th04/main/boss/bosses.hpp"
#include "th04/main/tile/bb.hpp"
#include "th04/main/tile/tile.hpp"
#include "th04/sprites/main_cdg.h"

static const int YUUKA6_BG_SHAPE_COUNT = 56;
static const pixel_t YUUKA6_BG_SHAPE_W = 16;
static const pixel_t YUUKA6_BG_SHAPE_H = 16;

struct yuuka6_bg_shape_t {
    SPPoint pos;
    unsigned char angle;
    SubpixelLength8 speed;
};

#pragma option -a

extern yuuka6_bg_shape_t bg_shapes[YUUKA6_BG_SHAPE_COUNT + 1];
extern main_patnum_t bg_shape_patnum;
extern Subpixel bg_shape_flyout_speed;
extern void (near pascal *near bg_shape_clip)(yuuka6_bg_shape_t near& shape);
extern unsigned char yuuka6_bg_state;
extern unsigned char yuuka6_bg_fade;
extern unsigned char yuuka6_bg_palette_latch;
extern bool palette_changed;
extern unsigned char elly_scythe_flag;
extern PlayfieldMotion elly_scythe_motion;
extern "C" void pascal near tiles_invalidate_around(const SPPoint center);

extern "C" void near playfield_fill(void);
void near playfield_checkerboard_grcg_tdw_(void);


void pascal near orange_bg_render(void)
{
    if(boss.phase == PHASE_HP_FILL) {
        if(boss.phase_frame >= 192) goto render_all;
        if(boss.phase_frame <= 2) goto render_all;
        goto render;
    }
    if(boss.phase == PHASE_BOSS_ENTRANCE_BB) {
        boss_backdrop_render(32, 136, 1);
        tiles_bb_invalidate(bb_boss_seg, (boss.phase_frame >> 1));
        tiles_redraw_invalidated();
        return;
    }
    if(boss.phase < PHASE_EXPLODE_BIG) {
        boss_backdrop_render(32, 136, 1);
        return;
    }
    if(boss.phase == PHASE_EXPLODE_BIG) goto render_all;
    if(boss.phase_frame > 2) goto render;
render_all:
    tiles_render_all();
    return;
render:
    tiles_render();
}

void pascal near kurumi_bg_render(void)
{
    if(boss.phase == PHASE_HP_FILL) goto render_all;
    if(boss.phase == PHASE_BOSS_ENTRANCE_BB) {
        boss_backdrop_render(32, 96, 0);
        tiles_bb_invalidate(bb_boss_seg, (boss.phase_frame >> 1));
        tiles_redraw_invalidated();
        return;
    }
    if(boss.phase < PHASE_EXPLODE_BIG) {
        boss_backdrop_render(32, 96, 0);
        return;
    }
    if(boss.phase == PHASE_EXPLODE_BIG) goto render_all;
    if(boss.phase_frame > 2) goto render;
render_all:
    tiles_render_all();
    return;
render:
    tiles_render();
}

static void near elly_bg_invalidate(void)
{
    tile_invalidate_box.x = 64;
    tile_invalidate_box.y = 64;
    tiles_invalidate_around(boss.pos.prev);
    if(elly_scythe_flag != 0) {
        tiles_invalidate_around(elly_scythe_motion.prev);
    }
}

void pascal near elly_bg_render(void)
{
    if(boss.phase <= PHASE_BOSS_ENTRANCE_BB) {
        if(boss.phase_frame <= 2) goto render_all;
        elly_bg_invalidate();
        goto render;
    }
    if(boss.phase == 2) {
        boss_backdrop_render(32, 16, 0);
        tiles_bb_invalidate(bb_boss_seg, (boss.phase_frame >> 1));
        tiles_redraw_invalidated();
        return;
    }
    if(boss.phase < PHASE_EXPLODE_BIG) {
        boss_backdrop_render(32, 16, 0);
        return;
    }
    if(boss.phase == PHASE_EXPLODE_BIG) goto render_all;
    if(boss.phase_frame > 2) goto render;
render_all:
    tiles_render_all();
    return;
render:
    tiles_render();
}

void pascal near reimu_marisa_bg_render(void)
{
    unsigned char entrance_cel;
    if(boss.phase == PHASE_HP_FILL) {
        if(boss.phase_frame <= 2) goto render_all;
        goto render;
    }
    if(boss.phase == PHASE_BOSS_ENTRANCE_BB) {
        entrance_cel = (boss.phase_frame / 8);
        if(entrance_cel < 8) {
            tiles_render_all();
        } else {
            grcg_setmode_tdw();
            grcg_setcolor_direct(1);
            reimu_marisa_backdrop_colorfill();
            grcg_off();
            cdg_put_noalpha_8(96, 72, CDG_BG_BOSS);
        }
        tiles_bb_put(bb_boss_seg, entrance_cel);
        return;
    }
    if(boss.phase < PHASE_EXPLODE_BIG) {
        boss_backdrop_render(96, 72, 1);
        return;
    }
    if(boss.phase == PHASE_EXPLODE_BIG) goto render_all;
    if(boss.phase_frame > 2) goto render;
render_all:
    tiles_render_all();
    return;
render:
    tiles_render();
}

void pascal near yuuka5_bg_render(void)
{
    unsigned char entrance_cel;
    if(boss.phase == PHASE_HP_FILL) {
        if(boss.phase_frame <= 2) goto render_all;
        goto render;
    }
    if(boss.phase == PHASE_BOSS_ENTRANCE_BB) {
        entrance_cel = (boss.phase_frame / 4);
        if(entrance_cel < 8) {
            tiles_render_all();
        } else {
            grcg_setmode_tdw();
            grcg_setcolor_direct(0);
            yuuka5_backdrop_colorfill();
            grcg_off();
            cdg_put_noalpha_8(128, 128, CDG_BG_BOSS);
        }
        tiles_bb_put(bb_boss_seg, entrance_cel);
        return;
    }
    if(boss.phase < PHASE_EXPLODE_BIG) {
        boss_backdrop_render(128, 128, 0);
        return;
    }
    if(boss.phase == PHASE_EXPLODE_BIG) goto render_all;
    if(boss.phase_frame > 2) goto render;
render_all:
    tiles_render_all();
    return;
render:
    tiles_render();
}

void pascal near bg_shape_clip_and_respawn_in_cen(yuuka6_bg_shape_t near& shape)
{
    shape.speed.v++;
    if(
        (shape.pos.x.v <= TO_SP(-(YUUKA6_BG_SHAPE_W / 2))) ||
        (shape.pos.x.v >= TO_SP(PLAYFIELD_W + (YUUKA6_BG_SHAPE_W / 2))) ||
        (shape.pos.y.v <= TO_SP(-(YUUKA6_BG_SHAPE_H / 2))) ||
        (shape.pos.y.v >= TO_SP(PLAYFIELD_H + YUUKA6_BG_SHAPE_H))
    ) {
        shape.pos.x.v = TO_SP(PLAYFIELD_W / 2);
        shape.pos.y.v = TO_SP(PLAYFIELD_H / 2);
        shape.speed.v = bg_shape_flyout_speed.v;
    }
}

void pascal near bg_shape_clip_and_wrap(yuuka6_bg_shape_t near& shape)
{
    if(shape.pos.x.v <= TO_SP(-(YUUKA6_BG_SHAPE_W / 2))) {
        shape.pos.x.v += TO_SP(PLAYFIELD_W + YUUKA6_BG_SHAPE_W);
    } else if(shape.pos.x.v >= TO_SP(PLAYFIELD_W + (YUUKA6_BG_SHAPE_W / 2))) {
        shape.pos.x.v -= TO_SP(PLAYFIELD_W + YUUKA6_BG_SHAPE_W);
    }
    if(shape.pos.y.v <= TO_SP(-(YUUKA6_BG_SHAPE_H / 2))) {
        shape.pos.y.v += TO_SP(PLAYFIELD_H + ((YUUKA6_BG_SHAPE_H / 2) * 3));
    } else if(shape.pos.y.v >= TO_SP(PLAYFIELD_H + YUUKA6_BG_SHAPE_H)) {
        shape.pos.y.v -= TO_SP(PLAYFIELD_H + ((YUUKA6_BG_SHAPE_H / 2) * 3));
    }
}
void pascal near z_super_put_16x16_mono_raw(int patnum);

extern "C" void near yuuka6_bg_update_render(void)
{
    int left;
    int patnum;
    int vector_x;
    int vector_y;
    unsigned char fade;
    register yuuka6_bg_shape_t near *shape;
    register int i;

    if(yuuka6_bg_fade == 0) {
        shape = bg_shapes;
        switch(yuuka6_bg_state) {
        case 0:
        case 8:
        case 12:
            bg_shape_clip = bg_shape_clip_and_wrap;
            break;
        case 6:
        case 10:
            bg_shape_clip = bg_shape_clip_and_respawn_in_cen;
            break;
        }
    }

    grcg_setmode_rmw();
    if(yuuka6_bg_fade < 0x80) {
        fade = yuuka6_bg_fade;
    } else {
        fade = (255 - yuuka6_bg_fade);
    }

    if(yuuka6_bg_state < 0x10) {
        _AH = 8;
        grcg_setcolor_direct_raw();
        if(yuuka6_bg_state & 1) {
            Palettes[0].c.r = fade;
            Palettes[0].c.b = fade;
        } else {
            Palettes[0].c.b = ((fade * 3) / 2);
        }
    } else {
        _AH = 9;
        grcg_setcolor_direct_raw();
        if(yuuka6_bg_palette_latch == 0) {
            Palettes[0].c.r = 0;
            Palettes[0].c.g = 0;
            Palettes[0].c.b = ((fade * 3) / 2);
            if(fade >= 0x7F) {
                yuuka6_bg_palette_latch = 1;
            }
        }
    }
    palette_changed = true;

    switch(yuuka6_bg_state) {
    case 0:
    case 1:
    case 2:
    case 3:
        if(boss.phase > 2) {
            yuuka6_bg_fade++;
            if(yuuka6_bg_fade < 254) {
                goto update_common;
            }
            bg_shape_patnum = static_cast<main_patnum_t>(120);
            yuuka6_bg_state = 4;
            shape = bg_shapes;
            for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
                shape->angle = 0x40;
                shape->speed.v = TO_SP(4);
            }
            yuuka6_bg_fade = 255;
            bg_shape_flyout_speed.v = TO_SP(4);
            goto update_common;
        }
        if(yuuka6_bg_fade != 255) {
            goto update_common;
        }
        bg_shape_patnum++;
        yuuka6_bg_state++;
        if(yuuka6_bg_state >= 4) {
            yuuka6_bg_state = 0;
            bg_shape_patnum = static_cast<main_patnum_t>(120);
        }
        shape = bg_shapes;
        for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
            shape->angle = (0x80 - shape->angle);
        }
        goto update_common;

    case 4:
    case 5:
        if(boss.phase > 4) {
            yuuka6_bg_fade++;
            if(yuuka6_bg_fade < 254) {
                goto update_common;
            }
            bg_shape_patnum = static_cast<main_patnum_t>(120);
            yuuka6_bg_state = 6;
            shape = bg_shapes;
            for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
                shape->angle = iatan2(
                    (shape->pos.y.v - TO_SP((PLAYFIELD_H / 2) + (YUUKA6_BG_SHAPE_H / 2))),
                    (shape->pos.x.v - TO_SP((PLAYFIELD_W / 2) + (YUUKA6_BG_SHAPE_W / 2)))
                );
                shape->speed.v = TO_SP(1);
            }
            bg_shape_flyout_speed.v = TO_SP(1);
            goto fade_reset;
        }
        if(yuuka6_bg_fade != 255) {
            goto update_common;
        }
        if(yuuka6_bg_state == 4) {
            goto state_increment;
        }
        goto state_decrement;

    case 6:
    case 7:
    case 10:
    case 11:
        if(
            (boss.phase == 7) ||
            (boss.phase == 8) ||
            (boss.phase == 11) ||
            (boss.phase == 12)
        ) {
            yuuka6_bg_fade++;
            if(yuuka6_bg_fade < 254) {
                goto update_common;
            }
            bg_shape_patnum = static_cast<main_patnum_t>(120);
            if(yuuka6_bg_state < 10) {
                _AL = 8;
            } else {
                _AL = 12;
            }
            yuuka6_bg_state = _AL;
            shape = bg_shapes;
            for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
                shape->pos.x.v = randring1_next16_mod(TO_SP(PLAYFIELD_W));
                shape->pos.y.v = randring1_next16_mod(TO_SP(PLAYFIELD_H));
                _AL = randring1_next16_and(0x0F);
                _AL += -0x48;
                shape->angle = _AL;
                shape->speed.v = 0x48;
            }
            goto flyout_speed_4;
        }
        if(yuuka6_bg_fade != 255) {
            goto update_common;
        }
        if(yuuka6_bg_state & 1) {
            goto state_decrement;
        }
        goto state_increment;

    case 8:
    case 9:
    case 12:
    case 13:
        if((boss.phase == 9) || (boss.phase == 10) || (boss.phase >= 13)) {
            yuuka6_bg_fade++;
            if(yuuka6_bg_fade < 254) {
                goto update_common;
            }
            bg_shape_patnum = static_cast<main_patnum_t>(120);
            if(yuuka6_bg_state < 12) {
                _AL = 10;
            } else {
                _AL = 14;
            }
            yuuka6_bg_state = _AL;
            shape = bg_shapes;
            for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
                shape->angle = iatan2(
                    (shape->pos.y.v - TO_SP((PLAYFIELD_H / 2) + (YUUKA6_BG_SHAPE_H / 2))),
                    (shape->pos.x.v - TO_SP((PLAYFIELD_W / 2) + (YUUKA6_BG_SHAPE_W / 2)))
                );
                if(yuuka6_bg_state != 14) {
                    shape->speed.v = TO_SP(1);
                } else {
                    shape->speed.v = TO_SP(4);
                }
            }
        flyout_speed_4:
            bg_shape_flyout_speed.v = TO_SP(4);
        fade_reset:
            yuuka6_bg_fade = 255;
            goto update_common;
        }
        if(yuuka6_bg_fade != 255) {
            goto update_common;
        }
        if(yuuka6_bg_state & 1) {
            goto state_decrement;
        }
        goto state_increment;

    case 14:
    case 15:
        shape = bg_shapes;
        if(yuuka6_bg_state == 14) {
            _AL = 2;
        } else {
            _AL = -2;
        }
        fade = _AL;
        for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
            shape->angle += fade;
        }
        if(boss.phase >= 15) {
            yuuka6_bg_fade++;
            if(yuuka6_bg_fade < 254) {
                goto update_common;
            }
            bg_shape_patnum = static_cast<main_patnum_t>(124);
            yuuka6_bg_state = 16;
            yuuka6_bg_fade = 255;
            shape = bg_shapes;
            for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
                shape->pos.x.v = randring1_next16_mod(TO_SP(PLAYFIELD_W));
                shape->pos.y.v = randring1_next16_mod(TO_SP(PLAYFIELD_H));
                shape->angle = 0x40;
                shape->speed.v = TO_SP(12);
            }
            bg_shape_flyout_speed.v = TO_SP(12);
            goto update_common;
        }
        if(yuuka6_bg_fade != 255) {
            goto update_common;
        }
        if(yuuka6_bg_state & 1) {
            goto state_decrement;
        }
        goto state_increment;
    state_decrement:
        yuuka6_bg_state--;
        goto update_common;
    state_increment:
        yuuka6_bg_state++;
        goto update_common;

    case 16:
        if(boss.phase < PHASE_EXPLODE_BIG) {
            goto update_common;
        }
        bg_shape_patnum = static_cast<main_patnum_t>(125);
        yuuka6_bg_state = 17;
        yuuka6_bg_fade = 255;
        shape = bg_shapes;
        for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
            shape->angle = 0x40;
            shape->speed.v = TO_SP(1);
        }
        bg_shape_flyout_speed.v = TO_SP(1);
    }

update_common:
    yuuka6_bg_fade++;
    shape = bg_shapes;
    for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
        vector2(vector_x, vector_y, shape->angle, shape->speed.v);
        shape->pos.x.v += vector_x;
        shape->pos.y.v += vector_y;
        bg_shape_clip(*shape);
    }

    _ES = 0xA800;
    shape = bg_shapes;
    for(i = 0; i < YUUKA6_BG_SHAPE_COUNT; (i++, shape++)) {
        patnum = bg_shape_patnum;
        if(yuuka6_bg_state >= 17) {
            patnum += (i % 3);
        }
        left = ((shape->pos.x.v >> 4) + (PLAYFIELD_LEFT - (YUUKA6_BG_SHAPE_W / 2)));
        _AX = ((shape->pos.y.v >> 4) + (PLAYFIELD_TOP - (YUUKA6_BG_SHAPE_H / 2)));
        _CX = left;
        z_super_put_16x16_mono_raw(patnum);
    }
    grcg_off();
}

#define TH04_BOSS_BG_MAIN01_COMBINED 1
#include "th04/y6bg.cpp"
