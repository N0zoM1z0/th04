#pragma option -G
#pragma option -zCBOSS_FG_TEXT -zPmain_01

#include "x86real.h"
#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th02/sprites/bullet16.h"
#include "th04/formats/super.h"
#include "th04/hardware/grcg.hpp"
#include "th04/main/bullet/clearzap.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/scroll.hpp"
#include "th04/sprites/main_pat.h"

extern "C" void near pellets_render_top(void);
extern "C" void near pellets_render_bottom(void);

extern "C" void pascal near bullets_render(void)
{
    int patnum;
    register bullet_t near *bullet;
    register int i;

    _ES = SEG_PLANE_B;
    bullet = &bullets[BULLET_COUNT - 1];
    i = 0;

    for(; i < BULLET16_COUNT; (i++, bullet--)) {
        if(bullet->flag != F_ALIVE) {
            continue;
        }
        if(bullet->spawn_flag <= BSF_CLOUD_BACKWARDS) {
            _DX = scroll_subpixel_y_to_vram_seg1(
                bullet->pos.cur.y.v + TO_SP(PLAYFIELD_TOP - (BULLET16_H / 2))
            );
            _AX = ((bullet->pos.cur.x.v >> 4) + PLAYFIELD_LEFT - (BULLET16_W / 2));
            z_super_roll_put_tiny_16x16_raw(bullet->patnum);
            continue;
        }

        if(
            (bullet->pos.cur.y.v < 0) ||
            (bullet->pos.cur.y.v >= TO_SP(PLAYFIELD_H)) ||
            (bullet->pos.cur.x.v < 0) ||
            (bullet->pos.cur.x.v >= TO_SP(PLAYFIELD_W))
        ) {
            continue;
        }

        _AX = bullet->patnum;
        if(
            (_AX == PAT_BULLET16_N_OUTLINED_BALL_GREEN) ||
            (_AX == PAT_BULLET16_N_OUTLINED_BALL_BLUE) ||
            (_AX == PAT_BULLET16_N_BALL_BLUE)
        ) {
            patnum = (PAT_CLOUD_BULLET16_BLUE - 1);
        } else {
            patnum = (PAT_CLOUD_BULLET16_RED - 1);
        }
        if(
            (bullet->patnum >= PAT_BULLET16_D_BLUE) &&
            (bullet->patnum < PAT_BULLET16_D_YELLOW)
        ) {
            patnum = (PAT_CLOUD_BULLET16_BLUE - 1);
        }
        patnum += (
            static_cast<unsigned char>(bullet->spawn_flag) /
            (BSF_CLOUD_FRAMES / BULLET_CLOUD_CELS)
        );

        _DX = scroll_subpixel_y_to_vram_seg1(bullet->pos.cur.y.v);
        _AX = ((bullet->pos.cur.x.v >> 4) + 16);
        z_super_roll_put_tiny_32x32_raw(patnum);
    }

    if((bullet_zap.active == 0) && (bullet_clear_time == 0)) {
        _AH = V_WHITE;
        grcg_setcolor_direct_raw();
        pellets_render_top();
        _AH = 9;
        grcg_setcolor_direct_raw();
        pellets_render_bottom();
    } else {
        i = 0;
        for(; i < PELLET_COUNT; (i++, bullet--)) {
            if(bullet->flag != F_ALIVE) {
                continue;
            }
            _DX = scroll_subpixel_y_to_vram_seg1(
                bullet->pos.cur.y.v + TO_SP(PLAYFIELD_TOP - (BULLET16_H / 2))
            );
            _AX = ((bullet->pos.cur.x.v >> 4) + PLAYFIELD_LEFT - (BULLET16_W / 2));
            z_super_roll_put_tiny_16x16_raw(bullet->patnum);
        }
    }
}
