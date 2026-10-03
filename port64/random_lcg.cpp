#include "random_lcg.hpp"

namespace th04::portable::rng {

std::uint16_t Lcg32::next15() {
    // Unsigned overflow is the required modulo-2^32 operation on every host.
    state_ = (state_ * multiplier) + increment;
    return static_cast<std::uint16_t>((state_ >> 16) & 0x7fffu);
}

std::uint8_t Lcg32::next_byte() {
    // MAIN's historical far IRand() declarations consume only AL.
    return static_cast<std::uint8_t>(next15());
}

} // namespace th04::portable::rng
