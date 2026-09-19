#pragma option -k-
#pragma option -zCCIRCLE_TEXT -zPmain_01

#include "platform.h"
#include "planar.h"
#include "src/shared/hardware/graphics.hpp"
#include "th04/common.h"
#include "th04/main/playfld.hpp"

extern "C" void near grcg_fill_playfield_rows(void);

void pascal near mugetsu_gengetsu_backdrop_colorfill(void)
{
    _AX = grcg_segment(0, (192 + PLAYFIELD_TOP));
    _ES = _AX;
    _DI = (((176 - 1) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT);
    grcg_fill_playfield_rows();
}
