#pragma once

#include <cstdint>

namespace th04::portable::motion {

using Subpixel = std::int16_t;
struct Point {
    Subpixel x = 0;
    Subpixel y = 0;
};
struct Motion {
    Point current{};
    Point previous{};
    Point velocity{};
    void update();
};

// Define the 16-bit wrap and arithmetic shift explicitly. C++17 signed
// narrowing/right-shift behavior is otherwise implementation-defined.
Subpixel wrap(std::int32_t value);
std::int32_t floor_shift8(std::int32_t value);
// Original signed magnitude comparison and byte-width XLAT, including
// -32768 displacements. A guest DIV fault becomes std::domain_error.
std::uint8_t angle_to(Point from, Point to);
Point polar(std::uint8_t angle, Subpixel length);

} // namespace th04::portable::motion
