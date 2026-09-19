#pragma option -G
#pragma option -zCMAIN__TEXT -zPmain_01

#include "platform.h"
#include "src/shared/hardware/graphics.hpp"
#include "th04/gaiji/gaiji.h"
#include "th04/main/score.hpp"
#include "src/shared/config/resident.hpp"
#include "th04/main/bullet/clearzap.hpp"
#include "th04/main/rank.hpp"
#include "th04/playchar.h"
#include "hud.hpp"
#pragma option -a2

#define HUD_LEFT 56
#define BAR_MAX 128

extern unsigned long score_delta_frame;
extern unsigned char score_unused;
extern unsigned char hiscore_popup_shown;
extern unsigned char overlay_popup_id_new;
extern nearfunc_t_near overlay2;
void pascal near overlay_popup_update_and_render(void);
extern "C" void pascal far snd_se_play(int se);
extern const char hud_lives_extra[];
extern const char hud_bombs_extra[];
extern unsigned char stage_point_items_collected;
extern unsigned int dream_score;
extern unsigned int stage_graze;
extern unsigned char power;
extern unsigned char shot_level;
extern hud_colors10_t HUD_POWER_COLORS;
extern hud_colors5_t HUD_HP_COLORS;
extern hud_bar9_t gHUD_HP_BLANK;
extern hud_bar9_t hud_bar_max;
extern const gaiji_th04_t gsENEMY[], gsHISCORE[], gsSCORE[], gsREIGEKI[];
extern const gaiji_th04_t gsBOMB[], gsREIMU[], gsPLAYER[], gsREIRYOKU[];
extern const gaiji_th04_t gsPOWER[], glEASY[];
extern "C" void pascal far stage_bonus_count_put(unsigned x, unsigned y, unsigned value);
extern "C" void pascal near hud_score_put(void);
extern "C" void pascal far playperf_raise(char delta);
#pragma samecodeseg playperf_raise


extern "C" void pascal near score_extend_update_and_render(void)
{
    signed char extend = 0;
    switch(extends_gained) {
    case 0: if(score.digits[6] >= 3) { extend = 1; } break;
    case 1: if(score.digits[6] >= 8) { extend = 1; } break;
    case 2: if((score.digits[7] >= 1) && (score.digits[6] >= 5)) { extend = 1; } break;
    case 3: if((score.digits[7] >= 2) && (score.digits[6] >= 2)) { extend = 1; } break;
    case 4: if(score.digits[7] >= 3) { extend = 1; } break;
    }
    if(extend == 0) { return; }
    playperf_raise(4);
    extends_gained++;
    if(resident->rem_lives <= 99) {
        resident->rem_lives++;
        if(bullet_clear_time < 20) { bullet_clear_time = 20; }
        hud_lives_put();
        overlay_popup_id_new = 1;
        overlay2 = overlay_popup_update_and_render;
        snd_se_play(7);
    }
}

void near score_reset(void)
{
    register int i;
    for(i = 1; i < SCORE_DIGITS; i++) { score.digits[i] = 0; }
    score_delta = 0;
    score_delta_frame = 0;
    score_unused = 0;
    extends_gained = 0;
    hiscore_popup_shown = 0;
}

void far hud_lives_put(void)
{
    signed char value;
    signed char i;
    register int x;
    value = (resident->rem_lives - 1);
    if(value < 6) {
        i = 0;
        x = 62;
        while(i < value) {
            gaiji_putca(x, 13, gs_YINYANG, TX_WHITE);
            x += 2;
            i++;
        }
        while(i < 5) {
            gaiji_putca(x, 13, g_EMPTY, TX_WHITE);
            x += 2;
            i++;
        }
    } else {
        text_putsa(62, 13, hud_lives_extra, TX_WHITE);
        if(value >= 10) {
            gaiji_putca(68, 13, (0xA0 + (value / 10)), TX_WHITE);
            value %= 10;
        }
        gaiji_putca(70, 13, (0xA0 + value), TX_WHITE);
    }
}

void far hud_bombs_put(void)
{
    signed char value;
    signed char i = 0;
    register int x;
    if(resident->rem_bombs <= 5) {
        x = 62;
        value = resident->rem_bombs;
        while(i < value) {
            gaiji_putca(x, 11, gs_BOMB, TX_WHITE);
            x += 2;
            i++;
        }
        while(i < 5) {
            gaiji_putca(x, 11, g_EMPTY, TX_WHITE);
            x += 2;
            i++;
        }
    } else {
        value = resident->rem_bombs;
        text_putsa(62, 11, hud_bombs_extra, TX_WHITE);
        if(value >= 10) {
            gaiji_putca(68, 11, (0xA0 + (value / 10)), TX_WHITE);
            value %= 10;
        }
        gaiji_putca(70, 11, (0xA0 + value), TX_WHITE);
    }
}

