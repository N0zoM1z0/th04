#pragma option -zCMAIN_034_TEXT -zPmain_03
#include "th04/snd/snd.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/custom.hpp"
#include "th04/main/player/player.hpp"

enum chasecross_flag_t {
    CCF_FREE = 0,
    CCF_ALIVE = 1,
    _chasecross_flag_t_FORCE_UINT8 = 0xFF
};

struct chasecross_t {
    chasecross_flag_t flag;
    unsigned char angle;
    PlayfieldPoint center;
    int8_t unused_1[4];
    PlayfieldPoint velocity;
    unsigned int age;
    int8_t unused_2[4];
    int hp;
    int damage_this_frame;
    SubpixelLength8 speed;
    int8_t padding;
};

#define chasecrosses (reinterpret_cast<chasecross_t *>(custom_entities))

void pascal near chasecrosses_add(
    unsigned char angle, subpixel_length_8_t speed
)
{
    chasecross_t near *p;
    int i;
    for((p = chasecrosses, i = 0); i < CUSTOM_COUNT; (i++, p++)) {
        if(p->flag == CCF_FREE) {
            p->flag = CCF_ALIVE;
            p->damage_this_frame = 0;
            p->age = 0;
            p->angle = angle;
            p->speed.v = speed;
            p->hp = 100;
            p->center.x.v = boss.pos.cur.x.v;
            p->center.y.v = boss.pos.cur.y.v;
            break;
        }
    }
}

enum safetycircle_flag_t {
    SCF_FREE = 0,
    SCF_GROW = 1,
    SCF_SHRINK = 2,
    _safetycircle_flag_t_FORCE_UINT8 = 0xFF
};

struct safetycircle_t {
    safetycircle_flag_t flag;
    int8_t unused_1;
    screen_point_t center;
    int8_t unused_2[8];
    unsigned int shrink_frame;
    pixel_t radius_filled;
    pixel_t radius_ring_distance;
    int8_t unused_3[4];
    vc_t col_ring;
    int8_t padding;
};

#define safetycircle ( \
    reinterpret_cast<safetycircle_t &>(custom_entities[CUSTOM_COUNT - 1]) \
)

extern "C" void near yuuka6_safetycircle_add(void)
{
    safetycircle_t near *p = &safetycircle;
    p->flag = SCF_GROW;
    p->shrink_frame = 0;
    p->col_ring = 8;
    p->center.x = ((player_pos.cur.x.v >> 4) + PLAYFIELD_LEFT);
    p->center.y = ((player_pos.cur.y.v >> 4) + PLAYFIELD_TOP);
    p->radius_filled = 8;
    p->radius_ring_distance = 80;
    snd_se_play(8);
}
