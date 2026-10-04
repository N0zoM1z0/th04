#pragma once
#include "enemy_bullets.hpp"

namespace th04::portable::midboss {
// Fixed-width owner of Stage 1's 22-byte DOS state and its three animation
// globals. Callback addresses become the active flag, never host pointers.
struct Snapshot {
    motion::Motion position{};
    std::uint16_t start_frame=3100;
    std::int16_t hp=800;
    std::uint8_t sprite=0,phase=0;
    std::int16_t phase_frame=0;
    std::uint8_t damaged=0,unused_angle=0;
    bool active=false;
    std::int16_t hp_bar=0,vram_y=0;
    std::uint8_t pattern_angle=0,defeat_angle=0;
};
enum class EventType { tile,sound,circle,homing,hit,hp,point,scroll,shake,zap,fire,item,gather };
struct Event {
    EventType type{};
    motion::Point position{};
    std::uint16_t value=0,count=0;
};
using Sink=std::function<void(const Event&)>;
struct Context {
    std::uint16_t frame=0;
    motion::Subpixel scroll_delta=0;
    std::int16_t scroll_line=0;
    std::uint8_t scroll_speed=0;
    bool scroll_active=true;
    bullet::Context bullets{};
    std::function<std::uint16_t(motion::Point,motion::Point)> hit;
};
struct Draw {
    int left=0,top=0,vram_top=0;
    unsigned pattern=0;
    bool white=false;
};
class System {
public:
    System();
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    void activate(std::uint16_t frame);
    void reset();
    void update(const Context& context,bullet::System& bullets,
                randring::SharedRandomRing& random,const Sink& sink={});
    // Called once per simulation frame. Repainting reads the cached list and
    // must not advance the defeat angle or consume the damage flash twice.
    void prepare_render(const Context& context);
    const std::vector<Draw>& draws() const { return draws_; }
    std::uint32_t score_delta() const { return score_delta_; }
private:
    Snapshot state_{};
    std::vector<Draw> draws_;
    std::uint32_t score_delta_=0;
};
} // namespace th04::portable::midboss
