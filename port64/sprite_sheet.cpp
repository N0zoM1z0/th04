#include "sprite_sheet.hpp"
#include <stdexcept>

namespace th04::portable::sprite {
Sheet::Sheet(const std::vector<std::uint8_t>& bytes) {
    if (bytes.size() < 32 || bytes[0] != 'B' || bytes[1] != 'F' ||
        bytes[2] != 'N' || bytes[3] != 'T' || bytes[4] != 26 || (bytes[5] & 127u) != 3) {
        throw std::invalid_argument("invalid BFNT sprite header");
    }
    const auto word = [&](unsigned at) { return unsigned(bytes[at]) | (unsigned(bytes[at+1]) << 8); };
    width_ = word(8); height_ = word(10);
    const auto first = word(12), last = word(14);
    if (!width_ || width_ > 256 || (width_ & 7u) || !height_ || height_ > 255 || last < first) {
        throw std::invalid_argument("invalid BFNT sprite geometry");
    }
    count_ = last - first + 1u;
    std::size_t at = 32u + word(28);
    has_palette_ = (bytes[5] & 128u) != 0;
    if (at > bytes.size() || (has_palette_ && bytes.size() - at < 48u)) {
        throw std::invalid_argument("truncated BFNT palette/extension");
    }
    if (has_palette_) {
        for (unsigned color = 0; color < 16; ++color) {
            // BFNT is BRG; the host renderer and PI palette use RGB.
            palette_[color*3] = bytes[at+color*3+1];
            palette_[color*3+1] = bytes[at+color*3+2];
            palette_[color*3+2] = bytes[at+color*3];
        }
        at += 48;
    }
    const std::size_t size = std::size_t(width_) * height_ / 2 * count_;
    if (size > bytes.size() - at) throw std::invalid_argument("truncated BFNT sprite pixels");
    packed_.assign(bytes.begin() + at, bytes.begin() + at + size);
}

std::uint8_t Sheet::pixel(unsigned image, unsigned x, unsigned y) const {
    if (image >= count_ || x >= width_ || y >= height_) throw std::out_of_range("BFNT sprite pixel");
    const auto packed = packed_[std::size_t(image) * width_ * height_ / 2 + std::size_t(y) * width_ / 2 + x/2];
    return (x & 1u) ? packed & 15u : packed >> 4;
}
} // namespace th04::portable::sprite
