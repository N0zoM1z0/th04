#pragma option -zCMAIN_035_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/gaiji/gaiji.h"
#include "th04/resident.hpp"
#include "th04/main/rank.hpp"
#include "th04/main/score.hpp"

#pragma codeseg MAIN_035_TEXT main_03
#pragma option -a

extern unsigned char power;
extern unsigned int dream_score;
extern unsigned char stage_point_items_collected;
extern unsigned char continues_used;
extern unsigned char boss_phase_state;
extern unsigned char stage_id;
extern unsigned int stage_graze;
extern unsigned char extends_gained;
extern unsigned long score_delta;
extern unsigned int __cdecl PaletteTone;

extern "C" void pascal far playperf_raise(char delta);
extern "C" void pascal far playperf_lower(char delta);
extern "C" void far hud_bombs_put(void);

extern const char far *STAGE_CLEAR_BONUS_DESC[];
extern const char gpCLEAR_BONUS[];
extern const char gpCONGRATULATION[];
extern const char aBONUS_STAGE[];
extern const char aPOWERX50[];
extern const char aBONUS_DREAM[];
extern const char aGRAZEX50[];
extern const char aBONUS_POINT[];
extern const char aBONUS_TOTAL[];
extern const char aBOMB_EXTEND[];
extern const char aALL_CLEAR[];
extern const char aPOWERX50_2[];
extern const char aBONUS_DREAM_2[];
extern const char aGRAZEX50_2[];
extern const char aPLAYER_REM_10000[];
extern const char aPLAYER_REM_30000[];
extern const char aBONUS_POINT_2[];
extern const char aBONUS_TOTAL_2[];

static void pascal near stage_bonus_value_put(int y, unsigned long value)
{
    char buf[9];
    unsigned long divisor = 1000000UL;
    unsigned long digit;
    register int i = 0;
    register int started = 0;

    while(divisor > 1) {
        digit = (value / divisor);
        value %= divisor;
        started |= (int)digit;
        if(started != 0) {
            buf[i] = (char)digit + gb_0;
        } else {
            buf[i] = g_EMPTY;
        }
        divisor /= 10;
        i++;
    }
    buf[6] = (char)value + gb_0;
    buf[7] = gb_0;
    buf[8] = 0;
    gaiji_putsa(34, y, buf, TX_WHITE);
}

extern "C" void pascal far stage_bonus_count_put(int left, int y, unsigned int value)
{
    register unsigned int divisor = 10000;
    register int i = 0;
    char buf[6];
    unsigned int digit;
    unsigned int started = 0;

    while(divisor > 1) {
        digit = (value / divisor);
        value %= divisor;
        started |= digit;
        if(started != 0) {
            buf[i] = (char)digit + gb_0;
        } else {
            buf[i] = g_EMPTY;
        }
        divisor /= 10;
        i++;
    }
    buf[4] = (char)value + gb_0;
    buf[5] = 0;
    gaiji_putsa(left, y, buf, TX_WHITE);
}

static void pascal near stage_bonus_factor_apply(
    int y, int desc, int factor, unsigned long far *points
)
{
    int color;
    *points *= factor;
    *points /= 10UL;
    color = ((factor < 10) ? TX_RED : TX_GREEN);
    text_putsa(6, y, STAGE_CLEAR_BONUS_DESC[desc], color);
}

static void pascal near stage_bonus_apply_modifiers(unsigned long far *points)
{
    if(boss_phase_state == 0) {
        stage_bonus_factor_apply(20, 0, 0, points);
        return;
    }

    switch(resident->credit_lives) {
    case 6: stage_bonus_factor_apply(18, 1, 3, points); break;
    case 5: stage_bonus_factor_apply(18, 2, 5, points); break;
    case 4: stage_bonus_factor_apply(18, 3, 7, points); break;
    }

    switch(continues_used) {
    case 1: stage_bonus_factor_apply(19, 4, 8, points); break;
    case 2: stage_bonus_factor_apply(19, 5, 6, points); break;
    case 3: stage_bonus_factor_apply(19, 6, 4, points); break;
    }

    switch(rank) {
    case RANK_EASY:    stage_bonus_factor_apply(20, 7, 5, points); break;
    case RANK_NORMAL:  stage_bonus_factor_apply(20, 8, 10, points); break;
    case RANK_HARD:    stage_bonus_factor_apply(20, 9, 12, points); break;
    case RANK_LUNATIC: stage_bonus_factor_apply(20, 10, 14, points); break;
    }
}

