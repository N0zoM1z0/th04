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
{
    unsigned char angle;
    marisa_bit_hp_t bit_hp = MARISA_BIT_HP;
    angle = randring2_next16();
    marisa_bit_t near *bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);

    for(int i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
        bit->flag = M4BF_MOVEOUT_SPIN;
        bit->angle_speed = marisa_bit_angle_speed;
        bit->angle = angle;
        angle += (256 / MARISA_BIT_COUNT);
        bit->patnum = (PAT_MARISA_BIT + i);
        bit->distance = 0;
        bit->hp = bit_hp.value[i];
        bit->moveout_speed = TO_SP(2);
    }
}

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
{
    volatile int i;
    int top;
    bits_alive = 0;
    register marisa_bit_t near *bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
    register int work;

    for(i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
        if(bit->flag == M4BF_FREE) {
            continue;
        }
        if(bit->flag >= M4BF_KILL_ANIM) {
            work = (bit->flag = (bit->flag + 1));
            work = (
                ((work - M4BF_KILL_ANIM) / MARISA_BIT_KILL_FRAMES_PER_CEL) +
                PAT_ENEMY_KILL
            );
            bit->patnum = work;
            if(work < (PAT_ENEMY_KILL + ENEMY_KILL_CELS)) {
                continue;
            }
            bit->flag = M4BF_FREE;
            continue;
        }

        bit->angle += bit->angle_speed;
        bit->distance += bit->moveout_speed;
        vector2_at(
            bit->center,
            boss.pos.cur.x.v,
            boss.pos.cur.y.v,
            bit->distance,
            bit->angle
        );

        if(bit->flag == M4BF_MOVEOUT_SPIN) {
            if(bit->distance >= TO_SP(64)) {
                bit->flag++;
                bit->moveout_speed = 0;
            }
        } else if(bit->flag == M4BF_SPIN) {
            if(bit->distance >= TO_SP(4)) {
                bit->flag++;
            }
        }

        shot_hitbox_radius.x.v = TO_SP(12);
        shot_hitbox_radius.y.v = TO_SP(12);
        shot_hitbox_center.x.v = bit->center.x.v;
        shot_hitbox_center.y.v = bit->center.y.v;
        bit->damage_this_frame = shots_hittest();
        bit->hp -= bit->damage_this_frame;

        if(bit->hp <= 0) {
            bit->patnum = PAT_ENEMY_KILL;
            bit->flag = M4BF_KILL_ANIM;
            snd_se_play(3);
            score_delta += 5120;
            sparks_add_random(bit->center.x, bit->center.y, TO_SP(4), 8);
            continue;
        }

        work = (bit->center.x.v - TO_SP(12));
        top = (bit->center.y.v - TO_SP(12));
        if(
            (static_cast<unsigned int>(player_pos.cur.x.v - work) < TO_SP(24)) &&
            (static_cast<unsigned int>(player_pos.cur.y.v - top) < TO_SP(24))
        ) {
            player_is_hit = true;
        }

        if(bit->center.y.v < homing_target.y.v) {
            homing_target.x.v = bit->center.x.v;
            homing_target.y.v = bit->center.y.v;
        }

        bit_center_x[bits_alive] = ((bit->center.x.v >> 4) + PLAYFIELD_LEFT);
        bit_center_y[bits_alive] = ((bit->center.y.v >> 4) + PLAYFIELD_TOP);
        bits_alive++;
    }
}

extern void (near pascal *near bit_fire)(marisa_bit_t near& bit);

extern "C" void near marisa_bits_fire(void)
{
    register marisa_bit_t near *bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
    for(int i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
        if((bit->flag != M4BF_FREE) && (bit->flag < M4BF_KILL_ANIM)) {
            bit_fire(*bit);
        }
    }
}

#include "th04/main/gather.hpp"

extern "C" unsigned char near marisa_phase_entry(void);

extern "C" void near marisa_phase_cloud_pair(void)
{
    unsigned char phase_state = marisa_phase_entry();
    if(phase_state == 2) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_SPREAD;
        bullet_template.angle = 0x80;
        bullet_template.delta.spread_angle = 8;
        bullet_template_tune();
        return;
    }
    if(phase_state != 1) {
        return;
    }

    if((boss.phase_frame % 2) == 0) {
        bullet_template.count = (randring2_next16_and(3) + 1);
        bullet_template.speed.v = (randring2_next16_and(0x1F) + TO_SP(2));
        bullet_template.angle -= 8;
        bullet_template.origin.x.v -= TO_SP(6);
        bullets_add_regular();

        bullet_template.count = (randring2_next16_and(3) + 1);
        bullet_template.speed.v = (randring2_next16_and(0x1F) + TO_SP(2));
        bullet_template.origin.x.v += TO_SP(12);
        bullets_add_regular();
    }

    if(bullet_template.angle == 0) {
        boss.phase_frame = 0;
        boss.mode = -1;
        boss.sprite = 129;
    }
}

