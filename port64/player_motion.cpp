#include "player_motion.hpp"
#include <algorithm>

namespace th04::portable::player {
namespace {
bool set_velocity(std::uint16_t input, motion::Point& velocity) {
    int x = 0, y = 0;
    switch (input) {
    case 0: break;
    case left: x = -1; break;
    case down | left: case 0x0400: x = -1; y = 1; break;
    case down: y = 1; break;
    case down | right: case 0x0800: x = 1; y = 1; break;
    case right: x = 1; break;
    case up | right: case 0x0200: x = 1; y = -1; break;
    case up: y = -1; break;
    case up | left: case 0x0100: x = -1; y = -1; break;
    default: return false;
    }
    const int speed = (x && y) ? 48 : 64;
    velocity = {motion::Subpixel(x * speed), motion::Subpixel(y * speed)};
    return true;
}
} // namespace

Movement::Movement() {
    position_.current = {192 * 16, 320 * 16};
    position_.previous = position_.current;
}

void Movement::update(std::uint16_t held_input, bool shift) {
    auto input = static_cast<std::uint16_t>(held_input & movement_mask);
    position_.velocity = {};
    bool retry = true;
    if (!set_velocity(input, position_.velocity) && previous_input_ != input) {
        // On a new conflicting chord, retry once after subtracting the old
        // keys. Preserve the previous latch on this retry; it gives the newly
        // pressed direction priority while the opposing old key stays held.
        input = static_cast<std::uint16_t>(input & ~previous_input_);
        retry = false;
        set_velocity(input, position_.velocity);
    }
    if (shift) {
        position_.velocity.x /= 2;
        position_.velocity.y /= 2;
    }
    position_.update();
    position_.current.x = std::clamp<motion::Subpixel>(position_.current.x, 8 * 16, 376 * 16);
    position_.current.y = std::clamp<motion::Subpixel>(position_.current.y, 8 * 16, 352 * 16);
    if (retry) previous_input_ = input;
}
} // namespace th04::portable::player
