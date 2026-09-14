#pragma option -zCDEMO_TEXT -zPmain_01

// TH04 stage/demo session setup and per-stage runtime state initialization.
// Target evidence binds both logical functions to one physical TC4J object.

#include "platform.h"
#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/playchar.h"
#include "th04/resident.hpp"
#include "th04/snd/snd.h"
#include "th04/main/stage/stage.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/frames.h"
#include "th04/main/player/bomb.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/playfld.hpp"
#include "th04/main/dialog/dialog.hpp"
#include "th04/formats/map.hpp"
#include "th04/formats/dialog.hpp"
#include "compat/rec98/th03/formats/cdg.h"

extern unsigned char page_front;
extern unsigned char page_back;
extern unsigned char power;
typedef void (near *callback_cdecl_t)(void);
extern callback_cdecl_t fp_23D90;
extern nearfunc_t_near overlay1;
extern nearfunc_t_near overlay2;
extern unsigned int __cdecl PaletteTone;

extern "C" void near demo_input_null(void);
extern "C" void pascal near nullfunc_near(void);
void near overlay_wipe(void);
void near overlay_black(void);
void pascal near overlay_stage_enter_update_and_render(void);
extern "C" void pascal near tiles_fill_initial(void);
void pascal near tiles_render_all(void);
void far tiles_activate(void);
#pragma samecodeseg tiles_activate
void near tiles_invalidate_reset(void);
extern "C" int pascal near mpn_load(const char *fn);
void near std_load(void);
void near gameplay_session_init(void);
void near demo_load(void);
void near DemoPlay(void);
void near sub_12024(void);
void near stage_runtime_init(void);
void near eyecatch_animate(void);
void far midboss_reset(void);
void near bomb_bg_load__ems_preload_playchar_cdgs(void);
extern "C" void pascal near bb_playchar_load(void);
void far hud_put(void);
void pascal near stage4_render(void);

void far stage1_setup(void);
void far stage2_setup(void);
void far stage3_setup(void);
void far stage4_setup(void);
void far stage5_setup(void);
void far stage6_setup(void);
void far stagex_setup(void);


extern unsigned int tile_ring_scroll_row_prev;
extern unsigned char scroll_row_advance_current;
extern unsigned char scroll_row_advance_previous;
extern unsigned int player_state_unknown_0;
extern unsigned int player_state_unknown_1;
extern unsigned int player_state_unknown_2;
extern unsigned int player_state_unknown_3;
extern unsigned char player_miss_animation_frame;


extern unsigned char miss_time;
extern bool player_is_hit;
extern unsigned char player_invincibility_time;
// The target defines this as a byte. The historical ReC98 header used an int.
extern unsigned char stage_point_items_collected;
extern unsigned char dream_items_collected;
extern nearfunc_t_near bg_render_bombing_func;
extern "C" void near stage_state_init(void);
void near shot_cycle_reset(void);
void far shot_level_update(void);
#pragma samecodeseg shot_level_update
void near randring_fill(void);
void far items_init(void);
void near bomb_state_reset(void);
extern "C" void near sparks_init(void);
extern "C" void pascal near hud_score_put(void);
void far thicklasers_init(void);
extern "C" void pascal near pointnums_init(void);
#pragma samecodeseg hud_put

extern int load_playchar_resources;
extern unsigned int stage_faceset_count;
extern char eye_rgb[];
extern char miko_bft[];
extern char mari_bft[];
extern char mikod_bft[];
extern char miko32_bft[];
extern char miko16_bft[];
extern char bss0_cd2[];
extern char bss1_cd2[];
extern char bss2_cd2[];
extern char kao3_cd2[];
extern char kao2_cd2[];
extern char bss4_cd2[];
extern char bss5_cd2[];
extern char bss6_cd2[];
extern char st00_bft[];
extern char st01_bft[];
extern char st02_bft[];
extern char st03_bft[];
extern char st04_bft[];
extern char st05_bft[];
extern char st06_bft[];
extern char st00_mpn[];
extern char st10_mpn[];
extern char st01_mpn[];
extern char st02_mpn[];
extern char st03_mpn[];
extern char st04_mpn[];
extern char st05_mpn[];
extern char st06_mpn[];
extern char far *stage_bgm_name;

