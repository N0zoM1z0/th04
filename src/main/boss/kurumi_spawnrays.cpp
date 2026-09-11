#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/custom.hpp"
#include "th04/math/vector.hpp"
#include "th04/snd/snd.h"

static const int KURUMI_SPAWNRAY_COUNT = 6;

extern unsigned char bullet_special_speed_delta;

enum kurumi_spawnray_flag_t {
    B2SF_FREE = 0,
    B2SF_GROW = 1,
    B2SF_SHRINK = 2,
};

struct kurumi_spawnray_t {
    kurumi_spawnray_flag_t flag;
    signed char unused;
    PlayfieldPoint target;
    PlayfieldPoint origin;
    PlayfieldPoint velocity;
    signed char padding[12];
};

#define kurumi_spawnrays ( \
    reinterpret_cast<kurumi_spawnray_t near *>(custom_entities) \
)

void pascal near kurumi_spawnrays_add(
    subpixel_t distance_from_center_x, unsigned char angle
)
{
    register kurumi_spawnray_t near *spawnray;
    register int i;

    for(
        (spawnray = kurumi_spawnrays, i = 0);
        i < KURUMI_SPAWNRAY_COUNT;
        (i++, spawnray++)
    ) {
        if(spawnray->flag != B2SF_FREE) {
            continue;
        }
        spawnray->flag = B2SF_GROW;
        spawnray->target.x.v = (boss.pos.cur.x.v + distance_from_center_x);
        spawnray->target.y.v = (boss.pos.cur.y.v - TO_SP(10));
        spawnray->origin.x.v = (boss.pos.cur.x.v + distance_from_center_x);
        spawnray->origin.y.v = (boss.pos.cur.y.v - TO_SP(10));
        vector2(
            spawnray->velocity.x.v,
            spawnray->velocity.y.v,
            angle,
            TO_SP(16)
        );
        snd_se_play(5);
        break;
    }
}

bool near kurumi_spawnrays_update(void)
{
    register kurumi_spawnray_t near *spawnray;
    register int spawnray_i;
    int free_count;
    int bullet_i;

    for(
        (spawnray = kurumi_spawnrays, spawnray_i = 0, free_count = 0);
        spawnray_i < KURUMI_SPAWNRAY_COUNT;
        (spawnray_i++, spawnray++)
    ) {
        if(spawnray->flag == B2SF_FREE) {
            free_count++;
        }

        if(spawnray->flag == B2SF_GROW) {
            if(
                (spawnray->target.x.v < TO_SP(PLAYFIELD_W)) &&
                (spawnray->target.y.v < TO_SP(PLAYFIELD_H)) &&
                (spawnray->target.x.v > 0) &&
                (spawnray->target.y.v > 0)
            ) {
                spawnray->target.x.v += spawnray->velocity.x.v;
                spawnray->target.y.v += spawnray->velocity.y.v;
            } else {
                bullet_template.origin.x.v = (
                    spawnray->target.x.v - spawnray->velocity.x.v
                );
                bullet_template.origin.y.v = (
                    spawnray->target.y.v - spawnray->velocity.y.v
                );
                bullet_template.special_motion = BSM_SPEEDUP;
                bullet_special_speed_delta = 1;
                bullet_i = 0;
                bullet_template.speed.v = TO_SP(2);
                for(
                    ; bullet_i < 3;
                    (bullet_i++, bullet_template.speed.v += 6)
                ) {
                    bullets_add_regular_fixedspeed();
                }
                spawnray->flag++;
                snd_se_play(6);
                circles_color = 9;
                circles_add_growing(
                    bullet_template.origin.x.v,
                    bullet_template.origin.y.v
                );
            }
        } else if(spawnray->flag == B2SF_SHRINK) {
            if(
                (spawnray->origin.x.v < TO_SP(PLAYFIELD_W)) &&
                (spawnray->origin.y.v < TO_SP(PLAYFIELD_H)) &&
                (spawnray->origin.x.v > 0) &&
                (spawnray->origin.y.v > 0)
            ) {
                spawnray->origin.x.v += spawnray->velocity.x.v;
                spawnray->origin.y.v += spawnray->velocity.y.v;
            } else {
                spawnray->flag = B2SF_FREE;
            }
        }
    }

    if(free_count == KURUMI_SPAWNRAY_COUNT) {
        return true;
    }
    return false;
}
