#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -zCMAIN_034_TEXT -zPmain_03

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

extern "C" void near elly_phase_ring(void)
{
    elly_orbit_update();
    elly_orbit_frame++;
    if(boss.phase_frame == 16) {
        elly_scythe_init();
    }
    if(boss.phase_frame > 16) {
        if((boss.phase_frame % 16) == 0) {
            bullet_template.angle = 0;
            bullet_template.spawn_type = BST_PELLET;
            bullet_template.speed.v = TO_SP(2);
            bullet_template.group = BG_RING_AIMED;
            bullet_template.count = 8;
            bullets_add_regular();
        }
        if(elly_scythe_mode == 0) {
            boss.mode = -1;
            boss.phase_frame = 0;
        }
    }
}
