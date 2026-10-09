#pragma once
#include "orange.hpp"
namespace th04::portable::mugetsu {
enum class Transition : std::uint8_t { first, teleport, long_teleport };
enum class Attack : std::uint8_t { accelerating_ring, cross_turns, cloud_ring, random_turns, random_rings, final_rings, saturation };
struct Snapshot {
    orange::Snapshot boss{};
    motion::Point anchor{};
    std::int16_t gather_offset=0,midboss_frames_until=0;
    Transition transition=Transition::first;
    std::uint8_t cycle=0,flash=0,bomb_invincibility=0;
    bool stage_vm_disabled=false;
};
struct Context : orange::Context { bool bombing=false; };
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    unsigned transition(const Context&,bullet::System&,gather::System&,const orange::Sink& sink={});
    void pattern(Attack,const Context&,bullet::System&,gather::System&,randring::SharedRandomRing&,const orange::Sink& sink={});
    void update(const Context&,bullet::System&,gather::System&,randring::SharedRandomRing&,const orange::Sink& sink={});
    void prepare_render();
    const std::vector<orange::Draw>& draws() const { return draws_; }
    void set_invincibility(std::uint8_t value) { state_.boss.invincibility=value; }
    void set_graphics(std::uint16_t tone,std::uint8_t color) { state_.boss.palette_tone=motion::wrap(tone);state_.boss.circle_color=color; }
private:
    Snapshot state_{};
    std::vector<orange::Draw> draws_;
};
// Shared Mugetsu/Gengetsu background request order. kind0=all tiles,
// 1=dirty tiles,2=picture,3=BB mask,4=lower filler,5=null stage renderer.
struct BackgroundDraw { unsigned kind=0;int x=0,y=0,value=0; };
std::vector<BackgroundDraw> background(std::uint8_t phase,std::int16_t clock);
}
