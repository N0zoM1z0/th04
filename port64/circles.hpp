#pragma once
#include "motion.hpp"
#include <array>
#include <vector>

namespace th04::portable::circle {
struct Entity {
    std::uint8_t flag=0,age=0;
    motion::Point center{}; // Screen pixels, not Q12.4 world coordinates.
    std::int16_t radius=0,delta=0;
};
struct Snapshot { std::array<Entity,16> entities{};std::uint8_t color=0; };
class System {
public:
    explicit System(Snapshot initial={}):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    bool add(motion::Point center,bool growing=false);
    void update();
    void set_color(std::uint8_t color) { state_.color=color; }
private:
    Snapshot state_;
};
struct Clip {
    std::int16_t left=0,top=0,right=639,bottom=399;
};
// Original GRCG midpoint outline. Coordinates include the clipping origin.
// The clipped lower half excludes the bottom row; all-inside includes it.
std::vector<motion::Point> raster(motion::Point center,std::uint16_t radius,Clip clip={});
} // namespace th04::portable::circle
