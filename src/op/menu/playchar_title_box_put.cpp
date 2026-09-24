#include "src/shared/hardware/graphics.hpp"
#include "src/shared/platform/x86.hpp"

static const screen_x_t REIMU_LEFT = 48;
static const screen_x_t MARISA_LEFT = 336;
static const screen_x_t PLAYCHAR_TITLE_OFFSET_X = 32;
static const vram_y_t PLAYCHAR_TITLE_TOP = 312;
static const pixel_t PLAYCHAR_TITLE_W = 192;
static const pixel_t PLAYCHAR_TITLE_H = 48;
static const pixel_t SHADOW_DISTANCE = 8;
static const pixel_t BOX_ROUND = 8;
static const vc2 COL_SHADOW = 1;
static const vc2 COL_BOX = 2;

#define playchar_title_left_for(left, playchar) 	switch(playchar) { 	case 0: left = (REIMU_LEFT + PLAYCHAR_TITLE_OFFSET_X); break; 	case 1: left = (MARISA_LEFT + PLAYCHAR_TITLE_OFFSET_X); break; 	}

#pragma codeseg OP_01_TEXT m_char_01
#include "src/op/menu/playchar_title_box_put.inl"
#pragma codeseg
