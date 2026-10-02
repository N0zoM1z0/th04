#include <string.h>

#include "src/shared/platform/types.hpp"
#include "src/shared/config/resident.hpp"
#include "src/shared/formats/cdg.hpp"
#include "src/shared/formats/pi.hpp"
#include "src/op/formats/cdg_put_nocolors.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/input.hpp"
#include "src/shared/hardware/putsa.hpp"
#include "src/shared/sound/api.hpp"
#include "src/op/title/cdg_slots.hpp"

typedef void (near pascal *near menu_render_t)(int, vc2);
extern menu_render_t menu_unput_and_put;
extern int8_t menu_sel;
extern int8_t in_option;
extern int8_t main_menu_unused_1;
extern bool quit;
extern bool extra_unlocked;
extern const char far *MENU_DESC[26];

void pascal near menu_sel_update_and_render(int8_t max, int8_t direction);
void near start_game(void);
void near start_extra(void);
void near regist_view_menu(void);
void near musicroom_menu(void);
void near main_cdg_load(void);
void near start_demo(void);
void far pascal egc_copy_rect_1_to_0_16(int, int, int, int);

enum main_choice_t {
    MC_GAME, MC_EXTRA, MC_REGIST_VIEW, MC_MUSICROOM, MC_OPTION, MC_QUIT,
    MC_COUNT
};
enum option_choice_t {
    OC_RANK, OC_LIVES, OC_BOMBS, OC_BGM, OC_SE, OC_TURBO_OR_SLOW,
    OC_RESET, OC_QUIT, OC_COUNT
};
enum { RANK_EASY = 0, RANK_NORMAL = 1, RANK_LUNATIC = 3 };
enum { CFG_LIVES_DEFAULT = 3, CFG_LIVES_MAX = 6 };
enum { CFG_BOMBS_DEFAULT = 2, CFG_BOMBS_MAX = 2 };

static const int LABEL_W = 96;
static const int LABEL_H = 16;
static const int CURSOR_W = 32;
static const int MENU_TOP = 224;
static const int COMMAND_LEFT = (RES_X - LABEL_W) / 2;
static const int COMMAND_H = LABEL_H + 4;
static const int COMMAND_CURSOR_LEFT_LEFT = COMMAND_LEFT - CURSOR_W / 2;
static const int COMMAND_CURSOR_RIGHT_LEFT = COMMAND_LEFT + LABEL_W - CURSOR_W / 2;
static const int COMMAND_CURSOR_LEFT_RIGHT_DISTANCE =
    COMMAND_CURSOR_RIGHT_LEFT - COMMAND_CURSOR_LEFT_LEFT;
static const int MENU_MAIN_LEFT = COMMAND_CURSOR_LEFT_LEFT;
static const int MENU_MAIN_W = COMMAND_CURSOR_RIGHT_LEFT + CURSOR_W - MENU_MAIN_LEFT;
static const int MENU_OPTION_LEFT = (RES_X - LABEL_W * 2) / 2;
static const int OPTION_LABEL_LEFT = MENU_OPTION_LEFT;
static const int OPTION_VALUE_LEFT = OPTION_LABEL_LEFT + LABEL_W;
static const int OPTION_CURSOR_LEFT_LEFT = OPTION_LABEL_LEFT;
static const int OPTION_CURSOR_RIGHT_LEFT = OPTION_VALUE_LEFT + LABEL_W - CURSOR_W;
static const int MENU_OPTION_W = OPTION_CURSOR_RIGHT_LEFT + CURSOR_W - MENU_OPTION_LEFT;
static const int DESC_TOP = RES_Y - GLYPH_H;
static const vc2 COL_INACTIVE = 1;
static const vc2 COL_ACTIVE = 8;
static const vc2 COL_LOCKED = 12;
static const vc2 COL_DESC = 15;
static const char MENU_MAIN_BG_FN[] = "op1.pi";
static const char BGM_MENU_MAIN_FN[] = "op";

inline screen_y_t main_choice_top(int sel) { return MENU_TOP + sel * COMMAND_H; }
inline screen_y_t option_choice_top(option_choice_t sel) {
    return (sel >= OC_QUIT)
        ? MENU_TOP + OC_RESET * LABEL_H + (sel - OC_RESET) * COMMAND_H
        : MENU_TOP + sel * LABEL_H;
}

#define command_put(top, slot) cdg_put_nocolors_8(COMMAND_LEFT, top, slot)
#define option_label_put(sel, slot) \
    cdg_put_nocolors_8(OPTION_LABEL_LEFT, option_choice_top(sel), slot)
#define option_value_put(sel, slot) \
    cdg_put_nocolors_8(OPTION_VALUE_LEFT, option_choice_top(sel), slot)
#define desc_unput_and_put(desc_id) { \
    egc_copy_rect_1_to_0_16(0, DESC_TOP, RES_X, GLYPH_H); \
    graph_putsa_fx_func = FX_WEIGHT_BOLD; \
    graph_putsa_fx(RES_X - GLYPH_FULL_W - strlen(MENU_DESC[desc_id]) * GLYPH_HALF_W, \
                    DESC_TOP, COL_DESC, MENU_DESC[desc_id]); \
}

#define menu_update_vertical(input, count) { \
    if((input) & INPUT_UP) menu_sel_update_and_render((count) - 1, -1); \
    if((input) & INPUT_DOWN) menu_sel_update_and_render((count) - 1, 1); \
}
#define menu_init(initialized, allowed, count, render, left, width, bottom) { \
    allowed = false; \
    egc_copy_rect_1_to_0_16(left, MENU_TOP, (width) + 32, \
                             (bottom) + 24 - MENU_TOP); \
    for(int i = 0; i < (count); i++) { \
        render(i, (menu_sel == i) ? COL_ACTIVE : COL_INACTIVE); \
    } \
    menu_unput_and_put = render; \
    initialized = true; \
    allowed = false; \
}
#define ring_inc_range(v, lo, hi) { if(++(v) > (hi)) (v) = (lo); }
#define ring_inc_ge_range(v, lo, hi) ring_inc_range(v, lo, hi)
#define ring_dec_range(v, lo, hi) { if((v) == (lo)) (v) = (hi) + 1; --(v); }

inline void return_from_other_screen_to_main(bool& initialized, int sel) {
    graph_accesspage(1);
    pi_fullres_load_palette_apply_put_free(0, MENU_MAIN_BG_FN);
    graph_copy_page(0);
    palette_100();
    initialized = false;
    in_option = false;
    menu_sel = sel;
}

inline void return_from_option_to_main(bool& initialized) {
    initialized = false;
    menu_sel = MC_OPTION;
    in_option = false;
}

inline void snd_redetermine_modes_and_restart_bgm(bool) {
    snd_kaja_func(KAJA_SONG_STOP, 0);
    snd_determine_modes(resident->bgm_mode, resident->se_mode);
    snd_load(BGM_MENU_MAIN_FN, SND_LOAD_SONG);
    snd_kaja_func(KAJA_SONG_PLAY, 0);
}

#pragma codeseg OP_NATIVE_TEXT OP_NATIVE_01
#include "src/op/main/main_unput_and_put.inl"
#include "src/op/main/option_unput_and_put.inl"
#include "src/op/main/main_update_and_render.inl"
#include "src/op/main/option_update_and_render.inl"
#pragma codeseg
