#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/phase.hpp"
#include "th04/main/homing.hpp"
#include "th04/main/midboss/midboss.hpp"
#include "th04/main/hud/hud.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/item/item.hpp"
#include "th04/main/gather.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma samecodeseg midboss_reset
#pragma option -a

extern unsigned char midboss2_pattern;
extern unsigned char midboss2_direction;
extern unsigned char midboss2_patterns_done;
extern unsigned char bullet_zap_active;
extern int playfield_shake_anim_time;
extern SPPoint homing_target;
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);

static void near midboss2_pattern_cloud_spreads(void)
{
    register int frame = midboss.phase_frame;
    if((frame % 8) == 0) {
        snd_se_play(3);
        bullet_template.angle = static_cast<unsigned char>((midboss2_direction << 5) + 0x20);
        if(((frame / 8) & 1) != 0) {
            bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
            bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
            bullet_template.group = BG_SINGLE;
            bullet_template.speed.v = (TO_SP(2) + 10);
            bullet_template_tune();
            bullets_add_regular();
            bullet_template.delta.spread_angle = 0x0F;
        } else {
            bullet_template.delta.spread_angle = 0x0A;
        }
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 6;
        bullet_template.speed.v = (TO_SP(2) + 4);
        bullet_template_tune();
        bullets_add_regular();
    }
    if(frame >= 64) {
        midboss.phase_frame = 0;
        midboss2_pattern = static_cast<unsigned char>(-1);
    }
}

static void near midboss2_pattern_ring(void)
{
    register int frame = midboss.phase_frame;
    if((frame % 8) == 0) {
        snd_se_play(3);
        bullet_template.angle = static_cast<unsigned char>((midboss2_direction << 5) + 0x20);
        bullet_template.speed.v = static_cast<unsigned char>((frame / 2) + TO_SP(2));
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template_tune();
        bullets_add_regular();
    }
    if(frame >= 32) {
        midboss.phase_frame = 0;
        midboss2_pattern = static_cast<unsigned char>(-1);
    }
}

static void near midboss2_pattern_quad(void)
{
    register int frame = midboss.phase_frame;
    if((frame % 4) == 0) {
        snd_se_play(3);
        bullet_template.speed.v = TO_SP(4);
        bullet_template.group = BG_SINGLE;
        bullet_template.angle = static_cast<unsigned char>((midboss2_direction << 5) + 0x08);
        bullet_template_tune();
        bullets_add_regular();
        bullet_template.angle = static_cast<unsigned char>((midboss2_direction << 5) + 0x10);
        bullets_add_regular();
        bullet_template.angle = static_cast<unsigned char>((midboss2_direction << 5) + 0x38);
        bullets_add_regular();
        bullet_template.angle = static_cast<unsigned char>((midboss2_direction << 5) + 0x30);
        bullets_add_regular();
    }
    if(frame >= 32) {
        midboss.phase_frame = 0;
        midboss2_pattern = static_cast<unsigned char>(-1);
    }
}

static void near midboss2_pattern_aimed_special(void)
{
    register int frame = (midboss.phase_frame - 1);
    if(frame == 0) {
        midboss.angle = iatan2(
            (player_pos.cur.y.v - midboss.pos.cur.y.v),
            (player_pos.cur.x.v - midboss.pos.cur.x.v)
        );
    }
    if((frame % 8) == 0) {
        snd_se_play(3);
        bullet_template.speed.v = (TO_SP(2) + 8);
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 5;
        bullet_template.delta.spread_angle = 0x10;
        bullet_template.angle = midboss.angle;
        bullet_template_tune();
        bullets_add_regular();
        bullet_template.speed.v = 10;
        bullet_template.angle = iatan2(
            (player_pos.cur.y.v - midboss.pos.cur.y.v),
            (player_pos.cur.x.v - midboss.pos.cur.x.v)
        );
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        bullet_template.group = BG_SINGLE;
        bullet_template.special_motion = BSM_NONE;
    }
    if((frame % 32) >= 24) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.speed.v += 10;
        bullets_add_special();
    }
    if(frame >= 64) {
        midboss.phase_frame = 0;
        midboss2_pattern = static_cast<unsigned char>(-1);
    }
}

