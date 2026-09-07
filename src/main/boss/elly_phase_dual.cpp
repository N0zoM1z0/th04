#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "th04/snd/snd.h"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#ifndef TH04_ELLY_MAIN034_COMBINED
#include "th04/main/bullet/bullet.hpp"
#endif
#include "th04/main/boss/boss.hpp"

#pragma option -a

#endif

extern unsigned char elly_scythe_mode;
extern int elly_orbit_frame;
extern "C" void near elly_scythe_init(void);
extern "C" void near elly_orbit_update(void);

extern "C" void near elly_phase_dual(void)
{
    elly_orbit_update();
    elly_orbit_frame++;
    elly_orbit_update();
    elly_orbit_frame++;

    if(boss.phase_frame == 16) {
        elly_scythe_init();
        bullet_template.angle = 0x40;
        bullet_template.spawn_type = BST_BULLET16_CLOUD_FORWARDS;
        bullet_template.speed.v = TO_SP(4);
        bullet_template.group = BG_SINGLE_AIMED;
        bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
        bullet_template_tune();
    }

    if(boss.phase_frame > 16) {
        if(stage_frame_mod8 == 0) {
            bullets_add_regular();
            bullet_template.angle = -bullet_template.angle;
            bullets_add_regular();
            bullet_template.angle = (-bullet_template.angle - 3);
            snd_se_play(3);
        }
        if(elly_scythe_mode == 0) {
            boss.mode = -1;
            boss.phase_frame = 0;
        }
    }
}
