#pragma once
#include "sprite_sheet.hpp"
#include <functional>
namespace th04::portable::wave {
// Mathematical signed seven-bit sine, with the original symmetric saturation.
int sine(std::uint8_t angle);
void raster(const sprite::Sheet&,unsigned image,std::int16_t left,std::int16_t top,
            std::int16_t length,std::uint16_t amplitude,std::uint16_t phase,
            const std::function<void(int,int,std::uint8_t)>& write);
}
