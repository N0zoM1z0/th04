#pragma option -zCSCORE_TEXT

#include "th04/formats/scoredat/scoredat.hpp"
#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th01/rank.h"
#if (GAME == 5)
#include "compat/rec98/th05/playchar.h"
#else
#include "th04/playchar.h"
#endif
#include "th04/gaiji/gaiji.h"

static const int SCORE_INITIAL_DIGIT = ((GAME == 5) ? 6 : 5);

void near scoredat_recreate(void)
{
	int i;
	int place;

	// ZUN bloat
#if (GAME == 5)
	#define c place
#else
	int c;
#endif

	// ACTUAL TYPE: gaiji_th04_t
	unsigned char digit = (gb_0 + 10 - (10 / SCOREDAT_PLACES));

	for(i = 0; i < SCOREDAT_PLACES; i++) {
		hi.score.cleared = SCOREDAT_NOT_CLEARED;
		for(c = 0; c < SCORE_DIGITS; c++) {
			hi.score.g_score[i].digits[c] = gb_0;
		}

		if(i == 0) {
			hi.score.g_score[i].digits[SCORE_INITIAL_DIGIT - 0] = gb_1;
		} else {
			hi.score.g_score[i].digits[SCORE_INITIAL_DIGIT - 1] = digit;

			// ZUN bloat: `digit -= (10 / SCOREDAT_PLACES);` would work for
			// both games.
#if (GAME == 4)
			static_assert(SCOREDAT_PLACES == 10);
			digit--;
#else
			digit -= (10 / SCOREDAT_PLACES);
#endif
		}

		// ZUN landmine: This assigns decreasing stage numbers even for TH05's
		// Extra Stage, which should default to a constant 1 according to the
		// loop below.
		// Classifying this as a landmine because it's impossible for the
		// MAINE.EXE version of this code to ever run within our criteria of
		// observability – OP.EXE will have always regenerated [SCOREDAT_FN] if
		// it didn't exist or was corrupted, so this code can only ever run if
		// the file was somehow modified or deleted from outside the game while
		// it was running.
#if ((GAME == 5) && (BINARY == 'E'))
		hi.score.g_stage[i] = (gb_6 - i);
#elif (GAME == 4)
		hi.score.g_stage[i] = (gb_5 - (i / 2));
#endif

		for(c = 0; c < SCOREDAT_NAME_LEN; c++) {
			hi.score.g_name[i][c] = gs_DOT;
		}
		hi.score.g_name[i][SCOREDAT_NAME_LEN] = g_NULL;
	}

	#undef c

#if (BINARY != 'O')
	#undef SCOREDAT_FN
	extern const char SCOREDAT_FN[];
#endif
	file_create(SCOREDAT_FN);
	for(i = 0; i < (RANK_COUNT * PLAYCHAR_COUNT); i++) {
#if ((GAME == 5) && (BINARY == 'O'))
		for(place = 0; place < SCOREDAT_PLACES; place++) {
			if((i % RANK_COUNT) == RANK_EXTRA) {
				hi.score.g_stage[place] = gb_1;
			} else {
				hi.score.g_stage[place] = (gb_1 + SCOREDAT_PLACES - place);
			}
		}
#endif
		// Well, OK, if you like to fully obfuscate the format by giving every
		// section its own encraption key...
		scoredat_encode_func();
		file_write(&hi, sizeof(hi));
		scoredat_decode_func();
	}
	file_close();
}

// This file is probably the prime reason why you'd rather want to work on the
// `debloated` or `anniversary` branches instead.

#if (GAME == 5)
#include "compat/rec98/th05/playchar.h"
typedef int playchar2;
#else
#if ((GAME == 4) && (BINARY == 'M'))
#include "th04/resident.hpp"
#endif
#include "th04/playchar.h"
typedef playchar_t playchar2;
#endif

// ZUN bloat: Take [rank] as a parameter instead.
extern unsigned char rank;

