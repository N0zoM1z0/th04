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

inline void resident_set_demo(int stage, int playchar, int shottype) {
    resident->playchar_ascii = '0' + playchar;
    resident->stage_ascii = '0' + stage;
    resident->shottype = shottype;
    resident->demo_stage = stage;
}

inline void op_exit_into_main(bool fade_out_bgm, bool allow_debug) {
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
    if(!allow_debug || !resident->debug) {
        execl(BINARY_MAIN, BINARY_MAIN, nullptr);
    } else {
        execl(BINARY_DEB, BINARY_DEB, nullptr);
    }
}

#pragma codeseg OP_NATIVE_TEXT OP_NATIVE_01
#include "src/op/main/start_demo.inl"
#pragma codeseg
