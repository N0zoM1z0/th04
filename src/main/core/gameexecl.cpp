#pragma option -zCMAIN_TEXT -zPmain_01

// TH04 executable-chain path.
// Target relocation topology binds FAR GameExecl() to a separate TC4J producer.

#include <process.h>
#include "platform.h"
#include "src/shared/runtime/api.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/config/resident.hpp"
#include "th04/hardware/input.h"
#include "th04/main/null.hpp"
#include "th04/main/score.hpp"
#include "th04/main/ems.hpp"
#include "th04/main/quit.hpp"
#include "th04/main/frames.h"
#include "th04/main/item/item.hpp"
#include "th04/main/stage/stage.hpp"
#include "th04/main/hiscore.hpp"
#include "th04/end/end.h"
#include "th04/snd/snd.h"

extern unsigned char gameover_fade_frame;
extern unsigned char continues_used;
extern unsigned char power;
extern unsigned char dream_items_collected;
extern nearfunc_t_near overlay1;
extern unsigned int __cdecl PaletteTone;
extern unsigned int enemies_gone;
extern unsigned int enemies_killed;
extern unsigned int max_valued_point_items;

extern const char gGAMEOVER[];
extern const char gCONTINUE_QUESTION[];
extern const char gYES[];
extern const char gNO[];
extern const char gCREDIT[];

void near overlay_wipe(void);
void near overlay_black(void);
void pascal far frame_delay(int frames);
void far end_game_bad(void);
#pragma samecodeseg end_game_bad

extern "C" void pascal near hud_score_put(void);
void near score_reset(void);
void far hud_lives_put(void);
void far hud_bombs_put(void);
void far shot_level_update(void);
extern "C" int pascal ems_free(unsigned handle);
#pragma samecodeseg hud_lives_put
#pragma samecodeseg hud_bombs_put
#pragma samecodeseg shot_level_update

extern "C" void pascal near bb_txt_free(void);
void pascal cdg_free_all(void);
void far bb_boss_free(void);
void near dialog_free(void);
extern "C" void pascal near bb_playchar_free(void);
void near std_free(void);
void near map_free(void);
void game_exit(void);

int pascal GameExecl(const char *binary_fn);
#pragma samecodeseg GameExecl
#define next_program_fn binary_fn

static const unsigned int GAMEOVER_GLYPH_G = 0xB0;
static const unsigned char POWER_MIN_VALUE = 1;
extern char gameover_erase_in[];
extern char gameover_erase_out[];
extern char maine_binary[];

void near game_state_save_score(void);

int pascal GameExecl(const char *binary_fn)
{
	// The resident block outlives MAIN. Publish the score and run counters before
	// freeing any gameplay storage so MAINE can render its verdict and OP can
	// retain the next random seed/configuration state.
    game_state_save_score();
    if(Ems) {
        ems_free(Ems);
    }
    resident->std_frames = total_std_frames;
    resident->items_spawned = items_spawned;
    resident->items_collected = items_collected;
    resident->point_items_collected = total_point_items_collected;
    resident->max_valued_point_items_collected = max_valued_point_items;
    resident->enemies_gone = enemies_gone;
    resident->enemies_killed = enemies_killed;
    resident->slow_frames = total_slow_frames;
    resident->frames = total_frames;

	// Release owners from the most specific gameplay allocations out to the
	// process-wide archive, display and input/sound services. In particular, do
	// not release the resident segment: ZUN.COM owns it across DOS overlays.
    bb_txt_free();
    cdg_free_all();
    bb_boss_free();
    dialog_free();
    bb_playchar_free();
    std_free();
    map_free();
    super_free();
    graph_hide();
    text_clear();
    gaiji_restore();
    game_exit();

	// On success DOS replaces this process, so the return value exists only for
	// execl() failure. Both argv[0] and the executable path use the same name.
    return execl(
		(char *)next_program_fn, (char *)next_program_fn, NULL
	);
}
