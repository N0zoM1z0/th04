#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "src/shared/runtime/api.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma option -a

#define EXPLOSION_SMALL_COUNT 2

struct Explosion {
    bool alive;
    unsigned char age;
    SPPoint center;
    SPPoint radius_cur;
    SPPoint radius_delta;
    signed char unused;
    unsigned char angle_offset;
};

extern Explosion explosions_small[EXPLOSION_SMALL_COUNT];
extern Explosion explosions_big;

void explosions_small_reset(void)
{
    explosions_small[0].alive = false;
    explosions_small[1].alive = false;
}

#define explosion_add_typed(p, type) { \
    (p).alive = true; \
    (p).age = 0; \
    (p).center.x = boss.pos.cur.x; \
    (p).center.y = boss.pos.cur.y; \
    (p).radius_cur.x.v = 8; \
    (p).radius_cur.y.v = 8; \
    (p).radius_delta.x.v = (11 << 4); \
    (p).radius_delta.y.v = (11 << 4); \
    (p).angle_offset = 0; \
    switch(type) { \
    case ET_NW_SE: \
        (p).angle_offset = 32; \
        break; \
    case ET_SW_NE: \
        (p).angle_offset = -32; \
        break; \
    case ET_HORIZONTAL: \
        (p).radius_delta.x.v = (13 << 4); \
        (p).radius_delta.y.v = (7 << 4); \
        break; \
    case ET_VERTICAL: \
        (p).radius_delta.x.v = (7 << 4); \
        (p).radius_delta.y.v = (13 << 4); \
        break; \
    } \
    snd_se_play(15); \
}

void pascal near boss_explode_small(explosion_type_t type)
{
    Explosion near *p = explosions_small;
    if(p->alive) {
        p++;
    }
    explosion_add_typed(*p, type);
}

void pascal near boss_explode_big(unsigned int type)
{
    Explosion near& p = explosions_big;
    explosion_add_typed(p, type);
}

#pragma codeseg
