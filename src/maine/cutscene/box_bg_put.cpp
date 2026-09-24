#include "src/shared/platform/pc98.hpp"

typedef unsigned short dots16_t;
typedef unsigned int size_t;
typedef int vram_offset_t;

struct planar16_t {
	dots16_t B;
	dots16_t R;
	dots16_t G;
	dots16_t E;
};

extern planar16_t far *box_bg;
extern unsigned char far *VRAM_PLANE_B;
extern unsigned char far *VRAM_PLANE_R;
extern unsigned char far *VRAM_PLANE_G;
extern unsigned char far *VRAM_PLANE_E;

static const screen_x_t BOX_LEFT = 80;
static const screen_y_t BOX_TOP = 320;
static const pixel_t BOX_H = 64;
static const vram_byte_amount_t BOX_VRAM_W = 60;

#pragma codeseg CUTSCENE_TEXT box_bg_put_01
#include "src/maine/cutscene/box_bg_put.inl"
#pragma codeseg
