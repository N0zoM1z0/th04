#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/player/player.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern unsigned char bullet_special_turns_max;
extern "C" unsigned char near gengetsu_phase_state(void);

extern "C" void near gengetsu_spread_pair_phase(void)
{
    switch(gengetsu_phase_state()) {
    case 2:
        bullet_template.group = BG_SPREAD;
        bullet_template.delta.spread_angle = 8;
        boss_statebyte[15] = static_cast<unsigned char>(
            iatan2(
                (player_pos.cur.y.v - bullet_template.origin.y.v),
                (player_pos.cur.x.v - bullet_template.origin.x.v)
            ) + (-0x40)
        );
        return;
    case 3:
        if(stage_frame_mod2 != 0) return;
        bullet_template.speed.v = (randring2_next16_and(0x3F) + 8);
        bullet_template.count = (randring2_next16_and(3) + 5);
        bullet_template.angle = boss_statebyte[15];
        bullets_add_regular();
        bullet_template.angle = static_cast<unsigned char>(0x80 - boss_statebyte[15]);
        bullets_add_regular();
        boss_statebyte[15] += 7;
        snd_se_play(9);
        return;
    case 4:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}

extern "C" void near gengetsu_bounce_phase(void)
{
    switch(gengetsu_phase_state()) {
    case 2:
        bullet_template.special_motion = BSM_BOUNCE_LEFT_RIGHT_TOP_BOTTOM;
        bullet_special_turns_max = 4;
        return;
    case 3:
        if(stage_frame_mod2 == 0) return;
        bullet_template.group = BG_SINGLE;
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.speed.v = (randring2_next16_and(0x3F) + TO_SP(2) + 10);
        bullet_template.origin.x.v = boss.pos.cur.x.v - TO_SP(32) + randring2_next16_mod(TO_SP(64));
        bullet_template.origin.y.v = boss.pos.cur.y.v - TO_SP(32) + randring2_next16_mod(TO_SP(32));
        bullet_template.angle = -0x20;
        bullets_add_special();
        bullet_template.speed.v = (randring2_next16_and(0x3F) + TO_SP(2) + 10);
        bullet_template.angle = -0x60;
        bullets_add_special();
        snd_se_play(9);
        if(stage_frame_mod16 != 1) return;
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        bullet_template.group = BG_RING_AIMED;
        bullet_template.count = 32;
        bullet_template.speed.v = TO_SP(5);
        bullets_add_regular();
        return;
    case 4:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}
