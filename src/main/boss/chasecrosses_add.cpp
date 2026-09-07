#pragma option -zCMAIN_034_TEXT -zPmain_03
#include "th04/main/boss/boss.hpp"
#include "th04/main/custom.hpp"

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
