#pragma option -zCMAIN_034_TEXT -zPmain_03

// Target relocation order proves that these four contiguous source families
// were emitted by one TC86 producer object. Keep ABI-bearing headers before
// the word-alignment switch, then enable -a only after the chase prefix.
#define TH04_YUUKA6_MAIN034_COMBINED 1
#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/snd/snd.h"
#include "th04/sprites/main_pat.h"
#include "th04/math/vector.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "th04/main/frames.h"
#include "th04/main/score.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/item/item.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/custom.hpp"
#include "th04/main/player/player.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th03/math/randring.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/rank.hpp"
#include "th04/main/bullet/laser_t.hpp"

#include "th04/chase.cpp"
#pragma option -a
#include "th04/anims.cpp"
#include "th04/y6gath.cpp"

extern unsigned char yuuka6_sprite_flag;

extern "C" bool near yuuka6_anim_parasol_back_close(void);
extern "C" bool near yuuka6_anim_parasol_back_open(void);
extern "C" bool near yuuka6_anim_parasol_back_pull_forward(void);
extern "C" bool near yuuka6_anim_parasol_back_pull_left(void);
extern "C" bool near yuuka6_anim_parasol_left_spin_back(void);
extern "C" void near yuuka6_safetycircle_add(void);
extern "C" void near y6_gather_side(void);
extern "C" void near y6_gather_center(void);

enum yuuka6_sprite_attack_flag_t {
    Y6SF_ATTACK_PARASOL_BACK_OPEN = 1,
    Y6SF_ATTACK_PARASOL_BACK_CLOSED = 2,
    Y6SF_ATTACK_PARASOL_LEFT = 4,
};

extern "C" void near y6_attack_ring_turn(void)
{
    if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_OPEN) {
        yuuka6_anim_parasol_back_close();
    }
    y6_gather_side();

    switch(boss.phase_frame) {
    case 48:
        bullet_template.speed.v = (TO_SP(2) + 8);
        // fall through
    case 64:
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.origin.x.v = boss.pos.cur.x.v;
        bullet_template.origin.y.v = (boss.pos.cur.y.v - TO_SP(4));
        bullet_template.angle = 0;
        bullet_template.group = BG_RING;
        bullet_template.special_motion = BSM_DECELERATE_THEN_TURN;
        bullet_template.count = 20;
        bullet_template_special_angle.turn_by = -0x40;
        bullet_template_tune();
        bullets_add_special_fixedspeed();
        bullet_template_special_angle.turn_by = 0x40;
        bullets_add_special_fixedspeed();
        snd_se_play(9);
        bullet_template.speed.v += TO_SP(1);
        break;

    case 80:
        boss.phase_frame = 0;
        boss.mode = -1;
        break;
    }
}

extern "C" void near y6_attack_spin_rings(void)
{
    unsigned char angle;

    if(boss.phase_frame < 48) {
        if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_back_pull_left();
        }
    } else if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_LEFT) {
        yuuka6_anim_parasol_left_spin_back();
        if(boss.phase_frame <= 80) {
            bullet_template.spawn_type = BST_PELLET;
            bullet_template.group = BG_RING;
            bullet_template.count = boss_statebyte[1];
            angle = (0 - (boss.phase_frame << 3));
            bullet_template.speed.v = (TO_SP(2) + 8);
            bullet_template.angle = angle;
            vector2_at(
                bullet_template.origin,
                boss.pos.cur.x.v,
                boss.pos.cur.y.v,
                TO_SP(34),
                angle
            );
            bullets_add_regular();

            angle = (0x80 - angle);
            vector2_at(
                bullet_template.origin,
                boss.pos.cur.x.v,
                boss.pos.cur.y.v,
                TO_SP(34),
                angle
            );
            bullet_template.speed.v = ((TO_SP(3) + 12) - (boss.phase_frame / 2));
            bullets_add_regular();
            if(stage_frame_mod4 == 0) {
                snd_se_play(9);
            }
        }
    }

    switch(boss.phase_frame) {
    case 32:
        circles_add_shrinking(
            (boss.pos.cur.x.v - TO_SP(40)),
            (boss.pos.cur.y.v + TO_SP(40))
        );
        circles_color = V_WHITE;
        break;

    case 96:
        boss.phase_frame = 0;
        boss.mode = -1;
        break;
    }
}

