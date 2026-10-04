#pragma once
#include "orange.hpp"
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
Snapshot prepare_stage4(orange::Snapshot previous,unsigned rank);
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    void add_moving();
    void add_spinning(std::uint8_t angle_offset,std::int16_t count);
    void update_orbs(const Context&,const Sink& sink={});
    void pulse();
    void update(const Context&,bullet::System&,gather::System&,spark::System&,
                randring::SharedRandomRing&,const Sink& sink={});
private:
    Snapshot state_{};
};
} // namespace th04::portable::reimu
