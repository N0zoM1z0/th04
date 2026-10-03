#include "bullet_geometry.hpp"

#include <stdexcept>

namespace th04::portable::bullet {
namespace {

Angle wrap_angle(unsigned value) {
    return static_cast<Angle>(value & 0xffu);
}

} // namespace

Angle spread_member_angle(
    std::uint16_t member_index, std::uint8_t count, Angle spread_step
) {
    if (!count || member_index >= count) {
        throw std::out_of_range("spread member outside group");
    }
    if (count & 1) {
        if (!member_index) {
            return 0;
        }
        const unsigned magnitude =
            unsigned((member_index + 1) / 2) * spread_step;
        return wrap_angle((member_index & 1)
            ? BULLET_ANGLE_FULL_TURN - wrap_angle(magnitude)
            : magnitude);
    }
    const unsigned magnitude =
        unsigned(spread_step / 2) + unsigned(member_index / 2) * spread_step;
    return wrap_angle((member_index & 1)
        ? BULLET_ANGLE_FULL_TURN - wrap_angle(magnitude)
        : magnitude);
}

Angle ring_member_angle(std::uint16_t member_index, std::uint8_t count) {
    if (!count || member_index >= count) {
        throw std::out_of_range("ring member outside group");
    }
    return wrap_angle(
        unsigned(member_index) * BULLET_ANGLE_FULL_TURN / count
    );
}

Angle apply_aim_and_rotation(
    Angle relative_angle, bool aimed, Angle aim_angle, Angle template_rotation
) {
    return wrap_angle(
        unsigned(relative_angle) + (aimed ? aim_angle : 0) + template_rotation
    );
}

std::uint8_t directional_sprite_cel(Angle angle) {
    constexpr unsigned cel_count = 16;
    constexpr unsigned period = 0x80u;
    constexpr unsigned step = period / cel_count;
    return std::uint8_t((unsigned(angle) + (step / 2) - 1) % period / step);
}

} // namespace th04::portable::bullet
