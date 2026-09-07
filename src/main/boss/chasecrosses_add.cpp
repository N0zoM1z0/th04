#ifndef TH04_YUUKA6_MAIN034_COMBINED
#pragma option -zCMAIN_034_TEXT -zPmain_03
#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/snd/snd.h"
#include "th04/sprites/main_pat.h"
#include "th04/math/vector.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "th04/main/frames.h"
#include "th04/main/score.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/item/item.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/custom.hpp"
#include "th04/main/player/player.hpp"
#endif
#pragma samecodeseg sparks_add_random
extern SPPoint shot_hitbox_center;
extern SPPoint shot_hitbox_radius;
int shots_hittest(void);

enum chasecross_flag_t {
    CCF_FREE = 0,
    CCF_ALIVE = 1,
    CCF_KILL_ANIM = (PAT_ENEMY_KILL * 4),
    _chasecross_flag_t_FORCE_UINT8 = 0xFF
};

struct chasecross_t {
    chasecross_flag_t flag;
    unsigned char angle;
    PlayfieldPoint center;
    int8_t unused_1[4];
    PlayfieldPoint velocity;
    unsigned int age;
    int8_t unused_2[4];
    int hp;
    int damage_this_frame;
    SubpixelLength8 speed;
    int8_t padding;
};

#define chasecrosses (reinterpret_cast<chasecross_t *>(custom_entities))

void pascal near chasecrosses_add(
    unsigned char angle, subpixel_length_8_t speed
)
{
    chasecross_t near *p;
    int i;
    for((p = chasecrosses, i = 0); i < CUSTOM_COUNT; (i++, p++)) {
        if(p->flag == CCF_FREE) {
            p->flag = CCF_ALIVE;
            p->damage_this_frame = 0;
            p->age = 0;
            p->angle = angle;
            p->speed.v = speed;
            p->hp = 100;
            p->center.x.v = boss.pos.cur.x.v;
            p->center.y.v = boss.pos.cur.y.v;
            break;
        }
    }
}

enum safetycircle_flag_t {
    SCF_FREE = 0,
    SCF_GROW = 1,
    SCF_SHRINK = 2,
    _safetycircle_flag_t_FORCE_UINT8 = 0xFF
};

struct safetycircle_t {
    safetycircle_flag_t flag;
    int8_t unused_1;
    screen_point_t center;
    int8_t unused_2[8];
    unsigned int shrink_frame;
    pixel_t radius_filled;
    pixel_t radius_ring_distance;
    int8_t unused_3[4];
    vc_t col_ring;
    int8_t padding;
};

#define safetycircle ( \
    reinterpret_cast<safetycircle_t &>(custom_entities[CUSTOM_COUNT - 1]) \
)

extern "C" void near yuuka6_safetycircle_add(void)
{
    safetycircle_t near *p = &safetycircle;
    p->flag = SCF_GROW;
    p->shrink_frame = 0;
    p->col_ring = 8;
    p->center.x = ((player_pos.cur.x.v >> 4) + PLAYFIELD_LEFT);
    p->center.y = ((player_pos.cur.y.v >> 4) + PLAYFIELD_TOP);
    p->radius_filled = 8;
    p->radius_ring_distance = 80;
    snd_se_play(8);
}


