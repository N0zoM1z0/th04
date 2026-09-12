#pragma option -zCB4M_UPDATE_TEXT -zPmain_03
#pragma codeseg M4_RENDER_TEXT main_01
void pascal near midboss4_render(void);
#pragma codeseg B4M_UPDATE_TEXT main_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/phase.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/homing.hpp"
#include "th04/main/midboss/midboss.hpp"
#include "th04/main/hud/hud.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/item/item.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
// Keep the target same-group far-call optimization to MIDBOSS_TEXT.
#pragma samecodeseg midboss_reset
#pragma option -a

extern unsigned char midboss4_pattern;
extern unsigned char midboss4_patterns_done;
extern unsigned char midboss4_unknown_state;
extern unsigned char midboss4_aim_toggle;
extern unsigned char bullet_zap_active;
extern int playfield_shake_anim_time;
extern SPPoint homing_target;
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);

static void near midboss4_pattern_random_spreads(void)
{
    if(midboss.phase_frame <= 24) {
        midboss.sprite = (midboss.phase_frame / 8);
        if(midboss.phase_frame == 24) {
            snd_se_play(6);
        }
        return;
    }
    if(midboss.phase_frame < 128) {
        if((midboss.phase_frame & 3) != 0) {
            return;
        }
        bullet_template.group = BG_SPREAD_AIMED;
        bullet_template.count = 2;
        bullet_template.delta.spread_angle = 6;
        bullet_template.speed.v = (randring2_next16_mod(0x18) + TO_SP(2));
        bullet_template.angle = (randring2_next16_mod(0x60) - 0x30);
        bullet_template_tune();
        bullets_add_regular();
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_SMALL_BALL_YELLOW;
        bullet_template.speed.v = (randring2_next16_mod(0x18) + TO_SP(2));
        bullet_template.angle = (randring2_next16_mod(0x60) - 0x30);
        bullets_add_regular();
        snd_se_play(3);
        return;
    }
    if(midboss.phase_frame < 152) {
        midboss.sprite = ((159 - midboss.phase_frame) / 8);
        return;
    }
    midboss.phase_frame = 0;
    midboss4_pattern = static_cast<unsigned char>(-1);
}

static void near midboss4_pattern_stack(void)
{
    unsigned char angle_prev;
    if(midboss.phase_frame <= 24) {
        midboss.sprite = (midboss.phase_frame / 8);
        if(midboss.phase_frame == 24) {
            snd_se_play(6);
            if(midboss.pos.cur.x.v < TO_SP(192)) {
                bullet_template.angle = 0x36;
            } else {
                bullet_template.angle = 0x56;
            }
            midboss4_aim_toggle++;
        }
        return;
    }
    if(midboss.phase_frame <= 136) {
        if(((midboss.phase_frame - 25) & 0x0F) != 0) {
            return;
        }
        bullet_template.group = BG_STACK;
        if((midboss4_aim_toggle & 1) != 0) {
            bullet_template.angle = iatan2(
                (player_pos.cur.y.v - midboss.pos.cur.y.v),
                (player_pos.cur.x.v - midboss.pos.cur.x.v)
            );
        } else {
            bullet_template.angle -= 8;
        }
        angle_prev = bullet_template.angle;
        snd_se_play(3);
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_SMALL_BALL_YELLOW;
        bullet_template_tune();
        bullet_template.speed.v = TO_SP(1);
        bullet_template.count = 12;
        bullet_template.delta.stack_speed.v = 7;
        bullets_add_regular_fixedspeed();
        if(midboss.pos.cur.x.v > TO_SP(192)) {
            _AL = static_cast<unsigned char>(-0x60);
        } else {
            _AL = 0x60;
        }
        _AL -= bullet_template.angle;
        bullet_template.angle = _AL;
        bullets_add_regular_fixedspeed();
        bullet_template.angle = angle_prev;
        return;
    }
    if(midboss.phase_frame < 160) {
        midboss.sprite = ((165 - midboss.phase_frame) / 8);
        return;
    }
    midboss.phase_frame = 0;
    midboss4_pattern = static_cast<unsigned char>(-1);
}

