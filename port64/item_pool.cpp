#include "item_pool.hpp"
#include <stdexcept>

namespace th04::portable::item {
void Pool::spawn(std::size_t slot, motion::Point position, Type type, Velocity velocity) {
    if (static_cast<unsigned>(type) > static_cast<unsigned>(Type::full_power)) {
        throw std::invalid_argument("invalid item type");
    }
    auto& entity = entities_[slot];
    entity.flag = Flag::alive;
    entity.position.current = position;
    entity.position.velocity = {velocity.x, velocity.y};
    entity.type = type;
    entity.pulled_to_player = false;
    spawned_ = static_cast<std::uint16_t>(spawned_ + 1u);
}

bool Pool::add(motion::Point position, Type type) {
    for (std::size_t i = 0; i < pool_size; ++i) {
        if (entities_[i].flag != Flag::free) continue;
        spawn(i, position, type, {0, -48});
        return true;
    }
    return false;
}

bool Pool::add_enemy_drop(motion::Point position, EnemyDropSequence& sequence) {
    // Advance before scanning the pool: even a full pool consumes the next
    // automatic-drop request. An odd request consumes no pool slot.
    const auto next = sequence.next();
    return next ? add(position, *next) : false;
}

MissSpawnResult Pool::add_miss(
    randring::SharedRandomRing& ring, motion::Point player,
    std::uint8_t remaining_lives
) {
    std::bitset<pool_size> free_slots;
    for (std::size_t i = 0; i < pool_size; ++i) {
        free_slots.set(i, entities_[i].flag == Flag::free);
    }
    const auto result = spawn_miss_items(ring, player.x, remaining_lives, free_slots);
    for (std::size_t i = 0; i < result.count; ++i) {
        const auto& entry = result.spawns[i];
        spawn(entry.pool_index, player, entry.type, entry.velocity);
    }
    return result;
}

UpdateResult Pool::update(
    ScoreState& score, motion::Point player, bool pull_to_player,
    std::uint8_t miss_time,
    const std::function<void(const CollectionEffects&,const ScoreState&)>& collected,
    const std::function<void(std::uint16_t)>& sound
) {
    UpdateResult result;
    for (std::size_t i = 0; i < pool_size; ++i) {
        auto& entity = entities_[i];
        auto& event = result.events[i];
        if (entity.flag == Flag::free) continue;
        if (entity.flag == Flag::remove) {
            // A removed sprite remains owned for one frame, giving the DOS
            // invalidator (or a future dirty host renderer) its previous
            // coordinates. Allocation cannot reuse it during that frame.
            entity.flag = Flag::free;
            continue;
        }
        if (pull_to_player) {
            entity.pulled_to_player = true;
            entity.position.velocity = motion::polar(
                motion::angle_to(entity.position.current, player), 160
            );
        } else if (entity.pulled_to_player) {
            entity.position.velocity = {};
            entity.pulled_to_player = false;
        }

        entity.position.update();
        const auto moved = entity.position.current;
        if (moved.x <= -128 || moved.x >= 392 * 16 || moved.y >= 376 * 16) {
            entity.flag = Flag::remove;
            event.missed = true;
            event.position = moved;
            event.miss = miss(score, entity.type);
            continue;
        }
        if (moved.y < -128) entity.position.current.y = -128;
        if (entity.position.velocity.y >= 0) entity.position.velocity.x = 0;

        // AX/DX retain the pre-clamp movement return in DOS. Use that point
        // for collision, then the stored (possibly clamped) Y for scoring.
        if (miss_time == 0 && overlaps_player_pickup_box(player.x, player.y, moved.x, moved.y)) {
            event.collected = true;
            event.position = entity.position.current;
            event.collection = collect(score, entity.type, entity.position.current.y, pull_to_player);
            if(collected)collected(event.collection,score);
            if(sound)sound(11);
            entity.flag = Flag::remove;
            continue;
        }
        entity.position.velocity.y = motion::wrap(std::int32_t(entity.position.velocity.y) + 1);
    }
    return result;
}
} // namespace th04::portable::item
