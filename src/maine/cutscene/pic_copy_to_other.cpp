#include "src/shared/hardware/graphics.hpp"

typedef int vram_offset_t;
typedef unsigned short egc_temp_t;

static const pixel_t CUTSCENE_PIC_W = 320;
static const pixel_t CUTSCENE_PIC_H = 200;
static const vram_byte_amount_t CUTSCENE_PIC_VRAM_W = (CUTSCENE_PIC_W / BYTE_DOTS);

extern unsigned char far *VRAM_PLANE_B;

void near egc_start_copy(void);

#pragma codeseg CUTSCENE_TEXT pic_copy_other_01
#include "src/maine/cutscene/pic_copy_to_other.inl"
#pragma codeseg
