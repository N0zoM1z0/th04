#include "player_shots.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::shot {
namespace {
using application::Playchar;
using application::ShotType;
void offset(Entity& entity, int pixels) {
    entity.position.current.x = motion::wrap(std::int32_t(entity.position.current.x)+pixels*16);
}
void aim(Entity& entity, int angle, int speed = 192) {
    entity.position.velocity = motion::polar(static_cast<std::uint8_t>(angle),static_cast<motion::Subpixel>(speed));
}
} // namespace

unsigned level_for_power(std::uint8_t power) {
    constexpr std::uint8_t thresholds[]{6,12,16,24,32,48,72,96,128};
    unsigned level = 0;
    while (level < 9 && power >= thresholds[level]) ++level;
    return level;
}
unsigned Laser::cel() const {
    if (style == LaserStyle::two || time <= 40) return 0;
    if (style == LaserStyle::four || time <= 48) return 1;
    if (style == LaserStyle::six || time <= 56) return 2;
    return style == LaserStyle::one_four_one ? 3 : 4;
}
std::uint8_t Laser::dots() const {
    constexpr std::uint8_t masks[]{0x18,0x3c,0x7e,0xbd,0xff};
    return masks[cel()];
}
System::System(Snapshot initial) : state_(initial) {
    if (state_.alive_count > pool_size || static_cast<unsigned>(state_.laser.style) > 4) {
        throw std::invalid_argument("invalid portable shot checkpoint");
    }
    for (unsigned i=0; i<state_.alive_count; ++i) {
        if (state_.collision_cache[i].index >= pool_size) throw std::invalid_argument("invalid shot cache index");
    }
}
bool System::advance_trigger(bool pressed) {
    if (pressed && state_.time <= 1) { state_.time = 18; return true; }
    if (!state_.time) return false;
    --state_.time;
    // A released key does not cancel the two remaining volleys.
    return state_.time == 12 || state_.time == 6;
}
Entity* System::allocate(motion::Point player) {
    while (allocation_cursor_ < pool_size) {
        auto& entity = state_.entities[allocation_cursor_++];
        if (entity.flag != free) continue;
        entity.flag = alive; entity.age = 0; // DOS stores both as one word.
        entity.position.current = player;
        entity.position.velocity = {0,-192};
        // Previous position, damage, pattern and unused angle stay owned by
        // the reused slot until the producer/update assigns them.
        return &entity;
    }
    // DOS increments shot_last_id only for occupied slots; after a successful
    // allocation at the final slot its next call can read past the 68 entries.
    // The host stops at the actual capacity instead of importing that read.
    return nullptr;
}
void System::laser_fire(unsigned level, motion::Point player) {
    constexpr std::uint16_t frames[]{64,72,88,104,128,144,168,192};
    constexpr LaserStyle styles[]{LaserStyle::two,LaserStyle::two,LaserStyle::four,LaserStyle::four,
        LaserStyle::six,LaserStyle::one_four_one,LaserStyle::one_four_one,LaserStyle::eight};
    auto& laser = state_.laser;
    if (!laser.time) {
        laser.time = frames[level-2]; laser.style = styles[level-2];
        laser.bottom.current = laser.bottom.previous = state_.options;
        laser.ring_cycle = 0;
    }
    if (laser.time < 48) return;
    ++laser.ring_cycle;
    if (laser.ring_cycle <= 4) {
        allocation_cursor_ = 0;
        for (int side : {-24,24}) {
            if (auto* entity = allocate(player)) {
                entity->pattern = 70; entity->damage = 9;
                entity->position.velocity.y = -288;
                entity->position.current.x = motion::wrap(std::int32_t(state_.options.x)+side*16);
            }
        }
    } else if (laser.ring_cycle >= 8) laser.ring_cycle = 0;
}

