#pragma once
#include "application_state.hpp"
#include "item_pool.hpp"
#include "player_motion.hpp"
#include "player_shots.hpp"
#include "enemy_system.hpp"
#include "enemy_bullets.hpp"
#include "effects.hpp"
#include <memory>

namespace th04::portable::gameplay {
// Live MAIN owns STD waves, enemies, player motion, shots, bullets,
// sparks, gather circles and items.
// Bombs, player death and HUD will join this same owner;
// absent systems do not generate substitute enemies or scripted fake scores.
class State {
public:
    explicit State(application::State& application);
    void update(std::uint16_t held_input, bool shift, bool pull_items = false,
                motion::Subpixel scroll_delta = 0);
    void load_stage(const stage::Program::Bytes& standard);
    const player::Movement& player() const { return player_; }
    const item::Pool& items() const { return items_; }
    const item::ScoreState& score() const { return score_; }
    const shot::System& shots() const { return shots_; }
    const bullet::System& bullets() const { return bullets_; }
    const spark::System& sparks() const { return sparks_; }
    const gather::System& gathers() const { return gathers_; }
    const std::vector<bullet::Event>& bullet_events() const { return bullet_events_; }
    const enemy::System& enemies() const { return enemies_; }
    const std::vector<enemy::Event>& enemy_events() const { return enemy_events_; }
    const item::UpdateResult& item_events() const { return item_events_; }
    std::uint32_t frames() const { return frames_; }
    bool add_item(motion::Point position, item::Type type) { return items_.add(position, type); }
    bool add_enemy_drop(motion::Point position) { return items_.add_enemy_drop(position, drops_); }
    item::MissSpawnResult add_miss_items();

private:
    player::Movement player_{};
    shot::System shots_{};
    enemy::System enemies_{};
    bullet::System bullets_{};
    spark::System sparks_{};
    gather::System gathers_{};
    std::vector<bullet::Event> bullet_events_;
    bool turbo_=true;
    std::unique_ptr<stage::Program> stage_;
    std::vector<enemy::Event> enemy_events_;
    std::uint8_t rank_ = 1, performance_ = 16;
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
