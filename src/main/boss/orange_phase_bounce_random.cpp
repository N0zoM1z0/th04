#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/rank.hpp"
#include "th04/math/randring.hpp"

extern "C" void near orange_phase_bounce_random(void)
{
    if(boss.phase_frame == 1) {
        boss.pos.velocity.x.v = (
            (boss.pos.cur.x.v < TO_SP(192)) ? TO_SP(1) : -TO_SP(1)
        );
        boss.angle = 0;
    }

    boss.pos.velocity.y.v = polar(0, TO_SP(1), SinTable8[boss.angle]);
    if(boss.pos.cur.y.v >= TO_SP(96)) {
        boss.pos.velocity.y.v = -TO_SP(1);
    }
    if(boss.pos.cur.y.v <= TO_SP(48)) {
        boss.pos.velocity.y.v = TO_SP(1);
    }
    boss.angle += 2;

    boss.pos.update_seg3();
    if((_AX <= TO_SP(32)) || (_AX >= TO_SP(352))) {
        boss.pos.velocity.x.v *= -1;
    }

    if(stage_frame_mod4 != 0) {
        return;
    }
    if((rank == RANK_EASY) && (stage_frame_mod8 == 0)) {
        return;
    }

    bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_WHITE;
    bullet_template.origin.x.v = (boss.pos.cur.x.v - TO_SP(32));
    bullet_template.origin.y.v = boss.pos.cur.y.v;
    bullet_template.group = BG_RANDOM_ANGLE;
    bullet_template.count = 1;
    if(boss.hp <= 700) {
        if(rank < RANK_LUNATIC) {
            bullet_template.count = 2;
        } else {
            bullet_template.count = 4;
        }
    }
    bullet_template.speed.v = TO_SP(2);
    bullet_template.spawn_type = (
        (randring2_next16_and(1) == 0)
        ? BST_PELLET
        : BST_BULLET16_CLOUD_FORWARDS
    );
    bullet_template.angle = randring2_next16();
    bullet_template_tune();
    bullets_add_regular();

    bullet_template.origin.x.v += TO_SP(64);
    bullet_template.spawn_type = (
        (randring2_next16_and(1) == 0)
        ? BST_PELLET
        : BST_BULLET16_CLOUD_FORWARDS
    );
    bullet_template.angle = randring2_next16();
    bullets_add_regular();
}
