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
;

extern unsigned char marisa_pattern_variant;

extern "C" void near marisa_phase_random_burst(void)
;

extern "C" void near marisa_phase_special_angles(void)
;

extern "C" void near marisa_phase_edge_stars(void)
;

extern "C" void near marisa_phase_ring_cycle(void)
;

extern "C" void near marisa_phase_spread_mirror(void)
{
    unsigned char phase_state = marisa_phase_entry();
    register marisa_bit_t near *bit;
    register int i;

    if(phase_state == 2) {
        boss_statebyte[14] = TO_SP(2);
        boss_statebyte[15] = randring2_next16_and(1);
    }
    if(marisa_phase_entry() != 1) {
        return;
    }

    if(bits_alive != 0) {
        if((boss.phase_frame % 4) == 0) {
            bit_fire = marisa_bit_fire_single;
            bullet_template.spawn_type = BST_PELLET;
            bullet_template.speed.v = TO_SP(2);
            bullet_template.group = BG_SINGLE;
            bullet_template.angle = static_cast<unsigned char>(stage_frame * 8);
            if(boss_statebyte[15] != 0) {
                bullet_template.angle = -bullet_template.angle;
            }
            bullet_template_tune();
            marisa_bits_fire();

            if((boss.phase_frame % 8) == 0) {
                bit_fire = marisa_bit_fire_spread;
                bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
                bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
                bullet_template.speed.v = boss_statebyte[14];
                boss_statebyte[14] += 2;
                bullet_template.group = BG_SINGLE;
                bullet_template.angle = 0;
                bullet_template_tune();
                marisa_bits_fire();
            }
            snd_se_play(9);
        }
        if(boss.phase_frame >= 160) {
            bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
            for(i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
                bit->angle_speed = -bit->angle_speed;
            }
            goto phase_done;
        }
        return;
    }

    if(marisa_flystep_pointreflected(72)) {
        goto phase_done;
    }
    if((boss.phase_frame % 8) != 0) {
        return;
    }
    bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
    bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
    bullet_template.group = BG_STACK_AIMED;
    bullet_template.count = 16;
    bullet_template.delta.stack_speed.v = 5;
    bullet_template.angle = 0;
    bullet_template.speed.v = TO_SP(1);
    bullet_template_tune();
    bullets_add_regular_fixedspeed();
    snd_se_play(15);
    return;

phase_done:
    boss.phase_frame = 0;
    boss.mode = -1;
    boss.sprite = 129;
}

extern "C" unsigned char near marisa_hittest_phase(void)
{
    boss.phase_frame++;
    boss.damage_this_frame = boss_hittest_shots_damage(TO_SP(24), TO_SP(24), 4);
    boss.hp -= (boss.damage_this_frame / (bits_alive + 1));
    if(boss.hp <= boss.phase_end_hp) {
        return 1;
    }
    return 0;
}

#ifdef TH04_MARISA_INCLUDE_UPDATE
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
#pragma codeseg MAI_TEXT main_01
extern void pascal near reimu_marisa_bg_render(void);
#pragma codeseg
extern bool palette_changed;
extern unsigned char bullet_clear_time;
extern unsigned char bullet_zap;
extern unsigned char player_invincibility_time;
extern SPPoint homing_target;
extern unsigned char marisa_prev_mode;
extern unsigned char marisa_prev_bits_alive;
extern unsigned char marisa_palette_direction;
extern unsigned char marisa_bitless_cycle;
extern "C" void near marisa_phase_move(void);
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);