void near stage_session_init(void)
{
    load_playchar_resources = 0;
    vsync_Count2 = 0;
    stage_id = resident->stage;

    if((stage_id == 0) || (stage_id == 6)) {
        load_playchar_resources = 1;
        text_fillca(' ', TX_BLACK | TX_REVERSE);
        fp_23D90 = demo_input_null;
        gameplay_session_init();

        if(resident->demo_num != 0) {
            demo_load();
            stage_id = (resident->stage = resident->demo_stage);
            power = POWER_MAX;
            resident->stage_ascii = ('0' + stage_id);
            fp_23D90 = DemoPlay;
            random_seed = 318;
        }
    }

    sub_12024();
    graph_accesspage(0);
    graph_showpage(0);
    palette_entry_rgb(eye_rgb);
    palette_show();
    PaletteTone = 0;
    palette_show();
    sub_12024();
    overlay_wipe();
    stage_runtime_init();
    hud_put();
    eyecatch_animate();
    midboss_reset();

    if(load_playchar_resources != 0) {
        bomb_bg_load__ems_preload_playchar_cdgs();
        bb_playchar_load();
        if(playchar == PLAYCHAR_REIMU) {
            super_entry_bfnt(miko_bft);
        } else {
            super_entry_bfnt(mari_bft);
        }
        super_entry_bfnt(mikod_bft);
        super_entry_bfnt(miko32_bft);
        super_entry_bfnt(miko16_bft);
        for(int i = 20; i < 120; i++) {
            super_convert_tiny(i);
        }
    }

    stage_bgm_name[2] = '0';
    stage_bgm_name[3] = resident->stage_ascii;

    switch(stage_id) {
    case 0:
        stage_faceset_count = 9;
        cdg_load_all(8, bss0_cd2);
        stage_bgm_name[2] = resident->playchar_ascii;
        super_entry_bfnt(st00_bft);
        stage1_setup();
        if(resident->playchar_ascii == ('0' + PLAYCHAR_REIMU)) {
            mpn_load(st00_mpn);
        } else {
            mpn_load(st10_mpn);
        }
        break;

    case 1:
        stage_faceset_count = 9;
        cdg_load_all(8, bss1_cd2);
        super_entry_bfnt(st01_bft);
        stage2_setup();
        mpn_load(st01_mpn);
        break;

    case 2:
        stage_faceset_count = 9;
        cdg_load_all(8, bss2_cd2);
        super_entry_bfnt(st02_bft);
        stage3_setup();
        mpn_load(st02_mpn);
        break;

    case 3:
        stage_faceset_count = 9;
        if(playchar == PLAYCHAR_REIMU) {
            cdg_load_all(8, kao3_cd2);
        } else {
            cdg_load_all(8, kao2_cd2);
        }
        super_entry_bfnt(st03_bft);
        stage4_setup();
        mpn_load(st03_mpn);
        stage_render = stage4_render;
        break;

    case 4:
        stage_faceset_count = 9;
        cdg_load_all(8, bss4_cd2);
        super_entry_bfnt(st04_bft);
        stage5_setup();
        mpn_load(st04_mpn);
        break;

    case 5:
        stage_faceset_count = 9;
        super_entry_bfnt(st05_bft);
        cdg_load_all(8, bss5_cd2);
        stage6_setup();
        mpn_load(st05_mpn);
        break;

    case 6:
        stage_faceset_count = 9;
        super_entry_bfnt(st06_bft);
        cdg_load_all(8, bss6_cd2);
        stagex_setup();
        mpn_load(st06_mpn);
        break;
    }

    map_load();
    std_load();
    dialog_load();
    tiles_fill_initial();
    graph_accesspage(0);
    while(vsync_Count2 < 0x80) {
    }
    palette_black_out(1);
    PaletteTone = 100;
    palette_show();
    overlay_black();
    tiles_render_all();
    page_back = 1;
    page_front = 0;
    graph_accesspage(1);
    graph_showpage(0);
    tiles_render_all();

    if(resident->demo_num == 0) {
        snd_load(stage_bgm_name, SND_LOAD_SONG);
        snd_kaja_func(KAJA_SONG_PLAY, 0);
    }

    tiles_activate();
    overlay1 = overlay_stage_enter_update_and_render;
    overlay2 = nullfunc_near;
}


