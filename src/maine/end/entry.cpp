#include <stddef.h>

#include "src/shared/platform/types.hpp"
#include "src/shared/config/resident.hpp"
#include "src/shared/core/game_init.hpp"
#include "src/shared/formats/pi.hpp"
#include "src/shared/hardware/frame_delay.hpp"
#include "src/shared/hardware/input.hpp"
#include "src/shared/sound/api.hpp"

// MAINE's configuration loader installs the resident segment pointer.
resident_t far *resident;
extern size_t mem_assign_paras;

resident_t __seg *near cfg_load_resident_ptr(void);
void near end_animate(void);
void near staffroll_animate(void);
void near verdict_animate(void);
void near regist_menu(void);
void pascal near game_exit_and_exec(char far *fn);

// The three filenames occur in the attested MAINE load image. The first is
// encoded as bytes so host source encoding cannot change its Shift-JIS name.
static const unsigned char OP_AND_END_PF_FN[] = "\x8c\xb6\x91z\x8b\xbd" "ed.dat";
static const char GAIJI_FN[] = "GAMEFT.bft";
static char BINARY_OP[] = "op";
#define MENU_BINARY BINARY_OP

enum {
    RANK_EASY = 0,
    RANK_EXTRA = 4,
    ES_EXTRA = 0xFD,
    ES_BAD = 0xFE,
    ES_GOOD = 0xFF,
};

#define congratulations_animate(pic_fn) { \
    graph_accesspage(1); \
    pi_fullres_load_palette_apply_put_free(0, pic_fn); \
    graph_copy_page(0); \
    palette_black_in(1); \
    input_wait_for_change(0); \
    palette_black_out(4); \
}

inline void delay_then_regist_menu(void)
{
    frame_delay(100);
    regist_menu();
}

#if defined(TH04P)
#pragma codeseg MAINE_E_TEXT GROUP_01
#else
#pragma codeseg MAINE_E_TEXT maine_e_01
#endif
#include "src/maine/end/main.inl"
#pragma codeseg
