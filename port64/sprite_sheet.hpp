#pragma once
#include <array>
#include <cstdint>
#include <vector>

namespace th04::portable::sprite {
class Sheet {
public:
    explicit Sheet(const std::vector<std::uint8_t>& bytes);
    unsigned width() const { return width_; }
    unsigned height() const { return height_; }
    unsigned count() const { return count_; }
    std::uint8_t pixel(unsigned image, unsigned x, unsigned y) const;
    const std::array<std::uint8_t, 48>& palette() const { return palette_; }
    bool has_palette() const { return has_palette_; }

private:
    unsigned width_ = 0, height_ = 0, count_ = 0;
    bool has_palette_ = false;
    std::array<std::uint8_t, 48> palette_{};
    std::vector<std::uint8_t> packed_;
};
} // namespace th04::portable::sprite
