#include "motion.hpp"
#include "motion_tables.hpp"

#include <stdexcept>

namespace th04::portable::motion {
namespace {
std::int16_t sine(std::uint8_t angle) {
    const unsigned quadrant = angle / 64u;
    const unsigned phase = angle % 64u;
    const auto value = sine_quarter[(quadrant & 1u) ? 64u - phase : phase];
    return (quadrant >= 2) ? static_cast<std::int16_t>(-value) : value;
}
} // namespace

Subpixel wrap(std::int32_t value) {
    const auto bits = static_cast<std::uint16_t>(value);
    return static_cast<Subpixel>(bits <= 32767u ? std::int32_t(bits)
                                               : std::int32_t(bits) - 65536);
}

std::int32_t floor_shift8(std::int32_t value) {
    return value >= 0 ? value / 256
                      : static_cast<std::int32_t>(-((-std::int64_t(value) + 255) / 256));
}

void Motion::update() {
    previous = current;
    current.x = wrap(std::int32_t(current.x) + velocity.x);
    current.y = wrap(std::int32_t(current.y) + velocity.y);
}

Point polar(std::uint8_t angle, Subpixel length) {
    return {
        wrap(floor_shift8(std::int32_t(sine(std::uint8_t(angle + 64u))) * length)),
        wrap(floor_shift8(std::int32_t(sine(angle)) * length)),
    };
}

std::uint8_t angle_to(Point from, Point to) {
    const auto x = wrap(std::int32_t(to.x) - from.x);
    const auto y = wrap(std::int32_t(to.y) - from.y);
    // The assembly's signed comparison of absolute magnitudes has an unusual
    // INT16_MIN edge. Gameplay never reaches that displacement; reject it
    // instead of introducing a silently different host quadrant or DIV fault.
    if (x == -32768 || y == -32768) {
        throw std::domain_error("iatan2 displacement outside gameplay range");
    }
    const std::uint32_t ax = x < 0 ? -std::int32_t(x) : x;
    const std::uint32_t ay = y < 0 ? -std::int32_t(y) : y;
    if ((ax | ay) == 0) return 0;
    unsigned angle;
    if (ax == ay) angle = 32;
    else if (ax > ay) angle = atan_ratio[(ay * 256u) / ax];
    else angle = 64u - atan_ratio[(ax * 256u) / ay];
    if (x < 0) angle = 128u - angle;
    if (y < 0) angle = 256u - angle;
    return static_cast<std::uint8_t>(angle);
}
} // namespace th04::portable::motion
