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
void raster_unconverted_tiny16(const Sheet& sheet, unsigned image,
    const std::function<void(unsigned, unsigned, std::uint8_t)>& write) {
    unsigned first = 0;
    for (unsigned x = 0; x < 8; ++x)
        if (sheet.pixel(image, x, 0)) first |= 128u >> x;
    if (first != 0x80) return;
    const auto stride = std::size_t(sheet.width()) * sheet.height() / 8;
    std::vector<std::uint8_t> planes(stride * 5, 0);
    for (unsigned y = 0; y < sheet.height(); ++y) for (unsigned x = 0; x < sheet.width(); ++x) {
        const auto color = sheet.pixel(image, x, y);
        const auto at = std::size_t(y) * (sheet.width() / 8) + x / 8;
        const auto bit = std::uint8_t(128u >> (x & 7u));
        if (color) planes[at] |= bit;
        for (unsigned p = 0; p < 4; ++p)
            if (color & (1u << p)) planes[(p + 1) * stride + at] |= bit;
    }
    for (std::size_t at = 0;; at += 34) {
        if (at >= planes.size()) throw std::out_of_range("raw tiny header outside planar pattern");
        if (planes[at] != 0x80) return;
        if (planes.size() - at < 34) throw std::out_of_range("raw tiny mask outside planar pattern");
        const auto color = std::uint8_t(planes[at + 1] & 15u);
        for (unsigned y = 0; y < 16; ++y) for (unsigned x = 0; x < 16; ++x)
            if (planes[at + 2 + y * 2 + x / 8] & (128u >> (x & 7u))) write(x, y, color);
    }
}
} // namespace th04::portable::sprite