extern "C" void near y6_attack_gravity(void)
{
    if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
        yuuka6_anim_parasol_back_open();
    }

    if((boss.phase_frame >= 48) && (boss.phase_frame <= 80)) {
        if(stage_frame_mod4 == 0) {
            bullet_template.spawn_type = ((stage_frame_mod8 / 4) + 1);
            bullet_template.patnum = PAT_BULLET16_N_SMALL_BALL_RED;
            bullet_template.origin.y.v = (boss.pos.cur.y.v - TO_SP(4));
            bullet_template.group = BG_RANDOM_ANGLE_AND_SPEED;
            bullet_template.count = 4;
            bullet_template.special_motion = BSM_GRAVITY;
            bullet_template.speed.v = (randring2_next16_mod(TO_SP(1) + 8) + 8);

            bullet_template.origin.x.v = (boss.pos.cur.x.v - TO_SP(20));
            bullet_template.angle = randring2_next16();
            bullet_special.speed_delta.v = 1;
            bullet_template_tune();
            bullets_add_special_fixedspeed();

            bullet_template.angle = randring2_next16();
            bullet_template.origin.x.v += TO_SP(44);
            bullets_add_special_fixedspeed();
            snd_se_play(9);
        }
    } else if(boss.phase_frame > 80) {
        boss.phase_frame = 0;
        boss.mode = -1;
    }
    y6_gather_side();
}

extern "C" void near y6_attack_safetycircle(void)
{
    if(boss.phase_frame < 64) {
        if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_OPEN) {
            yuuka6_anim_parasol_back_close();
        } else if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_back_pull_forward();
        }
    } else if((boss.phase_frame >= 64) && (boss.phase_frame <= 112)) {
        boss.sprite = PAT_YUUKA6_PARASOL_FORWARD_OPEN;
    } else if(boss.phase_frame >= 288) {
        if(yuuka6_sprite_flag != Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_left_spin_back();
        } else if(yuuka6_anim_parasol_back_open()) {
            boss.phase_frame = 0;
            boss.mode = -1;
        }
    }

    y6_gather_center();
    if(boss.phase_frame == 64) {
        yuuka6_safetycircle_add();
    }
}

extern "C" void near y6_attack_bullets(void)
{
    if(stage_frame_mod16 != 0) {
        return;
    }

    bullet_template.origin.x.v = boss.pos.cur.x.v;
    bullet_template.origin.y.v = boss.pos.cur.y.v;
    if(boss.phase == 6) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_SMALL_BALL_RED;
        bullet_template.angle = randring2_next16();
        bullet_template.group = BG_RING;
        bullet_template.count = 16;
        bullet_template.speed.v = (TO_SP(1) + 14);
        bullet_template_tune();
        bullets_add_regular();

        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.count = ((boss.phase_frame / 16) + 2);
        bullet_template.speed.v = (TO_SP(2) + 2);
    } else {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        bullet_template.angle = 0;
        bullet_template.group = BG_STACK_AIMED;
        bullet_template.count = 7;
        bullet_template.speed.v = TO_SP(2);
        bullet_template.delta.stack_speed.v = 10;
        bullet_template_tune();
        bullets_add_regular_fixedspeed();
        snd_se_play(15);

        bullet_template.spawn_type = BST_PELLET;
        bullet_template.group = BG_RANDOM_ANGLE_AND_SPEED;
        bullet_template.count = 4;
        bullet_template.speed.v = (TO_SP(1) + 8);
    }

    bullet_template_tune();
    bullets_add_regular();
}


extern SPPoint shot_hitbox_center;
extern SPPoint shot_hitbox_radius;
int shots_hittest(void);

extern SPPoint yuuka6_mirror_pos;
extern unsigned char yuuka6_mirror_state;
extern unsigned char yuuka6_mirror_damage;
extern "C" void near thicklaser_add(void);
extern "C" void near y6_gather_dual(void);
extern "C" void near y6_gather_self(void);

