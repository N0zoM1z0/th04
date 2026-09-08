#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/th03/math/randring.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"

extern "C" unsigned char near reimu_gather_intro(void);
extern unsigned char bullet_special_speed_delta;

extern "C" void near reimu_phase_cloud_ring_stack(void)
{
    unsigned char state = reimu_gather_intro();
    register int i;

    if(state != 1) {
        return;
    }

    if((boss.phase_frame % 32) == 0) {
        bullet_template.origin.x.v = (
            boss.pos.cur.x.v - TO_SP(32) + randring2_next16_mod(TO_SP(64))
        );
        bullet_template.origin.y.v = (
            boss.pos.cur.y.v - TO_SP(32) + randring2_next16_mod(TO_SP(64))
        );
        bullet_template.angle = randring2_next16();
        bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.speed.v = TO_SP(1);
        bullet_template.angle = 0;
        bullet_template.special_motion = BSM_SPEEDUP;
        bullet_special_speed_delta = 1;
        bullet_template.group = BG_RING;
        bullet_template.count = 16;
        bullet_template_tune();
        bullets_add_special_fixedspeed();
        snd_se_play(3);
    }

    if((boss.phase_frame % 32) == 16) {
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
        bullet_template.delta.stack_speed.v = 8;
        bullet_template_tune();
        for(
            i = 0, bullet_template.angle = randring2_next16();
            i < 12;
            i++, bullet_template.angle += 0x15
        ) {
            bullets_add_regular();
        }
        snd_se_play(3);
    }

    if(boss.phase_frame >= 288) {
        boss.sprite = 128;
        boss.phase_frame = 0;
        boss.mode = -1;
    }
}