#if ((GAME == 4) && (BINARY == 'M'))
#define recreated
#define loaded
// Loads the score data for the current resident player character at the global
// [rank] into [hi], recreating the defaults if necessary.
// ZUN bloat: Completely redundant.
void near hiscore_scoredat_load_for_cur(void)
#else
#define recreated true
#define loaded false
#if (GAME == 4) && (BINARY == 'O')
// Loads the score data for both characters at the global [rank] into [hi] and
// [hi2]. Returns `false` if the data was loaded and decoded correctly, or
// `true` if the defaults were recreated.
// ZUN bloat: Shouldn't exist. Give the regular version a `scoredat_section_t&`
// parameter and call it twice.
bool near hiscore_scoredat_load_both(void)
#else
// Loads the score data for the given [playchar] at the global [rank] into
// [hi]. Returns `false` if the data was loaded and decoded correctly, or
// `true` if the defaults were recreated.
// ZUN bloat: Use the regular `playchar_t` type.
bool pascal near hiscore_scoredat_load_for(playchar2 playchar)
#endif
#endif
{
#if (BINARY == 'O')
	#define SCOREDAT_FN_0 SCOREDAT_FN
	#define SCOREDAT_FN_1 SCOREDAT_FN
#else
	extern const char SCOREDAT_FN_0[];
	extern const char SCOREDAT_FN_1[];
#endif

	// ZUN bloat: Classic TOCTOU issue; file_ropen() also fails if the file
	// doesn't exist. Doesn't have any consequences in this case though: In the
	// very unlikely event that the file stops existing between file_exist()
	// and file_ropen(), the following will happen:
	// • All file-related calls will fail and leave old score data in [hi] and
	//   [hi2].
	// • scoredat_decode() re-decodes already decoded data and fails.
	// • The code then recreates score data just as it would have if the file
	//   hadn't existed in this initial check.
	// Hence, this is not a landmine, just bloat.
	if(file_exist(SCOREDAT_FN_0)) {
		file_ropen(SCOREDAT_FN_1);

		// ZUN bloat: The TH05 version is correct for both games and all
		// binaries.
#if (GAME == 5)
		file_seek(
			(((playchar * RANK_COUNT) + rank) * sizeof(scoredat_section_t)),
			SEEK_SET
		);
#else
		file_seek((rank * sizeof(scoredat_section_t)), SEEK_SET);
#if (BINARY == 'M')
		if(resident->playchar_ascii == ('0' + PLAYCHAR_MARISA)) {
			file_seek((RANK_COUNT * sizeof(scoredat_section_t)), SEEK_CUR);
		}
#elif (BINARY == 'E')
		if(playchar != PLAYCHAR_REIMU) {
			file_seek((RANK_COUNT * sizeof(scoredat_section_t)), SEEK_CUR);
		}
#endif
#endif
		file_read(&hi, sizeof(scoredat_section_t));
#if (GAME == 4) && (BINARY == 'O')
		file_seek(((RANK_COUNT - 1) * sizeof(scoredat_section_t)), SEEK_CUR);
		file_read(&hi2, sizeof(scoredat_section_t));
#endif
		file_close();

		// ZUN landmine: In TH04, scoredat_recreate() only writes to [hi] and
		// leaves [hi2] as it is. TH04's High Score viewer in OP.EXE uses both
		// sections and doesn't double-check whether it contains valid data,
		// because why should it, this is our job. But this means that it will
		// render garbage data in both cases:
		//
		// • If Reimu/[hi] is corrupt, scoredat_decode() exits early and
		//   doesn't decode [hi2]. The call site assumes that it got decoded,
		//   though, and consequently renders garbage. The fact that [hi]
		//   receives the default data from scoredat_recreate() doesn't even
		//   matter because the corruption from [hi2] will most likely mess up
		//   the entire screen.
		//
		// • If Marisa/[hi2] is corrupt, [hi2] did get decoded, but still
		//   carries the same garbage data that failed decoding.
		//
		// Both sections then only get loaded correctly on the next call to
		// this function.
		if(scoredat_decode_func() != 0) {
			scoredat_recreate();
			return recreated;
		}
	} else {
		// Same TH04 landmine as above.
		scoredat_recreate();
		return recreated;
	}
	return loaded;
}

// Leaves [hi] in encoded state.
void near hiscore_scoredat_save(void)
{
	#undef SCOREDAT_FN
	#define SCOREDAT_FN SCOREDAT_FN_2
	extern const char SCOREDAT_FN[];

	scoredat_encode_func();

	file_append(SCOREDAT_FN);

	// ZUN bloat: The TH05 version is correct for both games and all binaries.
#if (GAME == 5)
	file_seek(
		(((playchar * RANK_COUNT) + rank) * sizeof(scoredat_section_t)),
		SEEK_SET
	);
#else
	file_seek((rank * sizeof(scoredat_section_t)), SEEK_SET);
#if (BINARY == 'M')
	if(resident->playchar_ascii == ('0' + PLAYCHAR_MARISA)) {
		file_seek((RANK_COUNT * sizeof(scoredat_section_t)), SEEK_CUR);
	}
#else
	if(playchar != PLAYCHAR_REIMU) {
		file_seek((RANK_COUNT * sizeof(scoredat_section_t)), SEEK_CUR);
	}
#endif
#endif
	file_write(&hi, sizeof(scoredat_section_t));

#if (BINARY == 'E')
	// Re-encode the entire score file with newly randomized encraption keys.
	// ZUN bloat: Could have been its own function, and not thrashed [hi].
	for(int i = 0; i < ((RANK_COUNT * PLAYCHAR_COUNT)); i++) {
		file_seek((i * sizeof(scoredat_section_t)), SEEK_SET);
		file_read(&hi, sizeof(scoredat_section_t));
		scoredat_decode_func();
		scoredat_encode_func();
		file_seek((i * sizeof(scoredat_section_t)), SEEK_SET);
		file_write(&hi, sizeof(scoredat_section_t));
	}
#endif
	file_close();
}

