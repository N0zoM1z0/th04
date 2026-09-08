#ifdef TH04_MARISA_B4M_INCLUDED
#pragma codeseg MAIN_033_TEXT main_03
#else
#pragma option -zCMAIN_033_TEXT -zPmain_03
#endif

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#ifndef TH04_MARISA_B4M_INCLUDED
#include "th04/sprites/main_pat.h"
#include "th04/main/custom.hpp"
#endif
#include "th04/main/frames.h"
#include "compat/rec98/th03/math/randring.hpp"

struct marisa_bit_t {
    unsigned char flag;
    unsigned char angle;
    PlayfieldPoint center;
    int patnum;
    char unused_1[8];
    int distance;
    int moveout_speed;
    int hp;
    int damage_this_frame;
    char unused_2;
    signed char angle_speed;
};
typedef char marisa_bit_size_must_be_26[(sizeof(marisa_bit_t) == 26) ? 1 : -1];

struct marisa_bit_hp_t {
    int value[4];
};

extern marisa_bit_hp_t MARISA_BIT_HP;
extern unsigned char marisa_bit_angle_speed;

static const unsigned char M4BF_MOVEOUT_SPIN = 1;
static const int MARISA_BIT_COUNT = 4;

extern "C" void near marisa_bits_init(void)
;

#include "th04/snd/snd.h"
#include "th04/math/vector.hpp"
#include "th04/main/score.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"

#pragma samecodeseg sparks_add_random

extern SPPoint shot_hitbox_center;
extern SPPoint shot_hitbox_radius;
extern SPPoint homing_target;
extern screen_x_t bit_center_x[MARISA_BIT_COUNT];
extern screen_x_t bit_center_y[MARISA_BIT_COUNT];
extern unsigned char bits_alive;
extern int shots_hittest(void);

static const unsigned char M4BF_FREE = 0;
static const unsigned char M4BF_SPIN = 2;
static const unsigned char M4BF_KILL_ANIM = 0x80;
static const int MARISA_BIT_KILL_FRAMES_PER_CEL = 4;

extern "C" void near marisa_bits_update(void)
;

extern void (near pascal *near bit_fire)(marisa_bit_t near& bit);

extern "C" void near marisa_bits_fire(void)
;

#include "th04/main/gather.hpp"

extern "C" unsigned char near marisa_phase_entry(void);

extern "C" void near marisa_phase_cloud_pair(void)
;

extern "C" void near marisa_phase_gather_bits(void)
;

extern "C" void pascal near marisa_bit_fire_spread(marisa_bit_t near& bit)
;

extern bool pascal near marisa_flystep_pointreflected(int duration);

extern "C" void near marisa_phase_spread_bits(void)
;

extern "C" void pascal near marisa_bit_fire_single(marisa_bit_t near& bit)
;

extern "C" void near marisa_phase_star_bits(void)
;

