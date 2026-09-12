#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/midboss/midboss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/item/item.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma samecodeseg midboss_reset
#pragma option -a

extern unsigned char bullet_special_turns_max;

static void near midbossx_orbit_step_reverse(void)
{
    midboss.pos.prev.x.v = midboss.pos.cur.x.v;
    midboss.pos.prev.y.v = midboss.pos.cur.y.v;
    midboss.pos.cur.x.v = polar(
        TO_SP(192), midboss.hp, CosTable8[midboss.angle]
    );
    midboss.pos.cur.y.v = polar(
        TO_SP(96), midboss.hp, SinTable8[midboss.angle]
    );
    midboss.angle += -2;
}

static void near midbossx_wave_step(void)
{
    midboss.pos.prev.x.v = midboss.pos.cur.x.v;
    midboss.pos.prev.y.v = midboss.pos.cur.y.v;
    if(midboss.phase_frame == 1) {
        midboss.pos.velocity.x.v = TO_SP(1);
        midboss.angle = 0;
    }
    midboss.pos.cur.x.v += midboss.pos.velocity.x.v;
    if(midboss.phase <= 5) {
        if((midboss.pos.cur.x.v <= TO_SP(16)) ||
           (midboss.pos.cur.x.v >= TO_SP(368))) {
            midboss.pos.velocity.x.v *= -1;
        }
    }
    midboss.pos.cur.y.v = polar(
        TO_SP(96), midboss.hp, SinTable8[midboss.angle]
    );
    midboss.angle += 2;
}

static void near midbossx_pattern_ring(void)
{
    if(stage_frame_mod16 == 0) {
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template.angle = randring2_next16();
        bullet_template.speed.v = TO_SP(3);
        bullet_template_tune();
        bullets_add_regular();
    }
}

static void near midbossx_pattern_cloud_ring(void)
{
    if(stage_frame_mod16 == 0) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template.angle = randring2_next16();
        bullet_template.speed.v = static_cast<unsigned char>(
            (midboss.phase_frame / 4) + 10
        );
        bullet_template_tune();
        bullets_add_regular();
        snd_se_play(3);
    }
}

static void near midbossx_pattern_bounce_spread(void)
{
    if(stage_frame_mod16 == 0) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.special_motion = BSM_BOUNCE_LEFT_RIGHT_TOP;
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 5;
        bullet_template.delta.spread_angle = 0x0C;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.speed.v = TO_SP(2);
        bullet_template.angle = static_cast<unsigned char>(
            randring2_next16_and(0x0F) + 0xB8
        );
        bullet_template_tune();
        bullet_special_turns_max = 2;
        bullets_add_special();
        snd_se_play(9);
    }
}

static void near midbossx_pattern_dual_ring(void)
{
    if(stage_frame_mod16 == 0) {
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template.angle = randring2_next16();
        bullet_template.speed.v = TO_SP(2);
        bullet_template_tune();
        bullets_add_regular();

        bullet_template.group = BG_RING;
        bullet_template.count = 16;
        bullet_template.angle = randring2_next16();
        bullet_template.speed.v = TO_SP(3);
        bullet_template_tune();
        bullets_add_regular();
    }
}

static void near midbossx_pattern_events(void)
{
    switch(midboss.phase_frame) {
    case 250:
    case 258:
    case 266:
    case 274:
        snd_se_play(9);
        items_add(midboss.pos.cur.x.v, midboss.pos.cur.y.v, IT_DREAM);
        break;

    case 290:
    case 298:
    case 306:
    case 314:
    case 390:
    case 398:
    case 406:
    case 414:
    case 490:
    case 498:
    case 506:
    case 514:
        snd_se_play(3);
        bullet_template.group = BG_SPREAD_AIMED;
        bullet_template.count = 5;
        bullet_template.delta.spread_angle = 6;
        bullet_template.angle = 0;
        bullet_template.speed.v = TO_SP(4);
        bullet_template_tune();
        bullets_add_regular();
        break;

    case 350:
    case 358:
    case 366:
    case 374:
        snd_se_play(9);
        items_add(midboss.pos.cur.x.v, midboss.pos.cur.y.v, IT_BIGPOWER);
        break;

    case 450:
        snd_se_play(9);
        items_add(midboss.pos.cur.x.v, midboss.pos.cur.y.v, IT_1UP);
        break;
    }
}

void pascal far midbossx_update(void)
{
    bullet_template.origin.x.v = midboss.pos.cur.x.v;
    bullet_template.origin.y.v = midboss.pos.cur.y.v;
    bullet_template.spawn_type = BST_PELLET;

    switch(midboss.phase) {
    case 0:
        midbossx_orbit_step_reverse();
        midboss.phase_frame++;
        if(midboss.hp > 128) {
            midboss.hp -= 32;
        }
        if(midboss.phase_frame >= 128) {
            midbossx_pattern_ring();
            if(midboss.phase_frame >= 320) {
                goto advance_from_zero;
            }
        }
        break;

    case 1:
        midbossx_orbit_step_reverse();
        midboss.phase_frame++;
        if(midboss.hp < 896) {
            midboss.hp += 8;
        }
        if(midboss.phase_frame >= 128) {
            midbossx_pattern_ring();
            if(midboss.phase_frame >= 320) {
                goto advance_from_zero;
            }
        }
        break;

    case 2:
        midbossx_orbit_step_reverse();
        midboss.phase_frame++;
        if(midboss.hp > 128) {
            midboss.hp -= 32;
        }
        if(midboss.phase_frame >= 128) {
            midbossx_pattern_cloud_ring();
            if(midboss.phase_frame >= 320) {
                goto advance_from_zero;
            }
        }
        break;

    case 3:
        if(midboss.phase_frame < 128) {
            midbossx_orbit_step_reverse();
        } else {
            midbossx_wave_step();
            midbossx_pattern_bounce_spread();
            if(midboss.hp < 768) {
                midboss.hp += 8;
            }
        }
        midboss.phase_frame++;
        if(midboss.phase_frame < 640) {
            goto ret;
        }

    advance_from_zero:
        midboss.phase_frame = 0;
        goto advance_phase;

    case 4:
        midbossx_wave_step();
        if(midboss.phase_frame >= 160) {
            midbossx_pattern_dual_ring();
        }
        midboss.phase_frame++;
        if(midboss.phase_frame >= 440) {
            goto advance_from_two;
        }
        break;

    case 5:
        midbossx_wave_step();
        midbossx_pattern_events();
        midboss.phase_frame++;
        if(midboss.phase_frame < 520) {
            goto ret;
        }

    advance_from_two:
        midboss.phase_frame = 2;

    advance_phase:
        midboss.phase++;
        return;

    case 6:
        midbossx_wave_step();
        midboss.phase_frame++;
        if((midboss.pos.cur.x.v <= -TO_SP(16)) ||
           (midboss.pos.cur.x.v >= TO_SP(400))) {
            midboss_reset();
        }
        break;
    }

ret:
    return;
}

#pragma codeseg
