#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/th03/math/randring.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"

extern "C" void near reimu_phase_stack_octet(void)
{
    register int i;

    if(boss.phase_frame == 32) {
        boss.sprite = 136;
        boss.angle = 0;
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.angle = -0x40;
        bullet_template.special_motion = BSM_NONE;
        bullet_template.delta.stack_speed.v = 8;
    }

    if((boss.phase_frame >= 32) && ((boss.phase_frame % 16) == 0)) {
        bullet_template.origin.x.v = (
            boss.pos.cur.x.v - TO_SP(32) + randring2_next16_mod(TO_SP(64))
        );
        bullet_template.origin.y.v = (
            boss.pos.cur.y.v - TO_SP(32) + randring2_next16_mod(TO_SP(64))
        );
        bullet_template.angle = randring2_next16();
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.speed.v = (TO_SP(1) + 8);
        bullet_template.group = BG_STACK;
        bullet_template.count = 4;
        bullet_template.delta.stack_speed.v = 10;
        bullet_template_tune();
        for(i = 0, bullet_template.angle = randring2_next16(); i < 8; i++, bullet_template.angle += 0x20) {
            bullets_add_regular();
        }
        snd_se_play(3);
    }
}
