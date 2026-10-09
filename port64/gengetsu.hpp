#pragma once
#include "orange.hpp"
#include "thick_lasers.hpp"
namespace th04::portable::gengetsu {
enum class Attack : std::uint8_t { ring, spread_pair, bounce, turn_gather, cycle,
    aimed_spread, mirror_spread, columns, random_ring, dual_clusters, cloud_ring, blue_ring };
struct Column {
    std::array<std::uint8_t,2> unused{};
    motion::Point position{};
    std::array<std::uint8_t,20> padding{};
};
struct Snapshot {
    orange::Snapshot boss{};
    std::array<Column,16> columns{};
    laser::Snapshot lasers{};
    std::int16_t wave_target=0;
    std::uint8_t wave_amplitude=0,flash=0,bomb_invincibility=0;
};
struct Context : orange::Context { bool bombing=false; };
// Resume MAIN13A9:AD8A..AE0A after the retained second Extra dialogue.
// Reset only boss_reset() fields; shared lasers, columns and Bomb shield survive.
Snapshot prepare_after_dialog(Snapshot);
// Original body/explosion/laser request fields; kind11 is SUPER_WAVE_PUT.
struct Draw {
    unsigned kind=0;std::int16_t x=0,y=0;std::uint16_t value=0,color=0;
    std::int16_t end_x=0,end_y=0;std::uint16_t mode=0;
    std::int16_t wavelength=0;std::uint16_t amplitude=0,phase=0;
};
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    void gather_intro(bullet::System&,gather::System&,const orange::Sink& sink={});
    bool wave_step();
    bool wave_bounce();
    unsigned phase_state(const Context&,bullet::System&,gather::System&,const orange::Sink& sink={});
    bool hit(const Context&,const orange::Sink& sink={});
    void pattern(Attack,const Context&,bullet::System&,gather::System&,randring::SharedRandomRing&,const orange::Sink& sink={});
    void update(const Context&,bullet::System&,gather::System&,randring::SharedRandomRing&,const orange::Sink& sink={});
    // Execute once per MAIN foreground boundary; repaints consume cached draws.
    // The original pushes the adjacent amplitude byte in its WORD argument.
    void prepare_render(std::uint16_t frame,std::uint8_t amplitude_adjacent=0);
    const std::vector<Draw>& draws() const {return draws_;}
    void set_invincibility(std::uint8_t value) {state_.boss.invincibility=value;}
    void set_player_hit(std::uint8_t value) {state_.lasers.player_hit=value;}
    void set_graphics(std::uint16_t tone,std::uint8_t color) {state_.boss.palette_tone=motion::wrap(tone);state_.boss.circle_color=color;}
    void apply_departure(const transition::Departure& d) {
        state_.boss.phase_frame=d.frame;state_.boss.homing=d.homing;
        state_.boss.palette_tone=d.palette_tone;state_.boss.palette_changed=d.palette_changed;
    }
private:
    Snapshot state_{};
    std::vector<Draw> draws_;
};
}
