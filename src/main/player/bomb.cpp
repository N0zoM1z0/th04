#pragma option -zCMAIN__TEXT -zPmain_01
#include "x86real.h"
#include "src/shared/runtime/api.hpp"
#include "compat/rec98/th04/formats/bb.h"
#include "src/shared/config/resident.hpp"
#include "src/main/formats/cdg.hpp"
#include "th04/sprites/main_cdg.h"
#include "th04/main/player/bomb.hpp"
#include "th04/main/bg.hpp"

extern char far *bb_playchar_bb_fn;
extern char far *bb_playchar_cdg_fn;
extern bb_tiles8_t __seg *bb_playchar_seg;
extern "C" void pascal near nullfunc_near(void);

extern "C" void pascal near bb_playchar_load(void)
{
    bb_playchar_bb_fn[2] = resident->playchar_ascii;
    bb_playchar_cdg_fn[2] = resident->playchar_ascii;
    file_ropen(bb_playchar_bb_fn);
    bb_playchar_seg = reinterpret_cast<bb_tiles8_t __seg *>(hmem_allocbyte(BB_SIZE));
    file_read(bb_playchar_seg, BB_SIZE);
    file_close();
    cdg_load_single_noalpha(CDG_BG_PLAYCHAR_BOMB, bb_playchar_cdg_fn, 0);
}

extern "C" void pascal near bb_playchar_free(void)
{
    if(bb_playchar_seg) {
        hmem_free(bb_playchar_seg);
        bb_playchar_seg = 0;
    }
}

void near bomb_reset(void)
{
    bombing = false;
    bg_render_bombing = nullfunc_near;
}

#include "th04/main/player/player.hpp"
#include "th04/main/item/item.hpp"
#include "th04/main/bullet/clearzap.hpp"
#include "th04/main/tile/bb.hpp"
void pascal near tiles_bb_put_raw(int cel);
#include "th04/playchar.h"
#include "src/shared/hardware/graphics.hpp"
#include "compat/rec98/th02/snd/snd.h"

extern unsigned char miss_time;
extern unsigned char player_respawn_motion_time;
// Target uses a same-segment far call sequence for this function.
void hud_bombs_put(void);
#pragma samecodeseg hud_bombs_put

void pascal near player_bomb(void)
{
    if(bombing || !resident->rem_bombs || bombing_disabled) {
        return;
    }
    if(miss_time != 0) {
        if(miss_time <= 32) {
            return;
        }
        miss_time = 0;
        player_is_hit = false;
        player_respawn_motion_time = 0;
    }
    resident->rem_bombs--;
    hud_bombs_put();
    bombing = true;
    bomb_frame = 0;
    player_invincibility_time = 0xFF;
    bg_render_bombing = bg_render_bombing_func;
    bullet_clear_time = 192;
    snd_se_play(13);
    items_pull_to_player = true;
    resident->bombs_used++;
}

extern "C" void pascal near bb_playchar_put(int cel)
{
    tiles_bb_col = (playchar == PLAYCHAR_REIMU) ? 15 : 2;
    tiles_bb_seg = bb_playchar_seg;
    tiles_bb_put_raw(cel);
}

#include "src/main/hardware/grcg.hpp"
#include "th04/main/circle.hpp"
#pragma samecodeseg circles_add_growing
#include "th04/math/vector.hpp"
#include "src/main/math/randring.hpp"
#include "th04/main/frames.h"
#include "th04/main/playfld.hpp"

extern "C" void pascal near playfield_fillm_0_40_384_274(void);
extern bool palette_changed;
extern unsigned int __cdecl PaletteTone;
extern SPPoint drawpoint;
extern "C" void pascal near bomb_stars_update_and_render_for(int playchar);

static inline void bomb_grcg_off(void)
{
    _DX = 0x7C;
    _AL = 0;
    outportb(_DX, _AL);
}

