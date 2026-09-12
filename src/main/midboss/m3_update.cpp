#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/phase.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/homing.hpp"
#include "th04/main/midboss/midboss.hpp"
#include "th04/main/hud/hud.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/item/item.hpp"
#include "th04/main/gather.hpp"
#include "th04/math/randring.hpp"
#include "th04/math/vector.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma option -a

#define MIDBOSS3_PATTERNS_MAX 12
extern const unsigned char MIDBOSS3_FLY_ANGLES[MIDBOSS3_PATTERNS_MAX];
extern unsigned char midboss3_pattern;
extern unsigned char midboss3_mirror;
extern unsigned char midboss3_patterns_done;
extern unsigned char bullet_zap_active;
extern SPPoint homing_target;
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);

static void near midboss3_pattern_aimed_spreads(void)
{
    if(midboss.phase_frame == 2) {
        midboss.angle = iatan2(
            player_pos.cur.y.v - midboss.pos.cur.y.v,
            player_pos.cur.x.v - midboss.pos.cur.x.v
        );
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template.speed.v = TO_SP(2) + 8;
        bullet_template.angle = 0;
        bullet_template_tune();
        bullets_add_regular();
    }
    if((midboss.phase_frame % 4) == 0) {
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 2;
        bullet_template.delta.spread_angle = 0x0C;
        bullet_template.speed.v = TO_SP(3) + 4;
        bullet_template.angle = midboss.angle;
        bullet_template_tune();
        bullets_add_regular();
        snd_se_play(3);
    }
    if(midboss.phase_frame >= 32) {
        midboss3_pattern = static_cast<unsigned char>(-1);
        midboss.phase_frame = 0;
    }
}

static void near midboss3_pattern_cloud_ring(void)
{
    if(midboss.phase_frame >= 32) {
        midboss3_pattern = static_cast<unsigned char>(-1);
        midboss.phase_frame = 0;
        bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template.speed.v = TO_SP(2) + 8;
        bullet_template.angle = randring2_next16();
        bullet_template_tune();
        bullets_add_regular_fixedspeed();
        snd_se_play(9);
    }
}

static void near midboss3_pattern_spread_rotate(void)
{
    if(midboss.phase_frame == 1) {
        midboss.angle = 128;
    }
    if((midboss.phase_frame % 2) == 0) {
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 2;
        bullet_template.delta.spread_angle = 0x12;
        bullet_template.speed.v = TO_SP(2) + 14;
        bullet_template.angle = midboss.angle;
        midboss.angle -= 8;
        bullet_template_tune();
        bullets_add_regular();
        snd_se_play(3);
    }
    if(midboss.phase_frame >= 32) {
        midboss3_pattern = static_cast<unsigned char>(-1);
        midboss.phase_frame = 0;
    }
}

static void near midboss3_pattern_random_ring(void)
{
    if(midboss.phase_frame == 1) {
        midboss.angle = randring2_next16();
    }
    if((midboss.phase_frame % 6) == 0) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        bullet_template.group = BG_RING;
        bullet_template.speed.v = TO_SP(2);
        bullet_template.angle = midboss.angle;
        bullet_template.count = 24;
        bullet_template_tune();
        bullets_add_regular_fixedspeed();
        snd_se_play(9);
        midboss.angle += 6;
    }
    if(midboss.phase_frame >= 32) {
        midboss3_pattern = static_cast<unsigned char>(-1);
        midboss.phase_frame = 0;
    }
}

void pascal far midboss3_update(void)
{
    register int damage;
    unsigned char angle;

    homing_target.x.v = midboss.pos.cur.x.v;
    homing_target.y.v = midboss.pos.cur.y.v;

    if(midboss.phase == 0) {
        midboss.pos.update_seg3();
        midboss.phase_frame++;
        damage = midboss_hittest_shots_damage(TO_SP(24), TO_SP(24), 10);
        if(midboss.phase_frame >= 20) {
            midboss.phase++;
            midboss.phase_frame = 0;
            midboss.pos.velocity.x.v = 0;
            midboss.pos.velocity.y.v = 0;
            midboss3_pattern = randring2_next16_and(3);
            midboss3_mirror = randring2_next16_and(1);
            midboss3_patterns_done = 0;
        }
        goto update_hp;
    }

    if(midboss.phase == 1) {
        midboss.pos.update_seg3();
        midboss.phase_frame++;
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.origin.x.v = midboss.pos.cur.x.v;
        bullet_template.origin.y.v = midboss.pos.cur.y.v - TO_SP(16);

        switch(midboss3_pattern) {
        case 0: midboss3_pattern_aimed_spreads(); break;
        case 1: midboss3_pattern_cloud_ring(); break;
        case 2: midboss3_pattern_spread_rotate(); break;
        case 3: midboss3_pattern_random_ring(); break;
        case 0xFF:
            if(midboss3_patterns_done <= (MIDBOSS3_PATTERNS_MAX - 1)) {
                gather_template.center.x.v = midboss.pos.cur.x.v;
                gather_template.center.y.v = midboss.pos.cur.y.v;
                gather_add_only_3stack(midboss.phase_frame - 64, V_WHITE, static_cast<vc2>(9));
                switch(midboss.phase_frame) {
                case 64:
                    midboss.pos.velocity.x.v = 0;
                    midboss.pos.velocity.y.v = 0;
                    break;
                case 68:
                    midboss.phase_frame = 0;
                    midboss3_pattern = (midboss3_patterns_done & 3);
                    midboss.sprite = 0;
                    break;
                }
            }
            if(midboss.phase_frame == 1) {
                angle = MIDBOSS3_FLY_ANGLES[midboss3_patterns_done];
                if(midboss3_mirror != 0) {
                    angle = static_cast<unsigned char>(0x80 - angle);
                }
                vector2(midboss.pos.velocity.x.v, midboss.pos.velocity.y.v, angle, TO_SP(2));
                midboss3_patterns_done++;
                midboss.sprite = 1;
                gather_template.ring_points = 8;
            }
            break;
        }

        if((midboss.pos.cur.y.v >= TO_SP(368)) ||
           (midboss.pos.cur.x.v <= 0) ||
           (midboss.pos.cur.x.v >= TO_SP(384))) {
            midboss.phase = 3;
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
        midboss_score_bonus(20 - midboss3_patterns_done);
        midboss.phase = PHASE_EXPLODE_BIG;
        midboss.sprite = 4;
        midboss.phase_frame = 0;
        midboss.pos.velocity.x.v = 0;
        sparks_add_circle(midboss.pos.cur.x, midboss.pos.cur.y, TO_SP(6), 48);
        snd_se_play(12);
        items_add(midboss.pos.cur.x.v, midboss.pos.cur.y.v, IT_1UP);
        goto update_hp;
    }

    midboss_defeat_update();

update_hp:
    hud_hp_update_and_render(midboss.hp, 850);
}

#pragma codeseg
