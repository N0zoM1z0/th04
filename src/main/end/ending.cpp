#pragma option -zCEND_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/end/end.h"
#include "th04/resident.hpp"
#include "th04/snd/snd.h"

int pascal GameExecl(const char *binary_fn);
#pragma samecodeseg GameExecl

extern const char end_game_good_binary[];
extern const char end_game_bad_binary[];
extern const char end_extra_binary[];

void far end_game_good(void)
{
    resident->end_sequence = ES_GOOD;
    resident->end_type_ascii = '0';
    snd_kaja_func(KAJA_SONG_FADE, 4);
    palette_black_out(16);
    GameExecl(end_game_good_binary);
}

void far end_game_bad(void)
{
    resident->end_sequence = ES_BAD;
    resident->end_type_ascii = '1';
    snd_kaja_func(KAJA_SONG_FADE, 4);
    palette_black_out(16);
    GameExecl(end_game_bad_binary);
}

void far end_extra(void)
{
    resident->end_sequence = ES_EXTRA;
    snd_kaja_func(KAJA_SONG_FADE, 4);
    palette_black_out(16);
    GameExecl(end_extra_binary);
}