#include "th04/main/hiscore.hpp"
#include "th04/main/score.hpp"
#include "th04/main/stage/stage.hpp"
#include "th04/main/slowdown.hpp"
#include "th04/common.h"

void near hiscore_continue_enter_raw(void)
{
	struct hack {
		gaiji_th04_t x[8];
	};
	extern struct hack gCONTINUE_;

	int c;
	int i;

	// ZUN bloat: Not `static`, gets needlessly copied into a local variable.
	const struct hack gCONTINUE = gCONTINUE_;

	// ZUN bloat: Could have been local.
	extern uint8_t entered_place;

	for(i = (SCOREDAT_PLACES - 1); i >= 0; i--) {
		for(c = (SCORE_DIGITS - 1); c >= 0; c--) {
			// ZUN bug: The subtraction causes C to promote the right-hand side
			// of these comparisons to `int`, which leads to the same overflow
			// issue that causes the rendering bug in the High Score viewer. In
			// this instance, gaiji-offsetted digits ≥96 that overflowed to 0
			// will get interpreted as negative. And since any un-offsetted
			// [score] is larger than a negative digit, it always gets sorted
			// into the list *above* such an overflowed score, thus gradually
			// pushing the latter out of the list with each new call to this
			// function.
			// This bug reinforces the High Score viewer's soft score limit of
			// 959,999,999, or `A9 A9 A9 A9 A9 A9 A9 FF` in the gaiji-offsetted
			// [hi.score] list.
			// TH05 fixes this bug by subtracting and comparing unsigned bytes
			// instead.
			if(score.digits[c] > (hi.score.g_score[i].digits[c] - gb_0)) {
				break;
			}
			if(score.digits[c] < (hi.score.g_score[i].digits[c] - gb_0)) {
				goto found_place;
			}
		}
	}
	entered_place = 0;
	goto shift;

found_place:
	if(i == (SCOREDAT_PLACES - 1)) {
		entered_place = -1; // ZUN bloat
		return;
	}
	entered_place = (i + 1);

	// ZUN bloat: How about memcpy()? The next three inner loops perform a
	// total of 24 multiplications and 16 bit shifts.
shift:
	for(i = (SCOREDAT_PLACES - 2); i >= entered_place; i--) {
		for(c = (SCOREDAT_NAME_LEN - 1); c >= 0; c--) {
			hi.score.g_name[i + 1][c] = hi.score.g_name[i][c];
		}
		for(c = (SCORE_DIGITS - 1); c >= 0; c--) {
			hi.score.g_score[i + 1].digits[c] = hi.score.g_score[i].digits[c];
		}
		hi.score.g_stage[i + 1] = hi.score.g_stage[i];
	}

	static_assert(sizeof(gCONTINUE) == SCOREDAT_NAME_LEN);
	for(c = (SCOREDAT_NAME_LEN - 1); c >= 0; c--) {
		hi.score.g_name[entered_place][c] = gCONTINUE.x[c];
	}

	for(c = (SCORE_DIGITS - 1); c >= 0; c--) {
		hi.score.g_score[entered_place].digits[c] = (score.digits[c] + gb_0);
	}

	if(stage_id != STAGE_EXTRA) {
		hi.score.g_stage[entered_place] = (gb_1 + stage_id);
	} else {
		hi.score.g_stage[entered_place] = gb_1;
	}

	hiscore_scoredat_save();
}

void near hiscore_continue_enter(void)
{
	hiscore_scoredat_load_for_cur();
	if(turbo_mode) {
		hiscore_continue_enter_raw();
	}
}

void near hiscore_load(void)
{
	hiscore_scoredat_load_for_cur();
	for(int i = 0; i < SCORE_DIGITS; i++) {
		hiscore.digits[i] = (hi.score.g_score[0].digits[i] - gb_0);
	}
}
