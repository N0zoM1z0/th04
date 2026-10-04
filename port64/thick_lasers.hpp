#pragma once
#include "motion.hpp"
#include <array>
#include <cstdint>
#include <functional>
#include <vector>

namespace th04::portable::laser {
// MAIN's wire record is 24 bytes. These fields describe the record rather
// than depending on a host compiler's structure packing or enum width.
struct Beam {
    std::uint8_t flag=0,unused_first=0;
    motion::Point origin{}; // Q12.4; the radii below are whole pixels.
    std::array<std::uint8_t,4> unused_origin{};
    std::int16_t phase_frame=0,line_frames=0,static_frames=0;
    std::uint8_t outline=0,unused_color=0;
    std::int16_t maximum_radius=0,radius=0,radius_speed=0;
};
struct Snapshot {
    Beam scratch{};
    std::array<Beam,2> beams{};
    // This is a shared game latch. The caller clears it at the frame boundary;
    // this owner only sets it on a hit and does not consume invincibility.
    std::uint8_t player_hit=0;
};
using Sound=std::function<void(std::uint16_t)>;
enum class DrawKind : std::uint8_t { color=1,line,disc,rectangle,disable };
struct Draw {
    DrawKind kind{};
    std::uint16_t mode=0,color=0;
    std::int16_t x=0,y=0,end_x=0,end_y=0,radius=0;
};
// Draws describe the original ordered graphics calls, before clipping or
// physical VRAM writes. A consumer must preserve the three color layers and
// the final GRCG disable, including an empty pool's disable command.
class System {
public:
    explicit System(Snapshot state={}):state_(state) {}
    const Snapshot& snapshot() const { return state_; }
    Beam& scratch() { return state_.scratch; }
    void initialize();
    void pull(unsigned slot);
    bool add(const Sound& sound={});
    void update(motion::Point player,const Sound& sound={});
    std::vector<Draw> draws() const;
    void set_player_hit(std::uint8_t value) { state_.player_hit=value; }
private:
    Snapshot state_{};
};
} // namespace th04::portable::laser