void near stage_clear_bonus(void)
{
    unsigned long points;
    unsigned long points_before_modifiers;
    register unsigned int value;

    PaletteTone = 60;
    palette_show();
    gaiji_putsa(20, 4, gpCLEAR_BONUS, TX_WHITE);
    text_putsa(6, 7, aBONUS_STAGE, TX_WHITE);
    text_putsa(6, 9, aPOWERX50, TX_WHITE);
    text_putsa(6, 11, aBONUS_DREAM, TX_WHITE);
    text_putsa(6, 13, aGRAZEX50, TX_WHITE);
    text_putsa(6, 16, aBONUS_POINT, TX_WHITE);
    text_putsa(6, 21, aBONUS_TOTAL, TX_WHITE);
    text_putsa(6, 22, aBOMB_EXTEND, (TX_YELLOW + TX_BLINK));

    value = ((resident->stage * 100) + 100);
    points = value;
    stage_bonus_value_put(7, value);

    value = (power * 5);
    points += value;
    stage_bonus_value_put(9, value);

    value = dream_score;
    points += value;
    stage_bonus_value_put(11, value);

    value = (stage_graze * 5);
    points += value;
    stage_bonus_value_put(13, value);

    value = stage_point_items_collected;
    points *= value;
    stage_bonus_count_put(40, 16, value);

    points_before_modifiers = points;
    stage_bonus_apply_modifiers(&points);
    stage_bonus_value_put(21, points);
    score_delta += points;

    if(points_before_modifiers >= 1200000UL) {
        playperf_raise(4);
    } else if(points_before_modifiers >= 800000UL) {
        playperf_raise(2);
    } else if(points_before_modifiers >= 500000UL) {
        playperf_raise(1);
    } else if(points_before_modifiers <= 100000UL) {
        playperf_lower(2);
    } else if(points_before_modifiers <= 200000UL) {
        playperf_lower(1);
    }

    resident->rem_bombs++;
    hud_bombs_put();
    if(resident->miss_count <= stage_id) {
        playperf_raise(2);
    }
    if(resident->bombs_used <= (stage_id * 2)) {
        playperf_raise(2);
    }
}

void near stage_allclear_bonus(void)
{
    unsigned long points;
    register unsigned int value;

    PaletteTone = 60;
    palette_show();
    extends_gained = 10;
    gaiji_putsa(19, 4, gpCONGRATULATION, TX_WHITE);
    text_putsa(6, 6, aALL_CLEAR, TX_WHITE);
    text_putsa(6, 8, aPOWERX50_2, TX_WHITE);
    text_putsa(6, 10, aBONUS_DREAM_2, TX_WHITE);
    text_putsa(6, 12, aGRAZEX50_2, TX_WHITE);
    if(rank != RANK_EXTRA) {
        text_putsa(6, 14, aPLAYER_REM_10000, TX_WHITE);
    } else {
        text_putsa(6, 14, aPLAYER_REM_30000, TX_WHITE);
    }
    text_putsa(6, 17, aBONUS_POINT_2, TX_WHITE);
    text_putsa(6, 21, aBONUS_TOTAL_2, TX_WHITE);

    value = 1000;
    points = value;
    stage_bonus_value_put(6, value);

    value = (power * 5);
    points += value;
    stage_bonus_value_put(8, value);

    value = dream_score;
    points += value;
    stage_bonus_value_put(10, value);

    value = (stage_graze * 5);
    points += value;
    stage_bonus_value_put(12, value);

    if(rank != RANK_EXTRA) {
        value = ((resident->rem_lives * 1000) - 1000);
    } else {
        value = ((resident->rem_lives * 3000) - 3000);
    }
    points += value;
    stage_bonus_value_put(14, value);

    value = stage_point_items_collected;
    points *= value;
    stage_bonus_count_put(40, 17, value);

    stage_bonus_apply_modifiers(&points);
    stage_bonus_value_put(21, points);
    score_delta += points;
}

#pragma codeseg
