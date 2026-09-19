#ifndef TH04_MAIN_SPRITES_MAIN_PAT_HPP
#define TH04_MAIN_SPRITES_MAIN_PAT_HPP

// Pattern numbers consumed by maintained TH04 code that also retains a
// GAME==5 compiler-calibration branch. Keep only the actually used subset.
static const int PAT_EXPLOSION_BIG = 3;

#if (GAME == 5)
static const int PAT_BULLET16_D = 52;
static const int PAT_BULLET16_D_BLUE = PAT_BULLET16_D;
static const int PAT_BULLET16_D_BLUE_last = 67;
static const int PAT_BULLET16_D_GREEN = 68;
static const int PAT_BULLET16_D_GREEN_last = 83;
static const int PAT_BULLET16_V_RED = 84;
static const int PAT_BULLET16_V_RED_last = 115;
static const int PAT_BULLET16_V_BLUE = 116;
static const int PAT_BULLET_ZAP = 152;
static const int PAT_DECAY_PELLET = 156;
static const int PAT_DECAY_BULLET16 = 160;
static const int PAT_EXPLOSION_SMALL = 164;
#else
static const int PAT_EXPLOSION_SMALL = 68;

// The enclosing TH04 bullet/update.cpp translation unit keeps using these
// after the maintained prefix fragment.
static const int PAT_BULLET_ZAP = 72;
static const int PAT_DECAY_PELLET = 108;
static const int PAT_DECAY_BULLET16 = 112;
#endif

#endif
