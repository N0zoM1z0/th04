#pragma option -zCBOSS_FG_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th04/hardware/grcg.hpp"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/custom.hpp"

static const int GENGETSU_SPAWNCOLUMN_COUNT = 16;
static const unsigned PLANE_ALL_PUT = (0xFF00 | GC_RMW | GC_BRGI);

struct gengetsu_spawncolumn_t {
    signed char unused[2];
    PlayfieldPoint pos;
    signed char padding[20];
};

#define gengetsu_spawncolumns ( \
    reinterpret_cast<gengetsu_spawncolumn_t near *>(custom_entities) \
)

extern unsigned char gengetsu_wave_amp;
extern unsigned char gengetsu_damage_flash_cycle;

#pragma codeseg MAIN_01_TEXT main_01
extern "C" void near gengetsu_bomb_inv_render(void);
#pragma codeseg MAIN_TEXT main_01
extern "C" void near thicklasers_render(void);
#pragma codeseg

void pascal near gengetsu_fg_render(void)
{
    gengetsu_spawncolumn_t near *spawncolumn;
    register int left;
    #define top _SI

    if(boss.sprite != 0) {
        left = (boss.pos.cur.x.v >> 4) - 16;
        top = (boss.pos.cur.y.v >> 4) - 32;

        if(boss.phase < PHASE_EXPLODE_BIG) {
            if(gengetsu_wave_amp != 0) {
                super_wave_put(
                    left,
                    _AX,
                    boss.sprite,
                    (80 - gengetsu_wave_amp),
                    gengetsu_wave_amp,
                    boss.angle
                );
                super_wave_put(
                    (left + 48),
                    top,
                    (boss.sprite + 1),
                    (80 - gengetsu_wave_amp),
                    gengetsu_wave_amp,
                    boss.angle
                );
                boss.angle += 4;
            } else if(boss.damage_this_frame == 0) {
                super_put(left, top, boss.sprite);
                super_put((left + 48), top, (boss.sprite + 1));
                gengetsu_bomb_inv_render();
            } else {
                gengetsu_damage_flash_cycle++;
                if((gengetsu_damage_flash_cycle & 1) != 0) {
                    super_put(left, top, boss.sprite);
                    super_put((left + 48), top, (boss.sprite + 1));
                } else {
                    super_put_1plane(
                        left, top, boss.sprite, PATTERN_ERASE, PLANE_ALL_PUT
                    );
                    super_put_1plane(
                        (left + 48),
                        top,
                        (boss.sprite + 1),
                        PATTERN_ERASE,
                        PLANE_ALL_PUT
                    );
                }
                boss.damage_this_frame = 0;
            }
        } else if(boss.phase == PHASE_EXPLODE_BIG) {
            super_zoom(left, top, boss.sprite, 3);
        }
    }

    explosions_small_update_and_render();
    explosions_big_update_and_render();
    thicklasers_render();

    if(
        (boss.phase == 5) &&
        (boss.mode == 1) &&
        (boss.phase_frame >= 32) &&
        (boss.phase_frame < 96)
    ) {
        grcg_setmode_rmw();
        if(stage_frame_mod2 != 0) {
            _AH = 9;
        } else {
            _AH = V_WHITE;
        }
        grcg_setcolor_direct_raw();

        spawncolumn = gengetsu_spawncolumns;
        for(
            _SI = 0;
            static_cast<int16_t>(_SI) < GENGETSU_SPAWNCOLUMN_COUNT;
            (_SI++, spawncolumn++)
        ) {
            left = ((spawncolumn->pos.x.v / 16) + PLAYFIELD_LEFT);
            grcg_vline(left, 16, (PLAYFIELD_BOTTOM - 1));
        }
    }

    #undef top
}
