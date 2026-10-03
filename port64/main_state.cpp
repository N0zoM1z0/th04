#include "main_state.hpp"
#include <stdexcept>
#include <algorithm>

namespace th04::portable::gameplay {
State::State(application::State& application) {
    if (application.program() != application::Program::main) {
        throw std::logic_error("live MAIN requires a completed OP handoff");
    }
    score_.power = 1;
    playchar_ = application.resident().playchar;
    shot_type_ = application.resident().shot_type;
    turbo_ = application.resident().stage == 6 || application.resident().config.turbo;
    rank_ = application.resident().stage == 6 ? 4 : application.resident().config.rank;
    performance_ = rank_ == 2 ? 20 : (rank_ == 3 ? 22 : 16);
    score_.remaining_lives = application.resident().credit_lives;
    score_.remaining_bombs = application.resident().credit_bombs;
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
    homing_target_.reset();
}
void State::update(std::uint16_t held_input, bool shift, bool pull_items,motion::Subpixel scroll_delta,stage::Background* background) {
    enemy_events_.clear();
    bullet_events_.clear();
    midboss_events_.clear();
    enemy::Context context;
    context.player = player_.position().current;context.rank = rank_;context.performance = performance_;
    context.scroll_delta = scroll_delta;context.frame_mod2 = frames_%2;context.frame_mod4 = frames_%4;
    // STD dispatch precedes player movement; enemies created here can run
    // their first setup/move instructions later in this same frame.
    if (stage_) for (const auto& spawn:stage_->run(static_cast<std::uint16_t>(frames_),midboss_.snapshot().active)) {
        enemies_.add(spawn,context,ring_);
    }
    if (stage_) midboss_.activate(static_cast<std::uint16_t>(frames_));
    // MAIN's loop calls player_update before items_update. A pickup therefore
    // sees the player's new position for this frame, not the preceding one.
    sparks_.update();
    player_.update(held_input, shift);
    shots_.update((held_input & shot::input_shot) != 0, playchar_, shot_type_, score_.power,
                  player_.position(), ring_, homing_target_);
    context.player = player_.position().current;
    bullet::Context bullet_context;
    bullet_context.player=context.player;bullet_context.rank=rank_;bullet_context.performance=performance_;
    bullet_context.frame_mod2=context.frame_mod2;bullet_context.turbo=turbo_;
    constexpr std::uint16_t graze_scores[]{100,250,400,500,2560};
    bullet_context.graze_score=graze_scores[rank_];
    const auto bullet_sink=[this](const bullet::Event& event) {
        bullet_events_.push_back(event);
        if (event.type==bullet::EventType::sparks) sparks_.add_random(event.position,event.value,event.count,ring_);
        if (event.type==bullet::EventType::gather) gathers_.request(event);
    };
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
    midboss::Context midboss_context;
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
    item_events_ = items_.update(score_, player_.position().current, pull_items, 0);
    gathers_.update([this,&bullet_context,&bullet_sink](const bullet::Template& saved) {
        bullets_.release(saved,bullet_context,ring_,bullet_sink);
    });
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
    ++frames_;
    const unsigned interval=score_.remaining_lives>=10 ? 1000 : 6000-score_.remaining_lives*500;
    if (static_cast<std::uint16_t>(frames_)%interval==0) performance_=std::min(
        static_cast<std::uint8_t>(performance_+1),maximum[rank_]);
}

item::MissSpawnResult State::add_miss_items() {
    return items_.add_miss(ring_, player_.position().current, score_.remaining_lives);
}
} // namespace th04::portable::gameplay
