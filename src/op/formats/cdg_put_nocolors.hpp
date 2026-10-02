#ifndef TH04_OP_FORMATS_CDG_PUT_NOCOLORS_HPP
#define TH04_OP_FORMATS_CDG_PUT_NOCOLORS_HPP

#include "src/shared/platform/pc98.hpp"

// OP's single-plane CDG mask uses the caller's GRCG mode/color. The target
// SHARED 0DA1:0282 entry has a FAR Pascal ABI and ends with RETF 6.
extern "C" void far pascal cdg_put_nocolors_8(
    screen_x_t left, vram_y_t top, int slot
);

#endif