extern "C" void near y6_phase_dual_lasers(void)
{
    if(boss.phase_frame < 64) {
        if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_OPEN) {
            yuuka6_anim_parasol_back_close();
        } else if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_back_pull_forward();
        }
        bullet_template.speed.v = TO_SP(1);
    } else if((boss.phase_frame >= 64) && (boss.phase_frame <= 128)) {
        boss.sprite = PAT_YUUKA6_PARASOL_FORWARD_OPEN;
        if(stage_frame_mod8 == 0) {
            bullet_template.origin.x.v = boss.pos.cur.x.v;
            bullet_template.origin.y.v = boss.pos.cur.y.v;
            bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
            bullet_template.patnum = PAT_BULLET16_D_BLUE;
            bullet_template.group = BG_SPREAD;
            bullet_template.delta.spread_angle = 8;
            bullet_template.count = 3;
            bullet_template_tune();
            bullet_template.angle = 0x60;
            bullets_add_regular();
            bullet_template.angle = 0x20;
            bullets_add_regular();
            bullet_template.origin.x.v = yuuka6_mirror_pos.x.v;
            bullets_add_regular();
            bullet_template.angle = 0x60;
            bullets_add_regular();
            bullet_template.speed.v += 12;
            snd_se_play(3);
        }
    } else if(boss.phase_frame >= 128) {
        if(yuuka6_sprite_flag != Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_left_spin_back();
        } else if(yuuka6_anim_parasol_back_open()) {
            boss.phase_frame = 0;
            boss.mode = -1;
        }
    }

    y6_gather_dual();
    if(boss.phase_frame == 64) {
        thicklaser_template.radius_max = boss_statebyte[0];
        thicklaser_template.radius_speed = 4;
        thicklaser_template.line_frames = 36;
        thicklaser_template.static_frames = 40;
        thicklaser_template.col_outline = 8;
        thicklaser_template.origin.x.v = boss.pos.cur.x.v;
        thicklaser_template.origin.y.v = (boss.pos.cur.y.v + TO_SP(32));
        thicklaser_add();
        thicklaser_template.origin.x.v = yuuka6_mirror_pos.x.v;
        thicklaser_template.origin.y.v = (yuuka6_mirror_pos.y.v + TO_SP(40));
        thicklaser_add();
    }
}

extern "C" void near y6_phase_dual_spreads(void)
{
    if(boss.phase_frame < 64) {
        if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_OPEN) {
            yuuka6_anim_parasol_back_close();
        } else if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_back_pull_forward();
        }
        boss_statebyte[15] = 2;
    } else if((boss.phase_frame >= 64) && (boss.phase_frame <= 128)) {
        boss.sprite = PAT_YUUKA6_PARASOL_FORWARD_OPEN;
        if(stage_frame_mod4 == 0) {
            bullet_template.origin.y.v = (boss.pos.cur.y.v + TO_SP(32));
            bullet_template.spawn_type = BST_BULLET16;
            bullet_template.patnum = PAT_BULLET16_D_YELLOW;
            bullet_template.group = BG_SPREAD;
            bullet_template.count = 5;
            bullet_template.speed.v = (randring2_next16_and(0x1F) + 12);
            bullet_template.delta.spread_angle = 0x10;
            bullet_template.angle = (
                randring2_next16_mod(boss_statebyte[15] * 2) +
                (0x40 - boss_statebyte[15])
            );
            bullet_template.origin.x.v = boss.pos.cur.x.v;
            bullets_add_regular();
            bullet_template.angle = (
                randring2_next16_mod(boss_statebyte[15] * 2) +
                (0x40 - boss_statebyte[15])
            );
            bullet_template.origin.x.v = yuuka6_mirror_pos.x.v;
            bullets_add_regular();
            snd_se_play(9);
            boss_statebyte[15] += 6;
        }
    } else if(boss.phase_frame >= 128) {
        if(yuuka6_sprite_flag != Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_left_spin_back();
        } else if(yuuka6_anim_parasol_back_open()) {
            boss.phase_frame = 0;
            boss.mode = -1;
        }
    }
    y6_gather_dual();
}

