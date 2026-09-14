#pragma option -zCMAIN_TEXT -zPmain_01

// TH04 game-over, continue, and score-save path.
// Target relocation topology binds these five near functions to one TC4J producer.

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

unsigned char near gameover_fade_in(void)
{
    unsigned char cel_num;
    if(gameover_fade_frame >= 0x24) {
        overlay_wipe();
        overlay1 = nullfunc_near;
        return 1;
    }
    if((gameover_fade_frame % 4) == 0) {
        cel_num = (gameover_fade_frame / 4);
        if(cel_num != 0) {
            for(int y = 1; y < 24; y++) {
                for(int x = 4; x < 52; x += 2) {
                    gaiji_putca(x, y, (0x40 - cel_num), TX_BLACK);
                }
            }
        }
    }
    gameover_fade_frame++;
    return 0;
}

unsigned char near gameover_fade_out(void)
{
    unsigned char cel_num;
    if(gameover_fade_frame == 0) {
        overlay_black();
        overlay1 = nullfunc_near;
        return 1;
    }
    gameover_fade_frame--;
    if((gameover_fade_frame % 4) == 0) {
        cel_num = (gameover_fade_frame / 4);
        if(cel_num != 0) {
            for(int y = 1; y < 24; y++) {
                for(int x = 4; x < 52; x += 2) {
                    gaiji_putca(x, y, (0x40 - cel_num), TX_BLACK);
                }
            }
        }
    }
    return 0;
}

unsigned char near gameover_continue_menu(void);

unsigned char near gameover_run(void)
{
    int y;
    if(stage_id == 5) {
        end_game_bad();
    }
    gameover_fade_frame = 0x20;
    while(1) {
        if(gameover_fade_out()) {
            break;
        }
        frame_delay(1);
    }
    PaletteTone = 50;
    palette_show();
    while(1) {
        if(gameover_fade_in()) {
            break;
        }
        frame_delay(1);
    }
    for(y = 0x32; y > 8; y -= 2) {
        gaiji_putca(y, 12, GAMEOVER_GLYPH_G, TX_WHITE);
        frame_delay(1);
        text_putsa(y, 12, gameover_erase_in, TX_WHITE);
    }
    for(y = 8; y < 0x14; y += 2) {
        gaiji_putca(y, 12, GAMEOVER_GLYPH_G, TX_WHITE);
        frame_delay(1);
        text_putsa(y, 12, gameover_erase_out, TX_WHITE);
    }
    gaiji_putsa(20, 12, gGAMEOVER, TX_WHITE);
    input_wait_for_change(0);
    overlay_wipe();
    y = gameover_continue_menu();
    gameover_fade_frame = 0x20;
    while(1) {
        if(gameover_fade_out()) {
            break;
        }
        frame_delay(1);
    }
    if(y == Q_KEEP_RUNNING) {
        PaletteTone = 100;
        palette_show();
        while(1) {
            if(gameover_fade_in()) {
                break;
            }
            frame_delay(1);
        }
        overlay_wipe();
    } else {
        resident->end_sequence = ES_SCORE;
        snd_kaja_func(KAJA_SONG_FADE, 4);
        palette_black_out(4);
        GameExecl(maine_binary);
    }
    return static_cast<unsigned char>(y);
}

unsigned char near gameover_continue_menu(void)
{
    unsigned char atrb;
    unsigned char credits;
    int selected;
    int previous_input;

    if(stage_id == 6) {
        return 1;
    }
    selected = 0;
    previous_input = 1;
    credits = (3 - continues_used);
    if(credits == 0) {
        return 1;
    }

    gaiji_putsa(19, 10, gCONTINUE_QUESTION, TX_WHITE);
    gaiji_putsa(24, 13, gYES, (TX_GREEN | TX_REVERSE));
    gaiji_putsa(25, 15, gNO, TX_WHITE);
    gaiji_putsa(19, 22, gCREDIT, TX_GREEN);
    gaiji_putca(33, 22, (0xA0 + credits), TX_GREEN);
    input_reset_sense();

    for(;;) {
        input_sense();
        if(previous_input == 0) {
            previous_input = key_det;
            if((previous_input & INPUT_UP) || (previous_input & INPUT_DOWN)) {
                selected = (1 - selected);
                if(selected == 0) {
                    atrb = (TX_GREEN | TX_REVERSE);
                } else {
                    atrb = TX_WHITE;
                }
                gaiji_putsa(24, 13, gYES, atrb);
                if(selected == 1) {
                    atrb = (TX_GREEN | TX_REVERSE);
                } else {
                    atrb = TX_WHITE;
                }
                gaiji_putsa(25, 15, gNO, atrb);
            }
            if(previous_input & INPUT_CANCEL) {
                selected = 1;
                break;
            }
            if(previous_input & INPUT_OK) {
                break;
            }
            if(previous_input & INPUT_SHOT) {
                break;
            }
        } else {
            previous_input = key_det;
        }
        input_reset_sense();
        frame_delay(1);
    }

    if(selected == 0) {
        hiscore_continue_enter();
        power = POWER_MIN_VALUE;
        dream_items_collected = 0;
        resident->rem_bombs = resident->credit_bombs;
        resident->rem_lives = resident->credit_lives;
        shot_level_update();
        sub_EEE8();
        sub_EFA1();
        continues_used++;
        sub_EEB0();
        hud_score_put();
        return Q_KEEP_RUNNING;
    }
    return 1;
}

void near game_state_save_score(void)
{
    for(int i = 0; i < SCORE_DIGITS; i++) {
        resident->score_last.digits[i] = score.digits[i];
    }
}
