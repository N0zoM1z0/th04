#pragma once
#include "motion.hpp"

namespace th04::portable::player {
inline constexpr std::uint16_t up = 0x0001;
inline constexpr std::uint16_t down = 0x0002;
inline constexpr std::uint16_t left = 0x0004;
inline constexpr std::uint16_t right = 0x0008;
inline constexpr std::uint16_t movement_mask = 0x0f0f;

class Movement {
public:
    Movement();
    const motion::Motion& position() const { return position_; }
    std::uint16_t previous_input() const { return previous_input_; }
    void update(std::uint16_t held_input, bool shift);

private:
    motion::Motion position_{};
    std::uint16_t previous_input_ = 0;
};
} // namespace th04::portable::player
