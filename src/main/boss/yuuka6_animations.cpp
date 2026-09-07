#ifndef TH04_YUUKA6_MAIN034_COMBINED
#pragma option -a
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "th04/sprites/main_pat.h"
#include "th04/main/boss/boss.hpp"
#endif

extern unsigned char yuuka6_sprite_flag;
extern int yuuka6_anim_frame;

enum yuuka6_sprite_anim_flag_t {
    Y6SF_VANISHED = 0,
    Y6SF_PARASOL_BACK_OPEN = 1,
    Y6SF_PARASOL_BACK_CLOSED = 2,
    Y6SF_PARASOL_FORWARD = 3,
    Y6SF_PARASOL_LEFT = 4,
    Y6SF_PARASOL_SHIELD = 8,
};

extern "C" bool near yuuka6_anim_parasol_back_close(void)
{
    yuuka6_sprite_flag = Y6SF_PARASOL_BACK_OPEN;
    yuuka6_anim_frame++;
    switch(yuuka6_anim_frame) {
    case 1: boss.sprite = PAT_YUUKA6_PARASOL_BACK_OPEN; break;
    case 7: boss.sprite = PAT_YUUKA6_PARASOL_BACK_HALFOPEN; break;
    case 13: boss.sprite = PAT_YUUKA6_PARASOL_BACK_HALFCLOSED; break;
    case 19: boss.sprite = PAT_YUUKA6_PARASOL_BACK_CLOSED; break;
    case 25:
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_PARASOL_BACK_CLOSED;
        return true;
    }
    return false;
}

extern "C" bool near yuuka6_anim_parasol_back_open(void)
{
    yuuka6_sprite_flag = Y6SF_PARASOL_BACK_CLOSED;
    yuuka6_anim_frame++;
    switch(yuuka6_anim_frame) {
    case 1: boss.sprite = PAT_YUUKA6_PARASOL_BACK_CLOSED; break;
    case 7: boss.sprite = PAT_YUUKA6_PARASOL_BACK_HALFCLOSED; break;
    case 13: boss.sprite = PAT_YUUKA6_PARASOL_BACK_HALFOPEN; break;
    case 19: boss.sprite = PAT_YUUKA6_PARASOL_BACK_OPEN; break;
    case 25:
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_PARASOL_BACK_OPEN;
        return true;
    }
    return false;
}

extern "C" bool near yuuka6_anim_parasol_back_pull_forward(void)
{
    yuuka6_anim_frame++;
    switch(yuuka6_anim_frame) {
    case 1: boss.sprite = PAT_YUUKA6_PARASOL_BACK_CLOSED; break;
    case 7: boss.sprite = PAT_YUUKA6_PARASOL_LEFT_PULL; break;
    case 13: boss.sprite = PAT_YUUKA6_PARASOL_LEFT_FORWARD_PULL; break;
    case 19: boss.sprite = PAT_YUUKA6_PARASOL_FORWARD_CLOSED; break;
    case 25:
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_PARASOL_FORWARD;
        return true;
    }
    return false;
}

extern "C" bool near yuuka6_anim_parasol_back_pull_left(void)
{
    yuuka6_anim_frame++;
    switch(yuuka6_anim_frame) {
    case 1: boss.sprite = PAT_YUUKA6_PARASOL_BACK_CLOSED; break;
    case 7: boss.sprite = PAT_YUUKA6_PARASOL_LEFT_PULL; break;
    case 13: boss.sprite = PAT_YUUKA6_PARASOL_LEFT; break;
    case 19:
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_PARASOL_LEFT;
        return true;
    }
    return false;
}

extern "C" bool near yuuka6_anim_parasol_left_spin_back(void)
{
    yuuka6_anim_frame++;
    switch(yuuka6_anim_frame) {
    case 1: boss.sprite = PAT_YUUKA6_PARASOL_LEFT; break;
    case 4: boss.sprite = PAT_YUUKA6_PARASOL_LEFT_FORWARD_PULL; break;
    case 7: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_0; break;
    case 10: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_1; break;
    case 13: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_2; break;
    case 16: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_3; break;
    case 19: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_4; break;
    case 22: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_5; break;
    case 25: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_6; break;
    case 28: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_7; break;
    case 31: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_8; break;
    case 34: boss.sprite = PAT_YUUKA6_PARASOL_SPIN_BACK_9; break;
    case 37: boss.sprite = PAT_YUUKA6_PARASOL_BACK_CLOSED; break;
    case 40:
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_PARASOL_BACK_CLOSED;
        return true;
    }
    return false;
}

extern "C" bool near yuuka6_anim_vanish(void)
{
    yuuka6_anim_frame++;
    switch(yuuka6_anim_frame) {
    case 1: boss.sprite = PAT_YUUKA6_VANISH_0; break;
    case 8: boss.sprite = PAT_YUUKA6_VANISH_1; break;
    case 15: boss.sprite = PAT_YUUKA6_VANISH_2; break;
    case 22: boss.sprite = PAT_YUUKA6_VANISH_3; break;
    case 29: boss.sprite = 0; break;
    case 36:
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_VANISHED;
        return true;
    }
    return false;
}

extern "C" bool near yuuka6_anim_appear(void)
{
    yuuka6_anim_frame++;
    switch(yuuka6_anim_frame) {
    case 1: boss.sprite = PAT_YUUKA6_VANISH_3; break;
    case 8: boss.sprite = PAT_YUUKA6_VANISH_2; break;
    case 15: boss.sprite = PAT_YUUKA6_VANISH_1; break;
    case 22: boss.sprite = PAT_YUUKA6_VANISH_0; break;
    case 29: boss.sprite = PAT_YUUKA6_PARASOL_BACK_OPEN; break;
    case 36:
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_PARASOL_BACK_OPEN;
        return true;
    }
    return false;
}

extern "C" bool near yuuka6_anim_parasol_shield(void)
{
    yuuka6_anim_frame++;
    switch(yuuka6_anim_frame) {
    case 1: boss.sprite = PAT_YUUKA6_PARASOL_BACK_OPEN; break;
    case 7: boss.sprite = PAT_YUUKA6_PARASOL_SHIELD_0; break;
    case 13: boss.sprite = PAT_YUUKA6_PARASOL_SHIELD_1; break;
    case 19:
        yuuka6_anim_frame = 0;
        yuuka6_sprite_flag = Y6SF_PARASOL_SHIELD;
        return true;
    }
    return false;
}
