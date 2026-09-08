#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/gather.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern unsigned char bullet_special_turns_max;
extern "C" unsigned char near gengetsu_phase_state(void);

extern "C" void near gengetsu_turn_gather_phase(void)
{
    switch(gengetsu_phase_state()) {
    case 2:
        bullet_special_turns_max = 1;
        return;
    case 3:
        if(stage_frame_mod2 != 0) {
            bullet_template.special_motion = BSM_DECELERATE_THEN_TURN;
            bullet_template.group = BG_SINGLE;
            bullet_template.spawn_type = BST_BULLET16;
            bullet_template.patnum = PAT_BULLET16_N_SMALL_BALL_YELLOW;
            bullet_template.speed.v = (randring2_next16_and(0x3F) + TO_SP(1));
            bullet_template.origin.x.v = boss.pos.cur.x.v - TO_SP(32) + randring2_next16_mod(TO_SP(64));
            bullet_template.origin.y.v = boss.pos.cur.y.v - TO_SP(26) + randring2_next16_mod(TO_SP(32));
            bullet_template.speed.v = (randring2_next16_and(0x3F) + TO_SP(1));
            bullet_template.angle = 0x80;
            bullet_template_special_angle.turn_by = -0x40;
            bullets_add_special();
            bullet_template.angle = 0;
            bullet_template_special_angle.turn_by = 0x40;
            bullets_add_special();
            snd_se_play(9);
        }
        if(stage_frame_mod4 != 0) return;
        gather_template.ring_points = 8;
        gather_template.radius.v = TO_SP(64);
        gather_template.col = 14;
        bullet_template.spawn_type = BST_PELLET;
        gather_template.center.y.v = bullet_template.origin.y.v;
        gather_template.center.x.v = (randring2_next16_mod(TO_SP(320)) + TO_SP(32));
        bullet_template.group = BG_RING_AIMED;
        bullet_template.count = 16;
        bullet_template.speed.v = TO_SP(4);
        gather_add_bullets();
        return;
    case 4:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}
