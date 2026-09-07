#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "th04/sprites/main_pat.h"
#ifndef TH04_ELLY_MAIN034_COMBINED
#include "th04/main/bullet/bullet.hpp"
#endif
#include "th04/main/boss/boss.hpp"

#pragma option -a

#endif

extern "C" void near elly_phase_burst(void)
{
    boss.mode = -1;
    boss.phase_frame = 0;
    bullet_template.angle = 0;
    bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
    bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
    bullet_template.speed.v = TO_SP(2);
    bullet_template.group = BG_RING_AIMED;
    bullet_template.count = 48;
    bullet_template_tune();
    bullets_add_regular_fixedspeed();
}
