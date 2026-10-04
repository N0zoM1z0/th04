#pragma once
#include "orange.hpp"
#include "sprite_sheet.hpp"
namespace th04::portable::reimu {
// MAIN DATA:BCFE template and B204..B543 pool, each a26-byte DOS record.
// Retained fields are explicit; host structure size is not an ABI contract.
struct Orb {
    std::uint8_t flag=0,angle=0;
    motion::Point center{},origin{},velocity{};
    std::uint16_t spin_time=0;
    std::int16_t distance=0,unknown=0;
    std::array<std::uint8_t,4> padding{};
    std::uint8_t move_speed=0;
    std::int8_t angle_speed=0;
};
struct Snapshot {
    orange::Snapshot boss{};
    Orb scratch{};
    std::array<Orb,32> orbs{};
    std::int8_t angle_delta=0,pulse_direction=0;
    // Both historical visibility symbols alias the single BCFC trail byte.
    std::uint8_t orb_pattern=0,trail_visible=0,pattern8_angle=0,player_hit=0;
};
struct Context : orange::Context {
    // Orb shots use against-boss=false and cannot damage the BOSS body.
    std::function<std::uint16_t(motion::Point,motion::Point)> orb_hit;
};
using Sink=orange::Sink;
enum class BackdropKind { all_tiles,dirty_tiles,tiles_and_mask,picture_and_mask,picture };
struct Backdrop { BackdropKind kind=BackdropKind::all_tiles;std::uint8_t cel=0; };
Backdrop backdrop(std::uint8_t phase,std::int16_t clock);
// Original SUPER1PLANE and rolling sprites target a640x400 indexed surface.
// Consumers choose RGB conversion; partial plane writes retain the index.
void raster_sprite(const sprite::Sheet&,unsigned image,int left,int top,orange::DrawKind,
                   const std::function<std::uint8_t(int,int)>& read,
                   const std::function<void(int,int,std::uint8_t)>& write);
Snapshot prepare_stage4(orange::Snapshot previous,unsigned rank);
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    void add_moving();
    void add_spinning(std::uint8_t angle_offset,std::int16_t count);
    void update_orbs(const Context&,const Sink& sink={});
    void pulse();
    void prepare_render(std::uint16_t frame);
    const std::vector<orange::Draw>& draws() const { return draws_; }
    void apply_departure(const transition::Departure&);
    void set_palette_zero(std::array<std::uint8_t,3> value) { state_.boss.palette_zero=value; }
    void set_invincibility(std::uint8_t value) { state_.boss.invincibility=value; }
    void update(const Context&,bullet::System&,gather::System&,spark::System&,
                randring::SharedRandomRing&,const Sink& sink={});
private:
    Snapshot state_{};
    std::vector<orange::Draw> draws_;
};
} // namespace th04::portable::reimu
