#pragma once
#include <cstdint>
#include <vector>
namespace th04::portable::playfield {
struct Shake { std::int16_t x=0,y=0,time=0;std::int8_t redraw=0; };
struct Shift { std::int16_t x=0,y=0;bool invalidate=false; };
// MAIN_01_TEXT0AAF:2246: apply offsets before clearing the globals and
// invalidating both pages. The returned draw stays stable across repaints.
Shift update(Shake&,std::uint8_t mod2,std::uint8_t mod4);
// EGC moves the physical rectangle x32..415/y0..399. Vacated strips retain
// their previous pixels; text VRAM does not move. X precedes Y.
void move(std::vector<std::uint8_t>&,unsigned display_line,Shift);
void move(std::vector<std::uint32_t>&,unsigned display_line,Shift);
}