void near stage_runtime_init(void)
{
    stage_state_init();
    stage_frame = 0;
    bombing_disabled = false;
    scroll_line = 0;
    tile_ring_scroll_row_prev = 0;
    scroll_line_on_page[0] = 0;
    scroll_line_on_page[1] = 0;
    scroll_subpixel_line.v = 0;
    scroll_row_advance_current = 0;
    scroll_row_advance_previous = 0;
    playfield_shake_x = 0;
    playfield_shake_y = 0;
    player_pos.cur.x.v = (192 * 16);
    player_pos.cur.y.v = (320 * 16);
    player_pos.prev.x.v = (192 * 16);
    player_pos.prev.y.v = (320 * 16);
    player_state_unknown_0 = 0x40;
    player_state_unknown_1 = 0x40;
    player_state_unknown_2 = 0x30;
    player_state_unknown_3 = 0x30;
    player_miss_animation_frame = 0;
    miss_time = 0;
    player_is_hit = false;
    player_invincibility_time = 64;
    stage_point_items_collected = 0;
    dream_items_collected = 0;
    std_update = std_update_frames_then_animate_dialog_and_activate_boss_if_done;
    scroll_active = true;
    shot_cycle_reset();
    shot_level_update();
    randring_fill();
    items_init();
    bomb_state_reset();
    sparks_init();
    hud_score_put();
    thicklasers_init();
    pointnums_init();
    hud_put();
    bg_render_bombing_func = tiles_render_all;
    tiles_invalidate_reset();
}

#include "th04/sprites/main_cdg.h"

void far bb_boss_free(void);
void near dialog_free(void);
void near std_free(void);
void near map_free(void);

extern "C" void near stage_session_free(void)
{
    bb_boss_free();
    dialog_free();
    std_free();
    map_free();
    super_clean(128, 256);
    for(int i = CDG_FACESET_BOSS; i < (CDG_COUNT - 1); i++) {
        cdg_free(i);
    }
}

#include "th04/hardware/input.h"
extern char gsCHUUDAN[];
extern char gsSAIKAI[];
extern char gsSHUURYOU[];
extern char aGAME_PAUSE_SPACES_1[];
extern char aGAME_PAUSE_SPACES_2[];
extern char aGAME_PAUSE_SPACES_3[];
extern "C" int near pause(void)
{
    int selected = 0;
    while(key_det != INPUT_NONE) { input_reset_sense(); }
    gaiji_putsa(26, 12, gsCHUUDAN, TX_YELLOW);
    gaiji_putsa(26, 14, gsSAIKAI, (TX_WHITE + TX_UNDERLINE));
    gaiji_putsa(26, 15, gsSHUURYOU, TX_YELLOW);
    while(1) {
        input_wait_for_change(0);
        if((key_det & INPUT_UP) || (key_det & INPUT_DOWN)) {
            selected = 1 - selected;
            if(selected == 0) {
                gaiji_putsa(26, 14, gsSAIKAI, (TX_WHITE + TX_UNDERLINE));
                gaiji_putsa(26, 15, gsSHUURYOU, TX_YELLOW);
            } else {
                gaiji_putsa(26, 14, gsSAIKAI, TX_YELLOW);
                gaiji_putsa(26, 15, gsSHUURYOU, (TX_WHITE + TX_UNDERLINE));
            }
        }
        if(key_det & INPUT_Q) return 1;
        if(key_det & INPUT_CANCEL) { selected = 0; break; }
        if((key_det & INPUT_SHOT) || (key_det & INPUT_OK)) break;
    }
    while(key_det != INPUT_NONE) { input_reset_sense(); }
    text_putsa(26, 12, aGAME_PAUSE_SPACES_1, TX_WHITE);
    text_putsa(26, 14, aGAME_PAUSE_SPACES_2, TX_WHITE);
    text_putsa(26, 15, aGAME_PAUSE_SPACES_3, TX_WHITE);
    return selected;
}
