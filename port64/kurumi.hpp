#pragma once
#include "orange.hpp"

namespace th04::portable::kurumi {
// The actual custom-entity view is six 26-byte records: byte flag, one
// retained byte, three signed point pairs, then twelve retained bytes.
struct Spawnray {
    std::uint8_t flag=0,unused=0;
    motion::Point target{},origin{},velocity{};
    std::array<std::uint8_t,12> padding{};
};
struct Snapshot {
    // BOSS, bonus, explosion and departure state have the same target owners
    // as Orange. Its patterns and custom entities belong to this system.
    orange::Snapshot boss{};
    std::array<Spawnray,6> rays{};
    std::uint8_t turn_toggle=0,unknown_state=0;
};
using Context=orange::Context;
using Event=orange::Event;
using EventType=orange::EventType;
using Sink=orange::Sink;
using Draw=orange::Draw;
using DrawKind=orange::DrawKind;
enum class BackdropKind { all_tiles,dirty_tiles,picture,picture_and_tiles };
struct Backdrop {
    BackdropKind kind=BackdropKind::all_tiles;
    std::int16_t mask_cel=0;
};
Backdrop backdrop(const orange::Snapshot&);
// Stage2 setup resets the selected BOSS fields and two small alive flags.
// Process-global palette/clock resets belong to stage session initialization.
Snapshot prepare_stage2(orange::Snapshot previous,unsigned rank);
// Actual rays stay within the default640x400 clip. This raster uses the
// original16-bit fixed-point line stepping; generalized clipping is separate.
std::vector<motion::Point> ray_pixels(motion::Point target,motion::Point origin);
class System {
public:
    explicit System(unsigned rank=1);
    explicit System(Snapshot state):state_(state) {}
    const Snapshot& snapshot() const { return state_; }
    void update(const Context&,bullet::System&,gather::System&,spark::System&,
                randring::SharedRandomRing&,const Sink& sink={});
    void prepare_render(std::uint16_t frame);
    void apply_departure(const transition::Departure&);
    void set_palette_zero(std::array<std::uint8_t,3> value) { state_.boss.palette_zero=value; }
    void set_invincibility(std::uint8_t value) { state_.boss.invincibility=value; }
    void set_graphics(std::uint16_t tone,std::uint8_t color) { state_.boss.palette_tone=tone;state_.boss.circle_color=color; }
    const std::vector<Draw>& draws() const { return draws_; }
private:
    Snapshot state_{};
    std::vector<Draw> draws_;
};
} // namespace th04::portable::kurumi
