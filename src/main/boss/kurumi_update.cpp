#pragma option -zCMAIN_033_TEXT -zPmain_03
#define TH04_KURUMI_MAIN033_COMBINED 1

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th03/math/randring.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/custom.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/spark.hpp"
#include "th04/math/vector.hpp"
#include "th04/snd/snd.h"

#pragma option -a

#include "th04/kurrays.cpp"

extern "C" void near kurumi_orbit_step_forward(void)
{
    boss.pos.cur.x.v = polar(
        TO_SP(192), TO_SP(64), CosTable8[boss.angle]
    );
    boss.pos.cur.y.v = polar(
        TO_SP(91), TO_SP(20), SinTable8[boss.angle]
    );
    boss.angle++;
}

extern "C" void near kurumi_orbit_step_reverse(void)
{
    boss.pos.cur.x.v = polar(
        TO_SP(192), TO_SP(64), CosTable8[boss.angle]
    );
    boss.pos.cur.y.v = polar(
        TO_SP(91), TO_SP(20), SinTable8[boss.angle]
    );
    boss.angle--;
}

#include "th04/kphase.cpp"
#include "th04/kphase2.cpp"
#include "th04/kstack.cpp"

extern bool palette_changed;
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
extern unsigned char kurumi_unknown_state;
extern unsigned char bullet_zap;
extern unsigned char player_invincibility_time;
extern SPPoint homing_target;
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);

#pragma codeseg MAI_TEXT main_01
extern void pascal near kurumi_bg_render(void);
#pragma codeseg
bool near kurumi_spawnrays_update(void);

extern "C" void near kurumi_orbit_step_forward(void);
extern "C" void near kurumi_spawnray_phase_left(void);
extern "C" void near kurumi_spawnray_phase_right(void);
extern "C" void near kurumi_spawnray_phase_dual(void);
extern "C" void near kurumi_turning_bullets_phase(void);
extern "C" void near kurumi_spawnray_pattern_left(void);
extern "C" void near kurumi_spawnray_pattern_right(void);
extern "C" void near kurumi_spawnray_pattern_dual(void);

