#include "main_state.hpp"
#include "stage_session.hpp"
#include <stdexcept>
#include <algorithm>

namespace th04::portable::gameplay {
State::State(application::State& application,Mode mode,player::LifeState checkpoint,score_file::HostStore* storage)
    :application_(&application),life_(checkpoint),mode_(mode) {
    if (application.program() != application::Program::main) {
        throw std::logic_error("live MAIN requires a completed OP handoff");
    }
    application.initialize_main_gameplay();
    score_.power = 1;
    playchar_ = application.resident().playchar;
    shot_type_ = application.resident().shot_type;
    stage_id_=application.resident().resource_stage;
    bonus_context_.stage=application.resident().stage;
    bonus_context_.resource_stage=stage_id_;
    bonus_context_.credit_lives=application.resident().credit_lives;
    const bool demo=application.resident().demo_number!=0;
    turbo_ = demo || application.resident().stage == 6 || application.resident().config.turbo;
    rank_ = demo ? 2 : application.resident().stage == 6 ? 4 : application.resident().config.rank;
    bonus_context_.rank=rank_;
    // The demo branch first writes28, then the common Hard switch overwrites
    // it with20 before stage runtime begins (MAIN0AAF:035E).
    performance_ = rank_ == 2 ? 20 : (rank_ == 3 ? 22 : 16);
    score_.remaining_lives = application.resident().credit_lives;
    score_.remaining_bombs = application.resident().credit_bombs;
    application.publish_main_resources(score_.remaining_lives,score_.remaining_bombs);
    // Original gameplay_session_init clears MAIN's local eight digits;
    // it does not import the preceding run's resident publication.
    scoreboard_.digits.fill(0);
    scoreboard_.lives=score_.remaining_lives;
    constexpr std::uint8_t minimum[]{4,11,20,22,16},maximum[]{16,24,32,34,20};
    scoreboard_.performance=performance_;scoreboard_.minimum=minimum[rank_];scoreboard_.maximum=maximum[rank_];
    // hiscore_load precedes stage-runtime ring/drop/spark initialization. A
    // failed selected checksum repairs ten sections using MAIN's own stream,
    // before those later draws. Older isolated actor controls explicitly omit
    // storage and retain their supplied zero high-score context.
    if(storage)scoreboard_.hiscore=storage->read_main_highscore(std::uint8_t(playchar_),rank_,
        [&application]{return application.next_process_random();});
    // Original demo_load/stage publication/power/seed occur after hiscore_load,
    // before the runtime ring/drop/spark draws. Configured rank stays resident.
    if(demo) {
        application.initialize_demo_stage();score_.power=128;
        bonus_context_.stage=application.resident().stage;
    }
    score_events_=score::render(scoreboard_);
    // Consume the SAME process generator used by the rest of MAIN. Creating
    // a second LCG at this boundary would repeat the first stage sequence.
    ring_.fill([&application]() {
        return static_cast<std::uint8_t>(application.next_process_random());
    });
    drops_ = item::EnemyDropSequence(static_cast<std::uint8_t>(
        application.next_process_random() & 15u
    ));
    sparks_.initialize([&application]() {
        return static_cast<std::uint8_t>(application.next_process_random());
    });
    // First MAIN text_fillca uses reversed spaces. The playfield wipe then
    // restores transparent spaces; the right-hand HUD retains its own banks.
    for(int row=0;row<25;++row)for(int col=0;col<80;++col)
        hud_text_.put_ank(col,row,32,row>=1 && row<24 && col>=4 && col<52 ? 0xe1 : 5);
    initialize_hud();
    player_draws_=player::render_requests(life_.state(),player_.position(),
        shot::level_for_power(score_.power),playchar_==application::Playchar::reimu ? 38 : 39,0,0);
}

void State::initialize_hud() {
    hud::Values values;
    values.character=std::uint8_t(playchar_);values.rank=rank_;
    values.lives=score_.remaining_lives;values.bombs=score_.remaining_bombs;
    values.points=score_.stage_point_items_collected;values.dream=score_.dream_score;
    values.graze=bullets_.snapshot().graze;values.power=score_.power;
    values.shot_level=shot::level_for_power(score_.power);values.score=scoreboard_;
    hud::apply(hud_text_,hud::initialize(values));scoreboard_.hud=values.score.hud;
    // hud_put clears the display, preserving the process-global HP animator.
}
void State::apply_score_hud(const std::vector<score::Event>& events) {
    for(const auto& event:events) {
        if(event.kind==score::Kind::sound)sound_action(sound::ActionKind::play,std::uint16_t(event.value));
        else if(event.kind==score::Kind::gaiji)
            hud_text_.put_string(int(event.left),int(event.row),event.bytes,std::uint16_t(event.value));
        else if(event.kind==score::Kind::hud_lives)
            hud::apply(hud_text_,hud::lives(scoreboard_.lives));
    }
}

void State::load_stage(const stage::Program::Bytes& standard) {
    bomb_frame_={};
    stagex_.reset();midbossx_.reset();mugetsu_.reset();gengetsu_.reset();extra_battle_pending_=false;
    extra_post_dialog_blocked_=extra_handoff_resumed_=false;
    extra_final_dialog_finished_=extra_ending_requested_=false;extra_departure_.reset();
    bullet_render_clear_=bullet_render_zap_=0;
    yuuka6_.reset();yuuka6_active_=false;good_ending_requested_=false;
    yuuka6_background_=yuuka6::Background{};yuuka6_foreground_=yuuka6::Foreground{};yuuka6_entities_=yuuka6::Entities{};
    stage6_battle_pending_=false;
    stage_ = std::make_unique<stage::Program>(standard);
    enemies_ = enemy::System{};
    bullets_ = bullet::System{};
    gathers_ = gather::System{};
    midboss_ = midboss::System{};midboss2_.reset();midboss3_.reset();midboss4_.reset();stage5_.reset();stage6_.reset();stage5_midboss_draws_.clear();
    yuuka5_.reset();yuuka5_active_=false;bad_ending_requested_=false;thick_lasers_=laser::System{};thick_lasers_.initialize();
    marisa_.reset();marisa_active_=false;reimu_.reset();reimu_active_=false;orange_=orange::System{};kurumi_.reset();kurumi_active_=false;elly_.reset();elly_active_=false;life_.prepare_stage();circles_=circle::System{};
    if(stage_id_==6) {
        stagex_=stagex::prepare(orange_.snapshot(),midboss_.snapshot());
        midbossx_.emplace(stagex_->midboss);
    } else if(stage_id_==1) {
        midboss2::Snapshot actor;actor.actor=session::prepare_stage2_midboss(midboss_.snapshot());
        midboss2_.emplace(actor);kurumi_.emplace(kurumi::prepare_stage2({},rank_));
    } else if(stage_id_==2) {
        midboss3::Snapshot actor;actor.actor=session::prepare_stage3_midboss(midboss_.snapshot());
        midboss3_.emplace(actor);elly_.emplace(elly::prepare_stage3({}));
    } else if(stage_id_==3) {
        midboss4::Snapshot actor;actor.actor=session::prepare_stage4_midboss(midboss_.snapshot());
        midboss4_.emplace(actor);
        if(playchar_==application::Playchar::marisa)reimu_.emplace(reimu::prepare_stage4({},rank_));
        else marisa_.emplace(th04::portable::marisa::prepare_stage4({}));
    }
    orange_active_=false;post_boss_dialog_pending_=false;
    clear_bonus_.reset();departure_.reset();overlay_={};
    overlay_cell_={transition::TextKind::character,4,1,32,5};
    frame_suspended_=false;dialog_finished_=false;next_stage_requested_=false;leave_text_replaced_=false;
    homing_target_.reset();
    player_draws_=player::render_requests(life_.state(),player_.position(),
        shot::level_for_power(score_.power),playchar_==application::Playchar::reimu ? 38 : 39,
        static_cast<std::uint8_t>(frames_&3u),scroll_line_);
    initialize_hud();
}
void State::set_demo_replay(const std::vector<std::uint8_t>& bytes) {
    if(!application_->resident().demo_number || frames_ || demo_)
        throw std::logic_error("replay belongs to first demo session before gameplay");
    demo_.emplace(bytes);
}
void State::start_orange_after_dialog() {
    if (!stage_ || orange_active_ || midboss_.snapshot().active) throw std::logic_error("invalid Orange dialog handoff");
    orange_active_=true;
}
void State::start_kurumi_after_dialog(std::array<std::uint8_t,3> palette_zero) {
    if(stage_id_!=1 || !stage_ || !stage_->stopped() || boss_active() || midboss_state().active || !kurumi_)
        throw std::logic_error("invalid Kurumi dialog handoff");
    // Stage2 BFNT palette loading replaces the preceding boss color0.
    kurumi_->set_palette_zero(palette_zero);kurumi_active_=true;
}
void State::start_elly_after_dialog(std::array<std::uint8_t,3> palette_zero) {
    if(stage_id_!=2 || !stage_ || !stage_->stopped() || boss_active() || midboss_state().active || !elly_)
        throw std::logic_error("invalid Elly dialog handoff");
    elly_->set_palette_zero(palette_zero);elly_active_=true;
}
void State::start_marisa_after_dialog(std::array<std::uint8_t,3> palette_zero) {
    if(stage_id_!=3 || playchar_!=application::Playchar::reimu || !stage_ || !stage_->stopped() || boss_active() || midboss_state().active || !marisa_)
        throw std::logic_error("invalid Marisa dialog handoff");
    marisa_->set_palette_zero(palette_zero);marisa_active_=true;
}
void State::start_reimu_after_dialog(std::array<std::uint8_t,3> palette_zero) {
    if(stage_id_!=3 || playchar_!=application::Playchar::marisa || !stage_ || !stage_->stopped() || boss_active() || midboss_state().active || !reimu_)
        throw std::logic_error("invalid Reimu dialog handoff");
    reimu_->set_palette_zero(palette_zero);reimu_active_=true;
}
void State::start_yuuka5_after_dialog(std::array<std::uint8_t,3> palette_zero) {
    if(stage_id_!=4 || !stage_ || !stage_->stopped() || boss_active() || midboss_state().active || !stage5_)
        throw std::logic_error("invalid Yuuka5 dialog handoff");
    // Stage setup retains preceding boss metadata. Yuuka's private globals
    // have no earlier owner on this first encounter; they begin at loaded BSS
    // zero, rather than being part of a supposed generic boss reset.
    yuuka5::Snapshot initial;initial.boss=stage5_->boss;
    initial.boss.palette_zero=palette_zero;initial.midboss_frames_until=60000-65536;
    yuuka5_.emplace(initial);yuuka5_active_=true;
}
void State::begin_stage6_dialog(stage::Background& background) {
    if(!stage6_dialog_ready(background)) throw std::logic_error("invalid Stage6 dialogue gate");
    background.release_finished_streams();stage_.reset();stage6_battle_pending_=true;
}
void State::start_yuuka6_after_dialog(std::array<std::uint8_t,3> palette_zero) {
    if(stage_id_!=5 || !stage6_ || !stage6_battle_pending_ || stage_ || boss_active() || midboss_state().active)
        throw std::logic_error("invalid Yuuka6 dialog handoff");
    // Stage6 setup has already retained/reset the original common boss fields.
    // Do not repeat stage initialization, random-ring fill or laser reset here.
    yuuka6::Snapshot initial;initial.boss=stage6_->boss;initial.boss.palette_zero=palette_zero;
    yuuka6_.emplace(initial);yuuka6::BackgroundState bg;bg.palette_zero=palette_zero;
    yuuka6_background_=yuuka6::Background(bg);yuuka6_active_=true;stage6_battle_pending_=false;
}
void State::begin_extra_dialog(stage::Background& background) {
    if(!extra_dialog_ready(background))throw std::logic_error("invalid Extra dialogue gate");
    background.release_finished_streams();stage_.reset();extra_battle_pending_=true;
}
void State::start_mugetsu_after_dialog(std::array<std::uint8_t,3> palette_zero) {
    if(stage_id_!=6 || !stagex_ || !extra_battle_pending_ || stage_ || boss_active() || midboss_state().active)
        throw std::logic_error("invalid Mugetsu dialog handoff");
    mugetsu::Snapshot initial;initial.boss=stagex_->boss;initial.boss.palette_zero=palette_zero;
    initial.midboss_frames_until=motion::wrap(midboss_state().start_frame);
    mugetsu_.emplace(initial);extra_battle_pending_=false;
}
void State::start_gengetsu_after_dialog() {
    if(!gengetsu_dialog_pending() || !frame_suspended_ || !extra_post_dialog_blocked_)
        throw std::logic_error("Gengetsu handoff requires the suspended second dialogue");
    gengetsu::Snapshot initial;initial.boss=mugetsu_->snapshot().boss;
    initial.bomb_invincibility=mugetsu_->snapshot().bomb_invincibility;
    initial.lasers=thick_lasers_.snapshot();
    gengetsu_.emplace(gengetsu::prepare_after_dialog(initial));mugetsu_.reset();
    extra_post_dialog_blocked_=false;extra_handoff_resumed_=true;dialog_finished_=true;
}
void State::finish_extra_final_dialog() {
    if(!extra_final_dialog_blocked() || !frame_suspended_ || clear_bonus_)
        throw std::logic_error("Extra completion requires the suspended third dialogue");
    extra_final_dialog_finished_=true;dialog_finished_=true;
}
void State::prepare_next_stage_actors(const stage::Program::Bytes& standard) {
    if(!next_stage_requested_ || stage_id_>4 || application_->resident().stage!=stage_id_+1)
        throw std::logic_error("actor preparation requires the actual next-stage departure request");
    // Validate before changing the live owners or consuming process random.
    auto next=std::make_unique<stage::Program>(standard);
    const auto next_id=static_cast<std::uint8_t>(stage_id_+1);
    const auto preceding_midboss=midboss_state();
    const auto preceding_boss=boss_snapshot();
    auto boss=next_id==1 ? kurumi::prepare_stage2(orange_.snapshot(),rank_) : kurumi::Snapshot{};
    session::initialize_actors({player_,shots_,enemies_,bullets_,sparks_,gathers_,
        circles_,items_,score_,scoreboard_,ring_,drops_},[this] {
            return static_cast<std::uint8_t>(application_->next_process_random());
        });
    // Stage initialization arms the scratch LINE flag/radius before add().
    // Reset only the original fields; preserve retained beam/scratch metadata.
    thick_lasers_.initialize();
    stage_=std::move(next);stage_id_=next_id;frames_=0;
    if(next_id==1) {
        midboss2::Snapshot next_midboss;next_midboss.actor=session::prepare_stage2_midboss(preceding_midboss);
        midboss2_.emplace(next_midboss);
        // Stage-common globals have different reset ownership than boss_reset.
        boss.boss.background=orange::Background::tiles;boss.boss.slowdown=1;
        boss.boss.shake_x=boss.boss.shake_y=0;boss.boss.bombing_disabled=0;
        boss.boss.palette_tone=100;boss.boss.invincibility=64;kurumi_.emplace(boss);
    } else if(next_id==2) {
        midboss3::Snapshot next_midboss;next_midboss.actor=session::prepare_stage3_midboss(preceding_midboss);
        midboss3_.emplace(next_midboss);midboss2_.reset();
        if(!kurumi_) throw std::logic_error("Stage3 requires preceding Kurumi metadata");
        auto next_boss=elly::prepare_stage3(kurumi_->snapshot().boss);
        next_boss.boss.background=orange::Background::tiles;next_boss.boss.slowdown=1;
        next_boss.boss.shake_x=next_boss.boss.shake_y=0;next_boss.boss.bombing_disabled=0;
        next_boss.boss.palette_tone=100;next_boss.boss.invincibility=64;elly_.emplace(next_boss);
    } else if(next_id==3) {
        midboss4::Snapshot next_midboss;next_midboss.actor=session::prepare_stage4_midboss(preceding_midboss);
        midboss4_.emplace(next_midboss);midboss3_.reset();midboss2_.reset();
        if(playchar_==application::Playchar::marisa) {
            if(!elly_) throw std::logic_error("Stage4 requires preceding Elly metadata");
            auto npc=reimu::prepare_stage4(elly_->snapshot().boss,rank_);
            npc.boss.background=orange::Background::tiles;npc.boss.slowdown=1;
            npc.boss.shake_x=npc.boss.shake_y=0;npc.boss.bombing_disabled=0;
            npc.boss.palette_tone=100;npc.boss.invincibility=64;reimu_.emplace(npc);
        }
        else {
            if(!elly_) throw std::logic_error("Stage4 requires preceding Elly metadata");
            auto npc=th04::portable::marisa::prepare_stage4(elly_->snapshot().boss);
            // Stage-state init clears all832 custom bytes. Marisa private
            // globals have no earlier gameplay owner on this first encounter.
            npc.boss.background=orange::Background::tiles;npc.boss.slowdown=1;
            npc.boss.shake_x=npc.boss.shake_y=0;npc.boss.bombing_disabled=0;
            npc.boss.palette_tone=100;npc.boss.invincibility=64;marisa_.emplace(npc);
        }
    } else if(next_id==4) {
        stage5_=stage5::prepare(preceding_boss,preceding_midboss,rank_);
        auto& b=stage5_->boss;b.background=orange::Background::tiles;b.slowdown=1;
        b.shake_x=b.shake_y=0;b.bombing_disabled=0;b.palette_tone=100;b.invincibility=64;
        midboss4_.reset();midboss3_.reset();midboss2_.reset();stage5_midboss_draws_.clear();
    } else {
        stage6_=stage6::prepare(preceding_boss,preceding_midboss,rank_);
        auto& b=stage6_->boss;b.background=orange::Background::tiles;b.slowdown=1;
        b.shake_x=b.shake_y=0;b.bombing_disabled=0;b.palette_tone=100;b.invincibility=64;
        stage5_.reset();midboss4_.reset();midboss3_.reset();midboss2_.reset();stage5_midboss_draws_.clear();
    }
    yuuka5_active_=false;bad_ending_requested_=false;
    stage6_battle_pending_=false;
    life_.prepare_stage();kurumi_active_=false;elly_active_=false;reimu_active_=false;marisa_active_=false;
    orange_active_=false;clear_bonus_.reset();departure_.reset();overlay_={};
    overlay_cell_={transition::TextKind::character,4,1,32,5};
    frame_suspended_=false;dialog_finished_=false;post_boss_dialog_pending_=false;
    next_stage_requested_=false;leave_text_replaced_=false;
    palette_tone_before_frame_=100;
    bonus_context_.stage=next_id;bonus_context_.resource_stage=next_id;
    score_events_.clear();enemy_events_.clear();bullet_events_.clear();
    midboss_events_.clear();orange_events_.clear();item_events_={};
    player_draws_=player::render_requests(life_.state(),player_.position(),
        shot::level_for_power(score_.power),playchar_==application::Playchar::reimu ? 38 : 39,
        static_cast<std::uint8_t>(frames_&3u),scroll_line_);
    // Score/power/performance/resident statistics and MAIN generation/seed
    // persist. Asset replacement has a separate owner;
    // never run the Stage1 midboss callback under the new stage identity.
    initialize_hud();
}
void State::finish_post_boss_dialog() {
    if(!post_boss_dialog_pending_ || clear_bonus_) throw std::logic_error("invalid stage-clear bonus handoff");
    dialog_finished_=true;post_boss_dialog_pending_=false;
    // Original Stage5 Easy branches to end_game_bad before stage_clear_bonus.
    // Continue-used will share this predicate once the death/Continue owner
    // exists. Do not manufacture MAINE statistics or run its unported script.
    if(bad_yuuka5_dialog()) bad_ending_requested_=true;
}
void State::apply_clear_bonus(bool all_clear) {
    if(clear_bonus_) throw std::logic_error("repeated stage-clear bonus");
    bonus_context_.power=score_.power;bonus_context_.dream=score_.dream_score;
    bonus_context_.graze=bullets_.snapshot().graze;
    bonus_context_.point_items=score_.stage_point_items_collected;
    bonus_context_.remaining_lives=score_.remaining_lives;
    bonus_context_.defeated_in_time=boss_snapshot().patterns_or_bonus;
    constexpr std::uint8_t minimum[]{4,11,20,22,16},maximum[]{16,24,32,34,20};
    bonus::State state;state.score_delta=score_.score_delta;state.bombs=score_.remaining_bombs;
    state.performance=performance_;state.minimum=minimum[rank_];state.maximum=maximum[rank_];
    clear_bonus_=bonus::apply(bonus_context_,state,all_clear);
    if(all_clear) scoreboard_.extends=state.extends;
    score_.score_delta=state.score_delta;score_.remaining_bombs=state.bombs;performance_=state.performance;
    // Called at the original bonus position when the blocked frame resumes,
    // before items/gathers/render/clock/score drain complete that same frame.
}
void State::publish_boss_graphics() {
    const auto tone=life_.state().palette_tone;const auto color=life_.state().circle_color;
    if(gengetsu_)gengetsu_->set_graphics(tone,color);
    else if(mugetsu_)mugetsu_->set_graphics(tone,color);
    else if(yuuka6_active_)yuuka6_->set_graphics(tone,color);
    else if(yuuka5_active_)yuuka5_->set_graphics(tone,color);
    else if(marisa_active_)marisa_->set_graphics(tone,color);
    else if(reimu_active_)reimu_->set_graphics(tone,color);
    else if(elly_active_)elly_->set_graphics(tone,color);
    else if(kurumi_active_)kurumi_->set_graphics(tone,color);
    else if(orange_active_)orange_.set_graphics(tone,color);
}
player::LifeContext State::life_context() {
    constexpr std::uint8_t minimum[]{4,11,20,22,16};
    player::LifeContext context{score_,player_,shots_,performance_,11,2,0,{},{},{}};
    context.scroll_line=scroll_line_;context.minimum=minimum[rank_];context.credit_bombs=application_->resident().credit_bombs;
    context.sink=[this](const player::LifeEvent& event) {
        life_events_.push_back(event);
        if(event.kind==player::LifeKind::sound)sound_action(sound::ActionKind::play,std::uint16_t(event.value));
        else if(event.kind==player::LifeKind::fire)
            shots_.fire(playchar_,shot_type_,shot::level_for_power(score_.power),player_.position().current,ring_,homing_target_);
        else if(event.kind==player::LifeKind::miss_items)add_miss_items();
        else if(event.kind==player::LifeKind::hud_dream)hud::apply(hud_text_,hud::dream(score_.dream_score));
        else if(event.kind==player::LifeKind::shot_level)hud::apply(hud_text_,hud::power(score_.power,shot::level_for_power(score_.power)));
        else if(event.kind==player::LifeKind::hud_lives)hud::apply(hud_text_,hud::lives(score_.remaining_lives));
        else if(event.kind==player::LifeKind::hud_bombs)hud::apply(hud_text_,hud::bombs(score_.remaining_bombs));
    };
    context.game_over=[this]() -> std::optional<std::uint8_t> {
        if(gameover_)throw std::logic_error("duplicate Game Over call");
        const auto& resident=application_->resident();
        gameover_context_.emplace(gameover::Context{score_,scoreboard_,stage_id_,resident.credit_lives,resident.credit_bombs,
            [this](const gameover::Event& event) {
                gameover_events_.push_back(event);
                if(event.kind==gameover::Kind::song_fade)sound_action(sound::ActionKind::command,std::uint16_t(0x200|event.value));
                else if(event.kind==gameover::Kind::score_sequence)application_->prepare_main_score();
                else if(event.kind==gameover::Kind::maine)score_registration_requested_=true;
                else if(event.kind==gameover::Kind::bad_ending)bad_ending_requested_=true;
                else if(event.kind==gameover::Kind::shot_level)hud::apply(hud_text_,hud::power(score_.power,shot::level_for_power(score_.power)));
                else if(event.kind==gameover::Kind::hud_lives)hud::apply(hud_text_,hud::lives(score_.remaining_lives));
                else if(event.kind==gameover::Kind::hud_bombs)hud::apply(hud_text_,hud::bombs(score_.remaining_bombs));
                else if(event.kind==gameover::Kind::hud_score)apply_score_hud(score::render(scoreboard_));
                if(gameover_sink_)gameover_sink_(event);
            },[this] {
                if(!continue_save_)throw std::logic_error("Continue requires a real score store");
                continue_save_(scoreboard_.digits);
            }});
        gameover_=std::make_unique<gameover::Scene>(*gameover_context_,last_input_);
        return std::nullopt;
    };
    context.character_bomb=[this](player::LifeState& state) {
        bomb::Context context{state,ring_,circles_,std::uint16_t(frames_),std::uint8_t(frames_%4)};
        bomb_effect_.render(playchar_,context);
        for(const auto& draw:bomb_effect_.draws())if(draw.kind==bomb::Kind::sound)
            sound_action(sound::ActionKind::play,std::uint16_t(draw.value));
    };
    return context;
}
void State::update(std::uint16_t held_input, bool shift, bool pull_items,motion::Subpixel scroll_delta,stage::Background* background) {
    if(demo_exit_requested_)return;
    if(demo_ && !gameover_ && !player_frame_suspended_ && !frame_suspended_) {
        const auto physical=std::uint16_t(player::input_from_host_actions(held_input)|(held_input&0x4000u));
        demo_sample_=demo_->sample(std::uint16_t(frames_),physical,shift);
        if(demo_sample_.finished) {demo_exit_requested_=true;demo_.reset();return;}
        held_input=demo::host_input(std::uint8_t(demo_sample_.input));shift=demo_sample_.shift!=0;
    }
    if(background)scroll_line_=background->scroll_line();
    score_events_.clear();gameover_events_.clear();last_input_=player::input_from_host_actions(held_input);
    if(gameover_) {
        gameover_->advance(player::input_from_host_actions(held_input));
        if(!gameover_->finished())return;
        if(gameover_->phase()!=gameover::Phase::continue_run) {
            if(life_.suspended())life_.resolve_game_over(1);
            return;
        }
        life_.resolve_game_over(0);gameover_.reset();gameover_context_.reset();
    }
    if(next_stage_requested_ || bad_ending_requested_ || good_ending_requested_ ||
       score_registration_requested_ || stage6_battle_pending_ || extra_battle_pending_ || extra_ending_requested_) return;
    const bool resumed_player=player_frame_suspended_;
    // Hold at the genuine next-boss dialog gate until its battle owner joins.
    // STD and the stage midboss callbacks execute normally before it.
    if(!resumed_player && background && (stage2_dialog_ready(*background) || stage3_dialog_ready(*background) || stage4_dialog_ready(*background) || stage5_dialog_ready(*background) || stage6_dialog_ready(*background) || extra_dialog_ready(*background))) return;
    const bool resumed=frame_suspended_;
    if(resumed && !dialog_finished_) return;
    enemy::Context context;
    bullet::Context bullet_context;
    bullet_context.hud_graze=[this](std::uint16_t value) {hud::apply(hud_text_,hud::graze(value));};
    if(resumed || resumed_player) {
        context=suspended_context_;bullet_context=suspended_bullets_;pull_items=suspended_pull_items_;
    } else {
        enemy_events_.clear();bullet_events_.clear();midboss_events_.clear();orange_events_.clear();life_events_.clear();
        bomb_frame_={};
        bomb_frame_.retain_background=life_.state().bombing && life_.state().background==2;
        if(boss_active()) {
            palette_tone_before_frame_=boss_snapshot().palette_tone;
            orange_background_phase_=boss_snapshot().phase;
            orange_background_frame_=boss_snapshot().phase_frame;
        }
        context.player=player_.position().current;context.rank=rank_;context.performance=performance_;
        context.scroll_delta=scroll_delta;context.frame_mod2=frames_%2;context.frame_mod4=frames_%4;
    }
    const auto bullet_sink=[this](const bullet::Event& event) {
        bullet_events_.push_back(event);
        if(event.type==bullet::EventType::sparks) sparks_.add_random(event.position,event.value,event.count,ring_);
        if(event.type==bullet::EventType::gather) gathers_.request(event);
    };
    midboss::Context midboss_context;
    midboss_context.hp_previous=&hud_hp_previous_;
    if(!resumed) {
        if(!resumed_player) {
        if(stage_ && !boss_active()) run_frames_.standard_tick();
        // STD dispatch precedes player movement; enemies created here can run
        // their first setup/move instructions later in this same frame.
        if (stage_ && !boss_active()) for (const auto& spawn:stage_->run(static_cast<std::uint16_t>(frames_),midboss_state().active)) {
            enemies_.add(spawn,context,ring_);
        }
        if (stage_ && !boss_active()) {
            if(stage5_ || stage6_) {
                // The original still activates the null callback set at60000.
                // Retain that metadata write; never dispatch a previous boss.
                auto& actor=stage6_ ? stage6_->midboss : stage5_->midboss;
                if(static_cast<std::uint16_t>(frames_)==actor.start_frame) { actor.phase=0;actor.phase_frame=0;actor.active=true; }
            }
            else if(midbossx_) midbossx_->activate(static_cast<std::uint16_t>(frames_));
            else if(midboss4_) midboss4_->activate(static_cast<std::uint16_t>(frames_));
            else if(midboss3_) midboss3_->activate(static_cast<std::uint16_t>(frames_));
            else if(midboss2_) midboss2_->activate(static_cast<std::uint16_t>(frames_));
            else midboss_.activate(static_cast<std::uint16_t>(frames_));
        }
        // MAIN's loop calls player_update before items_update. A pickup therefore
        // sees the player's new position for this frame, not the preceding one.
        // Bullet spawn/update and thick lasers alias the original BYTE hit
        // latch. A blocked dialogue resumes below this prefix: clear once
        // per simulation frame, never once per host repaint or resumed suffix.
        if(yuuka6_active_) {
            // gameplay_loop renders the background BEFORE player, shots,
            // bullets and boss. Initialization/scatter consumes the same
            // ring; a cached host repaint must never repeat this prefix.
            yuuka6_background_.prepare_render(orange_background_phase_,orange_background_frame_,ring_);
            yuuka6_->set_palette_zero(yuuka6_background_.state().palette_zero);
        }
        circles_.update();sparks_.update();
        life_.set_clear_time(bullets_.snapshot().clear_time);
        life_.set_bombing_disabled(boss_active() ? boss_snapshot().bombing_disabled : 0);
        const bool hit=bullets_.snapshot().player_hit || enemies_.snapshot().player_hit ||
            thick_lasers_.snapshot().player_hit || (gengetsu_ && gengetsu_->snapshot().lasers.player_hit) || (reimu_active_ && reimu_->snapshot().player_hit) ||
            (marisa_active_ && marisa_->snapshot().player_hit);
        life_.latch_hit(mode_==Mode::ordinary && hit);
        bullets_.set_player_hit(false);enemies_.set_player_hit(false);thick_lasers_.set_player_hit(0);
        if(gengetsu_)gengetsu_->set_player_hit(0);
        if(reimu_active_)reimu_->set_player_hit(0);
        if(marisa_active_)marisa_->set_player_hit(0);
        if(boss_active())life_.synchronize_graphics(boss_snapshot().palette_tone,boss_snapshot().circle_color);
        auto player_context=life_context();
        life_.update(player::input_from_host_actions(held_input),shift,player_context);
        bullets_.set_clear_time(life_.state().clear_time);
        application_->publish_player_statistics(life_.state().misses,life_.state().bombs_used);
        application_->publish_main_resources(score_.remaining_lives,score_.remaining_bombs);
        if(life_.suspended()) {
            suspended_context_=context;suspended_pull_items_=pull_items;
            player_frame_suspended_=true;return;
        }
        }
        player_frame_suspended_=false;
        shots_.update_entities(life_.state().options);
        context.player = player_.position().current;context.performance=performance_;
        context.bombing=life_.state().bombing!=0;
        pull_items=pull_items || life_.state().pull_items;
        bullet_context.player=context.player;bullet_context.rank=rank_;bullet_context.performance=performance_;
        bullet_context.frame_mod2=context.frame_mod2;bullet_context.turbo=turbo_;
        bullet_context.invincibility=life_.state().invincibility;
        constexpr std::uint16_t graze_scores[]{100,250,400,500,2560};
        bullet_context.graze_score=graze_scores[rank_];
        const auto score_before=bullets_.snapshot().score_delta;
        bullets_.begin_frame();bullets_.update(bullet_context,bullet_sink);
        score_.score_delta+=bullets_.snapshot().score_delta-score_before;
        if (stage_) {
            const auto before = enemies_.snapshot().score_delta;
            enemies_.update(*stage_,context,ring_,shots_,[this,&bullet_context,&bullet_sink](const enemy::Event& event) {
                enemy_events_.push_back(event);
                if(event.type==enemy::EventType::sound)sound_action(sound::ActionKind::play,std::uint16_t(event.value));
                // Tune/add consumes the shared ring immediately, before another
                // enemy or another immediate opcode can draw from it.
                if (event.type==enemy::EventType::fire) bullets_.fire(event,bullet_context,ring_,bullet_sink);
                if (event.type==enemy::EventType::sparks) sparks_.add_random(event.position,event.value,event.count,ring_);
                if (event.type==enemy::EventType::drop) {
                    if (event.value==255) items_.add_enemy_drop(event.position,drops_);
                    else if (event.value<=6) items_.add(event.position,static_cast<item::Type>(event.value));
                }
            });
            score_.score_delta += enemies_.snapshot().score_delta-before;
        }
        homing_target_=enemies_.snapshot().homing_target;
        midboss_context.frame=static_cast<std::uint16_t>(frames_);
        midboss_context.scroll_delta=scroll_delta;
        midboss_context.scroll_line=background ? static_cast<std::int16_t>(background->scroll_line()) : 0;
        midboss_context.scroll_speed=background ? static_cast<std::uint8_t>(background->speed()) : 2;
        midboss_context.bullets=bullet_context;
        midboss_context.hit=[&](motion::Point center,motion::Point radius) {
            const auto before=shots_.snapshot().score_delta;
            const auto result=shots_.hittest(center,radius,{life_.state().bombing!=0,false,context.frame_mod2,context.frame_mod4});
            score_.score_delta+=shots_.snapshot().score_delta-before;
            for (unsigned i=0;i<result.spark_count;++i) sparks_.add_random(result.sparks[i],128,1,ring_);
            return result.damage;
        };
        if (midboss_state().active && !stage5_ && !stage6_) {
            const auto sink=[&](const midboss::Event& event) {
                midboss_events_.push_back(event);
                if(event.type==midboss::EventType::sound)sound_action(sound::ActionKind::play,std::uint16_t(event.value));
                if (event.type==midboss::EventType::circle) sparks_.add_circle(event.position,event.value,event.count);
                if (event.type==midboss::EventType::homing) homing_target_=event.position;
                if (event.type==midboss::EventType::item) items_.add(event.position,static_cast<item::Type>(event.value));
                if (event.type==midboss::EventType::hp)hud::apply(hud_text_,hud::hp(motion::wrap(event.value)));
                if (background && event.type==midboss::EventType::tile) background->set_tile(event.position.x,event.position.y,event.value);
                if (background && event.type==midboss::EventType::scroll) background->set_speed(static_cast<std::uint8_t>(event.value));
            };
            if(midbossx_) {
                midbossx_->update(midboss_context,bullets_,ring_,sink);
            } else if(midboss4_) {
                const auto before=midboss4_->score_delta();
                midboss4_->update(midboss_context,bullets_,gathers_,ring_,sink);
                score_.score_delta+=midboss4_->score_delta()-before;
            } else if(midboss3_) {
                const auto before=midboss3_->score_delta();
                midboss3_->update(midboss_context,bullets_,gathers_,ring_,sink);
                score_.score_delta+=midboss3_->score_delta()-before;
            } else if(midboss2_) {
                const auto before=midboss2_->score_delta();
                midboss2_->update(midboss_context,bullets_,gathers_,ring_,sink);
                score_.score_delta+=midboss2_->score_delta()-before;
            } else {
                const auto before=midboss_.score_delta();
                midboss_.update(midboss_context,bullets_,ring_,sink);
                score_.score_delta+=midboss_.score_delta()-before;
            }
        }
    } // Prefix executes once even if the dialog suspends this frame.
    if(boss_active()) {
        publish_boss_graphics();
        if(gengetsu_)gengetsu_->set_invincibility(life_.state().invincibility);else if(mugetsu_)mugetsu_->set_invincibility(life_.state().invincibility);else if(yuuka6_active_) yuuka6_->set_invincibility(life_.state().invincibility);else if(yuuka5_active_) yuuka5_->set_invincibility(life_.state().invincibility);else if(marisa_active_) marisa_->set_invincibility(life_.state().invincibility);else if(reimu_active_) reimu_->set_invincibility(life_.state().invincibility);else if(elly_active_) elly_->set_invincibility(life_.state().invincibility);else if(kurumi_active_) kurumi_->set_invincibility(life_.state().invincibility);else orange_.set_invincibility(life_.state().invincibility);
    }
    if(resumed && extra_handoff_resumed_) {
        // Return from Mugetsu's original boss_defeat_update() invocation.
        // Gengetsu's first update starts on the NEXT MAIN frame; foreground
        // already uses its newly installed callback in this resumed suffix.
        frame_suspended_=false;dialog_finished_=false;extra_handoff_resumed_=false;
    } else if(gengetsu_dialog_pending()) {
        mugetsu_->set_graphics(60,boss_snapshot().circle_color);
        life_.synchronize_graphics(60,boss_snapshot().circle_color);
        orange_events_.push_back({orange::EventType::tone,{},60,0});
        application_->add_stage_graze(bullets_.snapshot().graze);
        orange_events_.push_back({orange::EventType::dialog,{},0,0});
        suspended_context_=context;suspended_bullets_=bullet_context;suspended_pull_items_=pull_items;
        frame_suspended_=true;extra_post_dialog_blocked_=true;return;
    } else if(gengetsu_ && boss_snapshot().phase==255) {
        if(!extra_departure_) {
            transition::Departure d;d.frame=boss_snapshot().phase_frame;d.homing=boss_snapshot().homing;
            d.graze=application_->resident().graze;d.stage_graze=bullets_.snapshot().graze;
            extra_departure_=d;
        }
        const bool returning_dialog=extra_departure_->blocked;
        const bool ending=transition::update_extra_departure(*extra_departure_,!resumed && !extra_final_dialog_finished_,[&](const transition::Event& e) {
            if(e.kind==transition::Kind::tone)orange_events_.push_back({orange::EventType::tone,{},60,0});
            else if(e.kind==transition::Kind::dialog) {
                application_->add_stage_graze(extra_departure_->stage_graze);
                orange_events_.push_back({orange::EventType::dialog,{},0,0});
            } else if(e.kind==transition::Kind::all_clear) {
                apply_clear_bonus(true);orange_events_.push_back({orange::EventType::stage_bonus,{},0,0});
            }
        });
        gengetsu_->apply_departure(*extra_departure_);
        if(extra_departure_->blocked) {
            suspended_context_=context;suspended_bullets_=bullet_context;suspended_pull_items_=pull_items;
            frame_suspended_=true;return;
        }
        if(ending) {extra_ending_requested_=true;return;}
        frame_suspended_=false;dialog_finished_=false;
        if(!returning_dialog)homing_target_.reset();
    } else if(yuuka6_active_ && boss_snapshot().phase==255) {
        // Final Stage has no post-boss dialogue or next-stage departure. The
        // all-clear award runs at clock0; end_game is called at416 before the
        // frame tail. Keep its still-unported MAINE handoff as an explicit
        // request, preserving pending score rather than committing it early.
        transition::Departure d;d.frame=boss_snapshot().phase_frame;d.homing=boss_snapshot().homing;
        d.graze=application_->resident().graze;d.stage_graze=bullets_.snapshot().graze;
        const bool ending=transition::update_final_departure(d,[&](const transition::Event& e) {
            if(e.kind==transition::Kind::tone) orange_events_.push_back({orange::EventType::tone,{},60,0});
            else if(e.kind==transition::Kind::all_clear) {
                application_->add_stage_graze(d.stage_graze);apply_clear_bonus(true);
                orange_events_.push_back({orange::EventType::stage_bonus,{},0,0});
            }
        });
        yuuka6_->apply_departure(d);
        if(ending) { good_ending_requested_=true;return; }
        homing_target_.reset();
    } else if(!mugetsu_ && !gengetsu_ && boss_active() && boss_snapshot().phase==255) {
        if(!departure_) {
            transition::Departure d;d.frame=boss_snapshot().phase_frame;
            d.stage=application_->resident().stage;d.stage_ascii=application_->resident().stage_ascii;
            d.graze=application_->resident().graze;d.stage_graze=bullets_.snapshot().graze;
            d.homing=boss_snapshot().homing;departure_=d;
        }
        transition::update_departure(*departure_,overlay_,!resumed && !clear_bonus_,[&](const transition::Event& e) {
            switch(e.kind) {
            case transition::Kind::tone:orange_events_.push_back({orange::EventType::tone,{},60,0});break;
            case transition::Kind::dialog:
                application_->add_stage_graze(departure_->stage_graze);
                orange_events_.push_back({orange::EventType::dialog,{},0,0});break;
            case transition::Kind::bonus:apply_clear_bonus();orange_events_.push_back({orange::EventType::stage_bonus,{},0,0});break;
            case transition::Kind::fade:orange_events_.push_back({orange::EventType::fade,{},10,0});sound_action(sound::ActionKind::command,0x20a);break;
            case transition::Kind::next_stage:
                application_->advance_main_stage();next_stage_requested_=true;
                orange_events_.push_back({orange::EventType::next_stage,{},0,0});break;
            case transition::Kind::delay:orange_events_.push_back({orange::EventType::delay,{},1,0});break;
            case transition::Kind::all_clear:case transition::Kind::end_game:case transition::Kind::end_extra:
                throw std::logic_error("final-stage callback in ordinary departure");
            }
        });
        if(yuuka5_active_) yuuka5_->apply_departure(*departure_);else if(marisa_active_) marisa_->apply_departure(*departure_);else if(reimu_active_) reimu_->apply_departure(*departure_);else if(elly_active_) elly_->apply_departure(*departure_);else if(kurumi_active_) kurumi_->apply_departure(*departure_);else orange_.apply_departure(*departure_);
        if(departure_->blocked) {
            suspended_context_=context;suspended_bullets_=bullet_context;suspended_pull_items_=pull_items;
            frame_suspended_=true;post_boss_dialog_pending_=true;return;
        }
        frame_suspended_=false;dialog_finished_=false;homing_target_.reset();
    } else if (boss_active()) {
        elly::Context boss_context;boss_context.frame=static_cast<std::uint16_t>(frames_);
        boss_context.bullets=bullet_context;boss_context.power=score_.power;
        const auto shot_hit=[&](motion::Point center,motion::Point radius,bool against_boss) {
            const auto before=shots_.snapshot().score_delta;
            const auto result=shots_.hittest(center,radius,{life_.state().bombing!=0,against_boss,context.frame_mod2,context.frame_mod4});
            score_.score_delta+=shots_.snapshot().score_delta-before;
            for(unsigned i=0;i<result.spark_count;++i) sparks_.add_random(result.sparks[i],128,1,ring_);
            return result.damage;
        };
        boss_context.hit=[&](motion::Point center,motion::Point radius) { return shot_hit(center,radius,true); };
        boss_context.scythe_hit=[&](motion::Point center,motion::Point radius) { return shot_hit(center,radius,false); };
        const auto before=boss_snapshot().score_delta;
        const auto sink=[&](const orange::Event& event) {
            orange_events_.push_back(event);
            if(event.type==orange::EventType::sound)sound_action(sound::ActionKind::play,std::uint16_t(event.value));
            if(event.type==orange::EventType::fade)sound_action(sound::ActionKind::command,std::uint16_t(0x200|event.value));
            if (event.type==orange::EventType::circle) circles_.add(event.position,event.count!=0);
            if (event.type==orange::EventType::item) items_.add(event.position,static_cast<item::Type>(event.value));
            if (event.type==orange::EventType::hp)
                hud::apply(hud_text_,hud::hp_update(hud_hp_previous_,motion::wrap(event.value),motion::wrap(event.count)));
        };
        if(gengetsu_) {
            gengetsu::Context extra_context;static_cast<orange::Context&>(extra_context)=boss_context;
            extra_context.bombing=life_.state().bombing!=0;
            gengetsu_->set_player_hit(std::uint8_t(bullets_.snapshot().player_hit));
            gengetsu_->update(extra_context,bullets_,gathers_,ring_,sink);
            if(gengetsu_->snapshot().lasers.player_hit)bullets_.set_player_hit(true);
        } else if(mugetsu_) {
            th04::portable::mugetsu::Context extra_context;static_cast<orange::Context&>(extra_context)=boss_context;
            extra_context.bombing=life_.state().bombing!=0;
            mugetsu_->update(extra_context,bullets_,gathers_,ring_,sink);
        } else if(yuuka6_active_) {
            th04::portable::yuuka6::Context final_context;static_cast<orange::Context&>(final_context)=boss_context;
            final_context.ordinary_hit=[&](motion::Point center,motion::Point radius) { return shot_hit(center,radius,false); };
            if(bullets_.snapshot().player_hit) thick_lasers_.set_player_hit(1);
            yuuka6_->update(final_context,bullets_,gathers_,sparks_,thick_lasers_,yuuka6_entities_,ring_,sink);
            if(thick_lasers_.snapshot().player_hit) bullets_.set_player_hit(true);
        } else if(yuuka5_active_) {
            if(bullets_.snapshot().player_hit) thick_lasers_.set_player_hit(1);
            yuuka5_->update(boss_context,bullets_,gathers_,thick_lasers_,ring_,sink);
            if(thick_lasers_.snapshot().player_hit) bullets_.set_player_hit(true);
        } else if(marisa_active_) {
            th04::portable::marisa::Context npc;static_cast<orange::Context&>(npc)=boss_context;
            npc.bit_hit=[&](motion::Point center,motion::Point radius) { return shot_hit(center,radius,false); };
            npc.repair_flystep_zero_divisor=true;
            marisa_->update(npc,bullets_,gathers_,sparks_,ring_,sink);
        } else if(reimu_active_) {
            reimu::Context npc;static_cast<orange::Context&>(npc)=boss_context;
            npc.orb_hit=[&](motion::Point center,motion::Point radius) { return shot_hit(center,radius,false); };
            reimu_->update(npc,bullets_,gathers_,sparks_,ring_,sink);
        } else if(elly_active_) elly_->update(boss_context,bullets_,gathers_,sparks_,ring_,sink);
        else if(kurumi_active_) kurumi_->update(boss_context,bullets_,gathers_,sparks_,ring_,sink);
        else orange_.update(boss_context,bullets_,gathers_,sparks_,ring_,sink);
        life_.set_invincibility(boss_snapshot().invincibility);
        circles_.set_color(boss_snapshot().circle_color);
        score_.score_delta+=boss_snapshot().score_delta-before;
        const auto target=boss_snapshot().homing;
        if (target.x==-15984 && target.y==-15984) homing_target_.reset();else homing_target_=target;
    }
    item_events_ = items_.update(score_, player_.position().current, pull_items, life_.state().miss_time,
        [this](const item::CollectionEffects& effects,const item::ScoreState& current) {
            if(effects.shot_level_changed)hud::apply(hud_text_,hud::power(current.power,shot::level_for_power(current.power)));
            if(effects.hud_bombs_changed)hud::apply(hud_text_,hud::bombs(current.remaining_bombs));
            if(effects.hud_lives_changed)hud::apply(hud_text_,hud::lives(current.remaining_lives));
            if(effects.extend_sound)sound_action(sound::ActionKind::play,7);
            if(effects.hud_point_items_changed)hud::apply(hud_text_,hud::points(current.stage_point_items_collected));
            if(effects.hud_dream_changed)hud::apply(hud_text_,hud::dream(current.dream_score));
        },[this](std::uint16_t effect){sound_action(sound::ActionKind::play,effect);});
    gathers_.update([this,&bullet_context,&bullet_sink](const bullet::Template& saved) {
        bullets_.release(saved,bullet_context,ring_,bullet_sink);
    });
    if(boss_active())life_.synchronize_graphics(boss_snapshot().palette_tone,boss_snapshot().circle_color);
    // bullet_clear_time is one original global. The bullet update above may
    // have consumed it; publish that value before the Bomb render boundary.
    life_.set_clear_time(bullets_.snapshot().clear_time);
    auto bomb_context=life_context();
    const auto& before_bomb=life_.state();
    bomb_frame_.active=before_bomb.bombing!=0;
    bomb_frame_.frame=before_bomb.bomb_frame;
    bomb_frame_.scroll_line=scroll_line_;
    if(bomb_frame_.active) {
        if(before_bomb.bomb_frame<48) {
            bomb_frame_.pixels=bomb::Pixels::tiles;
            bomb_frame_.cel=before_bomb.bomb_frame<32 ? before_bomb.bomb_frame/4 : before_bomb.bomb_frame/2-8;
        } else if(before_bomb.bomb_frame<176)bomb_frame_.pixels=bomb::Pixels::character;
        if(bomb_observer_)bomb_observer_(before_bomb,ring_,bomb_effect_,circles_,std::uint16_t(frames_));
    }
    life_.render_bomb(bomb_context);
    bullet_render_clear_=bullets_.snapshot().clear_time;
    bullet_render_zap_=bullets_.snapshot().zap_frame;
    publish_boss_graphics();
    circles_.set_color(life_.state().circle_color);
    if(gengetsu_)gengetsu_->prepare_render(std::uint16_t(frames_));
    else if(mugetsu_)mugetsu_->prepare_render();
    else if(yuuka6_active_) {
        if(bullets_.snapshot().player_hit) thick_lasers_.set_player_hit(1);
        yuuka6_foreground_.prepare_render(*yuuka6_,static_cast<std::uint16_t>(frames_),thick_lasers_,yuuka6_entities_);
    } else if(yuuka5_active_) {
        // Gather releases occur after boss update and can also set the shared
        // spawn-contact latch. Death consumption remains a separate owner.
        if(bullets_.snapshot().player_hit) thick_lasers_.set_player_hit(1);
        yuuka5_->prepare_render(static_cast<std::uint16_t>(frames_),thick_lasers_);
    } else if(marisa_active_) marisa_->prepare_render();
    else if(reimu_active_) reimu_->prepare_render(static_cast<std::uint16_t>(frames_));
    else if(elly_active_) elly_->prepare_render(static_cast<std::uint16_t>(frames_));
    else if(kurumi_active_) kurumi_->prepare_render(static_cast<std::uint16_t>(frames_));
    else if (orange_active_) orange_.prepare_render(static_cast<std::uint16_t>(frames_));
    if (midboss_state().active && !stage5_ && !stage6_) {
        if(midbossx_) midbossx_->prepare_render(midboss_context);else if(midboss4_) midboss4_->prepare_render(midboss_context);else if(midboss3_) midboss3_->prepare_render(midboss_context);else if(midboss2_) midboss2_->prepare_render(midboss_context);else midboss_.prepare_render(midboss_context);
    }
    enemies_.prepare_render();
    // Retain the actual pre-increment rendering phase. Blocking scenes and
    // repeated host paints consume this cache without advancing the player.
    player_draws_=player::render_requests(life_.state(),player_.position(),
        shot::level_for_power(score_.power),playchar_==application::Playchar::reimu ? 38 : 39,
        static_cast<std::uint8_t>(frames_&3u),scroll_line_);
    // Item scoring already exposes performance events; apply their byte
    // clamps before the next frame's autofire interval decisions.
    constexpr std::uint8_t minimum[]{4,11,20,22,16},maximum[]{16,24,32,34,20};
    for (const auto& event:item_events_.events) {
        if (event.collection.playperf_raised) {
            const auto raised = static_cast<std::uint8_t>(performance_+event.collection.playperf_raised);
            performance_ = std::min(raised,maximum[rank_]);
        }
        if (event.miss.playperf_lowered) {
            const auto lowered = static_cast<std::uint8_t>(performance_-event.miss.playperf_lowered);
            const int signed_lowered = lowered<128 ? lowered : int(lowered)-256;
            performance_ = signed_lowered<int(minimum[rank_]) ? minimum[rank_] : lowered;
        }
    }
    const bool leaving=overlay_.callback==transition::Callback::leave;
    const auto writes=transition::update_overlay(overlay_);
    if(!writes.empty()) { overlay_cell_=writes.back();if(leaving) leave_text_replaced_=true; }
    run_frames_.complete(0,static_cast<std::uint16_t>(slowdown()));
    sound_action(sound::ActionKind::update);
    ++frames_;
    const unsigned interval=score_.remaining_lives>=10 ? 1000 : 6000-score_.remaining_lives*500;
    if (static_cast<std::uint16_t>(frames_)%interval==0) performance_=std::min(
        static_cast<std::uint8_t>(performance_+1),maximum[rank_]);
    // Original MAIN drains score AFTER the frame counter and periodic rank
    // raise. All actor/item awards above feed this same pending accumulator.
    scoreboard_.delta=score_.score_delta;scoreboard_.lives=score_.remaining_lives;
    scoreboard_.performance=performance_;scoreboard_.bullet_clear=bullets_.snapshot().clear_time;
    score_events_=score::update(scoreboard_);
    apply_score_hud(score_events_);
    score_.score_delta=scoreboard_.delta;score_.remaining_lives=scoreboard_.lives;
    performance_=scoreboard_.performance;
    if(scoreboard_.bullet_clear>bullets_.snapshot().clear_time) bullets_.clear();
    life_.set_clear_time(bullets_.snapshot().clear_time);
    application_->publish_main_resources(score_.remaining_lives,score_.remaining_bombs);
}

item::MissSpawnResult State::add_miss_items() {
    return items_.add_miss(ring_, player_.position().current, score_.remaining_lives);
}

application::RunStatistics State::run_statistics() const {
    return gameplay::run_statistics(scoreboard_,score_,items_.spawned(),
        enemies_.snapshot().gone,enemies_.snapshot().killed_count,run_frames_);
}
void State::observe_refreshes(std::uint16_t elapsed) {
    if(observed_frame_==run_frames_.total) return;
    run_frames_.slow+=elapsed>=slowdown();
    observed_frame_=run_frames_.total;
}
} // namespace th04::portable::gameplay
