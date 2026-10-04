#pragma once
#include "item_system.hpp"
#include "motion.hpp"

namespace th04::portable::item {
enum class Flag : std::uint8_t { free, alive, remove };
struct Entity {
    Flag flag = Flag::free;
    motion::Motion position{};
    Type type = Type::power;
    bool pulled_to_player = false;
};
struct UpdateEvent {
    bool collected = false;
    bool missed = false;
    motion::Point position{};
    CollectionEffects collection{};
    MissEffects miss{};
};
struct UpdateResult {
    // Slot order is part of score and side-effect ordering. A fixed array
    // retains it without allocating once per frame or losing simultaneous
    // pickups when the pool is full.
    std::array<UpdateEvent, pool_size> events{};
};

class Pool {
public:
    const std::array<Entity, pool_size>& entities() const { return entities_; }
    std::uint16_t spawned() const { return spawned_; }
    // Stage initialization clears entity storage, but not this run's counter.
    void reset_stage() { entities_={}; }
    bool add(motion::Point position, Type type);
    bool add_enemy_drop(motion::Point position, EnemyDropSequence& sequence);
    MissSpawnResult add_miss(
        randring::SharedRandomRing& ring, motion::Point player,
        std::uint8_t remaining_lives
    );
    UpdateResult update(
        ScoreState& score, motion::Point player, bool pull_to_player,
        std::uint8_t miss_time
    );

private:
    void spawn(std::size_t slot, motion::Point position, Type type, Velocity velocity);
    std::array<Entity, pool_size> entities_{};
    std::uint16_t spawned_ = 0;
};
} // namespace th04::portable::item