void pascal far kurumi_update(void)
{
    kurumi_spawnray_t near *spawnray;
    register int i;
    register int count;

    switch(boss.phase) {
    case 0:
        if(boss.phase_frame == 0) {
            boss.hp = 4800;
            boss.phase_end_hp = 4800;
            Palettes[0].c.r = 96;
            Palettes[0].c.g = 0;
            Palettes[0].c.b = 0;
            palette_changed = true;

            for(
                (spawnray = kurumi_spawnrays, i = 0);
                i < KURUMI_SPAWNRAY_COUNT;
                (i++, spawnray++)
            ) {
                spawnray->flag = B2SF_FREE;
            }

            gather_template.center.x.v = boss.pos.cur.x.v;
            gather_template.center.y.v = boss.pos.cur.y.v;
            gather_template.ring_points = 32;
            gather_template.radius.v = TO_SP(320);
            gather_template.angle_delta = -3;
            gather_template.col = V_WHITE;
        } else if(boss.phase_frame >= 288) {
            if(boss.phase_frame == 296) {
                gather_template.col = 9;
            }
            if((boss.phase_frame & 7) == 0) {
                gather_add_only();
            }
            if(boss.phase_frame >= 320) {
                boss.phase++;
                boss.phase_frame = 0;
                snd_se_play(13);
                kurumi_unknown_state = 0;
                bg_render_bombing_func = kurumi_bg_render;
                tiles_bb_col = 0;
            }
        } else if(boss.phase_frame == 128) {
            snd_se_play(8);
        }
        boss_hittest_shots_invincible();
        goto update_tail;

    case 1:
        boss_hittest_shots_invincible();
        if(boss.phase_frame >= 32) {
            boss_phase_next(ET_NONE, 3300);
            boss.mode = 3;
            boss.angle = 192;
            snd_se_play(6);
        }
        goto update_tail;

    case 2:
        switch(boss.mode) {
        case 0:
            kurumi_orbit_step_forward();
            if(boss.phase_frame >= 96) {
                boss.phase_frame = 0;
                boss.mode = (randring2_next16_and(3) + 1);
                boss.phase_state.patterns_seen++;
                if(boss.phase_state.patterns_seen > 10) {
                    goto phase_2_next;
                }

                bullet_template.spawn_type = BST_PELLET;
                bullet_template.origin.x.v = boss.pos.cur.x.v;
                bullet_template.origin.y.v = boss.pos.cur.y.v;
                bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
                bullet_template.group = BG_RING;
                bullet_template.count = 22;
                bullet_template.angle = randring2_next16();
                bullet_template_tune();
                bullet_template.speed.v = TO_SP(1);

                count = boss.phase_state.patterns_seen;
                if(count > 5) {
                    count = 5;
                }
                for(
                    i = 0;
                    i < count;
                    (i++, bullet_template.speed.v += 8, bullet_template.angle += -3)
                ) {
                    bullets_add_regular_fixedspeed();
                }
            }
            break;
        case 1:
            kurumi_spawnray_phase_left();
            break;
        case 2:
            kurumi_spawnray_phase_right();
            break;
        case 3:
        case 4:
            kurumi_spawnray_phase_dual();
            break;
        }

        if(!boss_hittest_shots()) {
            goto update_tail;
        }
        boss_score_bonus(10);
    phase_2_next:
        boss_phase_next(ET_NW_SE, 2050);
        bullet_template_special_angle.turn_by = 0x40;
        goto update_tail;

    case 3:
        kurumi_spawnrays_update();
        switch(boss.mode) {
        case 0:
            if(boss.phase_frame >= 128) {
                boss.phase_frame = 0;
                boss.mode = 1;
            }
            break;
        case 1:
            kurumi_turning_bullets_phase();
            break;
        }

        if(boss.phase_frame <= 2000) {
            if(!boss_hittest_shots()) {
                goto update_tail;
            }
            boss_score_bonus(10);
        }
        boss_phase_next(ET_SW_NE, 550);
        goto update_tail;

    case 4:
        switch(boss.mode) {
        case 0:
            kurumi_orbit_step_forward();
            if(boss.phase_frame >= 96) {
                boss.phase_frame = 0;
                boss.mode = (randring2_next16_mod(3) + 1);
                boss.phase_state.patterns_seen++;
                if(boss.phase_state.patterns_seen > 10) {
                    goto phase_4_next;
                }

                bullet_template.spawn_type = BST_PELLET;
                bullet_template.origin.x.v = boss.pos.cur.x.v;
                bullet_template.origin.y.v = boss.pos.cur.y.v;
                bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
                bullet_template.group = BG_RING;
                bullet_template.count = 22;
                bullet_template.angle = randring2_next16();
                bullet_template_tune();
                bullet_template.speed.v = TO_SP(1);

                count = boss.phase_state.patterns_seen;
                if(count > 5) {
                    count = 5;
                }
                for(
                    i = 0;
                    i < count;
                    (i++, bullet_template.speed.v += 8, bullet_template.angle += 3)
                ) {
                    bullets_add_regular_fixedspeed();
                }
            }
            break;
        case 1:
            kurumi_spawnray_pattern_left();
            break;
        case 2:
            kurumi_spawnray_pattern_right();
            break;
        case 3:
            kurumi_spawnray_pattern_dual();
            break;
        }

        if(!boss_hittest_shots()) {
            goto update_tail;
        }
        boss_score_bonus(10);
    phase_4_next:
        boss_phase_next(ET_HORIZONTAL, 0);
        goto update_tail;

    case 5:
        kurumi_spawnrays_update();
        switch(boss.mode) {
        case 0:
            if(boss.phase_frame == 144) {
                circles_add_shrinking(boss.pos.cur.x.v, boss.pos.cur.y.v);
                circles_color = V_WHITE;
            }
            if(boss.phase_frame > 64) {
                boss.phase_frame = 0;
                boss.mode = 1;
                boss.sprite = 12;
                boss.angle = 128;
            }

            if(boss.pos.cur.x.v < TO_SP(191)) {
                boss.pos.velocity.x.v = 24;
            } else if(boss.pos.cur.x.v > TO_SP(193)) {
                boss.pos.velocity.x.v = -24;
            }
            if(boss.pos.cur.y.v < TO_SP(79)) {
                boss.pos.velocity.y.v = 12;
            } else if(boss.pos.cur.y.v > TO_SP(81)) {
                boss.pos.velocity.y.v = -12;
            }
            boss.pos.update_seg3();
            break;
        case 1:
            kurumi_bullet_stacks_phase();
            break;
        }

        if(!boss_hittest_shots() && (boss.phase_frame < 700)) {
            goto update_tail;
        }
        boss.phase++;
        sparks_add_circle(
            boss.pos.cur.x,
            boss.pos.cur.y,
            TO_SP(8),
            48
        );
        boss_explode_small(ET_VERTICAL);
        if(boss.phase_frame < 600) {
            boss.phase_state.defeat_bonus = true;
        } else {
            boss.phase_state.defeat_bonus = false;
        }
        boss.phase_frame = 0;
        goto update_tail;

    case 6:
        kurumi_spawnrays_update();
        if(boss.pos.cur.x.v < TO_SP(191)) {
            boss.pos.velocity.x.v = 24;
        } else if(boss.pos.cur.x.v > TO_SP(193)) {
            boss.pos.velocity.x.v = -24;
        }
        if(boss.pos.cur.y.v < TO_SP(79)) {
            boss.pos.velocity.y.v = 12;
        } else if(boss.pos.cur.y.v > TO_SP(81)) {
            boss.pos.velocity.y.v = -12;
        }
        boss.pos.update_seg3();

        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_CIRCLE));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(20);
            }
            boss.sprite = 4;
            boss.phase_frame = 0;
            snd_se_play(12);
            Palettes[0].c.r = 0;
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
    hud_hp_update_and_render(boss.hp, 4800);
}
