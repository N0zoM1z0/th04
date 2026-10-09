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
#include "midboss4.hpp"
#include "orange.hpp"
#include "kurumi.hpp"
#include "elly.hpp"
#include "reimu.hpp"
#include "marisa.hpp"
#include "stage5.hpp"
#include "stage6.hpp"
#include "stagex.hpp"
#include "midbossx.hpp"
#include "mugetsu.hpp"
#include "gengetsu.hpp"
#include "yuuka5.hpp"
#include "yuuka6.hpp"
#include "yuuka6_foreground.hpp"
#include "yuuka6_background.hpp"
#include "yuuka6_entities.hpp"
#include "circles.hpp"
#include "dialog.hpp"
#include "stage_bonus.hpp"
#include "score.hpp"
#include "stage_background.hpp"
#include "run_statistics.hpp"
#include "player_bomb.hpp"
#include "player_render.hpp"
#include "gameover.hpp"
#include "host_score.hpp"
#include "hud.hpp"
#include "demo.hpp"
#include "sound_runtime.hpp"
#include <memory>

namespace th04::portable::gameplay {
// Older actor-only controls intentionally omit hit consumption. Ordinary
// gameplay always uses the real lifecycle; this mode is explicit in probes.
enum class Mode {ordinary,actor_control};
// Live MAIN owns STD waves, enemies, player motion, shots, bullets,
// sparks, gather circles, items and the Stage1 through Stage4 midbosses.
// Player lifecycle and blocking Game Over share this owner; graphics and
// the remaining HUD are separate frontend consumers.
// Absent systems do not generate substitute enemies or scripted fake scores.
class State {
public:
    // Explicit replay checkpoint; ordinary launches use the default.
    explicit State(application::State& application,Mode mode=Mode::ordinary,
                   player::LifeState player_checkpoint={},score_file::HostStore* storage=nullptr);
    void update(std::uint16_t held_input, bool shift, bool pull_items = false,
                motion::Subpixel scroll_delta = 0,stage::Background* background=nullptr);
    void load_stage(const stage::Program::Bytes& standard);
    void set_demo_replay(const std::vector<std::uint8_t>& bytes);
    bool demo_exit_requested() const {return demo_exit_requested_;}
    const demo::Sample& demo_sample() const {return demo_sample_;}
    std::uint8_t rank() const {return rank_;}
    bool turbo() const {return turbo_;}
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
    bool stage4_dialog_ready(const stage::Background& background) const {
        return stage_id_==3 && stage_ && stage_->stopped() && !boss_active() && !midboss_state().active &&
            dialog::stage_gate(static_cast<std::uint8_t>(background.speed()),static_cast<std::uint8_t>(1u^(frames_&1u)));
    }
    bool stage5_dialog_ready(const stage::Background& background) const {
        return stage_id_==4 && stage_ && stage_->stopped() && !boss_active() && !midboss_state().active &&
            dialog::stage_gate(static_cast<std::uint8_t>(background.speed()),static_cast<std::uint8_t>(1u^(frames_&1u)));
    }
    bool stage6_dialog_ready(const stage::Background& background) const {
        return stage_id_==5 && stage_ && stage_->stopped() && !boss_active() && !midboss_state().active &&
            dialog::stage_gate(static_cast<std::uint8_t>(background.speed()),static_cast<std::uint8_t>(1u^(frames_&1u)));
    }
    void begin_stage6_dialog(stage::Background& background);
    bool stage6_battle_pending() const { return stage6_battle_pending_; }
    const stage5::Setup* stage5_setup() const { return stage5_ ? &*stage5_ : nullptr; }
    const stagex::Setup* extra_setup() const {return stagex_ ? &*stagex_ : nullptr;}
    bool extra_dialog_ready(const stage::Background& background) const {
        return stage_id_==6 && stage_ && stage_->stopped() && !boss_active() && !midboss_state().active &&
            dialog::stage_gate(std::uint8_t(background.speed()),std::uint8_t(1u^(frames_&1u)));
    }
    void begin_extra_dialog(stage::Background& background);
    void start_mugetsu_after_dialog(std::array<std::uint8_t,3> palette_zero);
    void start_gengetsu_after_dialog();
    bool extra_post_dialog_blocked() const {return extra_post_dialog_blocked_;}
    bool gengetsu_active() const {return gengetsu_.has_value();}
    const gengetsu::System* gengetsu() const {return gengetsu_ ? &*gengetsu_ : nullptr;}
    bool extra_final_dialog_pending() const {return gengetsu_ && gengetsu_->snapshot().boss.phase==255 && gengetsu_->snapshot().boss.phase_frame==0 && !extra_final_dialog_finished_;}
    bool extra_final_dialog_blocked() const {return extra_departure_ && extra_departure_->blocked;}
    void finish_extra_final_dialog();
    bool extra_ending_requested() const {return extra_ending_requested_;}
    bool mugetsu_active() const {return mugetsu_.has_value();}
    const mugetsu::System* mugetsu() const {return mugetsu_ ? &*mugetsu_ : nullptr;}
    bool gengetsu_dialog_pending() const {return mugetsu_ && mugetsu_->snapshot().boss.phase==255;}
    const midboss::Snapshot& midboss_state() const { return midbossx_ ? midbossx_->snapshot() : (stage6_ ? stage6_->midboss : (stage5_ ? stage5_->midboss : (midboss4_ ? midboss4_->snapshot().actor : (midboss3_ ? midboss3_->snapshot().actor : (midboss2_ ? midboss2_->snapshot().actor : midboss_.snapshot()))))); }
    const std::vector<midboss::Draw>& midboss_draws() const { return midbossx_ ? midbossx_->draws() : ((stage5_ || stage6_) ? stage5_midboss_draws_ : (midboss4_ ? midboss4_->draws() : (midboss3_ ? midboss3_->draws() : (midboss2_ ? midboss2_->draws() : midboss_.draws())))); }
    const player::Movement& player() const { return player_; }
    const item::Pool& items() const { return items_; }
    const item::ScoreState& score() const { return score_; }
    const score::Snapshot& scoreboard() const { return scoreboard_; }
    const registration::TextPlane& hud_text_plane() const { return hud_text_; }
    std::int16_t hud_hp_previous() const { return hud_hp_previous_; }
    const std::array<std::uint8_t,256>& random_ring_bytes() const { return ring_.bytes(); }
    const std::vector<score::Event>& score_events() const { return score_events_; }
    std::uint32_t awarded_score_units() const { return score::numeric_units(scoreboard_.digits)+score_.score_delta; }
    const shot::System& shots() const { return shots_; }
    const bullet::System& bullets() const { return bullets_; }
    // Score/extend runs after foreground rendering. Its clear request belongs
    // to the next update; host repaint consumes the completed render boundary.
    std::uint8_t bullet_render_clear() const {return bullet_render_clear_;}
    std::uint8_t bullet_render_zap() const {return bullet_render_zap_;}
    const spark::System& sparks() const { return sparks_; }
    const gather::System& gathers() const { return gathers_; }
    const midboss::System& midboss() const { return midboss_; }
    const orange::System& orange() const { return orange_; }
    const circle::System& circles() const { return circles_; }
    bool orange_active() const { return orange_active_; }
    bool kurumi_active() const { return kurumi_active_; }
    bool elly_active() const { return elly_active_; }
    const elly::System* elly() const { return elly_ ? &*elly_ : nullptr; }
    bool reimu_active() const { return reimu_active_; }
    const reimu::System* reimu() const { return reimu_ ? &*reimu_ : nullptr; }
    bool marisa_active() const { return marisa_active_; }
    const marisa::System* marisa() const { return marisa_ ? &*marisa_ : nullptr; }
    bool yuuka5_active() const { return yuuka5_active_; }
    const yuuka5::System* yuuka5() const { return yuuka5_ ? &*yuuka5_ : nullptr; }
    bool yuuka6_active() const { return yuuka6_active_; }
    const yuuka6::System* yuuka6() const { return yuuka6_ ? &*yuuka6_ : nullptr; }
    const yuuka6::Background& yuuka6_background() const { return yuuka6_background_; }
    const yuuka6::Foreground& yuuka6_foreground() const { return yuuka6_foreground_; }
    const yuuka6::Entities& yuuka6_entities() const { return yuuka6_entities_; }
    bool good_ending_requested() const { return good_ending_requested_; }
    const laser::System& thick_lasers() const { return thick_lasers_; }
    // Ending rendering has not joined yet. This holds at the actual bad
    // Ending call boundary, before the normal clear bonus or Stage6 request.
    bool bad_ending_requested() const { return bad_ending_requested_; }
    bool bad_yuuka5_dialog() const { return yuuka5_active_ && th04::portable::yuuka5::bad_ending_after_defeat(stage_id_,rank_,0); }
    bool boss_active() const { return gengetsu_.has_value() || mugetsu_.has_value() || yuuka6_active_ || yuuka5_active_ || marisa_active_ || reimu_active_ || orange_active_ || kurumi_active_ || elly_active_; }
    const orange::Snapshot& boss_snapshot() const {
        if(gengetsu_)return gengetsu_->snapshot().boss;
        if(mugetsu_)return mugetsu_->snapshot().boss;
        if(stagex_)return stagex_->boss;
        if(yuuka6_active_)return yuuka6_->snapshot().boss;
        if(stage6_)return stage6_->boss;
        if(yuuka5_active_)return yuuka5_->snapshot().boss;
        if(stage5_)return stage5_->boss;
        if(marisa_active_)return marisa_->snapshot().boss;
        if(reimu_active_)return reimu_->snapshot().boss;
        if(elly_active_)return elly_->snapshot().boss;
        if(kurumi_active_)return kurumi_->snapshot().boss;
        return orange_.snapshot();
    }
    const std::vector<orange::Draw>& boss_draws() const { return mugetsu_ ? mugetsu_->draws() : marisa_active_ ? marisa_->draws() : (reimu_active_ ? reimu_->draws() : (elly_active_ ? elly_->draws() : (kurumi_active_ ? kurumi_->draws() : orange_.draws()))); }
    const kurumi::System* kurumi() const { return kurumi_ ? &*kurumi_ : nullptr; }
    std::uint8_t invincibility() const { return life_.state().invincibility; }
    const player::LifeState& life() const {return life_.state();}
    const std::vector<player::RenderDraw>& player_draws() const {return player_draws_;}
    const bomb::Effect& bomb_effect() const {return bomb_effect_;}
    const bomb::RenderFrame& bomb_frame() const {return bomb_frame_;}
    using BombObserver=std::function<void(const player::LifeState&,const randring::SharedRandomRing&,
        const bomb::Effect&,const circle::System&,std::uint16_t)>;
    void set_bomb_observer(BombObserver observer) {bomb_observer_=std::move(observer);}
    const std::vector<player::LifeEvent>& life_events() const {return life_events_;}
    const std::vector<gameover::Event>& gameover_events() const {return gameover_events_;}
    void set_sound_sink(sound::ActionSink sink) {sound_sink_=std::move(sink);}
    const gameover::Scene* game_over() const {return gameover_.get();}
    bool score_registration_requested() const {return score_registration_requested_;}
    void set_continue_save(std::function<void(const score::Digits&)> save) {continue_save_=std::move(save);}
    void set_gameover_sink(gameover::Sink sink) {gameover_sink_=std::move(sink);}
    void set_player_palette(std::array<std::uint8_t,3> color) {life_.set_palette14(color);}
    Mode mode() const {return mode_;}
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
    std::uint8_t drop_cycle() const { return drops_.cycle(); }
    // Caller completes the blocking pre-boss dialog before this handoff.
    void start_orange_after_dialog();
    void start_kurumi_after_dialog(std::array<std::uint8_t,3> palette_zero);
    void start_elly_after_dialog(std::array<std::uint8_t,3> palette_zero);
    void start_marisa_after_dialog(std::array<std::uint8_t,3> palette_zero);
    void start_reimu_after_dialog(std::array<std::uint8_t,3> palette_zero);
    void start_yuuka5_after_dialog(std::array<std::uint8_t,3> palette_zero);
    void start_yuuka6_after_dialog(std::array<std::uint8_t,3> palette_zero);
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
    application::RunStatistics run_statistics() const;
    // GUI calls once after a completed simulation/render tick. Headless
    // controls supply no clock sample; slowdown is never inferred from bullets.
    void observe_refreshes(std::uint16_t elapsed);
    bool add_item(motion::Point position, item::Type type) { return items_.add(position, type); }
    bool add_enemy_drop(motion::Point position) { return items_.add_enemy_drop(position, drops_); }
    item::MissSpawnResult add_miss_items();

private:
    player::LifeContext life_context();
    void publish_boss_graphics();
    std::uint16_t scroll_line_=0;
    sound::ActionSink sound_sink_;
    void sound_action(sound::ActionKind kind,std::uint16_t value=0) {if(sound_sink_)sound_sink_({kind,value,{}});}
    FrameCounts run_frames_;
    std::uint32_t observed_frame_=0;
    void apply_clear_bonus(bool all_clear=false);
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
    std::optional<midboss4::System> midboss4_;
    std::optional<stage5::Setup> stage5_;
    std::optional<stage6::Setup> stage6_;
    std::optional<stagex::Setup> stagex_;
    std::optional<midbossx::System> midbossx_;
    std::uint8_t bullet_render_clear_=0,bullet_render_zap_=0;
    bool stage6_battle_pending_=false,extra_battle_pending_=false;
    std::optional<mugetsu::System> mugetsu_;
    std::optional<gengetsu::System> gengetsu_;
    bool extra_post_dialog_blocked_=false,extra_handoff_resumed_=false;
    bool extra_final_dialog_finished_=false,extra_ending_requested_=false;
    std::optional<transition::Departure> extra_departure_;
    std::optional<yuuka6::System> yuuka6_;
    yuuka6::Background yuuka6_background_{};
    yuuka6::Foreground yuuka6_foreground_{};
    yuuka6::Entities yuuka6_entities_{};
    bool yuuka6_active_=false,good_ending_requested_=false;
    std::optional<yuuka5::System> yuuka5_;
    laser::System thick_lasers_{};
    bool yuuka5_active_=false,bad_ending_requested_=false;
    // A null original renderer emits no requests, including at frame60000.
    std::vector<midboss::Draw> stage5_midboss_draws_;
    orange::System orange_{};
    std::optional<kurumi::System> kurumi_;
    std::optional<elly::System> elly_;
    bool elly_active_=false;
    std::optional<marisa::System> marisa_;
    bool marisa_active_=false;
    std::optional<reimu::System> reimu_;
    bool reimu_active_=false;
    circle::System circles_{};
    bool orange_active_=false,post_boss_dialog_pending_=false;
    bool kurumi_active_=false;
    player::Lifecycle life_{};
    std::vector<player::RenderDraw> player_draws_;
    bomb::Effect bomb_effect_{};
    bomb::RenderFrame bomb_frame_{};
    BombObserver bomb_observer_;
    Mode mode_=Mode::ordinary;
    std::optional<demo::Replay> demo_;
    demo::Sample demo_sample_{};
    bool demo_exit_requested_=false;
    std::uint16_t last_input_=0;
    bool player_frame_suspended_=false,score_registration_requested_=false;
    std::vector<player::LifeEvent> life_events_;
    std::vector<gameover::Event> gameover_events_;
    gameover::Sink gameover_sink_;
    std::function<void(const score::Digits&)> continue_save_;
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
    registration::TextPlane hud_text_;
    std::int16_t hud_hp_previous_=0;
    void initialize_hud();
    void apply_score_hud(const std::vector<score::Event>&);
    std::vector<score::Event> score_events_;
    randring::SharedRandomRing ring_{};
    item::EnemyDropSequence drops_{};
    item::UpdateResult item_events_{};
    std::uint32_t frames_ = 0;
    std::optional<gameover::Context> gameover_context_;
    std::unique_ptr<gameover::Scene> gameover_;
};
} // namespace th04::portable::gameplay
