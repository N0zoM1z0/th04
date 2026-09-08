#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "th04/sprites/main_pat.h"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"

extern "C" unsigned char near reimu_gather_intro(void);

extern "C" void near reimu_phase_stack_fan(void)
{
    unsigned char state = reimu_gather_intro();
    register int i;

    if(state == 2) {
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.group = BG_STACK_AIMED;
        bullet_template.count = boss_statebyte[6];
        bullet_template.delta.stack_speed.v = 12;
        bullet_template.special_motion = BSM_NONE;
        bullet_template.angle = 0;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
    }

    if(state == 1) {
        if((boss.phase_frame % 32) == 16) {
            for(
                i = 0, bullet_template.angle = 0x20;
                i < 5;
                i++, bullet_template.angle += -0x10
            ) {
                bullets_add_special_fixedspeed();
            }
            snd_se_play(15);
        }
        if(boss.phase_frame >= 128) {
            boss.sprite = 128;
            boss.phase_frame = 0;
            boss.mode = -1;
        }
    }
}
