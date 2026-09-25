typedef int screen_x_t;
typedef int vram_y_t;
typedef unsigned char vc_t;

static const int PLAYCHAR_REIMU = 0;
static const int PLAYCHAR_MARISA = 1;
static const screen_x_t REIMU_LEFT = 48;
static const screen_x_t MARISA_LEFT = 336;
static const screen_x_t PLAYCHAR_TITLE_W = 256;
static const vram_y_t PLAYCHAR_TITLE_TOP = 312;
static const int BOX_ROUND = 8;
static const int GLYPH_H = 16;
static const vc_t COL_SELECTED = 15;
static const vc_t COL_NOT_SELECTED = 3;

extern const char far *PLAYCHAR_TITLE[2][2];

void far pascal graph_putsa_fx(
	screen_x_t left, vram_y_t top, vc_t color, const char far *str
);

#pragma codeseg OP_01_TEXT playchar_titles_put_01
#include "src/op/menu/playchar_titles_put.inl"
#pragma codeseg
