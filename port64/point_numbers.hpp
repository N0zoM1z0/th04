#pragma once
#include "motion.hpp"
#include <array>
#include <cstdint>
#include <functional>
#include <vector>

namespace th04::portable::pointnum {
constexpr unsigned count=400, ring_size=200, digits=4;
struct Entity {
    std::uint8_t flag=0,age=0;
    motion::Point center{};
    motion::Subpixel previous_y=0;
    std::array<std::uint8_t,digits> decimal{};
    std::uint16_t width=0;
    std::uint8_t times_two=0,padding=0;
};
struct Draw {int left=0,top=0;unsigned glyph=0;std::uint8_t color=15;};
struct Snapshot {
    std::array<Entity,count> entities{};
    std::uint8_t white_cursor=0,yellow_cursor=0;
    // Index+1 is the portable counterpart of a near pointer; zero terminates.
    std::array<std::uint16_t,count+1> alive{};
    std::uint16_t first_yellow=0;
};
class System {
public:
    explicit System(Snapshot state={}):state_(state) {}
    const Snapshot& snapshot() const {return state_;}
    const std::vector<Draw>& draws() const {return draws_;}
    void initialize();
    void add(motion::Point center,std::uint16_t points,bool yellow,bool times_two);
    void update();
    // Render mutates widths once at the simulation boundary. Host paints only
    // consume these cached glyph requests, including overwritten ring slots.
    void prepare_render(bool scrolling,std::uint16_t scroll_line);
private:
    Snapshot state_;
    std::vector<Draw> draws_;
};
class Font {
public:
    // The supplied original MAIN contains the small mono font. It is an
    // external asset, never an embedded executable or copied target array.
    explicit Font(const std::vector<std::uint8_t>& main);
    bool pixel(unsigned glyph,unsigned x,unsigned y) const;
private:
    std::array<std::array<std::uint8_t,8>,12> rows_{};
};
using PixelSink=std::function<void(int,int,std::uint8_t)>;
void raster(const Font& font,const Draw& draw,const PixelSink& put);
} // namespace th04::portable::pointnum