void pascal near bomb_reimu(void)
{
    unsigned char angle;
    grcg_setmode_tdw();
    _AH = 15;
    grcg_setcolor_direct_raw();
    playfield_fillm_0_40_384_274();
    bomb_grcg_off();
    cdg_put_noalpha_8(32, 56, 0);
    if(bomb_frame <= 80) {
        circles_color = 9;
        PaletteTone = (196 - ((bomb_frame - 48) * 3));
        palette_changed = true;
    } else if((bomb_frame <= 160) && (stage_frame_mod4 == 0)) {
        angle = (static_cast<unsigned char>(stage_frame) << 2);
        vector2_at(drawpoint, TO_SP(PLAYFIELD_W / 2), TO_SP(PLAYFIELD_H / 2), TO_SP(128), angle);
        circles_add_growing(drawpoint.x.v, drawpoint.y.v);
        angle = (0x80 - angle);
        vector2_at(drawpoint, TO_SP(PLAYFIELD_W / 2), TO_SP(PLAYFIELD_H / 2), TO_SP(128), angle);
        circles_add_growing(drawpoint.x.v, drawpoint.y.v);
        snd_se_play(9);
    }
    grcg_setmode_rmw();
    _AH = 14;
    grcg_setcolor_direct_raw();
    bomb_stars_update_and_render_for(PLAYCHAR_REIMU);
    bomb_grcg_off();
}

void pascal near bomb_marisa(void)
{
    int y;
    register int x;
    grcg_setmode_tdw();
    _AH = 1;
    grcg_setcolor_direct_raw();
    playfield_fillm_0_40_384_274();
    bomb_grcg_off();
    cdg_put_noalpha_8(32, 56, 0);
    if(bomb_frame <= 80) {
        circles_color = 15;
        PaletteTone = (196 - ((bomb_frame - 48) * 3));
        palette_changed = true;
    } else if((bomb_frame <= 160) && (stage_frame_mod4 == 0)) {
        x = ((bomb_frame - 80) * 4);
        y = (((161 - bomb_frame) * 3) + 40);
        if(bomb_frame < 120) {
            x += (randring1_next16_mod((bomb_frame - 80) * 8) - ((bomb_frame - 64) * 4));
        } else {
            x += (randring1_next16_mod((161 - bomb_frame) * 8) - ((161 - bomb_frame) * 4));
        }
        circles_add_growing((x << 4), (y << 4));
        snd_se_play(9);
    }
    grcg_setmode_rmw();
    _AH = 8;
    grcg_setcolor_direct_raw();
    bomb_stars_update_and_render_for(PLAYCHAR_MARISA);
    bomb_grcg_off();
}

#include "th04/main/scroll.hpp"
struct BombPaletteColor { unsigned char r, g, b; };
extern BombPaletteColor bomb_palette_color_backup;

void near bomb_update_and_render(void)
{
    if(!bombing) {
        return;
    }
    if(bomb_frame < 32) {
        bb_playchar_put(bomb_frame / 4);
    } else if(bomb_frame < 48) {
        bb_playchar_put((bomb_frame / 2) - 8);
    } else {
        if(bomb_frame == 48) {
            scroll_active = false;
            graph_scrollup(0);
            bg_render_bombing = nullfunc_near;
            bomb_palette_color_backup.r = Palettes[14].v[0];
            bomb_palette_color_backup.g = Palettes[14].v[1];
            bomb_palette_color_backup.b = Palettes[14].v[2];
            Palettes[14].v[0] = 240;
            Palettes[14].v[1] = 176;
            Palettes[14].v[2] = 192;
            goto render_playchar_bomb;
        }
        if(bomb_frame < 176) {
render_playchar_bomb:
            playchar_bomb_func();
        } else {
            if(bomb_frame == 176) {
                snd_se_play(15);
                scroll_active = true;
                items_pull_to_player = false;
                goto restore_palette;
            }
            if(bomb_frame < 226) {
restore_palette:
                Palettes[14].v[0] = bomb_palette_color_backup.r;
                Palettes[14].v[1] = bomb_palette_color_backup.g;
                Palettes[14].v[2] = bomb_palette_color_backup.b;
                bg_render_bombing = bg_render_bombing_func;
                PaletteTone = (200 - ((bomb_frame - 176) * 2));
                palette_changed = true;
                if(bomb_frame == 177) {
                    graph_scrollup(scroll_line);
                }
            } else {
                bombing = false;
                PaletteTone = 100;
                palette_changed = true;
                circles_color = 13;
            }
        }
    }
    bomb_frame++;
}