void System::fire(Playchar character, ShotType type, unsigned level, motion::Point player,
                  randring::SharedRandomRing& random, std::optional<motion::Point> homing_target) {
    if (level > 9 || static_cast<unsigned>(character)>1 || static_cast<unsigned>(type)>1) {
        throw std::invalid_argument("invalid shot route/level");
    }
    const bool reimu = character == Playchar::reimu, route_a = type == ShotType::a;
    if (!reimu && route_a && level >= 2) laser_fire(level,player);
    allocation_cursor_ = 0; // Laser rings and the ordinary volley scan separately.
    const auto jitter = [&](unsigned mask, int base) { return int(random.next16_and(mask))+base; };
    const auto homing = [&](Entity& entity, int angle) {
        const motion::Point from{entity.position.current.x,player.y};
        aim(entity,angle+motion::angle_to(from,*homing_target));
    };
    if (level < 2) {
        if (auto* entity = allocate(player)) {
            entity->pattern = reimu ? 28 : 34; entity->damage = 10;
            if (level == 1) aim(*entity,jitter(7,-68));
        }
        return;
    }
    unsigned count;
    int main_angle = -70;
    if (reimu) {
        // A level 8 increments the cycle without the level 9/other-level reset.
        if (!(route_a && level == 8) && state_.time == 18) state_.reimu_cycle = 0;
        const unsigned divisor = level <= 3 || (route_a && level == 4) ? 3 : 2;
        const bool extra = state_.reimu_cycle%divisor == 0;
        if (route_a) {
            constexpr unsigned base[]{1,2,3,3,3,5,7,7};
            count = base[level-2]+((level != 8 && extra) ? 2 : 0);
            main_angle = level == 5 || level == 6 ? -72 : -70;
        } else {
            constexpr unsigned base[]{1,2,3,3,3,3,5,7};
            count = base[level-2]+(extra ? (level <= 4 ? 2 : 4) : 0);
            if (level >= 8) main_angle = -72;
        }
        ++state_.reimu_cycle; // Advance even if no pool slot can be allocated.
    } else if (route_a) {
        count = level == 2 ? 1 : (level <= 4 ? 2 : (level <= 7 ? 3 : 5));
        main_angle = level <= 7 ? -72 : -76;
    } else {
        constexpr unsigned counts[]{3,4,4,5,7,7,8,10};
        count = counts[level-2]; main_angle = level <= 6 ? -72 : -74;
    }

    // Traverse each volley in the target's descending shot_count order.
    // Randomness is consumed only AFTER a pool slot has been allocated.
    for (unsigned remaining=count; remaining; --remaining) {
        auto* allocated = allocate(player);
        if (!allocated) break;
        auto& entity = *allocated;
        if (reimu && route_a) {
            if (level == 2 && remaining == 1) {
                aim(entity,jitter(15,-72)); entity.pattern = 28; entity.damage = 10;
            } else if (level == 3 && remaining <= 2) {
                offset(entity,remaining == 2 ? -8 : 8); entity.pattern = 28; entity.damage = 9;
            } else if (level >= 4 && remaining <= 3) {
                constexpr std::uint8_t damage[]{8,8,7,7,7,6};
                aim(entity,main_angle); main_angle += level == 5 || level == 6 ? 8 : 6;
                entity.pattern = 28; entity.damage = damage[level-4];
            } else if (level >= 7 && remaining <= 5) {
                offset(entity,remaining == 5 ? -24 : 24);
                aim(entity,remaining == 5 ? -72 : -56); entity.pattern = 28; entity.damage = 7;
            } else {
                const bool left = remaining == (level == 2 ? 3u : (level == 3 ? 4u : (level <= 6 ? 5u : (remaining <= 7 ? 7u : 9u))));
                offset(entity,left ? -24 : 24);
                entity.pattern = 30;
                entity.damage = level <= 3 ? 10 : (level <= 5 ? 9 : (level == 6 ? 8 : 7));
                if (level == 9 && remaining <= 7) {
                    entity.damage = 5;
                    if (homing_target) homing(entity,jitter(7,-4));
                    else aim(entity,remaining == 7 ? -76 : -52);
                } else if (homing_target) {
                    homing(entity,level == 9 ? 0 : jitter(7,-4));
                }
            }
        } else if (reimu) {
            const unsigned core = level == 2 ? 1 : (level == 3 ? 2 : (level <= 7 ? 3 : 5));
            if (remaining <= core) {
                if (level == 2) aim(entity,jitter(15,-72));
                else if (level == 3) offset(entity,remaining == 2 ? -8 : 8);
                else {
                    aim(entity,main_angle); main_angle += level == 5 ? 7 : (level >= 8 ? 4 : 6);
                }
                entity.pattern = 28; entity.damage = level <= 2 ? 10 : (level <= 4 ? 9 : 8);
            } else {
                int angle;
                if (level <= 4) {
                    const bool left = remaining == core+2;
                    offset(entity,left ? -24 : 24); angle = left ? -72 : -56;
                } else if (level <= 8) {
                    constexpr int angles[]{-57,-50,-71,-78}; // remaining-core = 1..4
                    angle = angles[remaining-core-1];
                    offset(entity,remaining-core >= 3 ? -24 : 24);
                } else {
                    switch (remaining) {
                    case 11: case 10: angle = -64; break;
                    case 9: angle = -84; break; case 8: angle = -44; break;
                    case 7: angle = -74; break; default: angle = -54; break;
                    }
                    offset(entity,remaining%2 ? -24 : 24);
                }
                aim(entity,angle); entity.pattern = 32; entity.damage = level == 2 ? 10 : 9;
            }
        } else if (route_a) {
            entity.pattern = 34;
            if (level == 2) { aim(entity,jitter(7,-68)); entity.damage = 9; }
            else if (level <= 4) { offset(entity,remaining == 2 ? -8 : 8); entity.damage = 9; }
            else { aim(entity,main_angle); main_angle += level <= 7 ? 8 : 6; entity.damage = level <= 7 ? 8 : 7; }
        } else {
            const unsigned core = level == 2 ? 1 : (level <= 4 ? 2 : (level <= 7 ? 3 : 4));
            if (remaining <= core) {
                entity.pattern = 34;
                if (level == 2) { aim(entity,jitter(7,-68)); entity.damage = 10; }
                else if (level <= 4) { offset(entity,remaining == 2 ? -8 : 8); entity.damage = 9; }
                else {
                    if (level >= 8 && remaining == 3) offset(entity,-8);
                    if (level >= 8 && remaining == 2) offset(entity,8);
                    aim(entity,main_angle);
                    if (!(level >= 8 && remaining == 3)) main_angle += level <= 6 ? 8 : 10;
                    entity.damage = level <= 6 ? 9 : 8;
                }
            } else {
                entity.pattern = 36; entity.damage = level <= 4 ? 6 : (level <= 8 ? 5 : 4);
                if (level <= 5) {
                    offset(entity,remaining == core+2 ? -24 : 24);
                    if (level >= 4) aim(entity,jitter(7,-68),256);
                    else entity.position.velocity.y = -256;
                } else {
                    constexpr int offsets4[]{-16,-32,16,32};
                    constexpr int offsets6[]{-16,-32,-48,16,32,48};
                    offset(entity,(level == 9 ? offsets6 : offsets4)[remaining-core-1]);
                    entity.position.velocity.y = -256;
                }
            }
        }
    }
}

