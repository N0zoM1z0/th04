#pragma once
#include "score.hpp"
#include <cstdint>
#include <vector>

namespace th04::portable::registration::numerals {
// MAINE SUPER_PUT scales a WORD pattern by2 with16-bit wrap. These offsets
// own MAINE's DGROUP lookup, not a flat host array or copied target memory.
struct Slot {
    std::uint16_t pattern,pointer_offset,dimensions_offset;
};
struct Request {std::uint16_t left,top;Slot slot;};
Slot address(std::uint16_t pattern);
std::vector<Request> row(const score::Digits&,unsigned place,bool selected,std::uint8_t character);
}
