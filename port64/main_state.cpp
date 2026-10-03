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
}

void State::load_stage(const stage::Program::Bytes& standard) {
    stage_ = std::make_unique<stage::Program>(standard);
    enemies_ = enemy::System{};
}
void State::update(std::uint16_t held_input, bool shift, bool pull_items,motion::Subpixel scroll_delta) {
    enemy_events_.clear();
    enemy::Context context;
    context.player = player_.position().current;context.rank = rank_;context.performance = performance_;
    context.scroll_delta = scroll_delta;context.frame_mod2 = frames_%2;context.frame_mod4 = frames_%4;
    // STD dispatch precedes player movement; enemies created here can run
    // their first setup/move instructions later in this same frame.
    if (stage_) for (const auto& spawn:stage_->run(static_cast<std::uint16_t>(frames_))) {
        enemies_.add(spawn,context,ring_);
    }
    // MAIN's loop calls player_update before items_update. A pickup therefore
    // sees the player's new position for this frame, not the preceding one.
    player_.update(held_input, shift);
    shots_.update((held_input & shot::input_shot) != 0, playchar_, shot_type_, score_.power,
                  player_.position(), ring_, enemies_.snapshot().homing_target);
    context.player = player_.position().current;
    if (stage_) {
        const auto before = enemies_.snapshot().score_delta;
        enemies_.update(*stage_,context,ring_,shots_,[this](const enemy::Event& event) {
            enemy_events_.push_back(event);
            if (event.type==enemy::EventType::drop) {
                if (event.value==255) items_.add_enemy_drop(event.position,drops_);
                else if (event.value<=6) items_.add(event.position,static_cast<item::Type>(event.value));
            }
        });
        score_.score_delta += enemies_.snapshot().score_delta-before;
    }
    item_events_ = items_.update(score_, player_.position().current, pull_items, 0);
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
