#pragma once
#include "motion.hpp"
#include "player_shots.hpp"
#include "stage_program.hpp"
#include <functional>

namespace th04::portable::enemy {
constexpr unsigned pool_size=32;
constexpr std::uint8_t free=0,alive=1,killed=2,first_frame=3,kill_animation=0x80;
enum class Opcode : std::uint8_t {
    kill=0x00,
    move_set_angle_speed=0x01,
    move_current_velocity=0x02,
    move_set_speed=0x03,
    move_turn=0x04,
    move_turn_with_acceleration=0x05,
    wait=0x06,
    move_cosine_x=0x07,
    move_cosine_y=0x08,
    aim_at_player=0x09,
    add_move_angle=0x0a,
    move_with_scroll=0x0b,
    add_move_speed=0x0c,
    move_turn_current=0x0d,
    move_turn_accel_current=0x0e,
    activate=0x10,
    randomize_move_angle=0x11,
    set_move_angle_speed=0x12,
    set_mirrored_angle_speed=0x13,
    set_move_speed=0x14,
    fire=0x20,
    set_bullet_template=0x21,
    set_bullet_spawn_type=0x22,
    set_bullet_offset=0x23,
    set_bullet_angle=0x24,
    add_bullet_angle=0x25,
    set_bullet_speed=0x26,
    add_bullet_speed=0x27,
    set_bullet_group=0x28,
    set_bullet_count=0x29,
    set_bullet_sprite=0x2a,
    autofire_on=0x2b,
    set_autofire_interval=0x2c,
    randomize_bullet_angle=0x2d,
    autofire_off=0x2e,
    set_bullet_spread_angle=0x30,
    loop_to_offset=0x80,
    loop_back=0x81,
    enable_x_clip=0x82,
    enable_y_clip=0x83,
    enable_xy_clip=0x84,
    set_animation=0x85,
    play_sound_effect=0x86,
    set_sprite=0x87,
    disable_damage_and_autofire=0x88,
    enable_damage_lunatic_autofire=0x89,
    set_position=0x8a,
    add_position=0x8b,
    disable_player_collision=0x8c,
    enable_player_collision=0x8d,
    add_sprite=0x8e,
    set_tile_ring=0x8f,
};
struct BulletTemplate {
    std::uint8_t spawn_type=0,pattern=0;
    motion::Point origin{},velocity{};
    std::uint8_t group=0,angle=0,speed=0,count=0,delta=0,unused_1=0,special_motion=0,unused_2=0;
};
struct Entity {
    std::uint8_t flag=free,age=0;
    motion::Motion position{};
    std::uint8_t pattern=0,unused_1=0;
    std::int16_t hp=0,unused_2=0,score=0;
    std::uint16_t script=0xffff; // no script, instead of DOS's null near pointer
    std::int16_t ip=0;
    std::uint8_t instruction_frame=0,loop=0;
    motion::Subpixel speed=0;
    std::uint8_t angle=0,angle_delta=0,clip_x=0,clip_y=0,unused_3=0,item=0,damaged=0;
    std::uint8_t animation_cels=0,frames_per_cel=0,cel=0,can_be_damaged=0,autofire=0;
    std::uint8_t player_collision=0,left_half=0;
    BulletTemplate bullet{};
    std::uint8_t autofire_frame=0,autofire_interval=0;
};
struct Context {
    motion::Point player{};
    motion::Subpixel scroll_delta=0;
    std::int16_t performance=16;
    std::uint8_t rank=1,frame_mod2=0,frame_mod4=0;
    bool bombing=false;
};
enum class EventType { fire,sound,tile_ring,drop,sparks };
struct Event {
    EventType type{};
    motion::Point position{};
    std::uint16_t value=0,count=0;
    BulletTemplate bullet{};
};
// Dispatch events synchronously: a future bullet/spark adapter must consume
// shared RNG at this exact boundary, before the next script instruction.
using Sink=std::function<void(const Event&)>;
bool run_script(Entity& entity,const stage::Program::Bytes& script,Context context,
                randring::SharedRandomRing& random,std::uint16_t& gone,const Sink& sink);
struct RenderSprite {
    bool visible=false,white=false;
    std::uint8_t pattern=0;
    motion::Point position{};
};
struct Snapshot {
    std::array<Entity,pool_size> entities{};
    std::uint16_t gone=0,killed_count=0;
    std::uint32_t score_delta=0;
    std::optional<motion::Point> homing_target{};
    bool player_hit=false;
};
class System {
public:
    explicit System(Snapshot initial={}):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    bool add(stage::Spawn spawn,Context context,randring::SharedRandomRing& random);
    void update(const stage::Program& program,Context context,randring::SharedRandomRing& random,
                shot::System& shots,const Sink& sink);
    void prepare_render();
    const std::array<RenderSprite,pool_size>& render_sprites() const { return render_; }
private:
    Snapshot state_;
    std::array<RenderSprite,pool_size> render_{};
};
} // namespace th04::portable::enemy
