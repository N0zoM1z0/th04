#pragma option -zCEND_TEXT -zPmain_01

#include "src/shared/hardware/graphics.hpp"
#include "th04/end/end.h"
#include "src/shared/config/resident.hpp"
#include "th04/snd/snd.h"

int pascal GameExecl(const char *binary_fn);
#pragma samecodeseg GameExecl

extern const char maine_binary[];

void far end_game_good(void)
{
	// MAINE dispatches its Ending/credits/registration route from this resident
	// value after MAIN has published run statistics in GameExecl().
    resident->end_sequence = ES_GOOD;
    resident->end_type_ascii = '0';
    snd_kaja_func(KAJA_SONG_FADE, 4);
    palette_black_out(16);
    GameExecl(maine_binary);
}

void far end_game_bad(void)
{
	// end_type_ascii selects the bad-ending script variant consumed by MAINE.
    resident->end_sequence = ES_BAD;
    resident->end_type_ascii = '1';
    snd_kaja_func(KAJA_SONG_FADE, 4);
    palette_black_out(16);
    GameExecl(maine_binary);
}

void far end_extra(void)
{
	// Extra has its own MAINE branch and does not consume end_type_ascii.
    resident->end_sequence = ES_EXTRA;
    snd_kaja_func(KAJA_SONG_FADE, 4);
    palette_black_out(16);
    GameExecl(maine_binary);
}
