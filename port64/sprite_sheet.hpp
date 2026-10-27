#pragma once
#include <array>
#include <cstdint>
#include <functional>
#include <vector>
#include <stdexcept>

namespace th04::portable::sprite {
class Sheet {
public:
    explicit Sheet(const std::vector<std::uint8_t>& bytes);
    unsigned width() const { return width_; }
    unsigned height() const { return height_; }
    unsigned count() const { return count_; }
    std::uint8_t pixel(unsigned image, unsigned x, unsigned y) const;
    const std::uint8_t* packed_row(unsigned image,unsigned y) const {
        if(image>=count_ || y>=height_)throw std::out_of_range("BFNT sprite row");
        return packed_.data()+(std::size_t(image)*height_+y)*width_/2;
    }
    const std::array<std::uint8_t, 48>& palette() const { return palette_; }
    bool has_palette() const { return has_palette_; }

private:
    unsigned width_ = 0, height_ = 0, count_ = 0;
    bool has_palette_ = false;
    std::array<std::uint8_t, 48> palette_{};
    std::vector<std::uint8_t> packed_;
};
// The original raw tiny entry tests the first planar byte for its 0x80
// color-mask header. A caller can pass a still-unconverted global pattern.
void raster_unconverted_tiny16(const Sheet& sheet, unsigned image,
    const std::function<void(unsigned, unsigned, std::uint8_t)>& write);
} // namespace th04::portable::sprite
