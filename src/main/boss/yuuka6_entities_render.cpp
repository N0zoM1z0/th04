#pragma option -zCMAIN_012_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/custom.hpp"

static const int CHASECROSS_COUNT = (CUSTOM_COUNT - 1);
static const int CHASECROSS_KILL_FRAMES_PER_CEL = 4;
static const int CHASECROSS_W = 32;
static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

enum chasecross_flag_t {
    CCF_FREE = 0,
    CCF_ALIVE = 1,
    CCF_KILL_ANIM = (PAT_ENEMY_KILL * CHASECROSS_KILL_FRAMES_PER_CEL),
    CCF_KILL_ANIM_END = (
        CCF_KILL_ANIM + (ENEMY_KILL_CELS * CHASECROSS_KILL_FRAMES_PER_CEL)
    ),
    _chasecross_flag_t_FORCE_UINT8 = 0xFF,
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

enum safetycircle_flag_t {
    SCF_FREE = 0,
    SCF_GROW = 1,
    SCF_SHRINK = 2,
    _safetycircle_flag_t_FORCE_UINT8 = 0xFF,
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

#define chasecrosses (reinterpret_cast<chasecross_t near *>(custom_entities))

extern "C" void near yuuka6_entities_render(void)
{
    int x;
    int y;
    register chasecross_t near *p;
    register int i;

    for((p = chasecrosses, i = 0); i < CHASECROSS_COUNT; (i++, p++)) {
        if(p->flag == CCF_FREE) {
            continue;
        }

        x = ((p->center.x.v >> 4) + (PLAYFIELD_LEFT - (CHASECROSS_W / 2)));
        y = (p->center.y.v >> 4);
        if(p->flag == CCF_ALIVE) {
            if(p->damage_this_frame == 0) {
                super_put(
                    x,
                    y,
                    (PAT_YUUKA6_CHASECROSS + ((p->age >> 1) & 3))
                );
            } else {
                super_put_1plane(
                    x,
                    y,
                    (PAT_YUUKA6_CHASECROSS + ((p->age >> 1) & 3)),
                    PATTERN_ERASE,
                    PLANE_ALL_PUT
                );
            }
        } else {
            super_put(x, y, (p->flag / CHASECROSS_KILL_FRAMES_PER_CEL));
            p->flag++;
            if(p->flag >= CCF_KILL_ANIM_END) {
                p->flag = CCF_FREE;
            }
        }
    }

    #define sc (*reinterpret_cast<safetycircle_t near *>(p))
    if(sc.flag != SCF_FREE) {
        grcg_setmode_rmw();
        _AH = 2;
        grcg_setcolor_direct_raw();
        grcg_circlefill(sc.center.x, sc.center.y, sc.radius_filled);
        if(sc.flag != SCF_GROW) {
            grcg_setcolor_direct(sc.col_ring);
            grcg_circle(
                sc.center.x,
                sc.center.y,
                (sc.radius_ring_distance + sc.radius_filled)
            );
            _DX = 0x7C;
            _AL = 0;
            outportb(_DX, _AL);
        }
    }
    #undef sc
}
