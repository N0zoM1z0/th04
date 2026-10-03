#pragma once
#include "application_state.hpp"
#include "item_pool.hpp"
#include "player_motion.hpp"
#include "player_shots.hpp"
#include "enemy_system.hpp"
#include "enemy_bullets.hpp"
#include "effects.hpp"
#include "midboss.hpp"
#include "orange.hpp"
#include "circles.hpp"
#include "dialog.hpp"
#include "stage_bonus.hpp"
#include "stage_background.hpp"
#include <memory>

namespace th04::portable::gameplay {
// Live MAIN owns STD waves, enemies, player motion, shots, bullets,
// sparks, gather circles, items and the Stage 1 midboss.
// Bombs, player death and HUD will join this same owner;
// absent systems do not generate substitute enemies or scripted fake scores.
class State {
public:
    explicit State(application::State& application);
    void update(std::uint16_t held_input, bool shift, bool pull_items = false,
                motion::Subpixel scroll_delta = 0,stage::Background* background=nullptr);
    void load_stage(const stage::Program::Bytes& standard);
    const player::Movement& player() const { return player_; }
    const item::Pool& items() const { return items_; }
    const item::ScoreState& score() const { return score_; }
    const shot::System& shots() const { return shots_; }
    const bullet::System& bullets() const { return bullets_; }
    const spark::System& sparks() const { return sparks_; }
    const gather::System& gathers() const { return gathers_; }
    const midboss::System& midboss() const { return midboss_; }
    const orange::System& orange() const { return orange_; }
    const circle::System& circles() const { return circles_; }
    bool orange_active() const { return orange_active_; }
    unsigned slowdown() const {
        const unsigned boss=orange_active_ ? orange_.snapshot().slowdown : 1;
        return boss>bullets_.snapshot().slowdown ? boss : bullets_.snapshot().slowdown;
    }
    bool post_boss_dialog_pending() const { return post_boss_dialog_pending_; }
    std::uint8_t orange_background_phase() const { return orange_background_phase_; }
    std::int16_t orange_background_frame() const { return orange_background_frame_; }
    bool stage1_dialog_ready(const stage::Background& background) const {
        // Session init sets back page1; every completed gameplay frame flips
        // it. Blocking dialog ticks do not increment this simulation clock.
        return stage_id_==0 && stage_ && stage_->stopped() && !orange_active_ &&
            dialog::stage_gate(static_cast<std::uint8_t>(background.speed()),static_cast<std::uint8_t>(1u^(frames_&1u)));
    }
    std::uint16_t random_cursor() const { return ring_.cursor(); }
    // Caller completes the blocking pre-boss dialog before this handoff.
    void start_orange_after_dialog();
    void finish_post_boss_dialog();
    const std::optional<bonus::Result>& clear_bonus() const { return clear_bonus_; }
    const std::vector<orange::Event>& orange_events() const { return orange_events_; }
    const std::vector<midboss::Event>& midboss_events() const { return midboss_events_; }
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
    midboss::System midboss_{};
    orange::System orange_{};
    circle::System circles_{};
    bool orange_active_=false,post_boss_dialog_pending_=false;
    bonus::Context bonus_context_{};
    std::optional<bonus::Result> clear_bonus_;
    std::uint8_t orange_background_phase_=0;
    std::int16_t orange_background_frame_=0;
    std::vector<orange::Event> orange_events_;
    std::vector<midboss::Event> midboss_events_;
    std::optional<motion::Point> homing_target_{};
    std::vector<bullet::Event> bullet_events_;
    bool turbo_=true;
    std::unique_ptr<stage::Program> stage_;
    std::vector<enemy::Event> enemy_events_;
    std::uint8_t rank_ = 1, performance_ = 16;
    std::uint8_t stage_id_=0;
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
