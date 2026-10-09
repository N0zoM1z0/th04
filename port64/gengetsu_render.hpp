#pragma once
#include "gengetsu.hpp"
namespace th04::portable::gengetsu_render {
using Draw=gengetsu::Draw;
std::vector<Draw> prepare(gengetsu::Snapshot&,std::uint16_t frame,std::uint8_t amplitude_adjacent);
}
