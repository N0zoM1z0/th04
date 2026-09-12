#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/phase.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/homing.hpp"
#include "th04/main/midboss/midboss.hpp"
#include "th04/main/hud/hud.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/tile/tile.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/spark.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma option -a

extern unsigned char midboss1_angle;
extern vram_y_t midboss1_vram_y;
extern unsigned char bullet_zap_active;
extern SPPoint homing_target;
extern SPPoint shot_hitbox_center;
extern SPPoint shot_hitbox_radius;
extern int shots_hittest(void);
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);

static void near midboss1_pattern_special_pair(void)
{
    register int frame;

    if(midboss.pos.cur.y.v >= TO_SP(256)) {
        return;
    }
    frame = midboss.phase_frame;
    if(frame == 1) {
        midboss1_angle = 1;
    }
    if((frame % 8) != 0) {
        return;
    }
    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_D_BLUE;
    bullet_template.angle = midboss1_angle;
    bullet_template.speed.v = TO_SP(2);
    bullet_template.group = BG_SINGLE;
    bullet_template.special_motion = BSM_NONE;
    bullet_template_tune();
    bullets_add_special();
    bullet_template.angle = static_cast<unsigned char>(0x80 - midboss1_angle);
    bullets_add_special();
    midboss1_angle += 0x0C;
}

void pascal far midboss1_update(void)
{
    register int damage;

    if(midboss.phase == 0) {
        midboss.pos.velocity.y.v = -TO_SP(1);
        midboss.pos.update_seg3();
        tile_ring_set_vo(midboss.pos.cur.x.v - TO_SP(16), midboss.pos.cur.y.v - TO_SP(16), tile_image_vo(40));
        tile_ring_set_vo(midboss.pos.cur.x.v, midboss.pos.cur.y.v - TO_SP(16), tile_image_vo(41));
        tile_ring_set_vo(midboss.pos.cur.x.v - TO_SP(16), midboss.pos.cur.y.v, tile_image_vo(56));
        tile_ring_set_vo(midboss.pos.cur.x.v, midboss.pos.cur.y.v, tile_image_vo(57));
        midboss.phase_frame++;
        if(midboss.phase_frame < 288) {
            goto update_hp;
        }
        midboss.phase = 1;
        midboss.phase_frame = 0;
        midboss.pos.velocity.y.v = 2;
        tile_ring_set_vo(midboss.pos.cur.x.v - TO_SP(16), midboss.pos.cur.y.v - TO_SP(16), tile_image_vo(42));
        tile_ring_set_vo(midboss.pos.cur.x.v, midboss.pos.cur.y.v - TO_SP(16), tile_image_vo(43));
        tile_ring_set_vo(midboss.pos.cur.x.v - TO_SP(16), midboss.pos.cur.y.v, tile_image_vo(58));
        tile_ring_set_vo(midboss.pos.cur.x.v, midboss.pos.cur.y.v, tile_image_vo(59));
        midboss.sprite = 136;
        midboss.pos.cur.y.v -= TO_SP(4);
        midboss.pos.cur.y.v += scroll_subpixel_line.v;
        midboss1_vram_y = scroll_subpixel_y_to_vram_seg3(midboss.pos.cur.y.v);
        sparks_add_circle(midboss.pos.cur.x, midboss.pos.cur.y, TO_SP(3), 32);
        snd_se_play(9);
        goto update_hp;
    }

    if(midboss.phase == 1) {
        midboss.pos.update_seg3();
        homing_target.x.v = midboss.pos.cur.x.v;
        homing_target.y.v = midboss.pos.cur.y.v;
        midboss.phase_frame++;
        if(midboss.sprite < 139) {
            if((midboss.phase_frame % 8) == 0) {
                midboss.sprite++;
            }
        } else if(midboss.phase_frame >= 96) {
            midboss.phase = 2;
            midboss.phase_frame = 0;
            midboss.sprite = 140;
            midboss.pos.cur.y.v -= TO_SP(16);
            midboss1_vram_y = scroll_subpixel_y_to_vram_seg3(midboss.pos.cur.y.v - TO_SP(16));
            sparks_add_circle(midboss.pos.cur.x, midboss.pos.cur.y, TO_SP(3), 32);
            snd_se_play(9);
        }
        shot_hitbox_radius.x.v = TO_SP(16);
        shot_hitbox_radius.y.v = TO_SP(12);
        shot_hitbox_center.x.v = midboss.pos.cur.x.v;
        shot_hitbox_center.y.v = midboss.pos.cur.y.v;
        if(shots_hittest() != 0) {
            snd_se_play(10);
        }
        goto update_hp;
    }

    if(midboss.phase == 2) {
        midboss.pos.update_seg3();
        homing_target.x.v = midboss.pos.cur.x.v;
        homing_target.y.v = midboss.pos.cur.y.v;
        midboss.phase_frame++;
        if(midboss.sprite < 146) {
            if((midboss.phase_frame % 8) == 0) {
                midboss.sprite += 2;
            }
        } else {
            midboss.phase = 3;
            midboss.phase_frame = 0;
        }
        shot_hitbox_radius.x.v = TO_SP(24);
        shot_hitbox_radius.y.v = TO_SP(16);
        shot_hitbox_center.x.v = midboss.pos.cur.x.v;
        shot_hitbox_center.y.v = midboss.pos.cur.y.v;
        if(shots_hittest() != 0) {
            snd_se_play(10);
        }
        goto update_hp;
    }

    if(midboss.phase == 3) {
        midboss.pos.update_seg3();
        if(scroll_speed.v > 2) {
            goto defeated;
        }
        homing_target.x.v = midboss.pos.cur.x.v;
        homing_target.y.v = midboss.pos.cur.y.v;
        midboss.phase_frame++;
        shot_hitbox_radius.x.v = TO_SP(24);
        shot_hitbox_radius.y.v = TO_SP(16);
        shot_hitbox_center.x.v = midboss.pos.cur.x.v;
        shot_hitbox_center.y.v = midboss.pos.cur.y.v;
        damage = shots_hittest();
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.origin.x.v = midboss.pos.cur.x.v;
        bullet_template.origin.y.v = midboss.pos.cur.y.v - TO_SP(1);
        midboss1_pattern_special_pair();
        if(damage == 0) {
            goto update_hp;
        }
        midboss.hp -= damage;
        if(midboss.hp > 0) {
            midboss.damage_this_frame = 1;
            snd_se_play(4);
            goto update_hp;
        }
        bullet_zap_active = 1;
        midboss_score_bonus(5);

defeated:
        midboss.phase = PHASE_EXPLODE_BIG;
        midboss.sprite = 4;
        midboss.phase_frame = 0;
        midboss.pos.velocity.y.v = 0;
        sparks_add_circle(midboss.pos.cur.x, midboss.pos.cur.y, TO_SP(8), 48);
        snd_se_play(12);
        scroll_speed.v = 4;
        goto update_hp;
    }

    midboss_defeat_update();

update_hp:
    hud_hp_update_and_render(midboss.hp, 620);
}

#pragma codeseg
