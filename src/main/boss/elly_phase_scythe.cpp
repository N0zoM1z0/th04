#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -a
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "th04/main/boss/boss.hpp"

#endif

extern unsigned char elly_scythe_mode;
extern "C" void near elly_scythe_init(void);

extern "C" void near elly_phase_scythe(void)
{
    if(boss.phase_frame == 32) {
        elly_scythe_init();
    }
    if((boss.phase_frame > 32) && (elly_scythe_mode == 0)) {
        boss.mode = -1;
        boss.phase_frame = 0;
    }
}
