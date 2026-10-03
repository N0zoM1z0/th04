#include "main_state.hpp"
#include <stdexcept>

namespace th04::portable::gameplay {
State::State(application::State& application) {
    if (application.program() != application::Program::main) {
        throw std::logic_error("live MAIN requires a completed OP handoff");
    }
    score_.power = 1;
    playchar_ = application.resident().playchar;
    shot_type_ = application.resident().shot_type;
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

void State::update(std::uint16_t held_input, bool shift, bool pull_items) {
    // MAIN's loop calls player_update before items_update. A pickup therefore
    // sees the player's new position for this frame, not the preceding one.
    player_.update(held_input, shift);
    shots_.update((held_input & shot::input_shot) != 0, playchar_, shot_type_, score_.power,
                  player_.position(), ring_);
    item_events_ = items_.update(score_, player_.position().current, pull_items, 0);
    ++frames_;
}

item::MissSpawnResult State::add_miss_items() {
    return items_.add_miss(ring_, player_.position().current, score_.remaining_lives);
}
} // namespace th04::portable::gameplay
