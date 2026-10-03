#include "item_system.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <stdexcept>

namespace th04::portable::item {
namespace {

constexpr std::array<Type, 64> enemy_drops{{
    Type::power, Type::point, Type::power, Type::power,
    Type::point, Type::point, Type::power, Type::point,
    Type::power, Type::point, Type::point, Type::point,
    Type::power, Type::power, Type::power, Type::dream,
    Type::point, Type::power, Type::point, Type::point,
    Type::power, Type::power, Type::point, Type::power,
    Type::point, Type::power, Type::power, Type::power,
    Type::point, Type::point, Type::point, Type::dream,
    Type::power, Type::point, Type::power, Type::power,
    Type::point, Type::point, Type::power, Type::point,
    Type::power, Type::point, Type::point, Type::point,
    Type::power, Type::power, Type::power, Type::dream,
    Type::point, Type::power, Type::point, Type::point,
    Type::power, Type::power, Type::point, Type::power,
    Type::point, Type::power, Type::power, Type::power,
    Type::point, Type::point, Type::point, Type::big_power,
}};

enum class MissField : std::uint8_t {
    left,
    center,
    right,
};

constexpr std::array<std::array<Velocity, miss_drop_count>, 3>
miss_velocities{{
    {{
        {to_subpixel(0), to_subpixel(-3)},
        {to_subpixel(0) + 12, to_subpixel(-3) - 8},
        {to_subpixel(1) + 8, to_subpixel(-4)},
        {to_subpixel(2) + 4, to_subpixel(-4) - 8},
        {to_subpixel(3), to_subpixel(-5)},
    }},
    {{
        {to_subpixel(-1) - 8, to_subpixel(-3)},
        {to_subpixel(0) - 12, to_subpixel(-3) - 8},
        {to_subpixel(0), to_subpixel(-4)},
        {to_subpixel(0) + 12, to_subpixel(-3) - 8},
        {to_subpixel(1) + 8, to_subpixel(-3)},
    }},
    {{
        {to_subpixel(0), to_subpixel(-3)},
        {to_subpixel(0) - 12, to_subpixel(-3) - 8},
        {to_subpixel(-1) - 8, to_subpixel(-4)},
        {to_subpixel(-2) - 4, to_subpixel(-4) - 8},
        {to_subpixel(-3), to_subpixel(-5)},
    }},
}};

constexpr std::array<std::uint16_t, 8> dream_score_per_items{{
    0, 100, 200, 400, 600, 800, 1000, 1280,
}};

constexpr std::array<std::uint16_t, power_overflow_max + 1>
power_overflow_bonus{{
    1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    20, 30, 40, 50, 60, 70, 80, 90, 100,
    150, 200, 250, 300, 350, 400, 450, 500, 550, 600,
    650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100,
    1200, 1250, 1280,
}};

MissField miss_field_for(Subpixel player_x) {
    if (player_x < to_subpixel(128)) {
        return MissField::left;
    }
    if (player_x <= to_subpixel(256)) {
        return MissField::center;
    }
    return MissField::right;
}

void add_wrapped(std::uint8_t& value, std::uint8_t delta) {
    value = static_cast<std::uint8_t>(
        static_cast<std::uint16_t>(value) + delta
    );
}

void increment_wrapped(std::uint16_t& value) {
    value = static_cast<std::uint16_t>(value + 1u);
}

void require_score_state_invariants(const ScoreState& state) {
    if (state.power > power_max || state.power_overflow < 0 ||
        state.power_overflow > power_overflow_max ||
        state.dream_items_collected > 7) {
        throw std::logic_error("portable item score state is outside TH04 bounds");
    }
}

std::uint16_t wrapped_axis_delta(
    Subpixel player, std::uint16_t player_bias, Subpixel item
) {
    const auto player_bits = static_cast<std::uint16_t>(player);
    const auto item_bits = static_cast<std::uint16_t>(item);
    return static_cast<std::uint16_t>(
        static_cast<std::uint32_t>(player_bits) + player_bias - item_bits
    );
}

} // namespace

void EnemyDropSequence::initialize(rng::Lcg32& process_random) {
    cycle_ = static_cast<std::uint8_t>(process_random.next15() & 0x0fu);
}

std::optional<Type> EnemyDropSequence::next() {
    cycle_ = static_cast<std::uint8_t>(cycle_ + 1u);
    if ((cycle_ & 1u) != 0) {
        return std::nullopt;
    }
    const auto index = static_cast<std::uint8_t>((cycle_ / 2u) % 64u);
    return enemy_drops[index];
}

MissSpawnResult spawn_miss_items(
    randring::SharedRandomRing& random_ring,
    Subpixel player_x,
    std::uint8_t remaining_lives,
    const std::bitset<pool_size>& free_slots
) {
    MissSpawnResult result;
    result.big_power_slot = static_cast<std::uint8_t>(
        random_ring.next16_mod(miss_drop_count)
    );
    ++result.ring_samples_consumed;
    do {
        result.discarded_distinct_slot = static_cast<std::uint8_t>(
            random_ring.next16_mod(miss_drop_count)
        );
        ++result.ring_samples_consumed;
    } while (result.discarded_distinct_slot == result.big_power_slot);

    const auto field = static_cast<std::size_t>(miss_field_for(player_x));
    for (std::size_t pool_index = 0; pool_index < pool_size; ++pool_index) {
        if (!free_slots.test(pool_index)) {
            continue;
        }

        const auto drop_slot = result.count;
        Type type;
        if (drop_slot == result.big_power_slot) {
            type = Type::big_power;
        } else {
            type = static_cast<Type>(random_ring.next16_and(1));
            ++result.ring_samples_consumed;
        }
        // Preserve call order: non-big slots consume their type draw before
        // the one-life override replaces the visible item type.
        if (remaining_lives == 1) {
            type = Type::full_power;
        }

        result.spawns[result.count] = {
            static_cast<std::uint8_t>(pool_index),
            drop_slot,
            type,
            miss_velocities[field][drop_slot],
        };
        ++result.count;
        if (result.count >= miss_drop_count) {
            break;
        }
    }
    return result;
}

CollectionEffects collect(
    ScoreState& state,
    Type type,
    Subpixel item_y,
    bool point_numbers_times_two
) {
    require_score_state_invariants(state);
    CollectionEffects effects;

    switch (type) {
    case Type::power:
        if (state.power < power_max) {
            if (state.power == power_max - 1u) {
                effects.bullets_cleared = true;
            }
            ++state.power;
            effects.shot_level_changed = true;
            effects.base_points = 1;
            break;
        }
        state.power_overflow = static_cast<std::int16_t>(
            std::min<std::int32_t>(
                static_cast<std::int32_t>(state.power_overflow) + 1,
                power_overflow_max
            )
        );
        effects.yellow_point_number = (
            state.power_overflow == power_overflow_max
        );
        effects.base_points = power_overflow_bonus[
            static_cast<std::size_t>(state.power_overflow)
        ];
        if (point_numbers_times_two) {
            add_wrapped(state.item_playperf_raise, 1);
        }
        break;

    case Type::point:
        if (item_y <= to_subpixel(52)) {
            effects.base_points = 5120;
            add_wrapped(
                state.item_playperf_raise,
                static_cast<std::uint8_t>(point_numbers_times_two ? 8 : 4)
            );
            increment_wrapped(state.max_valued_point_items);
            effects.yellow_point_number = true;
        } else {
            effects.base_points = static_cast<std::uint16_t>(
                3300 - (static_cast<std::int32_t>(item_y) / 2)
            );
            add_wrapped(
                state.item_playperf_raise,
                static_cast<std::uint8_t>(point_numbers_times_two ? 4 : 2)
            );
        }
        increment_wrapped(state.total_point_items_collected);
        effects.base_points = static_cast<std::uint16_t>(
            effects.base_points + state.dream_score
        );
        state.stage_point_items_collected = static_cast<std::uint8_t>(
            state.stage_point_items_collected + 1u
        );
        effects.hud_point_items_changed = true;
        break;

    case Type::dream:
        if (state.dream_items_collected <= 6) {
            ++state.dream_items_collected;
        }
        state.dream_score = dream_score_per_items[state.dream_items_collected];
        effects.base_points = state.dream_score;
        effects.hud_dream_changed = true;
        add_wrapped(
            state.item_playperf_raise,
            static_cast<std::uint8_t>(point_numbers_times_two ? 4 : 2)
        );
        break;

    case Type::big_power:
        if (state.power < power_max) {
            const auto raised_power = static_cast<std::uint16_t>(state.power) + 10u;
            if (raised_power >= power_max) {
                state.power = power_max;
                effects.bullets_cleared = true;
            } else {
                state.power = static_cast<std::uint8_t>(raised_power);
            }
            effects.shot_level_changed = true;
            effects.base_points = 1;
            break;
        }
        {
            const auto next_overflow = static_cast<std::int32_t>(
                state.power_overflow
            ) + 5;
            // The DOS source indexes before clamping, but every index at or
            // above 42 is then replaced by this fixed result. Branch first so
            // the portable build preserves the observable state without UB.
            if (next_overflow >= power_overflow_max) {
                state.power_overflow = power_overflow_max;
                effects.base_points = 2560;
                effects.yellow_point_number = true;
            } else {
                state.power_overflow = static_cast<std::int16_t>(next_overflow);
                effects.base_points = power_overflow_bonus[
                    static_cast<std::size_t>(state.power_overflow)
                ];
            }
        }
        break;

    case Type::bomb:
        state.remaining_bombs = static_cast<std::uint8_t>(
            state.remaining_bombs + 1u
        );
        effects.base_points = 100;
        effects.hud_bombs_changed = true;
        break;

    case Type::one_up:
        state.remaining_lives = static_cast<std::uint8_t>(
            state.remaining_lives + 1u
        );
        effects.base_points = 100;
        effects.hud_lives_changed = true;
        effects.extend_sound = true;
        effects.playperf_raised = 3;
        break;

    case Type::full_power:
        state.power = power_max;
        effects.base_points = 100;
        effects.shot_level_changed = true;
        effects.bullets_cleared = true;
        break;
    }

    effects.awarded_points = static_cast<std::uint32_t>(effects.base_points) *
        (point_numbers_times_two ? 2u : 1u);
    state.score_delta += effects.awarded_points;
    if (state.item_playperf_raise >= 32) {
        state.item_playperf_raise = static_cast<std::uint8_t>(
            state.item_playperf_raise - 32u
        );
        ++effects.playperf_raised;
    }
    increment_wrapped(state.items_collected);
    return effects;
}

MissEffects miss(ScoreState& state, Type type) {
    MissEffects effects;
    switch (type) {
    case Type::power:
    case Type::big_power:
        add_wrapped(state.item_playperf_lower, 1);
        break;
    case Type::point:
        add_wrapped(state.item_playperf_lower, 2);
        break;
    case Type::dream:
        add_wrapped(state.item_playperf_lower, 4);
        break;
    case Type::bomb:
        effects.playperf_lowered = 2;
        break;
    case Type::one_up:
        effects.playperf_lowered = 4;
        break;
    case Type::full_power:
        break;
    }
    if (state.item_playperf_lower >= 64) {
        state.item_playperf_lower = static_cast<std::uint8_t>(
            state.item_playperf_lower - 48u
        );
        ++effects.playperf_lowered;
    }
    return effects;
}

bool overlaps_player_pickup_box(
    Subpixel player_x,
    Subpixel player_y,
    Subpixel item_x,
    Subpixel item_y
) {
    const auto x = wrapped_axis_delta(player_x, to_subpixel(24), item_x);
    if (x > static_cast<std::uint16_t>(to_subpixel(48))) {
        return false;
    }
    const auto y = wrapped_axis_delta(player_y, to_subpixel(24), item_y);
    return y <= static_cast<std::uint16_t>(to_subpixel(38));
}

} // namespace th04::portable::item
