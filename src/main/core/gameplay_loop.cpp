#pragma option -zCDEMO_TEXT -zPmain_01

// Maintained natural source for the reviewed DEMO_TEXT gameplay loop.
// Current production-profile TC4J codegen is intentionally recorded as nonexact.

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th01/hardware/grcg.hpp"
#include "th04/hardware/input.h"
#include "th04/resident.hpp"
#include "th04/main/frames.h"
#include "th04/main/slowdown.hpp"
#include "th04/main/quit.hpp"
#include "th04/main/playperf.hpp"
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

void pascal far frame_delay(unsigned int frames);
int near pause(void);
void far midboss_activate_if_stage_frame_is_midboss_start_frame(void);
void pascal near pointnums_update(void);
void near circles_update(void);
void near sparks_update(void);
void near sub_10ABF(void);
void near sub_104B6(void);
void far bullets_update(void);
void pascal far enemies_update(void);
void far items_update(void);
void far gather_update(void);
void near bomb_update_and_render(void);
void pascal near enemies_render(void);
void near shots_render(void);
void pascal near player_render(void);
void near grcg_setmode_rmw(void);
void far gather_render(void);
void near sparks_render(void);
void pascal near items_render(void);
void pascal near pointnums_render(void);
void pascal near bullets_render(void);
void near circles_render(void);
void near playfield_shake_update_and_render(void);
void near sub_CCD6(void);
void far snd_se_update(void);

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
        shots_render();
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

        if(palette_changed) {
            palette_show();
            palette_changed = false;
        }

        sub_CCD6();
        graph_accesspage(page_front);
        graph_showpage(page_back);
        page_front = page_back;
        page_back ^= 1;
        snd_se_update();
        frames_unused++;

        stage_frame++;
        stage_frame_mod16 = (stage_frame & 15);
        stage_frame_mod8 = (stage_frame_mod16 & 7);
        stage_frame_mod4 = (stage_frame_mod8 & 3);
        stage_frame_mod2 = (stage_frame_mod4 & 1);

        int frames_per_playperf_raise = resident->rem_lives;
        if(frames_per_playperf_raise >= 10) {
            frames_per_playperf_raise = 1000;
        } else {
            frames_per_playperf_raise = (6000 - (frames_per_playperf_raise * 500));
        }
        if((stage_frame % frames_per_playperf_raise) == 0) {
            playperf_raise(1);
        }

        score_update_and_render();
    } while(quit == Q_KEEP_RUNNING);
}
