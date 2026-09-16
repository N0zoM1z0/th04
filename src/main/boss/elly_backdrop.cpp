#pragma option -k-
#pragma option -zCCIRCLE_TEXT -zPmain_01

#include "platform.h"
#include "planar.h"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/common.h"
#include "th04/main/playfld.hpp"

extern "C" void near grcg_fill_playfield_rows(void);

void pascal near elly_backdrop_colorfill(void)
{
    _AX = grcg_segment(0, (112 + PLAYFIELD_TOP));
    _ES = _AX;
    _DI = (((256 - 1) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT);
    grcg_fill_playfield_rows();
}
