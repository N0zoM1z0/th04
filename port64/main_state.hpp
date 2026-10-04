#pragma once
#include "application_state.hpp"
#include "item_pool.hpp"
#include "player_motion.hpp"
#include "player_shots.hpp"
#include "enemy_system.hpp"
#include "enemy_bullets.hpp"
#include "effects.hpp"
#include "midboss.hpp"
#include "midboss2.hpp"
#include "midboss3.hpp"
#include "orange.hpp"
#include "kurumi.hpp"
#include "elly.hpp"
#include "circles.hpp"
#include "dialog.hpp"
#include "stage_bonus.hpp"
#include "score.hpp"
#include "stage_background.hpp"
#include <memory>

namespace th04::portable::gameplay {
// Live MAIN owns STD waves, enemies, player motion, shots, bullets,
// sparks, gather circles, items and the Stage1/Stage2/Stage3 midbosses.
// Bombs, player death and the remaining HUD will join this same owner;
// absent systems do not generate substitute enemies or scripted fake scores.
class State {
public:
    explicit State(application::State& application);
    void update(std::uint16_t held_input, bool shift, bool pull_items = false,
                motion::Subpixel scroll_delta = 0,stage::Background* background=nullptr);
    void load_stage(const stage::Program::Bytes& standard);
    // Actor/STD preparation for the already requested next stage. The front end
    // must still replace its sprite/map/palette owners before consuming this.
    void prepare_next_stage_actors(const stage::Program::Bytes& standard);
    bool stage2_dialog_ready(const stage::Background& background) const {
        return stage_id_==1 && stage_ && stage_->stopped() && !boss_active() && !midboss_state().active &&
            dialog::stage_gate(static_cast<std::uint8_t>(background.speed()),static_cast<std::uint8_t>(1u^(frames_&1u)));
    }
    bool stage3_dialog_ready(const stage::Background& background) const {
        return stage_id_==2 && stage_ && stage_->stopped() && !boss_active() && !midboss_state().active &&
            dialog::stage_gate(static_cast<std::uint8_t>(background.speed()),static_cast<std::uint8_t>(1u^(frames_&1u)));
    }
    const midboss::Snapshot& midboss_state() const { return midboss3_ ? midboss3_->snapshot().actor : (midboss2_ ? midboss2_->snapshot().actor : midboss_.snapshot()); }
    const std::vector<midboss::Draw>& midboss_draws() const { return midboss3_ ? midboss3_->draws() : (midboss2_ ? midboss2_->draws() : midboss_.draws()); }
    const player::Movement& player() const { return player_; }
    const item::Pool& items() const { return items_; }
    const item::ScoreState& score() const { return score_; }
    const score::Snapshot& scoreboard() const { return scoreboard_; }
    const std::vector<score::Event>& score_events() const { return score_events_; }
    std::uint32_t awarded_score_units() const { return score::numeric_units(scoreboard_.digits)+score_.score_delta; }
    const shot::System& shots() const { return shots_; }
    const bullet::System& bullets() const { return bullets_; }
    const spark::System& sparks() const { return sparks_; }
    const gather::System& gathers() const { return gathers_; }
    const midboss::System& midboss() const { return midboss_; }
    const orange::System& orange() const { return orange_; }
    const circle::System& circles() const { return circles_; }
    bool orange_active() const { return orange_active_; }
    bool kurumi_active() const { return kurumi_active_; }
    bool elly_active() const { return elly_active_; }
    const elly::System* elly() const { return elly_ ? &*elly_ : nullptr; }
    bool boss_active() const { return orange_active_ || kurumi_active_ || elly_active_; }
    const orange::Snapshot& boss_snapshot() const { return elly_active_ ? elly_->snapshot().boss : (kurumi_active_ ? kurumi_->snapshot().boss : orange_.snapshot()); }
    const std::vector<orange::Draw>& boss_draws() const { return elly_active_ ? elly_->draws() : (kurumi_active_ ? kurumi_->draws() : orange_.draws()); }
    const kurumi::System* kurumi() const { return kurumi_ ? &*kurumi_ : nullptr; }
    std::uint8_t invincibility() const { return player_invincibility_; }
    unsigned slowdown() const {
        const unsigned boss=boss_active() ? boss_snapshot().slowdown : 1;
        return boss>bullets_.snapshot().slowdown ? boss : bullets_.snapshot().slowdown;
    }
    bool post_boss_dialog_pending() const { return post_boss_dialog_pending_; }
    std::int16_t palette_tone_before_frame() const { return palette_tone_before_frame_; }
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
    void start_kurumi_after_dialog(std::array<std::uint8_t,3> palette_zero);
    void start_elly_after_dialog(std::array<std::uint8_t,3> palette_zero);
    void finish_post_boss_dialog();
    bool next_stage_requested() const { return next_stage_requested_; }
    const transition::Overlay& overlay() const { return overlay_; }
    const transition::Text& overlay_cell() const { return overlay_cell_; }
    bool bonus_text_visible() const { return clear_bonus_.has_value() && !leave_text_replaced_; }
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
    void apply_clear_bonus();
    application::State* application_;
    transition::Overlay overlay_{};
    transition::Text overlay_cell_{transition::TextKind::character,4,1,32,5};
    std::optional<transition::Departure> departure_;
    bool frame_suspended_=false,dialog_finished_=false,next_stage_requested_=false,leave_text_replaced_=false;
    enemy::Context suspended_context_{};
    bullet::Context suspended_bullets_{};
    bool suspended_pull_items_=false;
    player::Movement player_{};
    shot::System shots_{};
    enemy::System enemies_{};
    bullet::System bullets_{};
    spark::System sparks_{};
    gather::System gathers_{};
    midboss::System midboss_{};
    std::optional<midboss2::System> midboss2_;
    std::optional<midboss3::System> midboss3_;
    orange::System orange_{};
    std::optional<kurumi::System> kurumi_;
    std::optional<elly::System> elly_;
    bool elly_active_=false;
    circle::System circles_{};
    bool orange_active_=false,post_boss_dialog_pending_=false;
    bool kurumi_active_=false;
    std::uint8_t player_invincibility_=64;
    bonus::Context bonus_context_{};
    std::optional<bonus::Result> clear_bonus_;
    std::int16_t palette_tone_before_frame_=100;
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
    score::Snapshot scoreboard_{};
    std::vector<score::Event> score_events_;
    randring::SharedRandomRing ring_{};
    item::EnemyDropSequence drops_{};
    item::UpdateResult item_events_{};
    std::uint32_t frames_ = 0;
};
} // namespace th04::portable::gameplay
