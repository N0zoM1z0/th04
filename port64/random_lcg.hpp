#pragma once

#include <cstdint>

namespace th04::portable::rng {

// Fixed-width form of TH04's process-local TC4J generator. The DOS source
// stores this bit pattern in a signed long, but performs every update as an
// unsigned 32-bit operation.
class Lcg32 {
public:
    static constexpr std::uint32_t default_seed = 1;
    static constexpr std::uint32_t demo_seed = 318;
    static constexpr std::uint32_t multiplier = 0x015a4e35u;
    static constexpr std::uint32_t increment = 1;

    explicit Lcg32(std::uint32_t seed = default_seed) : state_(seed) {}

    void reseed(std::uint32_t seed) { state_ = seed; }
    std::uint32_t state() const { return state_; }

    std::uint16_t next15();
    std::uint8_t next_byte();

private:
    std::uint32_t state_;
};

} // namespace th04::portable::rng