static void near midboss4_pattern_aimed(void)
{
    register int frame_mod32;
    if(midboss.phase_frame <= 24) {
        midboss.sprite = (midboss.phase_frame / 8);
        if(midboss.phase_frame == 24) {
            snd_se_play(6);
        }
        return;
    }
    if(midboss.phase_frame <= 120) {
        if((midboss.phase_frame & 7) == 0) {
            bullet_template.group = BG_SPREAD_AIMED;
            bullet_template.count = ((randring2_next16_and(3) * 2) + 1);
            bullet_template.delta.spread_angle = (randring2_next16_and(7) + 10);
            bullet_template.speed.v = (TO_SP(3) + 2);
            bullet_template.angle = 0;
            bullet_template_tune();
            bullets_add_regular_fixedspeed();
        }
        frame_mod32 = ((midboss.phase_frame - 25) & 0x1F);
        if(frame_mod32 == 0) {
            midboss.angle = iatan2(
                (player_pos.cur.y.v - midboss.pos.cur.y.v),
                (player_pos.cur.x.v - midboss.pos.cur.x.v)
            );
        }
        if((frame_mod32 & 3) != 0) {
            return;
        }
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.group = BG_SINGLE;
        bullet_template.patnum = PAT_BULLET16_D_YELLOW;
        bullet_template.speed.v = static_cast<unsigned char>((frame_mod32 * 3) + TO_SP(2) + 8);
        bullet_template.angle = midboss.angle;
        bullet_template_tune();
        bullets_add_regular_fixedspeed();
        snd_se_play(3);
        return;
    }
    if(midboss.phase_frame < 144) {
        midboss.sprite = ((151 - midboss.phase_frame) / 8);
        return;
    }
    midboss.phase_frame = 0;
    midboss4_pattern = static_cast<unsigned char>(-1);
}

static void near midboss4_pattern_spiral(void)
{
    if(midboss.phase_frame <= 24) {
        midboss.sprite = (midboss.phase_frame / 8);
        if(midboss.phase_frame == 24) {
            snd_se_play(6);
            bullet_template.angle = static_cast<unsigned char>(-0x20);
        }
        return;
    }
    if(midboss.phase_frame < 128) {
        if((midboss.phase_frame & 2) != 0) {
            return;
        }
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 3;
        bullet_template.delta.spread_angle = 6;
        bullet_template.speed.v = (TO_SP(3) + 12);
        if(midboss.pos.cur.x.v < TO_SP(192)) {
            bullet_template.angle = (0x80 - bullet_template.angle);
        }
        bullet_template_tune();
        bullets_add_regular();
        if(midboss.pos.cur.x.v < TO_SP(192)) {
            bullet_template.angle = (0x80 - bullet_template.angle);
        }
        snd_se_play(3);
        bullet_template.angle += 6;
        return;
    }
    if(midboss.phase_frame < 152) {
        midboss.sprite = ((159 - midboss.phase_frame) / 8);
        return;
    }
    midboss.phase_frame = 0;
    midboss4_pattern = static_cast<unsigned char>(-1);
}

