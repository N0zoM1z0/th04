#pragma option -zCDEMO_TEXT -zPmain_01

// Maintained natural source for the reviewed DEMO_TEXT gameplay loop.
// Target- and cross-game-backed source shape for the reviewed DEMO_TEXT gameplay loop.

#include "src/shared/runtime/api.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/main/hardware/grcg.hpp"
#include "th04/hardware/input.h"
#include "src/shared/config/resident.hpp"
#include "th04/main/frames.h"
#include "th04/main/slowdown.hpp"
#include "th04/main/quit.hpp"
#include "th04/main/score.hpp"

extern nearfunc_t_near fp_23D90;
extern bool bombing;
extern bool palette_changed;
extern unsigned char page_front;
extern unsigned char page_back;
extern bool (near *std_update)(void);
extern func_t_near stage_vm;
extern nearfunc_t_near bg_render_not_bombing;
extern nearfunc_t_near bg_render_bombing;
extern func_t_near midboss_update;
extern func_t_near boss_update;
extern nearfunc_t_near stage_render;
extern nearfunc_t_near boss_fg_render;
extern nearfunc_t_near midboss_render;
extern nearfunc_t_near overlay1;
extern nearfunc_t_near overlay2;

void pascal far frame_delay(int frames);
extern "C" int near pause(void);
extern "C" void pascal far playperf_raise(char delta);
#pragma samecodeseg playperf_raise
void far midboss_activate_if_stage_frame_is_midboss_start_frame(void);
extern "C" void pascal near pointnums_update(void);
void near circles_update(void);
extern "C" void near sparks_update(void);
void near sub_10ABF(void);
void near sub_104B6(void);
void far bullets_update(void);
extern "C" void pascal far enemies_update(void);
extern "C" void pascal far items_update(void);
void far gather_update(void);
void near bomb_update_and_render(void);
extern "C" void pascal near enemies_render(void);
void near SHOTS_RENDER(void);
extern "C" void pascal near player_render(void);
void near grcg_setmode_rmw(void);
void far gather_render(void);
extern "C" void near sparks_render(void);
extern "C" void pascal near items_render(void);
extern "C" void pascal near pointnums_render(void);
extern "C" void pascal near bullets_render(void);
void near circles_render(void);
void near playfield_shake_update_and_render(void);
void near sub_CCD6(void);
extern "C" void far snd_se_update(void);

void near gameplay_loop(void)
{
    slowdown_factor = 1;
    frame_delay(1);
    input_reset_sense();

    do {
        input_sense();
        fp_23D90();

        if(key_det & INPUT_CANCEL) {
            if(pause()) {
                quit = Q_QUIT_TO_OP;
            }
        }

        std_update();
        midboss_activate_if_stage_frame_is_midboss_start_frame();
        stage_vm();

        if(bombing == false) {
            bg_render_not_bombing();
        } else {
            bg_render_bombing();
        }

        pointnums_update();
        circles_update();
        sparks_update();
        sub_10ABF();
        sub_104B6();
        bullets_update();
        enemies_update();
        midboss_update();
        boss_update();
        items_update();
        gather_update();
        stage_render();
        bomb_update_and_render();
        boss_fg_render();
        midboss_render();
        enemies_render();
        SHOTS_RENDER();
        player_render();
        grcg_setmode_rmw();
        gather_render();
        sparks_render();
        items_render();
        pointnums_render();
        bullets_render();
        circles_render();
        grcg_off();
        overlay1();
        overlay2();
        playfield_shake_update_and_render();
        input_reset_sense();

        total_slow_frames += (vsync_Count1 >= slowdown_factor);
        total_frames++;
        slowdown_frame_delay();

        palette_changed
            ? (void)(palette_show(), palette_changed = false)
            : (void)0;

        sub_CCD6();
        graph_accesspage(page_front);
        graph_showpage(page_back);
        page_front = page_back;
        page_back ^= 1;
        snd_se_update();
        frames_unused++;

        // Shared TH04/TH05 compiler-visible frame-counter dataflow.
        _AX = stage_frame;
        _DX = _AX++;
        stage_frame = _AX;
        _AX &= 15;
        stage_frame_mod16 = _AL;
        stage_frame_mod8 = (_AL &= 7);
        stage_frame_mod4 = (_AL &= 3);
        stage_frame_mod2 = (_AL &= 1);

        int frames_per_playperf_raise = resident->rem_lives;
        frames_per_playperf_raise = (frames_per_playperf_raise >= 10)
            ? 1000 : (6000 - (frames_per_playperf_raise * 500));
        ((stage_frame % frames_per_playperf_raise) == 0)
            ? (void)playperf_raise(1)
            : (void)0;

        score_update_and_render();
    } while(quit == Q_KEEP_RUNNING);
}