void pascal far marisa_update(void)
{
    int candidate;

    bullet_template.origin.x.v = (boss.pos.cur.x.v - TO_SP(20));
    bullet_template.origin.y.v = (boss.pos.cur.y.v - TO_SP(8));

    switch(boss.phase) {
    case 0:
        if(boss.phase_frame == 0) {
            boss.hp = 6000;
            marisa_bit_angle_speed = 2;
        }
        boss_hittest_shots_invincible();
        if(boss.phase_frame <= 96) {
            goto update_tail;
        }
        boss.phase++;
        Palettes[0].c.r = 0;
        Palettes[0].c.g = 0;
        Palettes[0].c.b = 7;
        palette_changed = true;
        boss.phase_frame = 0;
        snd_se_play(13);
        bg_render_bombing_func = reimu_marisa_bg_render;
        tiles_bb_col = V_WHITE;
        marisa_palette_direction = 0;
        goto update_tail;

    case 1:
        boss.phase_frame++;
        boss_hittest_shots_invincible();
        if(boss.phase_frame < 128) {
            goto update_tail;
        }
        boss.phase++;
        boss.pos.velocity.x.v = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 10;
        boss.phase_frame = 0;
        boss.sprite = 129;
        marisa_bitless_cycle = 1;
        marisa_pattern_variant = 0;
        marisa_prev_mode = 10;
        marisa_prev_bits_alive = 0;
        boss_statebyte[13] = 0;
        goto update_tail;

    case 2:
        switch(boss.mode) {
        case 0:  marisa_phase_gather_bits(); break;
        case 1:  marisa_phase_spread_bits(); break;
        case 2:  marisa_phase_star_bits(); break;
        case 3:  marisa_phase_orbit_cloud(); break;
        case 4:  marisa_phase_random_burst(); break;
        case 5:  marisa_phase_special_angles(); break;
        case 6:  marisa_phase_edge_stars(); break;
        case 7:  marisa_phase_spread_mirror(); break;
        case 10: marisa_phase_cloud_pair(); break;
        case 11: marisa_phase_ring_cycle(); break;
        case 0xFF:
            marisa_phase_move();
            if(boss.phase_frame < 64) {
                break;
            }
            boss.phase_state.patterns_seen++;
            boss_statebyte[13] = 0;
            if((marisa_prev_bits_alive == 0) && (bits_alive == 0)) {
                marisa_bitless_cycle++;
                if(marisa_bitless_cycle >= 2) {
                    boss.mode = 0;
                    marisa_bitless_cycle = 0;
                } else {
                    boss.mode = (randring2_next16_and(1) + 10);
                }
            } else {
            choose_mode:
                candidate = (randring2_next16_mod(7) + 1);
                if(marisa_prev_mode == candidate) {
                    goto choose_mode;
                }
                boss.mode = candidate;
                marisa_prev_mode = candidate;
                marisa_prev_bits_alive = bits_alive;
            }
            boss.phase_frame = 0;
            if(boss.phase_state.patterns_seen >= 52) {
                boss.phase_state.patterns_seen = 0;
                goto phase_complete;
            }
            break;
        }

        if(marisa_hittest_phase()) {
            boss.phase_state.patterns_seen = 1;
        phase_complete:
            boss_explode_small(ET_HORIZONTAL);
            boss.phase++;
            boss.phase_frame = 0;
        }

        if(stage_frame_mod4 == 0) {
            if(marisa_palette_direction == 0) {
                Palettes[0].c.b = (Palettes[0].c.b + 2);
                if(Palettes[0].c.b >= 192) {
                    marisa_palette_direction = 1;
                }
            } else {
                Palettes[0].c.b = (Palettes[0].c.b - 2);
                if(Palettes[0].c.b <= 38) {
                    marisa_palette_direction = 0;
                }
            }
            palette_changed = true;
        }

        if((boss.hp <= 4500) && (marisa_pattern_variant == 0)) {
            goto hp_phase_done;
        }
        if((boss.hp <= 2500) && (marisa_pattern_variant == 1)) {
            goto hp_phase_done;
        }
        if((boss.hp <= 1000) && (marisa_pattern_variant == 2)) {
            goto hp_phase_done;
        }
        goto update_tail;

    hp_phase_done:
        boss_items_drop();
        if(bullet_clear_time < 20) {
            bullet_clear_time = 20;
        }
        boss_score_bonus(10);
        boss_explode_small(static_cast<explosion_type_t>(marisa_pattern_variant));
        marisa_pattern_variant++;
        goto update_tail;

    case 3:
        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_SW_NE));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(40);
            }
            boss.sprite = PAT_ENEMY_KILL;
            boss.phase_frame = 0;
            snd_se_play(12);
            Palettes[0].c.r = 0;
            Palettes[0].c.b = 0;
            palette_changed = true;
            player_invincibility_time = BOSS_DEFEAT_INVINCIBILITY_FRAMES;
        }
        goto update_tail;

    default:
        boss_defeat_update();
        return;
    }

update_tail:
    homing_target.x.v = boss.pos.cur.x.v;
    homing_target.y.v = boss.pos.cur.y.v;
    marisa_bits_update();
    hud_hp_update_and_render(boss.hp, 6000);
}
#endif
