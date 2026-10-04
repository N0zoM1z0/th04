#pragma once
#include "effects.hpp"
#include "stage_transition.hpp"

namespace th04::portable::orange {
struct Explosion {
    std::uint8_t alive=0,age=0;
    motion::Point center{},radius{},delta{};
    std::int8_t unused=0;
    std::uint8_t angle_offset=0;
};
enum class Background : std::uint8_t { unchanged,orange,tiles };
struct Snapshot {
    motion::Motion position{};
    std::int16_t hp=0;
    std::uint8_t sprite=128,phase=0;
    std::int16_t phase_frame=0;
    std::uint8_t damage=0,mode=0,angle=0,patterns_or_bonus=0;
    std::int16_t end_hp=0;
    std::array<std::uint8_t,16> additional{};
    motion::Point hitbox_radius{384,256},homing{};
    std::uint8_t timed_out=1;
    std::array<std::uint8_t,3> palette_zero{};
    std::uint8_t palette_changed=0,circle_color=0,tile_column=0,invincibility=0;
    std::array<Explosion,2> small{};
    Explosion big{};
    Background background=Background::unchanged;
    std::int16_t shake_x=0,shake_y=0;
    std::uint16_t slowdown=1;
    std::uint8_t bombing_disabled=0,point_times_two=0;
    std::uint32_t score_delta=0;
    std::int16_t big_frame=0,palette_tone=100;
};
enum class DrawKind { sprite,white_sprite,large_sprite,tiny_sprite,circle,line };
struct Draw {
    DrawKind kind{};
    std::int16_t left=0,top=0;
    std::uint16_t pattern_or_radius=0;
    std::uint8_t color=0;
    std::int16_t end_left=0,end_top=0;
};
enum class EventType { sound,hit,circle,point,item,hp,dialog,stage_bonus,fade,next_stage,delay,tone };
struct Event {
    EventType type{};
    motion::Point position{};
    std::uint16_t value=0,count=0;
};
using Sink=std::function<void(const Event&)>;
struct Context {
    std::uint16_t frame=0;
    std::uint8_t power=0;
    bullet::Context bullets{};
    // Shot adapter must apply the original against-boss flag (bomb damage),
    // and publish sparks/shot-score effects before returning the damage word.
    std::function<std::uint16_t(motion::Point,motion::Point)> hit;
};
// The original boss_defeat_update is shared by ordinary bosses. Keep it
// separate from Orange's pattern-specific gather-template writes.
void update_defeat(Snapshot&,const Context&,const Sink& sink={});
// Original ordinary bosses call the same small/big explosion render owners.
void prepare_explosions(Snapshot&,std::vector<Draw>&);
class System {
public:
    System();
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    // Caller activates this owner only after the pre-boss dialog completes.
    // STD exhaustion alone does not authorize skipping that blocking boundary.
    void update(const Context&,bullet::System&,gather::System&,spark::System&,
                randring::SharedRandomRing&,const Sink& sink={});
    // Exactly once per simulated frame. Host repaints read this cached list.
    void prepare_render(std::uint16_t frame);
    void apply_departure(const transition::Departure&);
    const std::vector<Draw>& draws() const { return draws_; }
private:
    Snapshot state_{};
    std::vector<Draw> draws_;
};
} // namespace th04::portable::orange
