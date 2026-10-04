#pragma once
#include "stage_background.hpp"
#include <array>
namespace th04::portable::stage4 {
using Ring=std::array<std::array<unsigned,24>,25>;
struct CarpetState { std::int16_t cel=0;std::uint8_t level=0;bool active=true; };
struct CarpetUpdate { bool invalidate_top=false,invalidate_all=false;std::array<std::uint8_t,1200> dirty{}; };
// The map describes bright tiles. The original callback substitutes dark/mid
// images in the live ring and opens the light outward over two eight-cel passes.
unsigned carpet_image(unsigned level,unsigned column);
unsigned carpet_animation(unsigned cel,unsigned column);
CarpetUpdate update_carpet(CarpetState&,Ring&,std::uint16_t frame,unsigned scroll_line);
} // namespace th04::portable::stage4
