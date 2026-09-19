#pragma option -k-
#pragma option -zCMAIN__TEXT -zPmain_01

#include "platform.h"
#include "planar.h"
#include "src/shared/hardware/graphics.hpp"
#include "th04/common.h"
#include "th04/main/playfld.hpp"

extern "C" void near grcg_fill_playfield_rows(void);

void pascal near orange_backdrop_colorfill(void)
{
    _DX = grcg_segment(0, PLAYFIELD_TOP);
    _ES = _DX;
    _DI = (((120 - 1) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT);
    grcg_fill_playfield_rows();

    disable();
    _DX = 0x7E;
    _AL ^= _AL;
    outportb(_DX, _AL);
    outportb(_DX, _AL);
    outportb(_DX, _AL);
    outportb(_DX, _AL);
    enable();

    _AX = grcg_segment(0, (248 + PLAYFIELD_TOP));
    _ES = _AX;
    _DI = (((120 - 1) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT);
    grcg_fill_playfield_rows();
}
