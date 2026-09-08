#pragma option -zCMAIN_036_TEXT -zPmain_03

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
    char angle_speed;
};

#define REIMU_ORB_COUNT CUSTOM_COUNT
#define reimu_orbs (reinterpret_cast<reimu_orb_t near *>(custom_entities))

extern reimu_orb_t orb_template;

void pascal near orbs_add_spinning(unsigned char angle_offset, int count)
{
    register reimu_orb_t near *orb;
    register int i;
    register int spawned;

    spawned = 0;
    orb = reimu_orbs;
    i = 0;

    for(; i < REIMU_ORB_COUNT; (i++, orb++)) {
        if(orb->flag != OF_FREE) {
            continue;
        }
        orb->flag = OF_MOVEOUT_SPIN;
        orb->spin_time = orb_template.spin_time;
        orb->center = orb_template.center;
        orb->origin = orb_template.origin;
        orb->unknown = orb_template.unknown;
        orb->move_speed = orb_template.move_speed;
        orb->angle = static_cast<unsigned char>(
            (((spawned << 8) / count) + angle_offset)
        );
        orb->distance.v = 0;
        orb->angle_speed = orb_template.angle_speed;
        spawned++;
        if(spawned >= count) {
            return;
        }
    }
}

#undef reimu_orbs
#undef REIMU_ORB_COUNT
