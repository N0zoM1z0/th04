#include "src/shared/hardware/graphics.hpp"

extern unsigned char playchar_menu_sel;
extern unsigned char shottype_menu_sel;

void far pascal cdg_put_noalpha_8(screen_x_t left, vram_y_t top, int slot);
void near shottype_title_box_put(void);
void pascal near shottype_titles_put(int sel);

static const screen_x_t SHOTTYPE_PIC_LEFT = 184;
static const vram_y_t SHOTTYPE_PIC_TOP = 44;
static const pixel_t PIC_W = 256;
static const pixel_t PIC_H = 244;
static const pixel_t RAISE_W = 8;
static const pixel_t RAISE_H = 8;
static const int CDG_PIC = 40;
static const int PLAYCHAR_REIMU = 0;
static const int PLAYCHAR_MARISA = 1;
static const vc2 COL_SHADOW = 1;

#pragma codeseg OP_01_TEXT shottype_menu_initial_01
#include "src/op/menu/shottype_menu_initial.inl"
#pragma codeseg
