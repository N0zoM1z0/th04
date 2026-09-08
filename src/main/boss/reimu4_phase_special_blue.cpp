#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "th04/sprites/main_pat.h"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/boss/boss.hpp"

extern "C" unsigned char near reimu_gather_intro(void);
extern unsigned char bullet_special_turns_max;

extern "C" void near reimu_phase_special_blue(void)
{
    unsigned char state = reimu_gather_intro();

    if(state == 2) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.speed.v = (TO_SP(5) + 5);
        bullet_template.angle = 0;
        bullet_template.special_motion = BSM_DECELERATE_THEN_TURN_AIMED;
        bullet_special_turns_max = boss_statebyte[2];
        bullet_template.group = BG_SPREAD_AIMED;
        bullet_template.count = 9;
        bullet_template.delta.spread_angle = 6;
        bullet_template_tune();
        bullets_add_special_fixedspeed();
    }

    if((state == 1) && (boss.phase_frame >= 128)) {
        boss.sprite = 128;
        boss.phase_frame = 0;
        boss.mode = -1;
    }
}
