#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/th03/math/randring.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"

extern "C" unsigned char near reimu_gather_intro(void);

extern "C" void near reimu_phase_pellet_and_cloud(void)
{
    unsigned char state = reimu_gather_intro();
    if(state != 1) {
        return;
    }

    if((boss.phase_frame % 4) == 0) {
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.speed.v = TO_SP(8);
        bullet_template.angle = static_cast<unsigned char>(
            randring2_next16_and(7) + (-0x44)
        );
        bullet_template.group = BG_SPREAD;
        bullet_template.count = boss_statebyte[3];
        bullet_template.delta.spread_angle = boss_statebyte[4];
        bullets_add_regular_fixedspeed();

        if((boss.phase_frame % 16) == 0) {
            bullet_template.origin.x.v = (
                boss.pos.cur.x.v - TO_SP(32) + randring2_next16_mod(TO_SP(64))
            );
            bullet_template.origin.y.v = (
                boss.pos.cur.y.v - TO_SP(32) + randring2_next16_mod(TO_SP(64))
            );
            bullet_template.group = BG_STACK_AIMED;
            bullet_template.count = static_cast<unsigned char>(rank + 3);
            bullet_template.delta.stack_speed.v = TO_SP(1);
            bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
            bullet_template.speed.v = TO_SP(2);
            bullet_template.angle = 0;
            bullet_template.patnum = PAT_BULLET16_N_BALL_RED;
            bullets_add_regular();
            snd_se_play(3);
        }
    }

    if(boss.phase_frame >= 192) {
        boss.sprite = 128;
        boss.phase_frame = 0;
        boss.mode = -1;
    }
}
