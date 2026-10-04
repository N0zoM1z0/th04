#pragma once
#include "motion.hpp"
#include <cstdint>
#include <vector>

namespace th04::portable::laser { class System; }
namespace th04::portable::yuuka6 {
class System;
class Entities;
// These two DATA BYTEs (46C3/46C4) belong to drawing, independently of the
// update dispatch. A hit alternates red and normal body sprites; a frame
// without a hit retains the cycle instead of resetting it.
struct ForegroundState {
    std::uint8_t body_flash=0,mirror_flash=0;
};
enum class DrawKind : std::uint8_t {
    sprite,white_sprite,large_sprite,tiny_sprite,circle,color,disc,
    rectangle,vertical_line,disable,zoom_sprite,red_sprite,mode
};
struct Draw {
    DrawKind kind{};
    std::int16_t x=0,y=0;
    std::uint16_t value=0,color=0;
    std::int16_t end_x=0,end_y=0;
    std::uint16_t mode=0;
};
class Foreground {
public:
    explicit Foreground(ForegroundState initial={}):state_(initial) {}
    // MAIN0AAF:712A..72A5. Run once per simulated frame: this consumes
    // visible damage and advances common explosion/custom death animations.
    // Repaints read draws() and never call prepare_render() a second time.
    void prepare_render(System&,std::uint16_t frame,const laser::System&,Entities&);
    const ForegroundState& state() const { return state_; }
    const std::vector<Draw>& draws() const { return draws_; }
private:
    ForegroundState state_{};
    std::vector<Draw> draws_;
};
} // namespace th04::portable::yuuka6
