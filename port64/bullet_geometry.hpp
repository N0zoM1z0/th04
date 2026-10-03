#pragma once

#include <cstdint>

#include "src/main/bullet/group_types.hpp"

namespace th04::portable::bullet {

using Angle = bullet_angle_t;

// Storage used by the native entity layer. The DOS enum's compiler width is
// deliberately not inherited by persistent portable state.
using GroupCode = std::uint8_t;

Angle spread_member_angle(
    std::uint16_t member_index, std::uint8_t count, Angle spread_step
);
Angle ring_member_angle(std::uint16_t member_index, std::uint8_t count);
Angle apply_aim_and_rotation(
    Angle relative_angle, bool aimed, Angle aim_angle, Angle template_rotation
);
std::uint8_t directional_sprite_cel(Angle angle);

} // namespace th04::portable::bullet
