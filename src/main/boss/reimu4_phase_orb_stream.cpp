#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "th04/main/custom.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"

enum reimu_orb_flag_t {
    OF_FREE = 0,
    OF_MOVEOUT_SPIN = 1,
    OF_MOVE = 2,
};

struct reimu_orb_t {
    reimu_orb_flag_t flag;
    unsigned char angle;
    PlayfieldPoint center;
    PlayfieldPoint origin;
    PlayfieldPoint velocity;
    unsigned int spin_time;
    Subpixel distance;
    int unknown;
    signed char unused[4];
    SubpixelLength8 move_speed;
    signed char angle_speed;
};

extern reimu_orb_t orb_template;
void pascal near orbs_add_moving(void);

extern "C" void near reimu_phase_orb_stream(void)
{
    if(boss.phase_frame == 32) {
        boss.sprite = 136;
        orb_template.angle = 0;
        orb_template.move_speed.v = 0x38;
        orb_template.center.x.v = boss.pos.cur.x.v;
        orb_template.center.y.v = boss.pos.cur.y.v;
        snd_se_play(8);
    }

    if(boss.phase_frame >= 32) {
        if((boss.phase_frame % boss_statebyte[1]) == 0) {
            orb_template.angle -= orb_template.angle_speed;
            orbs_add_moving();
        }
    }

    if(boss.phase_frame >= 180) {
        boss.phase_frame = 0;
        boss.mode = -1;
        orb_template.angle_speed = -orb_template.angle_speed;
    }
}