extern "C" void pascal far hud_point_items_put(void)
{
    stage_bonus_count_put(62, 15, stage_point_items_collected);
}

extern "C" void pascal far hud_dream_put(void)
{
    stage_bonus_count_put(62, 17, dream_score * 10);
}

void far hud_graze_put(void)
{
    stage_bonus_count_put(62, 19, stage_graze);
}

extern "C" void pascal far hud_power_put(void)
{
    const hud_colors10_t colors = HUD_POWER_COLORS;
    hud_bar_put(22, power, colors.v[shot_level]);
}

void pascal far hud_hp_put(int bar_value)
{
    const hud_bar9_t blank = gHUD_HP_BLANK;
    const hud_colors5_t colors = HUD_HP_COLORS;
    if(bar_value != 0) {
        gaiji_putsa(61, 8, reinterpret_cast<const char *>(gsENEMY), TX_YELLOW);
        hud_bar_put(9, bar_value, colors.v[bar_value / 32]);
    } else {
        gaiji_putsa(61, 8, reinterpret_cast<const char *>(&blank.v[5]), TX_WHITE);
        gaiji_putsa(56, 9, reinterpret_cast<const char *>(blank.v), TX_WHITE);
    }
}

extern "C" void pascal far hud_bar_put(int y, int value, int atrb)
{
    int value_rem;
    const hud_bar9_t bar_max = hud_bar_max;
    hud_bar9_t bar_notfull;
    register int i;
    if(value >= BAR_MAX) {
        gaiji_putsa(HUD_LEFT, y, reinterpret_cast<const char *>(bar_max.v), atrb);
        return;
    }
    value_rem = value;
    value_rem -= 16;
    i = 0;
    while(value_rem > 0) {
        bar_notfull.v[i] = g_BAR_16W;
        value_rem -= 16;
        i++;
    }
    value_rem = ((value - 1) & 15);
    bar_notfull.v[i] = (0x20 + value_rem);
    for(++i; i <= 7; i++) {
        bar_notfull.v[i] = g_EMPTY;
    }
    bar_notfull.v[8] = 0;
    gaiji_putsa(HUD_LEFT, y, reinterpret_cast<const char *>(bar_notfull.v), atrb);
}

void far hud_put(void)
{
    gaiji_putsa(60, 3, reinterpret_cast<const char *>(gsHISCORE), TX_YELLOW);
    gaiji_putsa(61, 5, reinterpret_cast<const char *>(gsSCORE), TX_YELLOW);
    hud_score_put();
    if(resident->playchar_ascii == ('0' + PLAYCHAR_REIMU)) {
        gaiji_putsa(57, 11, reinterpret_cast<const char *>(gsREIGEKI), TX_YELLOW);
    } else {
        gaiji_putsa(57, 11, reinterpret_cast<const char *>(gsBOMB), TX_YELLOW);
    }
    hud_bombs_put();
    hud_lives_put();
    if(resident->playchar_ascii == ('0' + PLAYCHAR_REIMU)) {
        gaiji_putsa(57, 13, reinterpret_cast<const char *>(gsREIMU), TX_YELLOW);
    } else {
        gaiji_putsa(57, 13, reinterpret_cast<const char *>(gsPLAYER), TX_YELLOW);
    }
    gaiji_putca(58, 15, gs_TEN, TX_YELLOW);
    hud_point_items_put();
    gaiji_putca(58, 17, gs_YUME, TX_YELLOW);
    hud_dream_put();
    gaiji_putca(58, 19, gs_TAMA, TX_YELLOW);
    hud_graze_put();
    if(resident->playchar_ascii == ('0' + PLAYCHAR_REIMU)) {
        gaiji_putsa(62, 21, reinterpret_cast<const char *>(gsREIRYOKU), TX_YELLOW);
    } else {
        gaiji_putsa(62, 21, reinterpret_cast<const char *>(gsPOWER), TX_YELLOW);
    }
    hud_power_put();
    gaiji_putsa(
        57,
        23,
        (const char near *)&glEASY[rank * 8],
        ((rank == RANK_EASY) ? TX_GREEN :
         (rank == RANK_NORMAL) ? TX_CYAN :
         (rank == RANK_HARD) ? TX_MAGENTA : TX_RED)
    );
    hud_hp_put(0);
}