extern "C" void near marisa_phase_gather_bits(void)
{
    marisa_phase_entry();

    switch(boss.phase_frame) {
    case 32:
        gather_template.center.x.v = boss.pos.cur.x.v;
        gather_template.center.y.v = boss.pos.cur.y.v;
        gather_template.ring_points = 32;
        gather_template.angle_delta = -2;
        gather_template.col = 9;
        gather_template.radius.v = TO_SP(256);
    add_gather:
        gather_add_only();
        return;

    case 34:
        gather_template.col = 8;
        goto add_gather;

    case 36:
        goto add_gather;

    case 64:
        marisa_bits_init();
        marisa_bit_angle_speed = -marisa_bit_angle_speed;
        return;

    case 96:
        boss.phase_frame = 0;
        boss.mode = -1;
        boss.sprite = 129;
        return;

    default:
        return;
    }
}

extern "C" void pascal near marisa_bit_fire_spread(marisa_bit_t near& bit)
{
    unsigned char angle;
    if(bits_alive <= 2) {
        bullet_template.count = 5;
    }
    angle = ((bit.angle_speed >= 0) ? -0x40 : 0x40);
    bullet_template.angle = (bit.angle + angle);
    bullet_template.origin = bit.center;
    bullets_add_regular();
}

extern bool pascal near marisa_flystep_pointreflected(int duration);

extern "C" void near marisa_phase_spread_bits(void)
{
    unsigned char phase_state = marisa_phase_entry();
    register marisa_bit_t near *bit;
    register int i;
    if(phase_state == 2) {
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.speed.v = (TO_SP(3) + 8);
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 3;
        bullet_template.delta.spread_angle = 8;
        bullet_template_tune();
        bit_fire = marisa_bit_fire_spread;
        boss_statebyte[15] = static_cast<unsigned char>(boss.phase_frame);
        return;
    }
    if(phase_state != 1) {
        return;
    }
    if((boss.phase_frame % 4) == 0) {
        if(bits_alive != 0) {
            marisa_bits_fire();
            boss_statebyte[15] = static_cast<unsigned char>(boss.phase_frame);
        } else {
            marisa_flystep_pointreflected(160 - boss_statebyte[15]);
            bullet_template.spawn_type = BST_BULLET16;
            bullet_template.patnum = PAT_BULLET16_D_BLUE;
            bullet_template.speed.v = (TO_SP(3) + 4);
            bullet_template.group = BG_SPREAD;
            bullet_template.count = 3;
            bullet_template.delta.spread_angle = 6;
            bullet_template.angle += 6;
            bullet_template_tune();
            bullets_add_regular();
            bullet_template.angle += 0x40;
            bullets_add_regular();
            bullet_template.angle += 0x40;
            bullets_add_regular();
            bullet_template.angle += 0x40;
            bullets_add_regular();
        }
        snd_se_play(9);
    }
    if(boss.phase_frame >= 160) {
        bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
        for(i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
            bit->angle_speed = -bit->angle_speed;
        }
        boss.phase_frame = 0;
        boss.mode = -1;
        boss.sprite = 129;
    }
}

extern "C" void pascal near marisa_bit_fire_single(marisa_bit_t near& bit)
{
    bullet_template.origin = bit.center;
    bullets_add_regular();
}

extern "C" void near marisa_phase_star_bits(void)
{
    unsigned char phase_state = marisa_phase_entry();
    register marisa_bit_t near *bit;
    register int i;
    if(phase_state == 2) {
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.speed.v = TO_SP(1);
        bullet_template.group = BG_SINGLE;
        bullet_template_tune();
        bit_fire = marisa_bit_fire_single;
        bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
        for(i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
            bit->angle_speed += bit->angle_speed;
        }
        boss_statebyte[15] = static_cast<unsigned char>(boss.phase_frame);
        return;
    }
    if(phase_state != 1) {
        return;
    }
    if((boss.phase_frame % 4) == 0) {
        bullet_template.angle = iatan2(
            (player_pos.cur.y.v - boss.pos.cur.y.v),
            (player_pos.cur.x.v - boss.pos.cur.x.v)
        );
        if(bits_alive != 0) {
            marisa_bits_fire();
            boss_statebyte[15] = static_cast<unsigned char>(boss.phase_frame);
        } else {
            marisa_flystep_pointreflected(160 - boss_statebyte[15]);
            bullet_template.spawn_type = BST_BULLET16;
            bullet_template.patnum = PAT_BULLET16_N_STAR;
            bullet_template.group = BG_SPREAD_AIMED;
            bullet_template.count = 3;
            bullet_template.delta.spread_angle = 0x0C;
            bullet_template.angle = 0;
            bullet_template_tune();
            bullets_add_regular();
        }
        bullet_template.speed.v += 4;
        snd_se_play(9);
    }
    if(boss.phase_frame >= 160) {
        bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
        for(i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
            bit->angle_speed /= 2;
        }
        boss.phase_frame = 0;
        boss.mode = -1;
        boss.sprite = 129;
    }
}
