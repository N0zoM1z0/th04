#pragma option -zCMAIN_012_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"

static const unsigned PLANE_RED_PUT = (0xFF00 | GC_RMW | GC_R);

extern unsigned char yuuka6_damage_flash_cycle;
extern unsigned char yuuka6_mirror_damage_flash_cycle;
extern unsigned char yuuka6_aux_flag;
extern SPPoint yuuka6_mirror_pos;
extern unsigned char yuuka6_mirror_state;
extern unsigned char yuuka6_mirror_damage;

#pragma codeseg MAIN_TEXT main_01
extern "C" void near thicklasers_render(void);
#pragma codeseg MAIN_012_TEXT main_01
extern "C" void near yuuka6_entities_render(void);
#pragma codeseg

void pascal near yuuka6_fg_render(void)
{
    register int left;
    register int top;

    left = ((boss.pos.cur.x.v >> 4) - 16);
    top = ((boss.pos.cur.y.v >> 4) - 32);

    if(boss.phase == PHASE_NONE) {
        return;
    }
    if(boss.phase == PHASE_EXPLODE_BIG) {
        super_zoom(left, top, boss.sprite, 3);
        return;
    }

    if(yuuka6_aux_flag != 0) {
        super_put(
            (left + 24),
            (top + 24),
            (182 + (stage_frame_mod16 / 4))
        );
    }

    if(boss.sprite != 0) {
        if(
            (boss.damage_this_frame == 0) ||
            ((yuuka6_damage_flash_cycle & 1) != 0)
        ) {
            super_put(left, top, boss.sprite);
            super_put((left + 48), top, (boss.sprite + 1));
        } else {
            super_put_1plane(
                left, top, boss.sprite, PATTERN_ERASE, PLANE_RED_PUT
            );
            super_put_1plane(
                (left + 48),
                top,
                (boss.sprite + 1),
                PATTERN_ERASE,
                PLANE_RED_PUT
            );
        }
        yuuka6_damage_flash_cycle += (boss.damage_this_frame != 0);
        boss.damage_this_frame = 0;

        if(yuuka6_mirror_state == 2) {
            left = ((yuuka6_mirror_pos.x.v >> 4) - 16);
            top = ((yuuka6_mirror_pos.y.v >> 4) - 32);
            if(
                (yuuka6_mirror_damage == 0) ||
                ((yuuka6_mirror_damage_flash_cycle & 1) != 0)
            ) {
                super_put(left, top, boss.sprite);
                super_put((left + 48), top, (boss.sprite + 1));
            } else {
                super_put_1plane(
                    left, top, boss.sprite, PATTERN_ERASE, PLANE_RED_PUT
                );
                super_put_1plane(
                    (left + 48),
                    top,
                    (boss.sprite + 1),
                    PATTERN_ERASE,
                    PLANE_RED_PUT
                );
            }
            yuuka6_mirror_damage_flash_cycle += (yuuka6_mirror_damage != 0);
            yuuka6_mirror_damage = 0;
        }
    }

    explosions_small_update_and_render();
    explosions_big_update_and_render();
    thicklasers_render();
    yuuka6_entities_render();

}
