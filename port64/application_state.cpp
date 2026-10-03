#include "application_state.hpp"

#include <array>
#include <stdexcept>

namespace th04::portable::application {
namespace {

struct DemoContract {
    std::uint8_t stage;
    Playchar playchar;
    ShotType shot_type;
};

constexpr std::array<DemoContract, 4> DEMOS{{
    {3, Playchar::reimu, ShotType::a},
    {0, Playchar::marisa, ShotType::a},
    {2, Playchar::reimu, ShotType::b},
    {1, Playchar::marisa, ShotType::b},
}};

} // namespace

void State::require_program(Program expected) const {
    if (program_ != expected) {
        throw std::logic_error("portable transition from wrong program state");
    }
}

void State::enter(Program next) {
    program_ = next;
    ++generation_;
}

void State::apply_options(const menu::Options& options) {
    require_program(Program::op);
    resident_.config = options;
}

void State::begin_main(
    std::uint8_t stage, std::uint8_t resource_stage,
    std::uint8_t lives, std::uint8_t bombs,
    Playchar playchar, ShotType shot_type, std::uint8_t demo_number
) {
    require_program(Program::op);
    resident_.stage = stage;
    resident_.resource_stage = resource_stage;
    resident_.credit_lives = lives;
    resident_.credit_bombs = bombs;
    resident_.playchar = playchar;
    resident_.shot_type = shot_type;
    resident_.demo_number = demo_number;
    resident_.demo_stage = resource_stage;
    resident_.end_sequence = EndSequence::in_game;
    enter(Program::main);
}

void State::start_normal(Playchar playchar, ShotType shot_type) {
    begin_main(
        0, 0, resident_.config.lives, resident_.config.bombs,
        playchar, shot_type, 0
    );
}

void State::start_extra(Playchar playchar, ShotType shot_type) {
    // TH04 Extra ignores configurable starting resources.
    begin_main(6, 6, 3, 2, playchar, shot_type, 0);
}

void State::start_next_demo() {
    require_program(Program::op);
    const std::uint8_t demo_number = std::uint8_t(
        (resident_.demo_number >= DEMOS.size()) ? 1 : resident_.demo_number + 1
    );
    const auto& demo = DEMOS[demo_number - 1];

    // Preserve TH04's split fields: the live stage starts at zero, while the
    // resource/demo stage selects the recorded stage loaded by MAIN.
    begin_main(
        0, demo.stage, 3, 3, demo.playchar, demo.shot_type, demo_number
    );
}

void State::publish_statistics(const RunStatistics& statistics) {
    resident_.score_digits = statistics.score_digits;
    resident_.statistics = statistics;
}

void State::return_from_main(const RunStatistics& statistics) {
    require_program(Program::main);
    publish_statistics(statistics);
    enter(Program::op);
}

void State::finish_main(
    const RunStatistics& statistics, EndSequence end_sequence
) {
    require_program(Program::main);
    if (end_sequence == EndSequence::in_game) {
        throw std::invalid_argument("MAINE requires a completed run state");
    }
    publish_statistics(statistics);
    resident_.end_sequence = end_sequence;
    if (end_sequence == EndSequence::good) {
        resident_.end_type_ascii = '0';
    } else if (end_sequence == EndSequence::bad) {
        resident_.end_type_ascii = '1';
    }
    enter(Program::maine);
}

MaineRoute State::maine_route() const {
    require_program(Program::maine);
    switch (resident_.end_sequence) {
    case EndSequence::good:
    case EndSequence::bad:
        return MaineRoute::ending;
    case EndSequence::extra:
        return MaineRoute::extra;
    case EndSequence::score:
        return MaineRoute::score_registration;
    case EndSequence::in_game:
        break;
    }
    throw std::logic_error("invalid MAINE resident end state");
}

void State::finish_maine() {
    require_program(Program::maine);
    enter(Program::op);
}

void State::exit_from_op() {
    require_program(Program::op);
    enter(Program::exited);
}

} // namespace th04::portable::application
