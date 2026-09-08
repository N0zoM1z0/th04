#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "th04/main/custom.hpp"
#include "th04/math/vector.hpp"

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
    char angle_speed;
};

#define REIMU_ORB_COUNT CUSTOM_COUNT
#define reimu_orbs (reinterpret_cast<reimu_orb_t near *>(custom_entities))

extern reimu_orb_t orb_template;

void pascal near orbs_add_moving(void)
{
    register reimu_orb_t near *orb = reimu_orbs;
    register int i = 0;

    for(; i < REIMU_ORB_COUNT; (i++, orb++)) {
        if(orb->flag != OF_FREE) {
            continue;
        }
        orb->flag = OF_MOVE;
        orb->center = orb_template.center;
        orb->origin = orb_template.origin;
        orb->unknown = orb_template.unknown;
        orb->move_speed = orb_template.move_speed;
        orb->angle = orb_template.angle;
        orb->distance.v = 0;
        vector2_near(orb->velocity, orb_template.angle, orb_template.move_speed.v);
        return;
    }
}

#undef reimu_orbs
#undef REIMU_ORB_COUNT
