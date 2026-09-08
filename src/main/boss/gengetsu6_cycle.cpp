#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/gather.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern unsigned char bullet_special_turns_max;
extern "C" unsigned char near gengetsu_phase_state(void);

extern "C" void near gengetsu_cycle_phase(void)
{
    register int i;
    switch(gengetsu_phase_state()) {
    case 0:
        bullet_template.patnum = PAT_BULLET16_N_HEART_BALL_RED;
        bullet_template.group = BG_SPREAD_AIMED;
        bullet_template.special_motion = BSM_NONE;
        bullet_template.delta.spread_angle = 0x10;
        bullet_template.angle = 0;
        bullet_template.count = 2;
        break;
    case 1:
        if((boss.phase_frame & 0xF) != 8) break;
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        i = 0;
        bullet_template.speed.v = TO_SP(1);
        for(; i < 4; (i++, bullet_template.speed.v += (TO_SP(1) + 4))) {
            bullets_add_special_fixedspeed();
        }
        snd_se_play(15);
        bullet_template.count += 2;
        bullet_template.delta.spread_angle += -2;
        break;
    case 2:
        bullet_template.group = BG_STACK_AIMED;
        bullet_template.count = 8;
        bullet_template.delta.stack_speed.v = 10;
        bullet_template.speed.v = TO_SP(2);
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.angle = 0;
        break;
    case 3:
        if((boss.phase_frame & 3) != 0) break;
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullets_add_regular();
        snd_se_play(15);
        break;
    case 4:
        boss.phase_frame = 0;
        boss.mode = -1;
        break;
    }
}
