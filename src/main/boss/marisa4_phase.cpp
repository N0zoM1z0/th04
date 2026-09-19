#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "src/shared/runtime/api.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/gather.hpp"
#include "src/main/math/randring.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma option -a

extern "C" unsigned char near marisa_phase_entry(void)
{
    if((boss.mode >= 1) && (boss.mode <= 6)) {
        switch(boss.phase_frame) {
        case 32:
            gather_template.center.x.v = (boss.pos.cur.x.v - TO_SP(20));
            gather_template.center.y.v = (boss.pos.cur.y.v - TO_SP(8));
            gather_template.ring_points = 16;
            gather_template.angle_delta = -2;
            gather_template.col = 3;
            gather_template.radius.v = TO_SP(256);
            goto add_gather;

        case 34:
            gather_template.col = 2;
            // fallthrough
        case 36:
        add_gather:
            gather_add_only();
            break;
        }
    }

    if(boss.phase_frame == 16) {
        boss.sprite = 130;
        snd_se_play(8);
    } else if(boss.phase_frame == 30) {
        circles_add_shrinking(
            (boss.pos.cur.x.v - TO_SP(20)),
            (boss.pos.cur.y.v - TO_SP(8))
        );
    } else if((boss.phase_frame >= 44) && (boss.phase_frame < 64)) {
        boss.sprite = static_cast<unsigned char>(
            ((boss.phase_frame - 32) / 4) + 128
        );
    } else if(boss.phase_frame == 64) {
        boss.sprite = 130;
        snd_se_play(15);
        return 2;
    }

    if(boss.phase_frame < 64) {
        return 0;
    }
    return 1;
}

extern "C" void near marisa_phase_move(void)
{
    if((boss.phase_frame & 0x1F) == 1) {
        if(boss.pos.cur.x.v <= TO_SP(112)) {
            boss.pos.velocity.x.v = TO_SP(2);
        } else if(boss.pos.cur.x.v >= TO_SP(272)) {
            boss.pos.velocity.x.v = -TO_SP(2);
        } else {
            boss.pos.velocity.x.v = (
                (randring2_next16_and(1) != 0) ? TO_SP(1) : -TO_SP(1)
            );
        }

        if(boss.pos.cur.y.v <= TO_SP(80)) {
            boss.pos.velocity.y.v = TO_SP(1);
        } else if(boss.pos.cur.y.v >= TO_SP(144)) {
            boss.pos.velocity.y.v = -TO_SP(1);
        } else {
            unsigned char direction = static_cast<unsigned char>(
                randring2_next16_and(3)
            );
            boss.pos.velocity.y.v = (
                (direction == 0) ? TO_SP(1) :
                (direction == 1) ? -TO_SP(1) :
                (direction == 2) ? 24 : -24
            );
        }
    }

    boss.pos.update_seg3();
}

#pragma codeseg