extern "C" void near yuuka6_entities_update(void)
{
    subpixel_t length;
    subpixel_t top;
    unsigned char angle;
    signed char angle_delta;
    chasecross_t near *p;
    int i;

    shot_hitbox_radius.x.v = TO_SP(12);
    shot_hitbox_radius.y.v = TO_SP(12);
    for((p = chasecrosses, i = 0); i < (CUSTOM_COUNT - 1); (i++, p++)) {
        if(p->flag != CCF_ALIVE) {
            continue;
        }
        vector2_near(p->velocity, p->angle, p->speed.v);
        p->center.x.v += p->velocity.x.v;
        p->center.y.v += p->velocity.y.v;
        if(
            (p->center.x.v <= TO_SP(-(32 / 2))) ||
            (p->center.x.v >= TO_SP(PLAYFIELD_W + (32 / 2))) ||
            (p->center.y.v >= TO_SP(PLAYFIELD_H + (32 / 2))) ||
            (p->center.y.v <= TO_SP(-(32 / 2)))
        ) {
            p->flag = CCF_FREE;
        }

        length = (p->center.x.v - TO_SP(12));
        top = (p->center.y.v - TO_SP(12));
        if(
            (static_cast<unsigned int>(player_pos.cur.x.v - length) < TO_SP(24)) &&
            (static_cast<unsigned int>(player_pos.cur.y.v - top) < TO_SP(24))
        ) {
            player_is_hit = true;
        }

        if(p->age < 56) {
            angle = iatan2(
                (player_pos.cur.y.v - p->center.y.v),
                (player_pos.cur.x.v - p->center.x.v)
            );
            angle -= p->angle;
            if(angle < 0x80) {
                p->angle++;
            } else if(angle >= 0x80) {
                p->angle--;
            }
        }

        shot_hitbox_center.x.v = p->center.x.v;
        shot_hitbox_center.y.v = p->center.y.v;
        if((p->damage_this_frame = shots_hittest()) != 0) {
            snd_se_play(4);
        }
        p->hp -= p->damage_this_frame;
        if(p->hp <= 0) {
            snd_se_play(3);
            score_delta += 3000;
            p->flag = CCF_KILL_ANIM;
            p->age = 0;
            sparks_add_random(p->center.x, p->center.y, TO_SP(4), 8);
            items_add(p->center.x.v, p->center.y.v, IT_BIGPOWER);
        }
        p->age++;
    }

    #define sc (*reinterpret_cast<safetycircle_t near *>(p))
    switch(sc.flag) {
    case SCF_GROW:
        if(sc.radius_filled <= 128) {
            sc.radius_filled += 8;
        } else {
            sc.flag = SCF_SHRINK;
        }
        return;
    case SCF_SHRINK:
        break;
    default:
        return;
    }

    if(sc.shrink_frame < 8) {
        sc.radius_ring_distance -= 8;
    } else if(sc.shrink_frame == 8) {
        sc.col_ring = 9;
    } else if(sc.shrink_frame < 16) {
        sc.radius_ring_distance -= 2;
    } else if(sc.shrink_frame < 160) {
        if((sc.shrink_frame & 0x1F) < 16) {
            sc.radius_ring_distance++;
        } else {
            sc.radius_ring_distance--;
        }
        if(stage_frame_mod2 != 0) {
            sc.col_ring = 15;
        } else {
            sc.col_ring = 9;
        }
        if(sc.shrink_frame <= 104) {
            sc.radius_filled--;
        }
        if((static_cast<unsigned char>(sc.shrink_frame) & 0x0F) == 0) {
            angle_delta = -0x40;
            if((static_cast<unsigned char>(sc.shrink_frame) & 0x1F) == 0) {
                bullet_template.origin.x.v = boss.pos.cur.x.v;
                bullet_template.origin.y.v = (boss.pos.cur.y.v + TO_SP(32));
                bullet_template.spawn_type = BST_BULLET16;
                bullet_template.patnum = PAT_BULLET16_N_SMALL_BALL_RED;
                bullet_template.group = BG_RING_AIMED;
                bullet_template.count = 32;
                bullet_template.speed.v = TO_SP(1);
                bullet_template.angle = 0;
                bullet_template_tune();
                bullets_add_regular();
                angle_delta = 0x40;
            }

            bullet_template.spawn_type = BST_PELLET;
            bullet_template.delta.spread_angle = 0x0C;
            angle = (stage_frame / 5);
            length = (sc.radius_filled + 4);
            for(i = 0; i < 8; (i++, angle += 0x20)) {
                bullet_template.angle = (angle + angle_delta);
                vector2_at(
                    bullet_template.origin,
                    sc.center.x,
                    sc.center.y,
                    length,
                    angle
                );
                bullet_template.origin.x.v -= TO_SP(2);
                bullet_template.origin.y.v -= TO_SP(1);
                bullet_template.origin.x.v *= SUBPIXEL_FACTOR;
                bullet_template.origin.y.v *= SUBPIXEL_FACTOR;
                bullet_template.group = BG_STACK;
                bullet_template.count = 8;
                bullet_template.speed.v = TO_SP(1);
                bullets_add_regular();
                bullet_template.group = BG_SPREAD;
                bullet_template.count = 4;
                bullet_template.speed.v = TO_SP(3);
                bullets_add_regular();
            }
            snd_se_play(3);
        }
    } else if(sc.shrink_frame < 176) {
        sc.radius_ring_distance += 16;
        sc.radius_filled -= 2;
    } else {
        sc.flag = SCF_FREE;
    }
    sc.shrink_frame++;
    #undef sc
}

