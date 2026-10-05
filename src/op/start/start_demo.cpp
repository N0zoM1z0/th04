#include <process.h>

#include "src/shared/platform/types.hpp"
#ifdef TH04P
#include "src/shared/runtime/api.hpp"
#endif
#include "src/shared/config/resident.hpp"
#include "src/shared/formats/pi.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/sound/api.hpp"

void near main_cdg_free(void);
void near cfg_save(void);
void game_exit(void);

enum { PLAYCHAR_REIMU = 0, PLAYCHAR_MARISA = 1 };
enum { SHOTTYPE_A = 0, SHOTTYPE_B = 1 };
static char BINARY_MAIN[] = "main";
static char BINARY_DEB[] = "deb";
#define GAMEPLAY_BINARY BINARY_MAIN
#define DEBUG_GAMEPLAY_BINARY BINARY_DEB

inline void resident_set_demo(int stage, int playchar, int shottype) {
	// stage_ascii selects the stage resources loaded by MAIN, while demo_stage
	// is copied into the live numeric stage after MAIN recognizes demo mode.
    resident->playchar_ascii = '0' + playchar;
    resident->stage_ascii = '0' + stage;
    resident->shottype = shottype;
    resident->demo_stage = stage;
}

inline void op_exit_into_main(bool fade_out_bgm, bool allow_debug) {
	// This is the demo counterpart of start_game()'s overlay handoff. Assets and
	// configuration belong to OP; the resident run contract belongs to ZUN.COM.
    main_cdg_free();
    cfg_save();
    gaiji_restore();
    if(fade_out_bgm) {
        snd_kaja_func(KAJA_SONG_FADE, 10);
    }
#ifdef TH04P
    // The native palette block belongs to OP; release it before DOS overlay.
    respal_free();
#endif
    game_exit();
    // A successful execl() replaces OP. The caller has no post-handoff work.
    if(!allow_debug || !resident->debug) {
        execl(GAMEPLAY_BINARY, GAMEPLAY_BINARY, nullptr);
    } else {
        execl(DEBUG_GAMEPLAY_BINARY, DEBUG_GAMEPLAY_BINARY, nullptr);
    }
}

#pragma codeseg OP_NATIVE_TEXT OP_NATIVE_01
#include "src/op/main/start_demo.inl"
#pragma codeseg
