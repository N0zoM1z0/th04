#pragma once
#include "orange.hpp"

namespace th04::portable::yuuka6 {
// MAIN DATA:B204 is a shared32x26-byte pool. Allocating a cross scans all32
// records; update/render scan31 and reinterpret record31 as a safety circle.
// Explicit fields preserve that alias without host unions, packing or casts.
struct EntitySlot {
    std::uint8_t flag=0,angle=0;
    motion::Point center{};
    std::array<std::uint8_t,4> unused_position{};
    motion::Point velocity{};
    std::uint16_t age=0;
    // Spare words for crosses; radius/ring distance for the final circle.
    std::int16_t filled_radius=0,ring_distance=0,hp=0,damage=0;
    std::uint8_t speed=0,padding=0;
};
struct EntitySnapshot {
    std::array<EntitySlot,32> slots{};
    motion::Point hit_center{},hit_radius{};
    // These are shared process globals. A live caller must bridge them once
    // per frame with bullet/boss state, not create a separate score stream.
    std::uint8_t player_hit=0;
    std::uint32_t score_delta=0;
};
struct EntityContext {
    std::uint16_t frame=0;
    motion::Point boss_origin{};
    bullet::Context bullets{};
    // Crosses use ordinary shots_hittest, with against-boss=false and WORD
    // damage. A boss hit callback would incorrectly add Bomb damage here.
    std::function<std::uint16_t(motion::Point,motion::Point)> hit;
};
enum class EntityDrawKind : std::uint8_t {
    sprite,white_sprite,mode,color,filled_circle,ring_circle,disable
};
struct EntityDraw {
    EntityDrawKind kind{};
    motion::Point position{};
    std::uint16_t value=0;
};
class Entities {
public:
    explicit Entities(EntitySnapshot initial={}):state_(initial) {}
    const EntitySnapshot& snapshot() const { return state_; }
    bool add_cross(motion::Point origin,std::uint8_t angle,std::uint8_t speed);
    void add_safety_circle(motion::Point player,const orange::Sink& sink={});
    void update(const EntityContext&,bullet::System&,spark::System&,
                randring::SharedRandomRing&,const orange::Sink& sink={});
    // The original ages death flags during drawing. Call once per simulated
    // frame, then reuse draws() for cached repaints without advancing again.
    void prepare_render();
    const std::vector<EntityDraw>& draws() const { return draws_; }
private:
    EntitySnapshot state_{};
    std::vector<EntityDraw> draws_;
};
} // namespace th04::portable::yuuka6