extern "C" void near marisa_phase_orbit_cloud(void)
{
    unsigned char phase_state = marisa_phase_entry();
    register marisa_bit_t near *bit;
    register int i;

    if(phase_state == 2) {
        bullet_template.spawn_type = BST_PELLET;
        bit_fire = marisa_bit_fire_spread;
        boss_statebyte[15] = 0;
        return;
    }
    if(phase_state != 1) {
        return;
    }

    if(bits_alive != 0) {
        if(boss.phase_frame <= 192) {
            bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
            for(i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
                bit->distance += 0x18;
            }
            return;
        }
        if(boss.phase_frame <= 256) {
            if((boss.phase_frame % 4) != 0) {
                return;
            }
            if((boss.phase_frame % 32) == 0) {
                bullet_template.speed.v = TO_SP(2);
                bullet_template.group = BG_RING_AIMED;
                bullet_template.count = 16;
                bullet_template_tune();
                bullets_add_regular();
            }
            bullet_template.group = BG_SPREAD;
            bullet_template.count = 3;
            bullet_template.delta.spread_angle = 6;
            bullet_template_tune();
            bullet_template.speed.v = TO_SP(4);
            snd_se_play(9);
            marisa_bits_fire();
            return;
        }
        if(boss.phase_frame <= 384) {
            bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
            for(i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
                bit->distance -= 0x18;
            }
            return;
        }
        bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
        for(i = 0; i < MARISA_BIT_COUNT; i += 2, bit += 2) {
            bit->angle_speed = -bit->angle_speed;
        }
        goto phase_done;
    }

    marisa_flystep_pointreflected(96);
    if(boss_statebyte[15] == 0) {
        boss_statebyte[15] = 1;
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_SPREAD;
        bullet_template.angle = 0x80;
        bullet_template.delta.spread_angle = 8;
        snd_se_play(15);
    }
    if((boss.phase_frame % 2) != 0) {
        return;
    }

    bullet_template.count = (randring2_next16_and(3) + 1);
    bullet_template.speed.v = (randring2_next16_and(0x1F) + TO_SP(1));
    if((boss_statebyte[15] & 1) != 0) {
        bullet_template.angle -= 8;
    } else {
        bullet_template.angle += 8;
    }
    bullet_template.origin.x.v -= TO_SP(6);
    bullets_add_regular();

    bullet_template.count = (randring2_next16_and(3) + 1);
    bullet_template.speed.v = (randring2_next16_and(0x1F) + TO_SP(1));
    bullet_template.origin.x.v += TO_SP(12);
    bullets_add_regular();

    if((bullet_template.angle != 0) && (bullet_template.angle < 0x80)) {
        return;
    }
    boss_statebyte[15]++;
    if(boss_statebyte[15] < 4) {
        goto play_sound;
    }

phase_done:
    boss.phase_frame = 0;
    boss.mode = -1;
    boss.sprite = 129;
    goto done;

play_sound:
    snd_se_play(15);

done:
    ;
}

extern unsigned char marisa_pattern_variant;

extern "C" void near marisa_phase_random_burst(void)
{
    int speed;
    unsigned char phase_state = marisa_phase_entry();
    register int i;
    register marisa_bit_t near *bit;

    if(phase_state == 2) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.speed.v = (TO_SP(3) + 2);
        bullet_template.group = BG_RING_AIMED;
        bullet_template.angle = 0;
        bullet_template_tune();
        bit_fire = marisa_bit_fire_single;
        return;
    }
    if(phase_state != 1) {
        return;
    }

    if(bits_alive != 0) {
        if((boss.phase_frame % 32) == 0) {
            bullet_template.count = (24 - (bits_alive * 2));
            if(marisa_pattern_variant == 2) {
                bullet_template.count = 28;
            }
            marisa_bits_fire();
            snd_se_play(9);
        }
        if(boss.phase_frame >= 160) {
            bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
            for(i = 0; i < MARISA_BIT_COUNT; i += 2, bit += 2) {
                bit->angle_speed = -bit->angle_speed;
            }
            goto phase_done;
        }
        return;
    }

    if(marisa_flystep_pointreflected(64)) {
        goto phase_done;
    }
    if((boss.phase_frame % 16) != 0) {
        return;
    }

    bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
    bullet_template.patnum = PAT_BULLET16_N_BALL_RED;
    bullet_template.group = BG_SINGLE_AIMED;
    bullet_template.special_motion = BSM_NONE;
    bullet_template_tune();

    for(i = 0; i < 32; i++) {
        bullet_template.origin.x.v = (
            boss.pos.cur.x.v - TO_SP(52) + randring2_next16_mod(TO_SP(64))
        );
        bullet_template.origin.y.v = (
            boss.pos.cur.y.v - TO_SP(40) + randring2_next16_mod(TO_SP(64))
        );
        speed = (randring2_next16_mod(TO_SP(6)) + TO_SP(1));
        bullet_template.speed.v = static_cast<unsigned char>(speed);
        if(speed >= TO_SP(4)) {
            bullet_template.angle = 0;
        } else {
            speed = (TO_SP(4) - speed);
            bullet_template.angle = (
                randring2_next16_mod(speed) - (speed / 2)
            );
        }
        bullets_add_special();
    }
    snd_se_play(15);
    return;

