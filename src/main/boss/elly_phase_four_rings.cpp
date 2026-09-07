#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "th04/snd/snd.h"
#include "compat/rec98/th03/math/randring.hpp"
#ifndef TH04_ELLY_MAIN034_COMBINED
#include "th04/main/bullet/bullet.hpp"
#endif
#include "th04/main/boss/boss.hpp"

#pragma option -a

#endif

extern "C" unsigned char near elly_gather_update(void);
extern "C" void near elly_phase_burst(void);

extern "C" void near elly_phase_four_rings(void)
{
    switch(elly_gather_update()) {
    case 0:
        break;
    case 2:
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.speed.v = TO_SP(2);
        bullet_template.group = BG_RING;
        bullet_template.count = 16;

        bullet_template.angle = randring2_next16();
        bullet_template.origin.x.v -= TO_SP(32);
        bullet_template_tune();
        bullets_add_regular();

        bullet_template.angle = randring2_next16();
        bullet_template.origin.x.v += TO_SP(64);
        bullets_add_regular();

        bullet_template.angle = randring2_next16();
        bullet_template.origin.x.v -= TO_SP(32);
        bullet_template.origin.y.v -= TO_SP(32);
        bullets_add_regular();

        bullet_template.angle = randring2_next16();
        bullet_template.origin.y.v += TO_SP(64);
        bullets_add_regular();
        snd_se_play(9);
        break;
    default:
        return;
    }

    if(boss.phase_frame >= 80) {
        elly_phase_burst();
    }
}
