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
    const std::uint32_t ax = x < 0 ? -std::int32_t(x) : x;
    const std::uint32_t ay = y < 0 ? -std::int32_t(y) : y;
    if ((ax | ay) == 0) return 0;
    unsigned angle;
    if (ax == ay) angle = 32;
    else {
        // Original MAIN0000:1DC9 uses signed JL on the 16-bit absolute
        // magnitudes. NEG leaves -32768 as 0x8000; it sorts below every
        // other magnitude. DIV remains unsigned, and XLAT uses only AL.
        const bool y_major = wrap(ax) < wrap(ay);
        const auto numerator = (y_major ? ax : ay) * 256u;
        const auto denominator = y_major ? ay : ax;
        if (!denominator || numerator / denominator > 65535u)
            throw std::domain_error("iatan2 divide error");
        angle = atan_ratio[(numerator / denominator) & 255u];
        if (y_major) angle = 64u - angle;
    }
    if (x < 0) angle = 128u - angle;
    if (y < 0) angle = 256u - angle;
    return static_cast<std::uint8_t>(angle);
}
} // namespace th04::portable::motion