void pascal far midboss4_update(void)
{
    register int damage;
    homing_target.x.v = midboss.pos.cur.x.v;
    homing_target.y.v = midboss.pos.cur.y.v;

    if(midboss.phase == 0) {
        midboss.pos.update_seg3();
        midboss.phase_frame++;
        damage = midboss_hittest_shots_damage(TO_SP(24), TO_SP(24), 10);
        if(midboss.phase_frame >= 48) {
            midboss.phase++;
            midboss.phase_frame = 0;
            midboss.pos.velocity.x.v = 0;
            midboss.pos.velocity.y.v = 0;
            midboss4_unknown_state = 0;
            midboss4_pattern = 0;
            midboss4_patterns_done = 0;
        }
        goto update_hp;
    }

    if(midboss.phase == 1) {
        midboss.pos.update_seg3();
        midboss.phase_frame++;
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.origin.x.v = midboss.pos.cur.x.v;
        bullet_template.origin.y.v = (midboss.pos.cur.y.v - TO_SP(16));
        switch(midboss4_pattern) {
        case 0: midboss4_pattern_random_spreads(); break;
        case 1: midboss4_pattern_aimed(); break;
        case 2: midboss4_pattern_stack(); break;
        case 3: midboss4_pattern_spiral(); break;
        case 0xFF:
            if(midboss.phase_frame == 1) {
                if(midboss.pos.cur.x.v >= TO_SP(180)) {
                    _AX = -TO_SP(4);
                } else {
                    _AX = TO_SP(4);
                }
                midboss.pos.velocity.x.v = _AX;
                break;
            }
            if(midboss4_patterns_done < 8) {
                if((midboss.pos.cur.x.v <= TO_SP(48)) ||
                   (midboss.pos.cur.x.v >= TO_SP(336))) {
                    midboss.pos.velocity.x.v = 0;
                    midboss.phase_frame = 0;
                    midboss4_patterns_done++;
                    midboss4_pattern = (midboss4_patterns_done & 3);
                }
            } else if((midboss.pos.cur.x.v <= -TO_SP(32)) ||
                      (midboss.pos.cur.x.v >= TO_SP(416))) {
                midboss.phase = 3;
            }
            break;
        }
        if((midboss.pos.cur.y.v >= TO_SP(368)) ||
           (midboss.pos.cur.x.v <= 0) ||
           (midboss.pos.cur.x.v >= TO_SP(384))) {
            midboss.phase = PHASE_NONE;
        }
        damage = midboss_hittest_shots_damage(TO_SP(24), TO_SP(24), 4);
        if(damage == 0) {
            goto update_hp;
        }
        midboss.hp -= damage;
        if(midboss.hp > 0) {
            midboss.damage_this_frame = 1;
            goto update_hp;
        }
        midboss.damage_this_frame = 1;
        damage = scroll_subpixel_y_to_vram_always(midboss.pos.cur.y.v - TO_SP(16));
        bullet_zap_active = 1;
        midboss_score_bonus(30 - midboss4_patterns_done);
        playfield_shake_anim_time = 12;
        midboss.phase = PHASE_EXPLODE_BIG;
        midboss.sprite = 4;
        midboss.phase_frame = 0;
        midboss.pos.velocity.x.v = 0;
        sparks_add_circle(midboss.pos.cur.x, midboss.pos.cur.y, TO_SP(6), 48);
        snd_se_play(12);
        if(midboss.frames_until == 2800) {
            items_add(midboss.pos.cur.x.v, midboss.pos.cur.y.v, IT_BOMB);
        } else {
            items_add(midboss.pos.cur.x.v, midboss.pos.cur.y.v, IT_1UP);
        }
        goto update_hp;
    }

    if(midboss.phase == PHASE_EXPLODE_BIG) {
        midboss.pos.velocity.x.v = 0;
        midboss.pos.velocity.y.v = 0;
        midboss.pos.update_seg3();
        midboss.phase_frame++;
        if((midboss.phase_frame % 16) == 0) {
            midboss.sprite++;
            if(midboss.sprite >= 12) {
                midboss.phase++;
                midboss.hp = 0;
            }
        }
        goto update_hp;
    }

    midboss_reset();
    if(midboss.frames_until == 2800) {
        midboss.frames_until = 5600;
        midboss_update_func = midboss4_update;
        midboss_render_func = midboss4_render;
        midboss.pos.cur.x.v = TO_SP(240);
        midboss.pos.cur.y.v = -TO_SP(32);
        midboss.pos.prev.x.v = TO_SP(240);
        midboss.pos.prev.y.v = -TO_SP(32);
        midboss.pos.velocity.x.v = -TO_SP(4);
        midboss.pos.velocity.y.v = TO_SP(2);
        midboss.hp = 1200;
        midboss.sprite = 0;
        midboss.phase_frame = 0;
        return;
    }

update_hp:
    hud_hp_update_and_render(midboss.hp, 1200);
}

#pragma codeseg
