#pragma once

#include <array>
#include <bitset>
#include <cstddef>
#include <cstdint>
#include <optional>

#include "random_lcg.hpp"
#include "random_ring.hpp"

namespace th04::portable::item {

using Subpixel = std::int16_t;

constexpr Subpixel to_subpixel(int pixels) {
    return static_cast<Subpixel>(pixels * 16);
}

enum class Type : std::uint8_t {
    power = 0,
    point = 1,
    dream = 2,
    big_power = 3,
    bomb = 4,
    one_up = 5,
    full_power = 6,
};

// The byte counter is independent of the fixed pool. Automatic enemy drops
// advance it even when the odd half-cycle produces no item or a later pool
// allocation fails.
class EnemyDropSequence {
public:
    EnemyDropSequence() = default;
    explicit EnemyDropSequence(std::uint8_t cycle) : cycle_(cycle) {}

    void initialize(rng::Lcg32& process_random);
    std::optional<Type> next();
    std::uint8_t cycle() const { return cycle_; }

private:
    std::uint8_t cycle_ = 0;
};

struct Velocity {
    Subpixel x = 0;
    Subpixel y = 0;
};

struct MissSpawn {
    std::uint8_t pool_index = 0;
    std::uint8_t drop_slot = 0;
    Type type = Type::power;
    Velocity velocity{};
};

constexpr std::size_t pool_size = 32;
constexpr std::size_t miss_drop_count = 5;

struct MissSpawnResult {
    std::array<MissSpawn, miss_drop_count> spawns{};
    std::uint8_t count = 0;
    std::uint8_t big_power_slot = 0;
    std::uint8_t discarded_distinct_slot = 0;
    std::uint16_t ring_samples_consumed = 0;
};

// A set bit represents one free entry in the historical fixed item pool.
MissSpawnResult spawn_miss_items(
    randring::SharedRandomRing& random_ring,
    Subpixel player_x,
    std::uint8_t remaining_lives,
    const std::bitset<pool_size>& free_slots
);

constexpr std::uint8_t power_max = 128;
constexpr std::int16_t power_overflow_max = 42;

struct ScoreState {
    std::uint8_t power = 0;
    std::int16_t power_overflow = 0;
    std::uint8_t dream_items_collected = 0;
    std::uint16_t dream_score = 0;
    std::uint8_t item_playperf_raise = 0;
    std::uint8_t item_playperf_lower = 0;
    std::uint32_t score_delta = 0;
    std::uint16_t max_valued_point_items = 0;
    std::uint16_t total_point_items_collected = 0;
    std::uint8_t stage_point_items_collected = 0;
    std::uint16_t items_collected = 0;
    std::uint8_t remaining_bombs = 0;
    std::uint8_t remaining_lives = 0;
};

struct CollectionEffects {
    std::uint16_t base_points = 0;
    std::uint32_t awarded_points = 0;
    bool yellow_point_number = false;
    bool shot_level_changed = false;
    bool bullets_cleared = false;
    bool hud_bombs_changed = false;
    bool hud_lives_changed = false;
    bool hud_point_items_changed = false;
    bool hud_dream_changed = false;
    bool extend_sound = false;
    std::uint8_t playperf_raised = 0;
};

CollectionEffects collect(
    ScoreState& state,
    Type type,
    Subpixel item_y,
    bool point_numbers_times_two
);

struct MissEffects {
    std::uint8_t playperf_lowered = 0;
};

MissEffects miss(ScoreState& state, Type type);

// The DOS code performs both comparisons with wrapped unsigned 16-bit
// subtraction. This helper makes the wrap explicit and avoids host signed
// overflow while retaining the asymmetric vertical pickup interval.
bool overlaps_player_pickup_box(
    Subpixel player_x,
    Subpixel player_y,
    Subpixel item_x,
    Subpixel item_y
);

} // namespace th04::portable::item
