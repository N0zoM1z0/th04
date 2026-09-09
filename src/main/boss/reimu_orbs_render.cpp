#pragma option -zCBOSS_FG_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/main/frames.h"
#include "th04/main/custom.hpp"

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

#define REIMU_ORB_COUNT CUSTOM_COUNT
#define reimu_orbs (reinterpret_cast<reimu_orb_t near *>(custom_entities))

extern unsigned char orb_patnum_base;

extern "C" void near reimu_orbs_render(void)
{
    int left;
    int top;
    int patnum;
    register reimu_orb_t near *orb = reimu_orbs;
    register int i = 0;

    for(; i < REIMU_ORB_COUNT; (i++, orb++)) {
        if(orb->flag == OF_FREE) {
            continue;
        }
        if(orb->center.y.v <= TO_SP(-16)) {
            continue;
        }
        left = ((orb->center.x.v >> 4) + 16);
        top = (orb->center.y.v >> 4);
        patnum = (
            orb_patnum_base + (((stage_frame + i) & 7) >> 1)
        );
        super_roll_put(left, top, patnum);
    }
}

#undef reimu_orbs
#undef REIMU_ORB_COUNT
