#pragma option -zCmain_0_TEXT -zPmain_01

#include "x86real.h"
#include "src/shared/hardware/graphics.hpp"
#include "th04/formats/super.h"
#include "src/main/hardware/grcg.hpp"
#include "th04/main/drawp.hpp"
#include "th04/main/frames.h"
#include "th04/main/player/player.hpp"
#include "th04/main/scroll.hpp"
#include "th04/math/vector.hpp"

static const unsigned char MISS_ANIM_FRAMES = 32;
static const unsigned char MISS_ANIM_EXPLODE_UNTIL = 31;
static const int MISS_EXPLOSION_COUNT = 8;
static const int MISS_EXPLOSION_W = 48;
static const int MISS_EXPLOSION_H = 48;
static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

extern unsigned char miss_time;
extern unsigned int miss_explosion_radius;
extern unsigned char miss_explosion_angle;
extern unsigned char player_invincibility_time;
extern unsigned char shot_level;
extern SPPoint player_option_pos_cur;
extern unsigned int player_option_patnum;

void pascal near player_render(void)
{
    vram_y_t screen_y;
    int i;
    unsigned char angle;
    register int patnum;
    register screen_x_t left;

    if((miss_time == 0) || (miss_time > MISS_ANIM_FRAMES)) {
        left = ((player_pos.cur.x.v >> 4) + PLAYFIELD_LEFT - (PLAYER_W / 2));
        screen_y = scroll_subpixel_y_to_vram_seg1(
            player_pos.cur.y.v + TO_SP(PLAYFIELD_TOP - (PLAYER_H / 2))
        );
        if(player_pos.velocity.x.v < 0) {
            patnum = 1;
        } else if(player_pos.velocity.x.v != 0) {
            patnum = 2;
        } else {
            patnum = 0;
        }

        if((player_invincibility_time != 0) && (stage_frame_mod4 == 0)) {
            super_roll_put_1plane(left, screen_y, patnum, 0, PLANE_ALL_PUT);
        } else {
            super_roll_put(left, screen_y, patnum);
        }

        if(shot_level < 2) {
            return;
        }
        grcg_setmode_rmw();
        left = (player_option_pos_cur.x.v >> 4);
        screen_y = scroll_subpixel_y_to_vram_seg1(
            player_option_pos_cur.y.v + TO_SP(PLAYFIELD_TOP - (PLAYER_OPTION_H / 2))
        );
        _AX = left;
        _DX = screen_y;
        z_super_roll_put_tiny_16x16_raw(player_option_patnum);
        _AX = (left + PLAYER_OPTION_TO_OPTION_DISTANCE);
        _DX = screen_y;
        z_super_roll_put_tiny_16x16_raw(player_option_patnum);
        _DX = 0x7C;
        _AL = 0;
        outportb(_DX, _AL);
        return;
    }

    if(miss_time <= (MISS_ANIM_FRAMES - MISS_ANIM_EXPLODE_UNTIL)) {
        return;
    }

    patnum = miss_explosion_radius;
    i = 0;
    angle = miss_explosion_angle;
    for(; i < MISS_EXPLOSION_COUNT; i++, angle += (256 / (MISS_EXPLOSION_COUNT / 2))) {
        if(i == (MISS_EXPLOSION_COUNT / 2)) {
            patnum /= 2;
            angle = -angle;
        }
        vector2_at(
            drawpoint,
            player_pos.cur.x.v,
            player_pos.cur.y.v,
            patnum,
            angle
        );
        if(
            (drawpoint.y.v < TO_SP(PLAYFIELD_TOP - (MISS_EXPLOSION_H / 2))) ||
            (drawpoint.y.v >= TO_SP(PLAYFIELD_BOTTOM - 8)) ||
            (drawpoint.x.v < TO_SP(PLAYFIELD_LEFT - 40)) ||
            (drawpoint.x.v >= TO_SP(PLAYFIELD_RIGHT - (MISS_EXPLOSION_W / 2)))
        ) {
            continue;
        }
        left = ((drawpoint.x.v >> 4) + PLAYFIELD_LEFT - (MISS_EXPLOSION_W / 2));
        screen_y = scroll_subpixel_y_to_vram_seg1(
            drawpoint.y.v + TO_SP(PLAYFIELD_TOP - (MISS_EXPLOSION_H / 2))
        );
        super_roll_put(left, screen_y, 3);
    }
}
