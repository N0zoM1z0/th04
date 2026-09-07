#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "th04/main/frames.h"
#include "th04/sprites/main_pat.h"
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

extern "C" void near elly_phase_orbit(void)
{
    elly_orbit_update();
    elly_orbit_frame++;
    if(boss.phase_frame == 16) {
        elly_scythe_init();
        bullet_template.angle = -0x40;
    }
    if(boss.phase_frame > 16) {
        if(stage_frame_mod16 == 0) {
            bullet_template.spawn_type = BST_BULLET16;
            bullet_template.patnum = PAT_BULLET16_D_YELLOW;
            bullet_template.speed.v = TO_SP(3);
            bullet_template.group = BG_SPREAD;
            bullet_template.count = 5;
            bullet_template.delta.spread_angle = 0x10;
            bullet_template_tune();
            bullets_add_regular();
            bullet_template.angle -= 0x10;
        }
        if(elly_scythe_mode == 0) {
            boss.mode = -1;
            boss.phase_frame = 0;
        }
    }
}
