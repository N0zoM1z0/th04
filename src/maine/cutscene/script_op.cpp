#include <ctype.h>

#include "src/maine/cutscene/state.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/input.hpp"
#include "src/shared/hardware/frame_delay.hpp"
#include "src/shared/hardware/putsa.hpp"
#include "src/shared/hardware/v_colors.hpp"
#include "src/shared/formats/pi.hpp"
#include "src/shared/sound/api.hpp"

static const screen_x_t BOX_LEFT = 80;
static const screen_y_t BOX_TOP = 320;
static const screen_y_t BOX_BOTTOM = 384;
static const screen_x_t CUTSCENE_PIC_LEFT = 0;
static const screen_y_t CUTSCENE_PIC_TOP = 64;
static const pixel_t CUTSCENE_PIC_W = 320;
static const pixel_t CUTSCENE_PIC_H = 200;
static const int CUTSCENE_PIC_SLOT = 0;
static const int TEXT_INTERVAL_DEFAULT = 1;
#ifndef PF_FN_LEN
static const int PF_FN_LEN = 13;
#endif
static const int PI_MASK_COUNT = 4;
static const int WEIGHT_BOLD = 2;

typedef unsigned int graph_putsa_fx_func_t;
enum script_ret_t { CONTINUE = 0, STOP = -1 };

#define box_wait_animate(frames) input_wait_for_change(frames)
#define str_sep_control_or_space(c) (iscntrl(c) || ((c) == ' '))

// The parameter readers themselves are TH04 CUTSCENE_TEXT owners. These
// adapters keep each command's default value in the original shared state.
#if defined(TH04P)
#pragma codeseg CUTSCENE_TEXT GROUP_01
#else
#pragma codeseg CUTSCENE_TEXT cutscene_01
#endif
void pascal near script_param_read_number_first(int& ret);
void pascal near script_param_read_number_second(int& ret);
inline void script_param_read_number_first(int& ret, int fallback) {
    script_param_number_default = fallback;
    script_param_read_number_first(ret);
}

#define script_param_read_fn(ret, length, c) { \
    for((length) = 0; (length) < (PF_FN_LEN - 1); (length)++) { \
        (c) = *script_p++; \
        if(str_sep_control_or_space(c)) break; \
        (ret)[length] = (c); \
    } \
    (ret)[length] = '\0'; \
}

#define script_op_fade(c, enter, leave, value) { \
    script_p++; \
    script_param_read_number_first(value, 1); \
    if((c) == 'i') enter(value); else leave(value); \
}

#define script_op_shake(skip, counter, duration) { \
    script_param_read_number_first(duration, 8); \
    for((counter) = 0; (counter) <= (duration); (counter)++) { \
        graph_scrollup(((counter) & 1) ? 4 : (RES_Y - 4)); \
        if(!(skip)) frame_delay(1); \
    } \
    graph_scrollup(0); \
}

#define script_op_bgm(stop_first, c, fn, length) { \
    (c) = *script_p; \
    if((c) == '$') { \
        script_p++; \
        snd_kaja_func(KAJA_SONG_STOP, 0); \
        if(stop_first) return CONTINUE; \
    } else if((c) == '*') { \
        script_p++; \
        snd_kaja_func(KAJA_SONG_PLAY, 0); \
        if(stop_first) return CONTINUE; \
    } else if((c) == ',') { \
        script_p++; \
        script_param_read_fn(fn, length, c); \
        if(stop_first) snd_kaja_func(KAJA_SONG_STOP, 0); \
        snd_load(fn, SND_LOAD_SONG); \
        snd_kaja_func(KAJA_SONG_PLAY, 0); \
    } \
}

#pragma warn -ccc
void near box_1_to_0_animate(void);
void near box_bg_put(void);
void near box_bg_allocate_and_snap(void);
void near cursor_advance_and_animate(void);
void pascal near pic_copy_to_other(screen_x_t left, vram_y_t top);
void pascal near pic_put_both_masked(screen_x_t left, vram_y_t top, int quarter, int mask_id);
void pascal pi_put_quarter_8(screen_x_t left, vram_y_t top, int slot, int quarter);

#include "src/maine/cutscene/script_op.inl"
#pragma codeseg
