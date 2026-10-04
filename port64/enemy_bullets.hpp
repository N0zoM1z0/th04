#pragma once
#include "bullet_geometry.hpp"
#include "enemy_system.hpp"

namespace th04::portable::bullet {
using Template = enemy::BulletTemplate;
constexpr unsigned pellet_count=240,large_count=200,pool_size=pellet_count+large_count;
enum class Spawn : std::uint8_t { pellet=1,large=2,gather_pellet=3,cloud_forward=4,cloud_backward=5 };
enum class Phase : std::uint8_t { grazeable=0,grazed=1,active=2,cloud_backward=3,cloud_forward=4,cloud_end=20 };
enum class Movement : std::uint8_t { decelerate=0,special=1,regular=2,decay=4,decay_end=20 };
enum class Special : std::uint8_t {
    decelerate_aim=128,decelerate_turn=129,accelerate=130,decelerate_to_angle=131,
    bounce_x=132,bounce_y=133,bounce_xy=134,bounce_x_top=135,gravity=136
};
struct Entity {
    std::uint8_t flag=0,age=0;
    motion::Motion position{};
    std::uint8_t group=0,unused=0,speed=0,angle=0;
    Phase phase=Phase::grazeable;
    Movement movement=Movement::decelerate;
    std::uint8_t special=0,final_speed=0,timer_or_turns=0,delta_or_angle=0;
    std::uint16_t pattern=0;
};
struct Context {
    motion::Point player{};
    std::uint8_t rank=1,performance=16,frame_mod2=0,invincibility=0;
    bool turbo=false;
    std::uint16_t graze_score=250;
};
enum class EventType { sparks,point_number,bonus_popup,gather };
struct Event {
    EventType type{};
    motion::Point position{};
    std::uint16_t value=0,count=0;
    Template bullet{};
};
using Sink=std::function<void(const Event&)>;
struct Snapshot {
    std::array<Entity,pool_size> entities{};
    // One process-wide scratch template: script FIRE retains unused fields,
    // while enemy autofire transfers the complete 18-byte template.
    Template scratch{};
    std::array<bool,pellet_count> pellet_visible{};
    std::uint8_t special_parameter=0,special_angle=0,clear_time=0,zap_frame=0;
    std::uint16_t graze=0,slowdown=1;
    std::uint32_t score_delta=0,bonus=0;
    bool player_hit=false;
};
std::uint8_t pellet_pixel(unsigned x,unsigned y);
void tune(Template& bullet,std::uint8_t rank,std::uint8_t performance);
class System {
public:
    explicit System(Snapshot initial={}):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    Template& scratch() { return state_.scratch; }
    void fire(const enemy::Event& event,Context context,randring::SharedRandomRing& random,const Sink& sink={});
    void release(const Template& saved,Context context,randring::SharedRandomRing& random,const Sink& sink={});
    void add(Template& bullet,Context context,randring::SharedRandomRing& random,
             bool special=false,bool fixed_speed=false,const Sink& sink={});
    void update(Context context,const Sink& sink={});
    void clear() { if (state_.clear_time<20) state_.clear_time=20; }
    void zap() { state_.zap_frame=1; } // Active flag and timer are the same byte.
    void set_zap(std::uint8_t value) { state_.zap_frame=value; }
    // Process-wide special-motion controls survive producer changes. Boss
    // patterns write these separately from the shared 18-byte template.
    void set_special_parameter(std::uint8_t value) { state_.special_parameter=value; }
    void set_special_angle(std::uint8_t value) { state_.special_angle=value; }
    void set_player_hit(bool value) { state_.player_hit=value; }
    void begin_frame() { state_.slowdown=1; }
private:
    void update_special(Entity& bullet,Context context);
    Snapshot state_;
};
} // namespace th04::portable::bullet