extern "C" void near y6_phase_rotating_ring(void)
{
    if(boss.phase_frame <= 48) {
        if(yuuka6_sprite_flag != 8) {
            yuuka6_anim_parasol_shield();
        }
    } else if(boss.phase_frame < 136) {
        boss.sprite = (((stage_frame_mod4 / 2) * 2) + 146);
        if(stage_frame_mod2 != 0) {
            bullets_add_regular_fixedspeed();
        }
        if(stage_frame_mod4 == 0) {
            snd_se_play(3);
        }
        if(boss.phase_frame >= 112) {
            bullet_template.angle += boss.angle;
        }
    } else if((rank >= RANK_HARD) && (boss.phase_frame < 150)) {
        bullet_template.angle -= boss.angle;
        if(stage_frame_mod2 != 0) {
            bullets_add_regular_fixedspeed();
        }
        if(stage_frame_mod4 == 0) {
            snd_se_play(3);
        }
    } else {
        boss.sprite = 146;
    }

    y6_gather_self();
    switch(boss.phase_frame) {
    case 48:
        bullet_template.angle = (
            iatan2(
                (boss.pos.cur.y.v - player_pos.cur.y.v),
                (boss.pos.cur.x.v - player_pos.cur.x.v)
            ) + 0x10
        );
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_RED;
        bullet_template.origin.x.v = boss.pos.cur.x.v;
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        bullet_template.group = BG_RING;
        bullet_template.count = 8;
        bullet_template.speed.v = TO_SP(9);
        if(rank != RANK_EASY) {
            boss.angle = (randring2_next16_and(1) ? 1 : -1);
        } else {
            boss.angle = 0;
        }
        break;

    case 144:
        if(rank >= RANK_HARD) {
            break;
        }
        // fall through
    case 156:
        boss.phase_frame = 0;
        boss.mode = -1;
        break;
    }
}

extern "C" void near y6_phase_growing_ring(void)
{
    if(boss.phase_frame > 48) {
        boss.sprite = (((stage_frame_mod4 / 2) * 2) + 146);
        if(stage_frame_mod8 == 0) {
            snd_se_play(3);
            bullet_template.angle += 2;
            bullet_template.group = BG_RING;
            bullet_template.spawn_type = BST_BULLET16;
            bullet_template.patnum = PAT_BULLET16_D_BLUE;
            bullet_template.speed.v = TO_SP(3);
            bullet_template.count = ((boss.phase_frame / 4) + 4);
            bullet_template_tune();
            bullets_add_regular();
        }
    } else {
        boss.sprite = 146;
    }
    y6_gather_self();
    if(boss.phase_frame == 144) {
        boss.phase_frame = 0;
        boss.mode = -1;
    }
}

extern "C" void near y6_phase_chasecrosses(void)
{
    if(boss.phase_frame > 48) {
        boss.sprite = (((stage_frame_mod4 / 2) * 2) + 146);
        if(stage_frame_mod8 == 0) {
            chasecrosses_add(randring2_next16(), TO_SP(2));
            chasecrosses_add(randring2_next16(), TO_SP(2));
            snd_se_play(3);
        }
    } else {
        boss.sprite = 146;
    }
    if(boss.phase_frame == 144) {
        boss.phase_frame = 0;
        boss.mode = -1;
    }
}

extern "C" void near y6_phase_alternating_rings(void)
{
    unsigned char phase_sub = (static_cast<unsigned char>(boss.phase_frame) & 0x1F);
    boss.sprite = (((stage_frame_mod4 / 2) * 2) + 146);
    if((phase_sub & 3) == 0) {
        bullet_template.origin.x.v = boss.pos.cur.x.v;
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        bullet_template.spawn_type = (BST_GATHER_PELLET - bullet_template.spawn_type);
        bullet_template.patnum = PAT_BULLET16_N_SMALL_BALL_RED;
        bullet_template.group = BG_RING;
        bullet_template.count = 8;
        bullet_template.speed.v = (phase_sub + TO_SP(2));
        bullet_template_tune();
        bullet_template.angle = (-0x7E - bullet_template.angle);
        bullets_add_regular_fixedspeed();
        bullet_template.angle = (0x80 - bullet_template.angle);
        bullets_add_regular_fixedspeed();
    }
    if(phase_sub == 0) {
        bullet_template.angle += 8;
        gather_template.ring_points = 8;
        gather_template.col = 9;
        gather_template.angle_delta = -gather_template.angle_delta;
        gather_add_only();
    }
}

