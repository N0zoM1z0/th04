#pragma once
#include "orange.hpp"
#include "thick_lasers.hpp"
namespace th04::portable::yuuka5 {
enum class Attack : std::uint8_t { sweep,clouds,gather,speedup_ring,aimed_spread,laser_burst,mirrored_streams };
struct Snapshot {
    orange::Snapshot boss{};
    std::int16_t sweep_x=0,midboss_frames_until=0;
    std::uint8_t cloud_step=0,cloud_accumulator=0,palette_tone=0,move_state=0;
    // The original writes a FAR nullfunc token, never a host-address pointer.
    // The game loop consumes this dispatch state to disable the STD VM.
    bool stage_vm_disabled=false;
};
using Context=orange::Context;
using Sink=orange::Sink;
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    bool move(std::uint16_t centered,randring::SharedRandomRing&);
    void pattern(Attack,const Context&,bullet::System&,gather::System&,laser::System&,
                 randring::SharedRandomRing&,const Sink& sink={});
    void update(const Context&,bullet::System&,gather::System&,laser::System&,
                randring::SharedRandomRing&,const Sink& sink={});
    void apply_departure(const transition::Departure& departure);
    void set_invincibility(std::uint8_t value) { state_.boss.invincibility=value; }
private:
    Snapshot state_{};
};
} // namespace th04::portable::yuuka5
