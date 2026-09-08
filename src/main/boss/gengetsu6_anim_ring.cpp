#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern "C" void near gengetsu_gather_intro(void);

extern "C" unsigned char near gengetsu_phase_state(void)
{
    gengetsu_gather_intro();
    if(boss.phase_frame < 8) {
        return 0;
    }
    if(boss.phase_frame == 8) {
        boss.sprite = 130;
        return 0;
    }
    if(boss.sprite < 32) {
        return 0;
    }
    if(boss.phase_frame < 80) {
        if(boss.phase_frame == 32) {
            snd_se_play(8);
        }
        if(stage_frame_mod2 != 0) {
            boss.sprite = 134;
        } else {
            boss.sprite = 130;
        }
        return 1;
    }
    if(boss.phase_frame == 80) {
        boss.sprite = 132;
        return 2;
    }
    if(boss.phase_frame < 144) {
        return 3;
    }
    boss.sprite = 132;
    return 4;
}

extern "C" void near gengetsu_ring_phase(void)
{
    switch(gengetsu_phase_state()) {
    case 2:
        bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
        bullet_template.patnum = PAT_BULLET16_N_HEART_BALL_RED;
        bullet_template.speed.v = (TO_SP(4) + 6);
        bullet_template.group = BG_RING;
        bullet_template.count = 90;
        bullet_template.angle = randring2_next16();
        bullets_add_regular();
        snd_se_play(9);
        return;
    case 4:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}