extern "C" void near y6_phase_dual_aimed_spreads(void)
{
    if(boss.phase_frame < 64) {
        if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_OPEN) {
            yuuka6_anim_parasol_back_close();
        } else if(yuuka6_sprite_flag == Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_back_pull_forward();
        }
    } else if((boss.phase_frame >= 64) && (boss.phase_frame <= 192)) {
        boss.sprite = PAT_YUUKA6_PARASOL_FORWARD_OPEN;
        if(stage_frame_mod16 == 0) {
            bullet_template.spawn_type = BST_BULLET16;
            bullet_template.patnum = PAT_BULLET16_D_BLUE;
            bullet_template.speed.v = (TO_SP(2) + 8);
            bullet_template.delta.spread_angle = 0x0E;
            if((stage_frame & 0x1F) == 0) {
                bullet_template.count = 10;
                bullet_template.group = BG_SPREAD;
                bullet_template.angle = 0x40;
            } else {
                bullet_template.count = 7;
                bullet_template.group = BG_SPREAD_AIMED;
                bullet_template.angle = 0;
            }
            bullet_template.origin.y.v = (boss.pos.cur.y.v + TO_SP(32));
            bullet_template.origin.x.v = boss.pos.cur.x.v;
            bullets_add_regular();
            bullet_template.origin.x.v = yuuka6_mirror_pos.x.v;
            bullets_add_regular();
            snd_se_play(3);
        }
    } else if(boss.phase_frame >= 192) {
        if(yuuka6_sprite_flag != Y6SF_ATTACK_PARASOL_BACK_CLOSED) {
            yuuka6_anim_parasol_left_spin_back();
        } else if(yuuka6_anim_parasol_back_open()) {
            boss.phase_frame = 0;
            boss.mode = -1;
        }
    }
    y6_gather_dual();
}

extern "C" bool near y6_mirror_hittest(void)
{
    if(yuuka6_mirror_state == 2) {
        shot_hitbox_radius.x.v = TO_SP(24);
        shot_hitbox_radius.y.v = TO_SP(48);
        shot_hitbox_center.x.v = yuuka6_mirror_pos.x.v;
        shot_hitbox_center.y.v = yuuka6_mirror_pos.y.v;
        if((yuuka6_mirror_damage = shots_hittest()) != 0) {
            snd_se_play(4);
        }
        boss.hp -= yuuka6_mirror_damage;
        if(boss.hp < 0) {
            return true;
        }
    }
    return false;
}


// Target-only final-boss dispatcher. Ghidra only constructs its first three
// bytes; the complete FAR body and compiler switch tables are recovered from
// target raw decoding plus the pinned local-PROC/table boundaries.
extern func_t_near stage_vm;
extern "C" void pascal far nullfunc_far(void);
extern int midboss_frames_until;
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
#pragma codeseg MAI_TEXT main_01
extern void pascal near yuuka6_bg_render(void);
#pragma codeseg
extern unsigned char yuuka6_pattern_prev;
extern unsigned char yuuka6_aux_flag;
extern unsigned char yuuka6_aux_state;
extern unsigned char bullet_clear_time;
extern unsigned char bullet_zap;
extern bool palette_changed;
extern unsigned char player_invincibility_time;
extern unsigned int __cdecl PaletteTone;
extern SPPoint homing_target;
extern "C" void near thicklasers_update(void);
extern "C" void pascal near yuuka6_phase_next(
    explosion_type_t explosion_type, int next_end_hp
)
{
    if(bullet_clear_time < 20) {
        bullet_clear_time = 20;
    }
    boss_explode_small(explosion_type);
    boss.phase++;
    boss.phase_frame = 0;
    boss.phase_state.patterns_seen = 0;
    boss.mode = 0;
    boss.hp = boss.phase_end_hp;
    boss.phase_end_hp = next_end_hp;
    yuuka6_anim_frame = 0;
    boss.sprite = PAT_YUUKA6_PARASOL_BACK_OPEN;
    yuuka6_anim_frame = 0;
    yuuka6_sprite_flag = Y6SF_ATTACK_PARASOL_BACK_OPEN;
}
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);

