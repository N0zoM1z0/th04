#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "th04/main/custom.hpp"
#include "th04/main/player/shot.hpp"
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
    signed char angle_speed;
};

#define REIMU_ORB_COUNT CUSTOM_COUNT
#define reimu_orbs (reinterpret_cast<reimu_orb_t near *>(custom_entities))

extern "C" void near reimu_orbs_update(void)
{
    int left;
    int top;
    register reimu_orb_t near *orb = reimu_orbs;
    register int i = 0;

    for(; i < REIMU_ORB_COUNT; (i++, orb++)) {
        if(orb->flag == OF_FREE) {
            continue;
        }

        if(orb->flag == OF_MOVEOUT_SPIN) {
            orb->center.x.v = polar(
                orb->origin.x.v,
                orb->distance.v,
                CosTable8[orb->angle]
            );
            orb->center.y.v = polar(
                orb->origin.y.v,
                orb->distance.v,
                SinTable8[orb->angle]
            );
            if(orb->distance.v < TO_SP(64)) {
                orb->distance.v += TO_SP(4);
            }
            orb->spin_time--;
            orb->angle += orb->angle_speed;
            if(orb->spin_time == 0) {
                if(orb->angle_speed >= 0) {
                    orb->angle += 0x40;
                } else {
                    orb->angle += -0x40;
                }
                vector2_near(orb->velocity, orb->angle, orb->move_speed.v);
                orb->flag++;
            }
        } else if(orb->flag == OF_MOVE) {
            orb->spin_time++;
            orb->center.x.v += orb->velocity.x.v;
            if((orb->center.x.v < 0) || (orb->center.x.v > TO_SP(PLAYFIELD_W))) {
                orb->velocity.x.v = -orb->velocity.x.v;
            }
            orb->center.y.v += orb->velocity.y.v;
            if(orb->center.y.v >= TO_SP(PLAYFIELD_H)) {
                orb->flag = OF_FREE;
            }
            orb->velocity.y.v++;
        }

        shot_hitbox_radius.x.v = TO_SP(12);
        shot_hitbox_radius.y.v = TO_SP(12);
        shot_hitbox_center.x.v = orb->center.x.v;
        shot_hitbox_center.y.v = orb->center.y.v;
        shots_hittest();

        left = (orb->center.x.v - TO_SP(12));
        top = (orb->center.y.v - TO_SP(12));
        if(
            (static_cast<unsigned int>(player_pos.cur.x.v - left) < TO_SP(24)) &&
            (static_cast<unsigned int>(player_pos.cur.y.v - top) < TO_SP(24))
        ) {
            player_is_hit = true;
        }
    }
}

#undef reimu_orbs
#undef REIMU_ORB_COUNT
