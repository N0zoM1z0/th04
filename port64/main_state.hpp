#pragma once
#include "application_state.hpp"
#include "item_pool.hpp"
#include "player_motion.hpp"
#include "player_shots.hpp"

namespace th04::portable::gameplay {
// Live MAIN owns player motion, shots and items. The
// stage VM, bombs, collision/death and HUD will join this same owner;
// absent systems do not generate substitute enemies or scripted fake scores.
class State {
public:
    explicit State(application::State& application);
    void update(std::uint16_t held_input, bool shift, bool pull_items = false);
    const player::Movement& player() const { return player_; }
    const item::Pool& items() const { return items_; }
    const item::ScoreState& score() const { return score_; }
    const shot::System& shots() const { return shots_; }
    const item::UpdateResult& item_events() const { return item_events_; }
    std::uint32_t frames() const { return frames_; }
    bool add_item(motion::Point position, item::Type type) { return items_.add(position, type); }
    bool add_enemy_drop(motion::Point position) { return items_.add_enemy_drop(position, drops_); }
    item::MissSpawnResult add_miss_items();

private:
    player::Movement player_{};
    shot::System shots_{};
    application::Playchar playchar_ = application::Playchar::reimu;
    application::ShotType shot_type_ = application::ShotType::a;
    item::Pool items_{};
    item::ScoreState score_{};
    randring::SharedRandomRing ring_{};
    item::EnemyDropSequence drops_{};
    item::UpdateResult item_events_{};
    std::uint32_t frames_ = 0;
};
} // namespace th04::portable::gameplay
