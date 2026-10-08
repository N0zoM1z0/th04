#pragma once
#include "orange.hpp"
namespace th04::portable::elly {
// MAIN DATA:46E6..46F8. The scythe has its own unsigned animation clock,
// byte speed/angle and signed turn, independent of the signed BOSS clock.
struct Scythe {
    std::uint8_t mode=0,flag=0;
    motion::Motion position{};
    std::uint16_t frame=0;
    std::uint8_t angle=0,speed=0;
    std::int8_t turn=0;
};
struct Snapshot {
    orange::Snapshot boss{};
    Scythe scythe{};
    std::int16_t orbit_frame=0;
    std::uint8_t pattern_group=0,player_hit=0;
};
struct Context : orange::Context {
    // The scythe consumes shots with against-boss=false; body hits use true.
    std::function<std::uint16_t(motion::Point,motion::Point)> scythe_hit;
};
enum class BackdropKind { all_tiles,dirty_tiles,picture,picture_and_tiles };
struct Backdrop { BackdropKind kind=BackdropKind::all_tiles;std::int16_t mask_cel=0;std::vector<motion::Point> invalidations; };
Backdrop backdrop(const Snapshot&);
using Sink=orange::Sink;
using Draw=orange::Draw;
Snapshot prepare_stage3(orange::Snapshot previous);
class System {
public:
    explicit System(Snapshot state):state_(state) {}
    const Snapshot& snapshot() const { return state_; }
    void update(const Context&,bullet::System&,gather::System&,spark::System&,
                randring::SharedRandomRing&,const Sink& sink={});
    void prepare_render(std::uint16_t frame);
    void apply_departure(const transition::Departure&);
    void set_invincibility(std::uint8_t value) { state_.boss.invincibility=value; }
    void set_graphics(std::uint16_t tone,std::uint8_t color) { state_.boss.palette_tone=tone;state_.boss.circle_color=color; }
    void set_palette_zero(std::array<std::uint8_t,3> value) { state_.boss.palette_zero=value; }
    const std::vector<Draw>& draws() const { return draws_; }
    // Bounded helper entry points are also checked directly against the target.
    void initialize_scythe(motion::Point player);
    void update_scythe(const Context&,const Sink& sink={});
    void update_orbit();
private:
    Snapshot state_{};
    std::vector<Draw> draws_;
};
} // namespace th04::portable::elly
