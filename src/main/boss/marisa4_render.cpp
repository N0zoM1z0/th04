#pragma option -zCMAIN__TEXT -zPmain_01

#include "platform.h"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/main/custom.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/main/boss/boss.hpp"

static const int MARISA_BIT_COUNT = 4;
static const unsigned char MARISA_BIT_FREE = 0;
static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

struct marisa_bit_t {
    unsigned char flag;
    unsigned char angle;
    PlayfieldPoint center;
    int patnum;
    char unused_1[8];
    int distance;
    int moveout_speed;
    int hp;
    int damage_this_frame;
    char unused_2;
    signed char angle_speed;
};
typedef char marisa_bit_size_must_be_26[(sizeof(marisa_bit_t) == 26) ? 1 : -1];

extern screen_x_t bit_center_x[MARISA_BIT_COUNT];
extern screen_x_t bit_center_y[MARISA_BIT_COUNT];
extern unsigned char bits_alive;

static void near marisa_bits_render(void)
{
    int left;
    int top;
    register marisa_bit_t near *bit;
    register int i;

    grcg_setmode_rmw();
    _AH = 9;
    grcg_setcolor_direct_raw();

    for(i = 1; i < bits_alive; i++) {
        grcg_line(
            bit_center_x[i - 1], bit_center_y[i - 1],
            bit_center_x[i], bit_center_y[i]
        );
    }
    if(bits_alive >= 3) {
        grcg_line(
            bit_center_x[i - 1], bit_center_y[i - 1],
            bit_center_x[0], bit_center_y[0]
        );
    }

    _DX = 0x7C;
    _AL = 0;
    outportb(_DX, _AL);

    bit = reinterpret_cast<marisa_bit_t near *>(custom_entities);
    for(i = 0; i < MARISA_BIT_COUNT; i++, bit++) {
        if(bit->flag == MARISA_BIT_FREE) {
            continue;
        }
        if(bit->center.x.v <= TO_SP(-16)) {
            continue;
        }
        if(bit->center.x.v >= TO_SP(PLAYFIELD_W)) {
            continue;
        }
        if(bit->center.y.v <= TO_SP(-16)) {
            continue;
        }
        if(bit->center.y.v >= TO_SP(PLAYFIELD_H)) {
            continue;
        }

        left = ((bit->center.x.v >> 4) + (PLAYFIELD_LEFT - 16));
        top = (bit->center.y.v >> 4);
        if(bit->damage_this_frame == 0) {
            super_roll_put(left, top, bit->patnum);
        } else {
            super_roll_put_1plane(
                left, top, bit->patnum, PATTERN_ERASE, PLANE_ALL_PUT
            );
            bit->damage_this_frame = 0;
        }
    }
}

void pascal near marisa_fg_render(void)
{
    #define left _SI
    #define top _DI

    left = (boss.pos.cur.x.v >> 4);
    top = ((boss.pos.cur.y.v >> 4) - 16);
    if(boss.phase < PHASE_EXPLODE_BIG) {
        if(boss.damage_this_frame == 0) {
            super_put(left, _AX, boss.sprite);
        } else {
            super_put_1plane(
                left, top, boss.sprite, PATTERN_ERASE, PLANE_ALL_PUT
            );
            boss.damage_this_frame = 0;
        }
        marisa_bits_render();
    } else if(boss.phase == PHASE_EXPLODE_BIG) {
        super_large_put(left, top, boss.sprite);
    }

    explosions_small_update_and_render();
    explosions_big_update_and_render();

    #undef top
    #undef left
}
