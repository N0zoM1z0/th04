#pragma once
#include <cstdint>
#include <functional>
namespace th04::portable::sprite::super {
// Callbacks retain segment ownership. A WORD at FFFF reads the next physical
// byte before SI wraps; consumers decide memory mapping and GRCG effects.
using Read=std::function<std::uint16_t(std::uint16_t,unsigned)>;
using Write=std::function<void(std::uint16_t,unsigned,std::uint16_t)>;
using Port=std::function<void(unsigned,std::uint8_t)>;
void put(std::uint16_t left,std::uint16_t top,std::uint16_t packed_size,
         const Read&,const Write&,const Port&);
}