void System::update_entities(motion::Point options) {
    state_.options = options;
    state_.alive_count = 0;
    for (unsigned index=0; index<pool_size; ++index) {
        auto& entity = state_.entities[index];
        if (entity.flag >= remove) entity.flag = free;
        if (entity.flag == free) continue;
        entity.position.update();
        const auto point = entity.position.current;
        if (point.x <= -128 || point.x >= 392*16 || point.y <= -128 || point.y >= 376*16) {
            entity.flag = remove; continue;
        }
        if (entity.flag > alive) {
            ++entity.flag;
            if ((entity.flag & 3u) == hit) ++entity.pattern;
        } else {
            state_.collision_cache[state_.alive_count++] = {point,static_cast<std::uint16_t>(index)};
            ++entity.age;
        }
    }
    if (state_.laser.time) {
        state_.laser.bottom.previous = state_.laser.bottom.current;
        state_.laser.bottom.current = options;
        --state_.laser.time;
    }
}
bool System::update(bool pressed, Playchar character, ShotType type, std::uint8_t power,
                    const motion::Motion& player, randring::SharedRandomRing& random,
                    std::optional<motion::Point> homing_target) {
    const bool fired = advance_trigger(pressed);
    // Laser initialization/rings use options from the previous player update.
    if (fired) fire(character,type,level_for_power(power),player.current,random,homing_target);
    update_entities({motion::wrap(std::int32_t(player.current.x)-player.velocity.x),
                     motion::wrap(std::int32_t(player.current.y)-player.velocity.y)});
    return fired;
}
HitResult System::hittest(motion::Point center, motion::Point radius, HitContext context) {
    const auto left = motion::wrap(std::int32_t(center.x)-radius.x);
    const auto top = motion::wrap(std::int32_t(center.y)-radius.y);
    const auto width = static_cast<std::uint16_t>(std::int32_t(radius.x)*2);
    const auto height = static_cast<std::uint16_t>(std::int32_t(radius.y)*2);
    const auto within = [](motion::Subpixel value,motion::Subpixel minimum,std::uint16_t extent) {
        return static_cast<std::uint16_t>(std::int32_t(value)-minimum) <= extent;
    };
    HitResult result; unsigned hits = 0;
    for (unsigned i=0; i<state_.alive_count; ++i) {
        const auto& cached = state_.collision_cache[i];
        if (!within(cached.position.x,left,width) || !within(cached.position.y,top,height)) continue;
        // Deliberately use the frame's cache even if an earlier enemy already
        // marked this shot hit. DOS does not recheck the pool flag here.
        auto& entity = state_.entities[cached.index];
        entity.flag = hit; entity.pattern = 40;
        entity.position.velocity.x /= 6; entity.position.velocity.y /= 6;
        result.damage = static_cast<std::uint16_t>(result.damage+entity.damage/++hits);
        if (++state_.spark_cycle & 1u) result.sparks[result.spark_count++] = entity.position.current;
    }
    if (context.bombing) {
        if (!context.frame_mod4) result.damage = static_cast<std::uint16_t>(result.damage+5);
        if (context.against_boss) result.damage /= 4;
    }
    if (context.frame_mod2 && state_.laser.time > 32 &&
        static_cast<std::uint16_t>(top) <= static_cast<std::uint16_t>(state_.laser.bottom.current.y)) {
        for (int side : {-24,24}) {
            const auto x = motion::wrap(std::int32_t(state_.laser.bottom.current.x)+side*16);
            if (!within(x,left,width)) continue;
            result.damage = static_cast<std::uint16_t>(result.damage+3);
            if ((++state_.spark_cycle & 3u) == 0) result.sparks[result.spark_count++] = {x,center.y};
        }
    }
    state_.score_delta += result.damage;
    return result;
}
} // namespace th04::portable::shot
