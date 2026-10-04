#include "main_state.hpp"
#include "stage_session.hpp"
#include <stdexcept>
#include <algorithm>

namespace th04::portable::gameplay {
State::State(application::State& application):application_(&application) {
    if (application.program() != application::Program::main) {
        throw std::logic_error("live MAIN requires a completed OP handoff");
    }
    score_.power = 1;
    playchar_ = application.resident().playchar;
    shot_type_ = application.resident().shot_type;
    stage_id_=application.resident().resource_stage;
    bonus_context_.stage=application.resident().stage;
    bonus_context_.resource_stage=stage_id_;
    bonus_context_.credit_lives=application.resident().credit_lives;
    turbo_ = application.resident().stage == 6 || application.resident().config.turbo;
    rank_ = application.resident().stage == 6 ? 4 : application.resident().config.rank;
    bonus_context_.rank=rank_;
    performance_ = rank_ == 2 ? 20 : (rank_ == 3 ? 22 : 16);
    score_.remaining_lives = application.resident().credit_lives;
    score_.remaining_bombs = application.resident().credit_bombs;
    application.publish_main_resources(score_.remaining_lives,score_.remaining_bombs);
    scoreboard_.digits=application.resident().score_digits;
    scoreboard_.lives=score_.remaining_lives;
    constexpr std::uint8_t minimum[]{4,11,20,22,16},maximum[]{16,24,32,34,20};
    scoreboard_.performance=performance_;scoreboard_.minimum=minimum[rank_];scoreboard_.maximum=maximum[rank_];
    // Saved high-score loading is a separate OP/persistence boundary. Until
    // it joins, the preview starts with the original zero-valued HUD state.
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
}

void State::load_stage(const stage::Program::Bytes& standard) {
    stage_ = std::make_unique<stage::Program>(standard);
    enemies_ = enemy::System{};
    bullets_ = bullet::System{};
    gathers_ = gather::System{};
    midboss_ = midboss::System{};
    orange_=orange::System{};circles_=circle::System{};
    orange_active_=false;post_boss_dialog_pending_=false;
    clear_bonus_.reset();departure_.reset();overlay_={};
    overlay_cell_={transition::TextKind::character,4,1,32,5};
    frame_suspended_=false;dialog_finished_=false;next_stage_requested_=false;leave_text_replaced_=false;
    homing_target_.reset();
}
void State::start_orange_after_dialog() {
    if (!stage_ || orange_active_ || midboss_.snapshot().active) throw std::logic_error("invalid Orange dialog handoff");
    orange_active_=true;
}
void State::prepare_next_stage_actors(const stage::Program::Bytes& standard) {
    if(!next_stage_requested_ || stage_id_!=0 || application_->resident().stage!=1)
        throw std::logic_error("Stage2 actor preparation requires its actual departure request");
    // Validate before changing the live owners or consuming process random.
    auto next=std::make_unique<stage::Program>(standard);
    session::initialize_actors({player_,shots_,enemies_,bullets_,sparks_,gathers_,
        circles_,items_,score_,scoreboard_,ring_,drops_},[this] {
            return static_cast<std::uint8_t>(application_->next_process_random());
        });
    stage_=std::move(next);stage_id_=1;frames_=0;
    midboss_=midboss::System(session::prepare_stage2_midboss(midboss_.snapshot()));
    orange_active_=false;clear_bonus_.reset();departure_.reset();overlay_={};
    overlay_cell_={transition::TextKind::character,4,1,32,5};
    frame_suspended_=false;dialog_finished_=false;post_boss_dialog_pending_=false;
    next_stage_requested_=false;leave_text_replaced_=false;
    palette_tone_before_frame_=100;
    bonus_context_.stage=1;bonus_context_.resource_stage=1;
    score_events_.clear();enemy_events_.clear();bullet_events_.clear();
    midboss_events_.clear();orange_events_.clear();item_events_={};
    // Score/power/performance/resident statistics and MAIN generation/seed
    // persist. Asset replacement and midboss2/Kurumi are separate consumers;
    // never run the Stage1 midboss callback under the new stage identity.
}
void State::finish_post_boss_dialog() {
    if(!post_boss_dialog_pending_ || clear_bonus_) throw std::logic_error("invalid stage-clear bonus handoff");
    dialog_finished_=true;post_boss_dialog_pending_=false;
}
void State::apply_clear_bonus() {
    if(clear_bonus_) throw std::logic_error("repeated stage-clear bonus");
    bonus_context_.power=score_.power;bonus_context_.dream=score_.dream_score;
    bonus_context_.graze=bullets_.snapshot().graze;
    bonus_context_.point_items=score_.stage_point_items_collected;
    bonus_context_.remaining_lives=score_.remaining_lives;
    bonus_context_.defeated_in_time=orange_.snapshot().patterns_or_bonus;
    constexpr std::uint8_t minimum[]{4,11,20,22,16},maximum[]{16,24,32,34,20};
    bonus::State state;state.score_delta=score_.score_delta;state.bombs=score_.remaining_bombs;
    state.performance=performance_;state.minimum=minimum[rank_];state.maximum=maximum[rank_];
    clear_bonus_=bonus::apply(bonus_context_,state);
    score_.score_delta=state.score_delta;score_.remaining_bombs=state.bombs;performance_=state.performance;
    // Called at the original bonus position when the blocked frame resumes,
    // before items/gathers/render/clock/score drain complete that same frame.
}
void State::update(std::uint16_t held_input, bool shift, bool pull_items,motion::Subpixel scroll_delta,stage::Background* background) {
    score_events_.clear();
    if(next_stage_requested_) return; // Stage2 resources have a separate owner.
    if(awaiting_stage2_midboss()) return;
    const bool resumed=frame_suspended_;
    if(resumed && !dialog_finished_) return;
    enemy::Context context;
    bullet::Context bullet_context;
    if(resumed) {
        context=suspended_context_;bullet_context=suspended_bullets_;pull_items=suspended_pull_items_;
    } else {
        enemy_events_.clear();bullet_events_.clear();midboss_events_.clear();orange_events_.clear();
        if(orange_active_) {
            palette_tone_before_frame_=orange_.snapshot().palette_tone;
            orange_background_phase_=orange_.snapshot().phase;
            orange_background_frame_=orange_.snapshot().phase_frame;
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
    if(!resumed) {
        // STD dispatch precedes player movement; enemies created here can run
        // their first setup/move instructions later in this same frame.
        if (stage_ && !orange_active_) for (const auto& spawn:stage_->run(static_cast<std::uint16_t>(frames_),midboss_.snapshot().active)) {
            enemies_.add(spawn,context,ring_);
        }
        if (stage_ && !orange_active_) midboss_.activate(static_cast<std::uint16_t>(frames_));
        // MAIN's loop calls player_update before items_update. A pickup therefore
        // sees the player's new position for this frame, not the preceding one.
        circles_.update();sparks_.update();
        player_.update(held_input, shift);
        shots_.update((held_input & shot::input_shot) != 0, playchar_, shot_type_, score_.power,
                      player_.position(), ring_, homing_target_);
        context.player = player_.position().current;
        bullet_context.player=context.player;bullet_context.rank=rank_;bullet_context.performance=performance_;
        bullet_context.frame_mod2=context.frame_mod2;bullet_context.turbo=turbo_;
        if (orange_active_) bullet_context.invincibility=orange_.snapshot().invincibility;
        constexpr std::uint16_t graze_scores[]{100,250,400,500,2560};
        bullet_context.graze_score=graze_scores[rank_];
        const auto score_before=bullets_.snapshot().score_delta;
        bullets_.begin_frame();bullets_.update(bullet_context,bullet_sink);
        score_.score_delta+=bullets_.snapshot().score_delta-score_before;
        if (stage_) {
            const auto before = enemies_.snapshot().score_delta;
            enemies_.update(*stage_,context,ring_,shots_,[this,&bullet_context,&bullet_sink](const enemy::Event& event) {
                enemy_events_.push_back(event);
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
            const auto result=shots_.hittest(center,radius,{false,false,context.frame_mod2,context.frame_mod4});
            score_.score_delta+=shots_.snapshot().score_delta-before;
            for (unsigned i=0;i<result.spark_count;++i) sparks_.add_random(result.sparks[i],128,1,ring_);
            return result.damage;
        };
        if (midboss_.snapshot().active) {
            const auto before=midboss_.score_delta();
            midboss_.update(midboss_context,bullets_,ring_,[&](const midboss::Event& event) {
                midboss_events_.push_back(event);
                if (event.type==midboss::EventType::circle) sparks_.add_circle(event.position,event.value,event.count);
                if (event.type==midboss::EventType::homing) homing_target_=event.position;
                if (background && event.type==midboss::EventType::tile) background->set_tile(event.position.x,event.position.y,event.value);
                if (background && event.type==midboss::EventType::scroll) background->set_speed(static_cast<std::uint8_t>(event.value));
            });
            score_.score_delta+=midboss_.score_delta()-before;
        }
    } // Prefix executes once even if the dialog suspends this frame.
    if(orange_active_ && orange_.snapshot().phase==255) {
        if(!departure_) {
            transition::Departure d;d.frame=orange_.snapshot().phase_frame;
            d.stage=application_->resident().stage;d.stage_ascii=application_->resident().stage_ascii;
            d.graze=application_->resident().graze;d.stage_graze=bullets_.snapshot().graze;
            d.homing=orange_.snapshot().homing;departure_=d;
        }
        transition::update_departure(*departure_,overlay_,!resumed && !clear_bonus_,[&](const transition::Event& e) {
            switch(e.kind) {
            case transition::Kind::tone:orange_events_.push_back({orange::EventType::tone,{},60,0});break;
            case transition::Kind::dialog:
                application_->add_stage_graze(departure_->stage_graze);
                orange_events_.push_back({orange::EventType::dialog,{},0,0});break;
            case transition::Kind::bonus:apply_clear_bonus();orange_events_.push_back({orange::EventType::stage_bonus,{},0,0});break;
            case transition::Kind::fade:orange_events_.push_back({orange::EventType::fade,{},10,0});break;
            case transition::Kind::next_stage:
                application_->advance_main_stage();next_stage_requested_=true;
                orange_events_.push_back({orange::EventType::next_stage,{},0,0});break;
            case transition::Kind::delay:orange_events_.push_back({orange::EventType::delay,{},1,0});break;
            }
        });
        orange_.apply_departure(*departure_);
        if(departure_->blocked) {
            suspended_context_=context;suspended_bullets_=bullet_context;suspended_pull_items_=pull_items;
            frame_suspended_=true;post_boss_dialog_pending_=true;return;
        }
        frame_suspended_=false;dialog_finished_=false;homing_target_.reset();
    } else if (orange_active_) {
        orange::Context boss_context;boss_context.frame=static_cast<std::uint16_t>(frames_);
        boss_context.bullets=bullet_context;boss_context.power=score_.power;
        boss_context.hit=[&](motion::Point center,motion::Point radius) {
            const auto before=shots_.snapshot().score_delta;
            const auto result=shots_.hittest(center,radius,{false,true,context.frame_mod2,context.frame_mod4});
            score_.score_delta+=shots_.snapshot().score_delta-before;
            for (unsigned i=0;i<result.spark_count;++i) sparks_.add_random(result.sparks[i],128,1,ring_);
            return result.damage;
        };
        const auto before=orange_.snapshot().score_delta;
        orange_.update(boss_context,bullets_,gathers_,sparks_,ring_,[&](const orange::Event& event) {
            orange_events_.push_back(event);
            if (event.type==orange::EventType::circle) circles_.add(event.position);
            if (event.type==orange::EventType::item) items_.add(event.position,static_cast<item::Type>(event.value));
        });
        circles_.set_color(orange_.snapshot().circle_color);
        score_.score_delta+=orange_.snapshot().score_delta-before;
        const auto target=orange_.snapshot().homing;
        if (target.x==-15984 && target.y==-15984) homing_target_.reset();else homing_target_=target;
    }
    item_events_ = items_.update(score_, player_.position().current, pull_items, 0);
    gathers_.update([this,&bullet_context,&bullet_sink](const bullet::Template& saved) {
        bullets_.release(saved,bullet_context,ring_,bullet_sink);
    });
    if (orange_active_) orange_.prepare_render(static_cast<std::uint16_t>(frames_));
    if (midboss_.snapshot().active) midboss_.prepare_render(midboss_context);
    enemies_.prepare_render();
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
    ++frames_;
    const unsigned interval=score_.remaining_lives>=10 ? 1000 : 6000-score_.remaining_lives*500;
    if (static_cast<std::uint16_t>(frames_)%interval==0) performance_=std::min(
        static_cast<std::uint8_t>(performance_+1),maximum[rank_]);
    // Original MAIN drains score AFTER the frame counter and periodic rank
    // raise. All actor/item awards above feed this same pending accumulator.
    scoreboard_.delta=score_.score_delta;scoreboard_.lives=score_.remaining_lives;
    scoreboard_.performance=performance_;scoreboard_.bullet_clear=bullets_.snapshot().clear_time;
    score_events_=score::update(scoreboard_);
    score_.score_delta=scoreboard_.delta;score_.remaining_lives=scoreboard_.lives;
    performance_=scoreboard_.performance;
    if(scoreboard_.bullet_clear>bullets_.snapshot().clear_time) bullets_.clear();
    application_->publish_main_resources(score_.remaining_lives,score_.remaining_bombs);
}

item::MissSpawnResult State::add_miss_items() {
    return items_.add_miss(ring_, player_.position().current, score_.remaining_lives);
}
} // namespace th04::portable::gameplay
