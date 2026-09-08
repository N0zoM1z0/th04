#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th03/math/randring.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"
#include "th04/snd/snd.h"

extern "C" unsigned char near reimu_gather_intro(void);
extern unsigned char bullet_special_speed_delta;

extern "C" void near reimu_phase_random_aimed(void)
{
    unsigned char state = reimu_gather_intro();

    if(state == 2) {
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.speed.v = (TO_SP(3) + 6);
        bullet_template.angle = iatan2(
            (player_pos.cur.y.v - boss.pos.cur.y.v),
            (player_pos.cur.x.v - boss.pos.cur.x.v)
        );
        bullet_template.group = BG_RANDOM_ANGLE_AND_SPEED;
        bullet_template.count = 3;
        bullet_template_tune();
    }

    if(state != 1) {
        return;
    }

    if(boss.phase_frame < 96) {
        if((boss.phase_frame % 2) != 0) {
            return;
        }
        bullets_add_regular();
        snd_se_play(3);
        return;
    }

    if(boss.phase_frame <= 128) {
        if((boss.phase_frame % 16) != 0) {
            return;
        }
        bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template.angle = randring2_next16();
        bullet_template.speed.v = TO_SP(3);
        bullet_template.special_motion = BSM_SPEEDUP;
        bullet_special_speed_delta = 1;
        bullet_template_tune();
        bullets_add_special();
        snd_se_play(15);
        return;
    }

    boss.sprite = 128;
    boss.phase_frame = 0;
    boss.mode = -1;
}