void far yuuka6_update(void)
{
    switch(boss.phase) {
    case 0:
        if(boss.phase_frame == 0) {
            stage_vm = nullfunc_far;
            midboss_frames_until = 0;
            yuuka6_aux_flag = 0;
            yuuka6_aux_state = 0;
        }
        boss_hittest_shots_invincible();
        if(boss.phase_frame <= 128) {
            break;
        }
        boss.phase++;
        boss.phase_frame = 0;
        snd_se_play(13);
        yuuka6_pattern_prev = 0;
        bg_render_bombing_func = yuuka6_bg_render;
        tiles_bb_col = V_WHITE;
        break;

    case 1:
        boss_hittest_shots_invincible();
        if(boss.phase_frame < 64) {
            break;
        }
        boss.phase++;
        boss.pos.velocity.x.v = 0;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        boss.hp = 13300;
        boss.phase_end_hp = 10600;
        boss.phase_frame = 0;
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_ATTACK_PARASOL_BACK_OPEN;
        yuuka6_phase2_fly_path = randring2_next16_and(1);
        break;

    case 2:
        switch(boss.mode) {
        case 0:
            y6_attack_ring_turn();
            break;
        case 1:
            y6_attack_spin_rings();
            break;
        case 2:
            y6_attack_gravity();
            break;
        case 0xFF:
            if(yuuka6_phase2_fly()) {
                boss.mode = (boss.phase_state.patterns_seen % 3);
                if(boss.phase_state.patterns_seen >= 10) {
                    goto phase2_done;
                }
            }
            break;
        }
        if(boss.sprite == 0) {
            goto phase_frame_only;
        }
        if(!boss_hittest_shots()) {
            break;
        }
        boss_score_bonus(20);
        boss_items_drop();
    phase2_done:
        yuuka6_phase_next(ET_CIRCLE, 7600);
        break;

    case 3:
        boss.phase_frame++;
        if(yuuka6_move_towards(TO_SP(PLAYFIELD_W / 2), TO_SP(80))) {
            boss.phase++;
            boss.phase_frame = 0;
            boss.phase_state.patterns_seen = 0;
        }
        break;

    case 4:
        switch(boss.mode) {
        case 0:
            y6_attack_safetycircle();
            break;
        case 0xFF:
            if(yuuka6_move_towards(
                (randring2_next16_mod(TO_SP(288)) + TO_SP(48)),
                TO_SP(80)
            )) {
                boss.mode = 0;
                if(boss.phase_state.patterns_seen >= 10) {
                    goto phase4_done;
                }
            }
            break;
        }
        if((boss.sprite == 0) || (boss.mode == 0xFF)) {
            goto phase_frame_only;
        }
        if(!boss_hittest_shots()) {
            break;
        }
        boss_score_bonus(20);
        boss_items_drop();
    phase4_done:
        yuuka6_phase_next(ET_CIRCLE, 5400);
        yuuka6_aux_flag = 1;
        break;

    case 5:
    case 9:
        boss.phase_frame++;
        if(yuuka6_sprite_flag != 0) {
            yuuka6_anim_vanish();
            break;
        }
        boss.phase++;
        boss.phase_frame = 0;
        break;

    case 6:
    case 10:
        y6_attack_bullets();
        boss.phase_frame++;
        yuuka6_horizontal_wave();
        if((boss.phase_frame < 320) || (boss.pos.cur.y.v != TO_SP(80))) {
            break;
        }
        boss_explode_small(ET_SW_NE);
        if(bullet_clear_time < 20) {
            bullet_clear_time = 20;
        }
        boss.phase++;
        boss.phase_frame = 0;
        yuuka6_anim_frame = 0;
        break;

    case 7:
    case 11:
        boss_hittest_shots();
        if(!yuuka6_move_to_center()) {
            break;
        }
        boss.phase++;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0xFF;
        boss.phase_frame = 0;
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_ATTACK_PARASOL_BACK_CLOSED;
        yuuka6_aux_state = 1;
        yuuka6_pattern_prev = 0xFF;
        break;

    case 8:
    case 12:
        switch(boss.mode) {
        case 0:
            y6_phase_dual_lasers();
            break;
        case 1:
            y6_phase_dual_spreads();
            break;
        case 2:
            y6_phase_dual_aimed_spreads();
            break;
        case 0xFF:
            if(yuuka6_move_towards(
                (randring2_next16_mod(TO_SP(144)) + TO_SP(48)),
                TO_SP(80)
            )) {
                do {
                    boss.mode = randring2_next16_mod(3);
                } while(yuuka6_pattern_prev == boss.mode);
                yuuka6_pattern_prev = boss.mode;
                if(boss.phase_state.patterns_seen >= 10) {
                    goto phase8_done;
                }
            }
            break;
        }
        if(boss.sprite == 0) {
            goto phase_frame_only;
        }
        if(boss.mode <= 2) {
            boss_hittest_shots();
            y6_mirror_hittest();
        } else {
            boss.phase_frame++;
        }
        if(boss.hp > boss.phase_end_hp) {
            break;
        }
        boss_score_bonus(20);
        boss_items_drop();
    phase8_done:
        if(boss.phase == 8) {
            yuuka6_phase_next(ET_CIRCLE, 3400);
        } else {
            yuuka6_phase_next(ET_CIRCLE, 1200);
        }
        if(boss.phase == 9) {
            yuuka6_aux_flag = 1;
        }
        yuuka6_aux_state = 0;
        break;

    phase_frame_only:
        boss.phase_frame++;
        break;

    case 13:
        boss_hittest_shots_invincible();
        if(!yuuka6_move_to_center()) {
            break;
        }
        boss.phase++;
        boss.phase_state.patterns_seen = 0;
        boss.mode = 0;
        boss.phase_frame = 0;
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_ATTACK_PARASOL_BACK_CLOSED;
        yuuka6_aux_state = 1;
        break;

    case 14:
        switch(boss.mode) {
        case 0:
            y6_phase_rotating_ring();
            break;
        case 1:
            y6_phase_growing_ring();
            break;
        case 2:
            y6_phase_chasecrosses();
            break;
        case 0xFF:
            boss.phase_state.patterns_seen++;
            boss.mode = (boss.phase_state.patterns_seen % 3);
            if(boss.phase_state.patterns_seen >= 18) {
                goto phase14_done;
            }
            break;
        }
        if(!boss_hittest_shots()) {
            break;
        }
        boss_score_bonus(20);
        boss_items_drop();
    phase14_done:
        yuuka6_phase_next(ET_HORIZONTAL, 0);
        boss.sprite = 146;
        break;

    case 15:
        boss_hittest_shots();
        if(boss.phase_frame < 128) {
            break;
        }
        boss.phase++;
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.angle = 0;
        break;

    case 16:
        y6_phase_alternating_rings();
        if(!boss_hittest_shots() && (boss.phase_frame < 2500)) {
            break;
        }
        boss_explode_small(ET_NW_SE);
        boss.phase++;
        if(boss.phase_frame < 2500) {
            boss.phase_state.patterns_seen = 1;
        } else {
            boss.phase_state.patterns_seen = 0;
        }
        boss.phase_frame = 0;
        boss.mode = 0;
        PaletteTone = 100;
        palette_changed = true;
        break;

    case 17:
        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_SW_NE));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(70);
            }
            boss.sprite = PAT_ENEMY_KILL;
            boss.phase_frame = 0;
            snd_se_play(12);
            palette_changed = true;
            player_invincibility_time = BOSS_DEFEAT_INVINCIBILITY_FRAMES;
        }
        break;

    default:
        boss_defeat_update();
        return;
    }

    homing_target.x.v = boss.pos.cur.x.v;
    homing_target.y.v = boss.pos.cur.y.v;
    thicklasers_update();
    yuuka6_entities_update();
    hud_hp_update_and_render(boss.hp, 13300);
}

#undef TH04_YUUKA6_MAIN034_COMBINED
