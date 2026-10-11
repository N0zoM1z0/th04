#pragma once
#include "item_system.hpp"
#include "motion.hpp"
#include <functional>
#include <vector>

namespace th04::portable::item {
enum class Flag : std::uint8_t { free, alive, remove };
struct Splash {
    std::uint8_t flag=0,time=0;
    motion::Point center{};
    motion::Subpixel radius=0,previous_radius=0;
};
struct SplashState {
    std::array<Splash,8> entities{};
    std::uint8_t cursor=0;
};
class Splashes {
public:
    explicit Splashes(SplashState initial={}):state_(initial) {}
    const SplashState& snapshot() const { return state_; }
    void reset_stage() { state_={}; }
    bool add(motion::Point center);
    void update();
    // Screen pixels relative to the drawing scroll line, before shake.
    std::vector<motion::Point> dots() const;
private:
    SplashState state_{};
};
struct Entity {
    Flag flag = Flag::free;
    motion::Motion position{};
    Type type = Type::power;
    bool pulled_to_player = false;
    // Original item_t retains both spare bytes and its selected sprite WORD.
    std::uint8_t unused = 0, unknown = 0;
    std::uint16_t pattern = 0;
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
    const Splashes& splashes() const { return splashes_; }
    // Stage initialization clears entity storage, but not this run's counter.
    void reset_stage() { entities_={};splashes_.reset_stage(); }
    bool add(motion::Point position, Type type);
    bool add_enemy_drop(motion::Point position, EnemyDropSequence& sequence);
    MissSpawnResult add_miss(
        randring::SharedRandomRing& ring, motion::Point player,
        std::uint8_t remaining_lives
    );
    UpdateResult update(
        ScoreState& score, motion::Point player, bool pull_to_player,
        std::uint8_t miss_time,
        const std::function<void(const CollectionEffects&,const ScoreState&)>& collected={},
        const std::function<void(std::uint16_t)>& sound={}
    );

private:
    void spawn(std::size_t slot, motion::Point position, Type type, Velocity velocity);
    std::array<Entity, pool_size> entities_{};
    std::uint16_t spawned_ = 0;
    Splashes splashes_{};
};
} // namespace th04::portable::item
