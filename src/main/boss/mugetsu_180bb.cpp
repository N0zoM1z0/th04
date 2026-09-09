#pragma option -zCMAIN_033_TEXT -zPmain_03
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"

extern int mugetsu_gather_frame_offset;
extern "C" void near mugetsu_gather_intro(void);

extern "C" unsigned char near mugetsu_180BB(void)
{
    mugetsu_gather_frame_offset = 0x10;
    mugetsu_gather_intro();
    if(boss.phase_frame < 16) {
        goto ret0;
    }
    if(boss.phase_frame == 16) {
        goto sprite_129;
    }
    if(boss.sprite < 24) {
        goto ret0;
    }
    if(boss.phase_frame >= 48) {
        goto after_transition;
    }
    if(boss.phase_frame == 24) {
        snd_se_play(8);
    }
    if(stage_frame_mod2 != 0) {
        boss.sprite = 130;
        goto ret0;
    }

sprite_129:
    boss.sprite = 129;
    goto ret0;

after_transition:
    if(boss.phase_frame == 48) {
        boss.sprite = 128;
        return 1;
    }
    if(boss.phase_frame < 128) {
        return 2;
    }
    return 3;

ret0:
    return 0;
}
