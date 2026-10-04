#pragma once
#include "orange.hpp"

namespace th04::portable::laser { class System; }
namespace th04::portable::yuuka6 {
class Entities;
class Foreground;
// One clock is shared by every animation. Callers choose when to change an
// animation; choosing one does not itself reset the counter or sprite flag.
// MAIN13A9:6AAD..6E76 owns these eight animation entries.
enum class Animation : std::uint8_t {
    close,open,pull_forward,pull_left,spin_back,vanish,appear,shield
};
enum class Gathering : std::uint8_t { side,pair,center,dual,self };
enum class Attack : std::uint8_t {
    ring_turn,spin_rings,gravity,safety_circle,bullets,dual_lasers,
    dual_spreads,rotating_ring,growing_ring,chase_crosses,
    alternating_rings,dual_aimed_spreads
};
struct Snapshot {
    orange::Snapshot boss{};
    std::uint8_t sprite_flag=0,fly_path=0,aux_flag=0,unused_animation=0;
    std::int16_t animation_frame=0;
    motion::Point mirror{};
    std::uint8_t mirror_state=0;
    // Process-owned dispatch and ordinary-shot scratch, separate from the
    // boss hitbox. The mirror's stored damage is a BYTE, not the shot WORD.
    std::uint8_t mirror_damage=0,pattern_previous=0;
    std::int16_t midboss_frames_until=0;
    bool stage_vm_disabled=false;
    motion::Point shot_center{},shot_radius{};
};
struct Context : orange::Context {
    // Ordinary shots do not set against-boss or add Bomb damage. Both the
    // mirror and custom crosses use this callback; the main body uses hit.
    std::function<std::uint16_t(motion::Point,motion::Point)> ordinary_hit;
};
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    bool animate(Animation);
    // These helpers do not advance phase_frame. The dispatcher/hit-test owns
    // that increment; the completion cases reset it and increment the BYTE
    // patterns counter. Both clocks retain explicit signed 16-bit wrapping.
    bool phase2_fly();
    bool move_towards(motion::Point destination);
    void horizontal_wave();
    bool move_to_center();
    // All entries retain the same gather/bullet templates. They neither
    // advance phase_frame nor update the resulting entity pools. A caller
    // owns the frame prefix/tail. An attack can reset phase_frame after an
    // animation completes, before a later gather test within the same call.
    void gathering(Gathering,gather::System&,const bullet::Template&,
                   const orange::Sink& sink={});
    void attack(Attack,const orange::Context&,bullet::System&,gather::System&,
                laser::System&,Entities&,randring::SharedRandomRing&,
                const orange::Sink& sink={});
    bool mirror_hittest(const Context&,const orange::Sink& sink={});
    void phase_next(unsigned explosion_type,std::int16_t end_hp,
                    bullet::System&,const orange::Sink& sink={});
    void update(const Context&,bullet::System&,gather::System&,spark::System&,
                laser::System&,Entities&,randring::SharedRandomRing&,
                const orange::Sink& sink={});
private:
    friend class Foreground; // Rendering consumes visible hit bytes in the core state.
    Snapshot state_{};
};
} // namespace th04::portable::yuuka6
