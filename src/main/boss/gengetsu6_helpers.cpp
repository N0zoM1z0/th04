#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern unsigned char gengetsu_wave_amp;
extern unsigned char boss_bomb_invincibility_frames;

extern "C" void near gengetsu_dual_clusters(void)
{
    if(stage_frame_mod4 == 0) {
        boss.sprite = 134;
    bullet_template.group = BG_SPREAD;
    bullet_template.delta.spread_angle = 9;
    bullet_template.count = 8;
    bullet_template.speed.v = (TO_SP(3) + 8);
    bullet_template.angle = static_cast<unsigned char>(stage_frame * 2);
    if((stage_frame & 511) >= 256) {
        bullet_template.angle = -bullet_template.angle;
    }
    bullets_add_regular();
    bullet_template.angle += 0x80;
    bullets_add_regular();

    bullet_template.speed.v = TO_SP(2);
    bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
    bullet_template.delta.spread_angle = 1;
    bullet_template.count = 3;
    bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
    bullet_template.origin.y.v = (
        randring2_next16_mod(TO_SP(32)) +
        (boss.pos.cur.y.v - TO_SP(26))
    );
    bullet_template.origin.x.v = (
        boss.pos.cur.x.v +
        (static_cast<unsigned int>(boss_statebyte[15]) << 4)
    );
    bullet_template.angle = boss_statebyte[14];
    bullets_add_regular();
    bullet_template.origin.x.v = (
        boss.pos.cur.x.v -
        (static_cast<unsigned int>(boss_statebyte[15]) << 4)
    );
    bullet_template.angle = -boss_statebyte[14];
    bullets_add_regular();
    boss_statebyte[15] += 16;
    if(boss_statebyte[15] > 176) {
        boss_statebyte[15] = 16;
    }
        boss_statebyte[14] += 0x0B;
        snd_se_play(3);
    } else {
        boss.sprite = 130;
    }
}

extern "C" void near gengetsu_random_cloud_ring(void)
{
    if(stage_frame_mod2 != 0) {
        boss.sprite = 134;
    } else {
        boss.sprite = 130;
    }
    if(stage_frame_mod4 != 0) {
        return;
    }

    bullet_template.spawn_type = randring2_next16_and(1);
    bullet_template.origin.x.v = (
        randring2_next16_mod(TO_SP(64)) +
        (boss.pos.cur.x.v - TO_SP(32))
    );
    bullet_template.origin.y.v = (
        randring2_next16_mod(TO_SP(32)) +
        (boss.pos.cur.y.v - TO_SP(26))
    );
    bullet_template.group = BG_RING;
    bullet_template.count = 32;
    bullet_template.angle = randring2_next16();
    bullet_template.speed.v = (TO_SP(6) + 4);
    bullets_add_regular();
    snd_se_play(3);
}

extern "C" bool near gengetsu_hittest(void)
{
    if((boss_bomb_invincibility_frames != 0) && (gengetsu_wave_amp == 0)) {
        boss_hittest_shots_damage(TO_SP(48), TO_SP(48), 10);
    } else if((boss.sprite != 0) && (gengetsu_wave_amp == 0)) {
        return boss_hittest_shots();
    }
    boss.phase_frame++;
    return false;
}

extern "C" void near gengetsu_blue_ring(void)
{
    if(stage_frame_mod8 != 0) {
        return;
    }
    bullet_template.group = BG_RING;
    bullet_template.count = 32;
    bullet_template.patnum = PAT_BULLET16_D_BLUE;
    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.angle = randring2_next16();
    bullet_template.speed.v = TO_SP(7);
    bullets_add_regular();
}
