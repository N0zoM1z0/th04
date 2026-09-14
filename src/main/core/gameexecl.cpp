#pragma option -zCMAIN_TEXT -zPmain_01

// TH04 executable-chain path.
// Target relocation topology binds FAR GameExecl() to a separate TC4J producer.

#include <process.h>
#include "platform.h"
#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/resident.hpp"
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
void near sub_EEB0(void);
extern "C" void far sub_EEE8(void);
extern "C" void far sub_EFA1(void);
void far shot_level_update(void);
extern "C" int pascal ems_free(unsigned handle);
#pragma samecodeseg sub_EEE8
#pragma samecodeseg sub_EFA1
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

static const unsigned int GAMEOVER_GLYPH_G = 0xB0;
static const unsigned char POWER_MIN_VALUE = 1;
extern char gameover_erase_in[];
extern char gameover_erase_out[];
extern char maine_binary[];

void near game_state_save_score(void);

int pascal GameExecl(const char *binary_fn)
{
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
    return execl((char *)binary_fn, (char *)binary_fn, NULL);
}
