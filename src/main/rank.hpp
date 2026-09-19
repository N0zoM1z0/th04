#ifndef TH04_MAIN_RANK_HPP
#define TH04_MAIN_RANK_HPP

#include "src/shared/platform/abi.hpp"

typedef enum {
	RANK_EASY,
	RANK_NORMAL,
	RANK_HARD,
	RANK_LUNATIC,

#if ((GAME != 1) && (GAME != 3))
	RANK_EXTRA,
#endif

	RANK_COUNT,

#if (GAME >= 4)
	RANK_SHOW_SETUP_MENU = 0xFF,
#endif

	_rank_t_FORCE_INT16 = 0x7FFF
} rank_t;

#define RANKS_CAPS { 	"EASY", "NORMAL", "HARD", "LUNATIC" }

#define RANKS_CAPS_CENTERED { 	" EASY ", 	"NORMAL", 	" HARD ", 	"LUNATIC" }

extern unsigned char rank;

extern "C" {
int TH04_PASCAL select_for_rank(
	int for_easy, int for_normal, int for_hard, int for_lunatic
);
}

#endif