static const int YUUKA6_PHASE2_FLY_NODES = 5;
extern uint8_t yuuka6_phase2_fly_path;
extern const unsigned char YUUKA6_PHASE2_FLY_ANGLES[2][YUUKA6_PHASE2_FLY_NODES];
extern "C" bool pascal near yuuka6_move_towards(subpixel_t x, subpixel_t y);

bool near yuuka6_phase2_fly(void)
{
    if((boss.phase_state.patterns_seen % (YUUKA6_PHASE2_FLY_NODES + 1)) < YUUKA6_PHASE2_FLY_NODES) {
        switch(boss.phase_frame) {
        case 1:
            vector2_near(
                boss.pos.velocity,
                YUUKA6_PHASE2_FLY_ANGLES[yuuka6_phase2_fly_path][
                    boss.phase_state.patterns_seen % (YUUKA6_PHASE2_FLY_NODES + 1)
                ],
                8
            );
            break;
        case 112:
            boss.phase_frame = 0;
            boss.phase_state.patterns_seen++;
            return true;
        }
        boss.pos.cur.x.v += boss.pos.velocity.x.v;
        boss.pos.cur.y.v += boss.pos.velocity.y.v;
        return false;
    }
    return yuuka6_move_towards(TO_SP(PLAYFIELD_W / 2), TO_SP(80));
}


// Target-local auxiliary state used while moving Yuuka in phase 2. The
// original ASM kept these labels private; exact replay exposes zero-byte
// aliases without changing their storage or layout.
extern unsigned char yuuka6_aux_state;
extern unsigned char yuuka6_aux_flag;
extern SPPoint yuuka6_aux_pos;
extern unsigned char yuuka6_sprite_flag;
extern "C" bool near yuuka6_anim_vanish(void);
extern "C" bool near yuuka6_anim_appear(void);

enum yuuka6_sprite_flag_move_t {
    Y6SF_MOVE_VANISHED = 0,
};

bool pascal near yuuka6_move_towards(
    subpixel_t x, subpixel_t y
)
{
    if(boss.phase_frame < 64) {
        if(yuuka6_sprite_flag != Y6SF_MOVE_VANISHED) {
            yuuka6_anim_vanish();
        }
    } else if(yuuka6_sprite_flag == Y6SF_MOVE_VANISHED) {
        yuuka6_anim_appear();
    }

    switch(boss.phase_frame) {
    case 64:
        boss.pos.cur.x.v = x;
        boss.pos.cur.y.v = y;
        if(yuuka6_aux_state != 0) {
            yuuka6_aux_state = 2;
            yuuka6_aux_pos.x.v = (TO_SP(PLAYFIELD_W) - x);
            yuuka6_aux_pos.y.v = y;
        }
        break;

    case 128:
        boss.phase_frame = 0;
        boss.phase_state.patterns_seen++;
        return true;
    }
    return false;
}


void near yuuka6_horizontal_wave(void)
{
    if(boss.phase_frame == 1) {
        boss.pos.velocity.x.v = TO_SP(2);
        boss.angle = 0;
    }
    boss.pos.cur.x.v += boss.pos.velocity.x.v;
    if((boss.pos.cur.x.v <= TO_SP(48)) || (boss.pos.cur.x.v >= TO_SP(336))) {
        boss.pos.velocity.x.v *= -1;
    }
    boss.pos.cur.y.v = polar(TO_SP(80), TO_SP(48), SinTable8[boss.angle]);
    boss.angle += 2;
}


bool near yuuka6_move_to_center(void)
{
    if(yuuka6_sprite_flag == Y6SF_MOVE_VANISHED) {
        yuuka6_anim_appear();
    } else {
        yuuka6_aux_flag = 0;
        if(boss.pos.cur.x.v < TO_SP(192)) {
            boss.pos.cur.x.v += TO_SP(1);
        } else if(boss.pos.cur.x.v >= TO_SP(193)) {
            boss.pos.cur.x.v -= TO_SP(1);
        } else {
            return true;
        }
    }
    return false;
}
