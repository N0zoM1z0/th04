#ifndef TH04_MAIN_PLAYCHAR_HPP
#define TH04_MAIN_PLAYCHAR_HPP

#include "src/shared/platform/abi.hpp"

#if (GAME == 5)
typedef enum {
	PLAYCHAR_REIMU = 0,
	PLAYCHAR_MARISA = 1,
	PLAYCHAR_MIMA = 2,
	PLAYCHAR_YUUKA = 3,
	PLAYCHAR_COUNT = 4,

	_playchar_t_FORCE_UINT8 = 0xFF
} playchar_t;
#else
typedef enum {
	PLAYCHAR_REIMU = 0,
	PLAYCHAR_MARISA = 1,
	PLAYCHAR_COUNT = 2
} playchar_t;

typedef enum {
	SHOTTYPE_A = 0,
	SHOTTYPE_B = 1,
	SHOTTYPE_COUNT,
} shottype_t;

// Used way too often...
inline playchar_t playchar_other(playchar_t playchar) {
	return static_cast<playchar_t>(PLAYCHAR_MARISA - playchar);
}
#endif

extern playchar_t playchar;

#if (GAME == 5)
// Present only in the four-character game variant that also compiles a subset
// of the maintained TH04 translation units during replay calibration.
int TH04_PASCAL select_for_playchar(
	int for_reimu, int for_marisa, int for_mima, int for_yuuka
);
#endif

#endif