phase_done:
    boss.phase_frame = 0;
    boss.mode = -1;
    boss.sprite = 129;
}

extern "C" void near marisa_phase_special_angles(void)
{
    unsigned char phase_state = marisa_phase_entry();
    register int i;

    if(phase_state == 2) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_STAR;
        bullet_template.speed.v = (TO_SP(5) + 12);
        bullet_template.group = BG_SINGLE;
        bullet_template.special_motion = BSM_DECELERATE_TO_ANGLE;
        bullet_template_tune();
        bit_fire = marisa_bit_fire_single;
        boss_statebyte[15] = 0;
        return;
    }
    if(phase_state != 1) {
        return;
    }

    if(bits_alive != 0) {
        if(boss.phase_frame > 96) {
            goto alive_128;
        }
        if((boss.phase_frame % 4) != 0) {
            goto frame_done;
        }
        bullet_template_special_angle.target = 0x40;
        bullet_template.angle = 0x10;
        for(i = 0; i < 4; i++) {
            bullets_add_special_fixedspeed();
            bullet_template.angle += 0x20;
        }
        goto sound3;

alive_128:
        if(boss.phase_frame > 128) {
            goto alive_160;
        }
        if((boss.phase_frame % 4) != 0) {
            goto frame_done;
        }
        bullet_template_special_angle.target = 0x30;
        bullet_template.angle = -0x70;
        bullets_add_special_fixedspeed();
        bullet_template_special_angle.target = 0x50;
        bullet_template.angle = -0x50;
        bullets_add_special_fixedspeed();
        bullet_template_special_angle.target = 0x30;
        bullet_template.angle = -0x30;
        bullets_add_special_fixedspeed();
        bullet_template_special_angle.target = 0x50;
        bullet_template.angle = -0x10;
        bullets_add_special_fixedspeed();

sound3:
        snd_se_play(3);
        goto frame_done;

alive_160:
        if(boss.phase_frame > 160) {
            goto alive_192;
        }
        if((boss.phase_frame % 4) != 0) {
            goto frame_done;
        }
        bullet_template_special_angle.target = 0x70;
        bullet_template.angle = 0x10;
        for(i = 0; i < 4; i++) {
            bullets_add_special_fixedspeed();
            bullet_template.angle += 0x20;
        }
        goto sound3;

alive_192:
        if(boss.phase_frame > 192) {
            goto alive_224;
        }
        if((boss.phase_frame % 4) != 0) {
            goto frame_done;
        }
        bullet_template_special_angle.target = 0x10;
        bullet_template.angle = 0x10;
        for(i = 0; i < 4; i++) {
            bullets_add_special_fixedspeed();
            bullet_template.angle += 0x20;
        }
        goto sound3;

alive_224:
        if(boss.phase_frame > 224) {
            goto frame_done;
        }
        if((boss.phase_frame % 4) != 0) {
            goto frame_done;
        }
        bullet_template_special_angle.target = 0x40;
        bullet_template.angle = 0x10;
        for(i = 0; i < 4; i++) {
            bullets_add_special_fixedspeed();
            bullet_template.angle += 0x20;
        }
        goto sound3;
    }

    marisa_flystep_pointreflected(128);
    if(boss_statebyte[15] == 0) {
        bullet_template.angle = (0x80 - randring2_next16_and(0x1F));
        boss_statebyte[15] = 1;
    }
    if((boss.phase_frame % 8) == 0) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_STACK;
        bullet_template.count = 16;
        bullet_template.delta.stack_speed.v = 5;
        bullet_template.speed.v = TO_SP(1);
        bullet_template_tune();
        bullets_add_regular_fixedspeed();
        bullet_template.angle -= 8;
        snd_se_play(15);
    }

    if(bullet_template.angle > 0x80) {
        if(bullet_template.angle <= 0xE0) {
            goto phase_done;
        }
    }

