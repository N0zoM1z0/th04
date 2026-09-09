#pragma option -zCMAIN_01_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/main/boss/boss.hpp"

static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

extern unsigned char mugetsu_damage_flash_cycle;

#pragma codeseg MAIN_01_TEXT main_01
extern "C" void near gengetsu_bomb_inv_render(void);
#pragma codeseg

void pascal near mugetsu_fg_render(void)
{
    #define left _SI
    register int top;

    if(boss.sprite != 0) {
        left = (boss.pos.cur.x.v >> 4);
        top = ((boss.pos.cur.y.v >> 4) - 32);

        if(boss.phase < PHASE_EXPLODE_BIG) {
            if(boss.damage_this_frame == 0) {
                super_put(left, _AX, boss.sprite);
                gengetsu_bomb_inv_render();
            } else {
                mugetsu_damage_flash_cycle++;
                if((mugetsu_damage_flash_cycle & 1) != 0) {
                    super_put(left, top, boss.sprite);
                } else {
                    super_put_1plane(
                        left, top, boss.sprite, PATTERN_ERASE, PLANE_ALL_PUT
                    );
                }
                boss.damage_this_frame = 0;
            }
        } else if(boss.phase == PHASE_EXPLODE_BIG) {
            super_large_put(left, top, boss.sprite);
        }
    }

    explosions_small_update_and_render();
    explosions_big_update_and_render();

    #undef left
}
