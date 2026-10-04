#pragma once
#include <array>
#include <cstdint>
#include <vector>

using Bytes = std::vector<std::uint8_t>;
struct PiImage {
    unsigned width{}, height{};
    std::array<std::uint8_t,48> palette{};
    Bytes pixels; // Packed high nibble first, two indexed pixels per byte.
};
// Shared by OP resource bring-up and the MAINE graphics owner. Original
// private PI resources are decoded at runtime, never embedded in the product.
PiImage decode_pi(const Bytes& data);
