#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/th03/math/randring.hpp"
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
void pascal near orbs_add_spinning(unsigned char angle_offset, int count);

extern "C" void near reimu_phase_orb_spawn(void)
{
    if(boss.phase_frame == 32) {
        boss.sprite = 136;
        orb_template.spin_time = 64;
        orb_template.move_speed.v = 0x38;
        orb_template.origin = boss.pos.cur;
        orbs_add_spinning(randring2_next16(), boss_statebyte[0]);
        snd_se_play(8);
    }

    if(boss.phase_frame >= 96) {
        boss.phase_frame = 0;
        boss.mode = -1;
        orb_template.angle_speed = -orb_template.angle_speed;
    }
}
