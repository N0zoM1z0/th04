#include "src/shared/hardware/graphics.hpp"
#include "src/shared/platform/x86.hpp"

typedef unsigned int vram_offset_t;
typedef unsigned long dots32_t;
typedef unsigned char playchar_t;

extern unsigned char far *VRAM_PLANE_B;

static const pixel_t PIC_W = 256;
static const pixel_t PIC_H = 244;
static const screen_x_t REIMU_LEFT = 48;
static const screen_x_t MARISA_LEFT = 336;
static const screen_y_t PLAYCHAR_TOP = 52;

#pragma codeseg OP_01_TEXT m_char_01
#include "src/op/menu/pic_darken.inl"
#pragma codeseg
