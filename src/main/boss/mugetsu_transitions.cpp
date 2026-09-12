#ifndef TH04_MUGETSU_MAIN033_COMBINED
#pragma option -a
#pragma option -zCMAIN_033_TEXT -zPmain_03
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"
#endif

extern int mugetsu_gather_frame_offset;
extern SPPoint mugetsu_anchor;
extern "C" void near mugetsu_gather_intro(void);

extern "C" unsigned char near mugetsu_1812A(void)
{
    mugetsu_gather_frame_offset = 0;
    mugetsu_gather_intro();

    switch(boss.phase_frame) {
    case 34:
        boss.sprite = 0;
        boss.pos.cur.x.v = mugetsu_anchor.x.v;
        boss.pos.cur.y.v = mugetsu_anchor.y.v;
        break;
    case 32: case 38: boss.sprite = 135; break;
    case 30: case 40: boss.sprite = 134; break;
    case 28: case 42: boss.sprite = 133; break;
    case 26: case 44: boss.sprite = 132; break;
    case 24: case 46: boss.sprite = 131; break;
    case 16: case 48: boss.sprite = 129;
    }

    if(boss.phase_frame < 48) {
        goto ret0;
    }
    if(boss.phase_frame < 64) {
        if(boss.phase_frame == 32) {
            snd_se_play(8);
        }
        if(stage_frame_mod2 != 0) {
            boss.sprite = 130;
            goto ret0;
        }
        boss.sprite = 129;
        goto ret0;
    }
    if(boss.phase_frame == 64) {
        boss.sprite = 128;
        return 1;
    }
    if(boss.phase_frame < 144) {
        return 2;
    }
    return 3;
ret0:
    return 0;
}

extern "C" unsigned char near mugetsu_1821E(void)
{
    mugetsu_gather_frame_offset = -80;
    mugetsu_gather_intro();

    switch(boss.phase_frame) {
    case 34:
        boss.sprite = 0;
        boss.pos.cur.x.v = mugetsu_anchor.x.v;
        boss.pos.cur.y.v = mugetsu_anchor.y.v;
        break;
    case 32: case 38: boss.sprite = 135; break;
    case 30: case 40: boss.sprite = 134; break;
    case 28: case 42: boss.sprite = 133; break;
    case 26: case 44: boss.sprite = 132; break;
    case 24: case 46: boss.sprite = 131; break;
    case 16: case 48: boss.sprite = 129;
    }

    if(boss.phase_frame < 48) {
        goto ret0;
    }
    if(boss.phase_frame < 128) {
        if(boss.phase_frame == 48) {
            snd_se_play(8);
        }
        if(stage_frame_mod2 != 0) {
            boss.sprite = 130;
            goto ret0;
        }
        boss.sprite = 129;
        goto ret0;
    }
    if(boss.phase_frame == 128) {
        boss.sprite = 128;
        return 1;
    }
    if(boss.phase_frame < 192) {
        return 2;
    }
    return 3;
ret0:
    return 0;
}
