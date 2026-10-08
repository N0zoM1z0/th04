#pragma once
#include "application_state.hpp"
#include "motion.hpp"
#include "random_ring.hpp"
#include <array>
#include <optional>

namespace th04::portable::shot {
constexpr unsigned pool_size = 68;
constexpr std::uint16_t input_shot = 0x0020;
constexpr std::uint8_t free = 0, alive = 1, hit = 2, remove = 18;
struct Entity {
    std::uint8_t flag = free, age = 0;
    motion::Motion position{};
    std::uint16_t pattern = 0;
    std::uint8_t damage = 0, unused_angle = 0;
};
enum class LaserStyle : std::uint8_t { two, four, six, one_four_one, eight };
struct Laser {
    std::uint16_t time = 0;
    LaserStyle style = LaserStyle::two;
    std::uint8_t ring_cycle = 0;
    motion::Motion bottom{};
    unsigned cel() const;
    std::uint8_t dots() const;
};
struct CacheEntry { motion::Point position{}; std::uint16_t index = 0; };
struct Snapshot {
    std::array<Entity,pool_size> entities{};
    std::array<CacheEntry,pool_size> collision_cache{};
    std::uint16_t alive_count = 0;
    std::uint8_t time = 0, reimu_cycle = 0, spark_cycle = 0;
    Laser laser{};
    motion::Point options{};
    std::uint32_t score_delta = 0;
};
struct HitResult {
    std::uint16_t damage = 0;
    std::array<motion::Point,pool_size+2> sparks{};
    unsigned spark_count = 0;
};
struct HitContext {
    bool bombing = false, against_boss = false;
    std::uint8_t frame_mod2 = 0, frame_mod4 = 0;
};
unsigned level_for_power(std::uint8_t power);

// Snapshot is a portable checkpoint, not the segmented DOS structure layout.
// Requests for sound/sparks stay outside this owner so adapters can dispatch
// them at the original call boundaries using the shared process state.
class System {
public:
    explicit System(Snapshot initial = {});
    const Snapshot& snapshot() const { return state_; }
    void limit_laser_time(std::uint16_t maximum) {
        if(state_.laser.time>maximum)state_.laser.time=maximum;
    }
    void set_options(motion::Point options) {state_.options=options;}
    bool advance_trigger(bool pressed);
    void fire(application::Playchar character, application::ShotType type,
              unsigned level, motion::Point player,
              randring::SharedRandomRing& random,
              std::optional<motion::Point> homing_target = {});
    void update_entities(motion::Point options);
    bool update(bool pressed, application::Playchar character,
                application::ShotType type, std::uint8_t power,
                const motion::Motion& player, randring::SharedRandomRing& random,
                std::optional<motion::Point> homing_target = {});
    HitResult hittest(motion::Point center, motion::Point radius, HitContext context);
private:
    Entity* allocate(motion::Point player);
    void laser_fire(unsigned level, motion::Point player);
    Snapshot state_;
    unsigned allocation_cursor_ = 0;
};
} // namespace th04::portable::shot