frame_done:
    if(boss.phase_frame < 256) {
        return;
    }

phase_done:
    boss.phase_frame = 0;
    boss.mode = -1;
    boss.sprite = 129;
}

extern "C" void near marisa_phase_edge_stars(void)
{
    unsigned char phase_state = marisa_phase_entry();

    if(phase_state == 2) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_STAR;
        bullet_template.group = BG_SINGLE;
        bullet_template.special_motion = BSM_NONE;
        bullet_template.angle = -0x40;
        bullet_template.speed.v = TO_SP(6);
        bit_fire = marisa_bit_fire_single;
        boss_statebyte[15] = 0;
        return;
    }
    if(phase_state != 1) {
        return;
    }

    if(bits_alive != 0) {
        if(boss.phase_frame <= 128) {
            if(stage_frame_mod4 != 0) {
                return;
            }
            marisa_bits_fire();
            snd_se_play(9);
            return;
        }
        if(boss.phase_frame <= 192) {
            if(stage_frame_mod4 != 0) {
                return;
            }

            bullet_template.origin.x.v = 0;
            bullet_template.origin.y.v = randring2_next16_mod(TO_SP(192));
            bullet_template.speed.v = (randring2_next16_and(0x1F) + TO_SP(1));
            bullet_template.angle = (0x30 - randring2_next16_and(0x1F));
            bullets_add_special();

            bullet_template.origin.x.v = TO_SP(384);
            bullet_template.origin.y.v = randring2_next16_mod(TO_SP(192));
            bullet_template.speed.v = (randring2_next16_and(0x1F) + TO_SP(1));
            bullet_template.angle = (randring2_next16_and(0x1F) + 0x50);
            bullets_add_special();

            bullet_template.origin.x.v = randring2_next16_mod(TO_SP(384));
            bullet_template.origin.y.v = 0;
            bullet_template.speed.v = (randring2_next16_and(0x1F) + TO_SP(1));
            bullet_template.angle = (randring2_next16_and(0x1F) + 0x30);
            bullets_add_special();
            return;
        }
        if(boss.phase_frame >= 256) {
            goto phase_done;
        }
        return;
    }

    marisa_flystep_pointreflected(160);
    if(boss_statebyte[15] == 0) {
        bullet_template.angle = randring2_next16_and(0x1F);
        boss_statebyte[15] = 1;
    }
    if((boss.phase_frame % 8) == 0) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_STACK;
        bullet_template.count = 16;
        bullet_template.delta.stack_speed.v = 5;
        bullet_template.speed.v = TO_SP(1);
        bullet_template_tune();
        bullets_add_regular_fixedspeed();
        bullet_template.angle += 8;
        snd_se_play(15);
    }
    if(boss.phase_frame < 192) {
        return;
    }

phase_done:
    boss.phase_frame = 0;
    boss.mode = -1;
    boss.sprite = 129;
}

extern "C" void near marisa_phase_ring_cycle(void)
{
    unsigned char phase_state = marisa_phase_entry();
    if(phase_state == 2) {
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.count = 32;
        bullet_template.group = BG_RING;
        bullet_template.speed.v = (TO_SP(3) + 8);
        bullet_template_tune();
        boss_statebyte[15] = ((randring2_next16_and(1) == 0) ? 1 : -1);
        return;
    }
    if(phase_state != 1) {
        return;
    }
    if((boss.phase_frame % 8) == 0) {
        bullets_add_regular();
        bullet_template.angle += boss_statebyte[15];
        snd_se_play(9);
    }
    if(boss.phase_frame >= 128) {
        boss.phase_frame = 0;
        boss.mode = -1;
        boss.sprite = 129;
    }
}