void pascal far midboss2_update(void)
{
    register int damage;
    homing_target.x.v = midboss.pos.cur.x.v;
    homing_target.y.v = midboss.pos.cur.y.v;

    if(midboss.phase == 0) {
        midboss.pos.update_seg3();
        midboss.phase_frame++;
        damage = midboss_hittest_shots_damage(TO_SP(24), TO_SP(24), 10);
        if(midboss.phase_frame >= 96) {
            midboss.phase++;
            midboss.phase_frame = 0;
            midboss.pos.velocity.x.v = 0;
            midboss.pos.velocity.y.v = 0;
            midboss2_pattern = 0;
            midboss2_direction = 1;
            midboss2_patterns_done = 0;
        }
        goto update_hp;
    }

    if(midboss.phase == 1) {
        midboss.pos.update_seg3();
        midboss.phase_frame++;
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.origin.x.v = midboss.pos.cur.x.v;
        bullet_template.origin.y.v = (midboss.pos.cur.y.v - TO_SP(16));
        switch(midboss2_pattern) {
        case 0: midboss2_pattern_cloud_spreads(); break;
        case 1: midboss2_pattern_ring(); break;
        case 2: midboss2_pattern_quad(); break;
        case 3: midboss2_pattern_aimed_special(); break;
        case 0xFF:
            gather_template.center.x.v = midboss.pos.cur.x.v;
            gather_template.center.y.v = midboss.pos.cur.y.v;
            gather_add_only_3stack(
                (midboss.phase_frame - 48), V_WHITE, static_cast<vc2>(7)
            );
            switch(midboss.phase_frame) {
            case 48:
                midboss.pos.velocity.x.v = 0;
                break;
            case 52:
                midboss.phase_frame = 0;
                if(midboss2_direction == 1) {
                    midboss.sprite = 0;
                }
                midboss2_patterns_done++;
                midboss2_pattern = (midboss2_patterns_done & 3);
                if(midboss2_patterns_done > 16) {
                    goto defeated;
                }
                break;
            case 1:
                gather_template.ring_points = 8;
                gather_template.radius.v = TO_SP(96);
                if(midboss2_direction == 1) {
                    if((randring2_next16() & 1) != 0) {
                        midboss.sprite = 1;
                        midboss2_direction = 0;
                        midboss.pos.velocity.x.v = -TO_SP(3);
                    } else {
                        midboss.sprite = 2;
                        midboss2_direction = 2;
                        midboss.pos.velocity.x.v = TO_SP(3);
                    }
                } else if(midboss2_direction == 0) {
                    midboss2_direction = 1;
                    midboss.pos.velocity.x.v = TO_SP(3);
                    midboss.sprite = 2;
                } else if(midboss2_direction == 2) {
                    midboss2_direction = 1;
                    midboss.pos.velocity.x.v = -TO_SP(3);
                    midboss.sprite = 1;
                }
                break;
            }
            break;
        }

        damage = midboss_hittest_shots_damage(TO_SP(24), TO_SP(24), 10);
        if(damage == 0) {
            goto update_hp;
        }
        midboss.hp -= damage;
        if(midboss.hp > 0) {
            midboss.damage_this_frame = 1;
            snd_se_play(4);
            goto update_hp;
        }
        midboss.damage_this_frame = 1;
        bullet_zap_active = 1;
        midboss_score_bonus(18 - midboss2_patterns_done);
        items_add(midboss.pos.cur.x.v, midboss.pos.cur.y.v, IT_BOMB);
        playfield_shake_anim_time = 12;

defeated:
        // Stage 2 uses a private explosion phase value, distinct from PHASE_EXPLODE_BIG.
        midboss.phase = 2;
        midboss.sprite = 0;
        midboss.phase_frame = 0;
        midboss.pos.velocity.x.v = 0;
        midboss.pos.velocity.y.v = -TO_SP(1);
        sparks_add_circle(midboss.pos.cur.x, midboss.pos.cur.y, TO_SP(8), 48);
        snd_se_play(12);
        goto update_hp;
    }

    if(midboss.phase == 2) {
        midboss.pos.update_seg3();
        midboss.phase_frame++;
        if(midboss.pos.cur.y.v <= 0) {
            midboss.phase++;
            midboss.hp = 0;
        }
        if(stage_frame_mod16 == 0) {
            sparks_add_circle(midboss.pos.cur.x, midboss.pos.cur.y, TO_SP(8), 16);
        }
        goto update_hp;
    }

    midboss_reset();

update_hp:
    hud_hp_update_and_render(midboss.hp, 750);
}

#pragma codeseg
