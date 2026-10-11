#pragma once
#include <cstdint>

namespace th04::portable::pc98_palette {
// Match the recorded DOSBox-X PC-98 analog DAC scanout path: expand the
// four-bit port value to six bits, then expand those six bits to RGB8.
// Apply palette tone in the four-bit domain before calling this function.
// Physical PC-98 output and other emulator DAC paths remain separate claims.
constexpr std::uint8_t analog_rgb8(unsigned nibble) {
    const unsigned four = nibble & 15u;
    const unsigned six = (four << 2) | (four >> 2);
    return std::uint8_t((six << 2) | (six >> 4));
}
} // namespace th04::portable::pc98_palette
