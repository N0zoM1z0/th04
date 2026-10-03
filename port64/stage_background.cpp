#include "stage_background.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::stage {
namespace {
unsigned word(const Bytes& bytes, std::size_t at) {
    if (at >= bytes.size() || bytes.size()-at < 2) throw std::invalid_argument("truncated stage word");
    return unsigned(bytes[at]) | (unsigned(bytes[at+1]) << 8);
}
unsigned image_from_vram(unsigned offset) {
    // tile_image_vo(id): 72 + 2*(id/25) + 1280*(id%25).
    // Only 24 visible columns are decoded; 8 storage-only words may be zero.
    if (offset < 72) throw std::invalid_argument("invalid MAP tile address");
    const unsigned relative = offset-72, column = (relative%1280)/2, row = relative/1280;
    if (relative%2 || relative%1280 > 6 || row >= 25) throw std::invalid_argument("invalid MAP tile address");
    return column*25 + row;
}
} // namespace

TileImages::TileImages(const Bytes& bytes) {
    if (bytes.size() < 54 || bytes[0]!='M' || bytes[1]!='P' || bytes[2]!='T' || bytes[3]!='N') {
        throw std::invalid_argument("invalid MPN header");
    }
    count_ = unsigned(bytes[4])+1;
    const unsigned size = count_*128;
    if (bytes.size()-54 < size) throw std::invalid_argument("truncated MPN planes");
    // Expand planes once at load time, keeping four-plane work out of the
    // host per-frame blit path.
    pixels_.resize(count_*256);
    for (unsigned image=0; image<count_; ++image) for (unsigned y=0; y<16; ++y) {
        for (unsigned x=0; x<16; ++x) {
            unsigned color = 0;
            for (unsigned plane=0; plane<4; ++plane) {
                const auto value = bytes[54+image*128+plane*32+y*2+x/8];
                color |= ((value >> (7-x%8)) & 1u) << plane;
            }
            pixels_[image*256+y*16+x] = static_cast<std::uint8_t>(color);
        }
    }
}

std::uint8_t TileImages::pixel(unsigned image, unsigned x, unsigned y) const {
    if (image >= count_ || x >= 16 || y >= 16) throw std::out_of_range("MPN tile pixel");
    return pixels_[image*256+y*16+x];
}

Background::Background(const Bytes& map, const Bytes& standard) {
    const auto size = word(map,0);
    if (!size || size%320 || size/320 > 32 || map.size() < 8u+size) {
        throw std::invalid_argument("invalid MAP section extent");
    }
    sections_.resize(size/320);
    for (unsigned section=0; section<sections_.size(); ++section) {
        for (unsigned row=0; row<5; ++row) {
            for (unsigned col=0; col<24; ++col) {
                const unsigned image = image_from_vram(word(map,8 + section*320 + row*64 + col*2));
                sections_[section][row][col] = image;
                required_image_count_ = std::max(required_image_count_,image+1);
            }
        }
    }
    const auto standard_size = word(standard,0);
    if (standard_size < 2 || standard.size() < 2u+standard_size) throw std::invalid_argument("truncated STD extent");
    const unsigned order_count = standard[2];
    const std::size_t speed_at = 3u+order_count;
    if (order_count < 5 || speed_at >= 2u+standard_size) throw std::invalid_argument("invalid STD map order");
    const auto speed_count = standard[speed_at];
    if (speed_count < order_count+1u || speed_at+1u+speed_count > 2u+standard_size) {
        throw std::invalid_argument("invalid STD speed stream");
    }
    order_.assign(standard.begin()+3,standard.begin()+speed_at);
    speeds_.assign(standard.begin()+speed_at+1,standard.begin()+speed_at+1+speed_count);
    if (speeds_[order_count] != 0) throw std::invalid_argument("STD scroll terminator missing");
    for (const auto section : order_) if (section >= sections_.size()) throw std::invalid_argument("STD map section missing");
    // std_load initially stores the speed CHUNK LENGTH. The first ring-row
    // crossing consumes the intended speed at stream index 5.
    speed_ = speed_count;
    for (unsigned section=0; section<5; ++section) {
        for (unsigned row=0; row<5; ++row) refill((4-section)*5+row,order_[section],row);
    }
}

void Background::refill(unsigned ring_row, unsigned section, unsigned row) {
    ring_[ring_row] = sections_[section][row];
}

void Background::update(bool scroll_active) {
    // Publish the hardware origin BEFORE advancing the ring for this frame.
    if (previous_advance_ && scroll_active) display_line_ = scroll_line_;
    fraction_ = static_cast<std::uint8_t>(unsigned(fraction_)+speed_);
    unsigned advance = 0;
    if (fraction_ >= 16) {
        advance = fraction_/16;
        scroll_line_ = (scroll_line_+400-advance)%400;
        fraction_ &= 15;
    }
    // This remains published even if the tile helper stops the stream on
    // the same call. Enemy MOVE_WITH_SCROLL consumes it next frame.
    last_delta_ = static_cast<std::int16_t>(advance*16);
    if ((advance == 0 && previous_advance_ == 0) || speed_ == 0) return;
    const auto ring_row = scroll_line_/16;
    if (ring_row != ring_row_previous_) {
        ring_row_previous_ = ring_row;
        if (row_in_section_ == 0) {
            row_in_section_ = 4;
            ++section_cursor_; ++speed_cursor_;
            if (speed_cursor_ >= speeds_.size()) throw std::out_of_range("STD speed cursor");
            speed_ = speeds_[speed_cursor_];
            if (speed_ == 0) {
                scroll_line_ = 0;
                previous_advance_ = 0;
                return;
            }
        } else --row_in_section_;
        if (section_cursor_ >= order_.size()) throw std::out_of_range("STD map cursor");
        refill(ring_row,order_[section_cursor_],row_in_section_);
    }
    previous_advance_ = static_cast<std::uint8_t>(advance);
}

unsigned Background::image_at(unsigned screen_x, unsigned screen_y) const {
    if (screen_x >= 384 || screen_y >= 400) throw std::out_of_range("background pixel coordinate");
    return ring_[((screen_y+display_line_)%400)/16][screen_x/16];
}
void Background::set_tile(std::int16_t x,std::int16_t y,unsigned image) {
    const auto pixels=[](int value) { return value>=0 ? value/16 : -((-value+15)/16); };
    const int col=pixels(x)/16;
    // tile_ring_set_vo forces scrolling on while converting Y+16 pixels.
    const unsigned wrapped=static_cast<std::uint16_t>(int(y)+256);
    const int signed_y=wrapped<32768 ? int(wrapped) : int(wrapped)-65536;
    int top=pixels(signed_y)+int(scroll_line_);
    if (top<0) top+=400;
    else if (top>=400) top-=400;
    const int row=top/16;
    if (row<0 || row>=25 || col<0 || col>=24) throw std::out_of_range("stage tile write");
    ring_[row][col]=image;
    required_image_count_=std::max(required_image_count_,image+1);
}
} // namespace th04::portable::stage
