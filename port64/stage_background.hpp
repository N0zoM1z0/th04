#pragma once
#include <array>
#include <cstdint>
#include <vector>

namespace th04::portable::stage {
using Bytes = std::vector<std::uint8_t>;

// MPN stores a last-image index and four 16x16 B/R/G/I planes per image.
class TileImages {
public:
    explicit TileImages(const Bytes& bytes);
    unsigned count() const { return count_; }
    std::uint8_t pixel(unsigned image, unsigned x, unsigned y) const;
private:
    unsigned count_ = 0;
    Bytes pixels_;
};

class Background {
public:
    Background(const Bytes& map, const Bytes& standard);
    void update(bool scroll_active = true);
    void set_speed(std::uint8_t speed) { speed_=speed; }
    void set_tile(std::int16_t x,std::int16_t y,unsigned image);
    unsigned image_at(unsigned screen_x, unsigned screen_y) const;
    unsigned row_pixel(unsigned screen_y) const { return (screen_y + display_line_) % 16; }
    unsigned scroll_line() const { return scroll_line_; }
    unsigned display_line() const { return display_line_; }
    unsigned speed() const { return speed_; }
    std::int16_t last_delta() const { return last_delta_; }
    unsigned section_cursor() const { return section_cursor_; }
    unsigned row_in_section() const { return row_in_section_; }
    unsigned required_image_count() const { return required_image_count_; }
    bool stopped() const { return speed_ == 0; }
    const std::array<std::array<unsigned,24>,25>& ring() const { return ring_; }
private:
    void refill(unsigned ring_row, unsigned section, unsigned row);
    std::vector<std::array<std::array<unsigned,24>,5>> sections_;
    Bytes order_, speeds_;
    std::array<std::array<unsigned,24>,25> ring_{};
    unsigned required_image_count_ = 0;
    unsigned section_cursor_ = 4, speed_cursor_ = 4, row_in_section_ = 0;
    unsigned scroll_line_ = 0, display_line_ = 0, ring_row_previous_ = 0;
    std::uint8_t fraction_ = 0, speed_ = 0, previous_advance_ = 0;
    std::int16_t last_delta_ = 0;
};
} // namespace th04::portable::stage
