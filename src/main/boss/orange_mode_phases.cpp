#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/player/player.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern "C" int near orange_phase_entry(void);

extern "C" void near orange_phase_random_rings(void)
{
    if(orange_phase_entry() != 2) {
        return;
    }
    if(boss.phase_frame == 86) {
        boss.phase_state.patterns_seen = randring2_next16_and(1);
        boss.angle = ((boss.phase_state.patterns_seen == 0) ? 0 : 0x80);
        boss.phase_state.patterns_seen = (
            (boss.phase_state.patterns_seen == 0)
            ? 0x0B
            : static_cast<unsigned char>(-0x0B)
        );
    }
    if(stage_frame_mod2 == 0) {
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.origin.x.v = boss.pos.cur.x.v;
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        bullet_template.group = BG_RING;
        bullet_template.count = 2;
        bullet_template.angle = boss.angle;
        bullet_template.speed.v = (TO_SP(1) + 14);
        bullets_add_regular();
        bullet_template.angle += 5;
        bullet_template.speed.v = (TO_SP(1) + 4);
        bullets_add_regular();
        boss.angle += boss.phase_state.patterns_seen;
        snd_se_play(9);
    }
    if(boss.phase_frame >= 118) {
        boss.mode = 0;
    }
}

extern "C" void near orange_phase_aimed_clouds(void)
{
    if(orange_phase_entry() != 2) {
        return;
    }
    if(boss.phase_frame == 86) {
        boss.angle = iatan2(
            (player_pos.cur.y.v - boss.pos.cur.y.v),
            (player_pos.cur.x.v - boss.pos.cur.x.v)
        );
        bullet_template.speed.v = TO_SP(1);
    }
    if(stage_frame_mod4 == 0) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_WHITE;
        bullet_template.origin.x.v = boss.pos.cur.x.v;
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 3;
        bullet_template.delta.spread_angle = 0x0C;
        bullet_template.special_motion = BSM_NONE;
        bullet_template.angle = (boss.angle - 0x20);
        bullet_template_tune();
        bullets_add_special();
        bullet_template.angle += 0x40;
        bullets_add_special();
        snd_se_play(3);
        bullet_template.speed.v += 6;
    }
    if(boss.phase_frame >= 118) {
        boss.mode = 0;
    }
}

extern "C" void near orange_phase_ring16(void)
{
    if(orange_phase_entry() != 2) {
        return;
    }
    if(stage_frame_mod8 == 0) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_WHITE;
        bullet_template.origin.x.v = boss.pos.cur.x.v;
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        bullet_template.group = BG_RING_AIMED;
        bullet_template.count = 16;
        bullet_template.speed.v = TO_SP(2);
        bullet_template.angle = 0;
        bullet_template_tune();
        bullets_add_regular();
        snd_se_play(9);
    }
    if(boss.phase_frame >= 118) {
        boss.mode = 0;
    }
}

extern "C" void near orange_phase_side_rings(void)
{
    if(orange_phase_entry() != 2) {
        return;
    }
    if(stage_frame_mod8 == 0) {
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.origin.x.v = (boss.pos.cur.x.v - TO_SP(32));
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        bullet_template.group = BG_RING;
        bullet_template.count = 8;
        bullet_template.speed.v = (TO_SP(1) + 14);
        bullet_template.angle += 8;
        bullet_template_tune();
        bullets_add_regular();
        bullet_template.origin.x.v += TO_SP(64);
        bullets_add_regular();
        snd_se_play(9);
    }
    if(boss.phase_frame >= 118) {
        boss.mode = 0;
    }
}
