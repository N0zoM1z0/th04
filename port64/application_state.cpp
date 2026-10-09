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
    // DOS execl() loaded a fresh initialized data image for every transition.
    process_random_.reseed(rng::Lcg32::default_seed);
}

void State::apply_options(const menu::Options& options) {
    require_program(Program::op);
    resident_.config = options;
}

void State::advance_op_menu_frame() {
    require_program(Program::op);
    // uint32_t gives the resident accumulator its historical wrap semantics.
    ++resident_.random_seed_source;
}

void State::begin_main(
    std::uint8_t stage, std::uint8_t resource_stage,
    std::uint8_t lives, std::uint8_t bombs,
    Playchar playchar, ShotType shot_type, std::uint8_t demo_number
) {
    require_program(Program::op);
    resident_.stage = stage;
    resident_.stage_ascii=static_cast<std::uint8_t>('0'+(demo_number ? resource_stage : stage));
    resident_.resource_stage = resource_stage;
    resident_.credit_lives = lives;
    resident_.credit_bombs = bombs;
    resident_.playchar = playchar;
    resident_.shot_type = shot_type;
    resident_.demo_number = demo_number;
    resident_.demo_stage = resource_stage;
    resident_.end_sequence = EndSequence::in_game;
    resident_.miss_count=0;resident_.bombs_used=0;
    enter(Program::main);

    // MAIN copies the resident value once after process startup. Recorded demos
    // replace it before their first Stage runtime initialization.
    process_random_.reseed(resident_.random_seed_source);
}

void State::start_normal(Playchar playchar, ShotType shot_type) {
    begin_main(
        0, 0, resident_.config.lives, resident_.config.bombs,
        playchar, shot_type, 0
    );
}

void State::initialize_main_gameplay() {
    require_program(Program::main);
    // MAIN gameplay_session_init owns these resets after process startup.
    // Resident score digits still describe the outgoing run until publication.
    resident_.graze=0;resident_.miss_count=0;resident_.bombs_used=0;
    resident_.end_sequence=EndSequence::in_game;
}

void State::initialize_demo_stage() {
    require_program(Program::main);
    if(!resident_.demo_number || resident_.stage!=0)
        throw std::logic_error("demo stage requires first MAIN session");
    resident_.stage=resident_.demo_stage;
    resident_.stage_ascii=static_cast<std::uint8_t>('0'+resident_.stage);
    process_random_.reseed(rng::Lcg32::demo_seed);
}

void State::start_extra(Playchar playchar, ShotType shot_type) {
    // TH04 Extra ignores configurable starting resources.
    begin_main(6, 6, 3, 2, playchar, shot_type, 0);
}

void State::start_next_demo() {
    prepare_next_demo();start_prepared_demo();
}
void State::prepare_next_demo() {
    require_program(Program::op);
    if(demo_prepared_)throw std::logic_error("OP demo already prepared");
    const std::uint8_t demo_number = std::uint8_t(
        (resident_.demo_number >= DEMOS.size()) ? 1 : resident_.demo_number + 1
    );
    const auto& demo = DEMOS[demo_number - 1];

    // Preserve TH04's split fields: the live stage starts at zero, while the
    // resource/demo stage selects the recorded stage loaded by MAIN.
    resident_.stage=0;resident_.resource_stage=demo.stage;
    resident_.stage_ascii=std::uint8_t('0'+demo.stage);
    resident_.credit_lives=resident_.credit_bombs=3;
    resident_.playchar=demo.playchar;resident_.shot_type=demo.shot_type;
    resident_.demo_number=demo_number;resident_.demo_stage=demo.stage;
    demo_prepared_=true;
}
void State::start_prepared_demo() {
    require_program(Program::op);
    if(!demo_prepared_)throw std::logic_error("MAIN demo requires its OP preparation");
    demo_prepared_=false;enter(Program::main);
    process_random_.reseed(resident_.random_seed_source);
}

void State::publish_main_resources(std::uint8_t lives,std::uint8_t bombs) {
    require_program(Program::main);
    resident_.remaining_lives=lives;resident_.remaining_bombs=bombs;
}
void State::publish_player_statistics(std::uint8_t misses,std::uint8_t bombs) {
    require_program(Program::main);resident_.miss_count=misses;resident_.bombs_used=bombs;
}
void State::prepare_main_score() {
    require_program(Program::main);resident_.end_sequence=EndSequence::score;
}
void State::add_stage_graze(std::uint16_t amount) {
    require_program(Program::main);
    resident_.graze=static_cast<std::uint16_t>(resident_.graze+amount);
}
void State::publish_main_resource_stage(std::uint8_t stage) {
    require_program(Program::main);
    if(stage!=resident_.stage) throw std::logic_error("resource stage does not match requested MAIN stage");
    resident_.resource_stage=stage;
}

void State::advance_main_stage() {
    require_program(Program::main);
    ++resident_.stage;++resident_.stage_ascii;
    // Stage-owned resources join only when the next session loads. This
    // request neither replaces MAIN nor reseeds its process-local generator.
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
    const RunStatistics& statistics, EndSequence end_sequence,
    const std::function<void()>& release_main
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
    if(release_main) release_main();
    enter(Program::maine);
}

void State::prepare_main_ending(EndSequence sequence) {
    require_program(Program::main);
    if(sequence!=EndSequence::good && sequence!=EndSequence::bad)
        throw std::invalid_argument("Ending requires a Good or Bad completion");
    // end_game_* writes these before fade16. MAIN storage and generator still
    // live until GameExecl publishes statistics and replaces the process.
    resident_.end_sequence=sequence;
    resident_.end_type_ascii=sequence==EndSequence::good ? '0' : '1';
}

void State::prepare_main_extra() {
    require_program(Program::main);
    if(resident_.stage!=6 || resident_.resource_stage!=6)
        throw std::logic_error("Extra completion requires Extra MAIN");
    // MAIN0AAF:0D1F writes only ES_EXTRA before its fade16. end_type_ascii
    // survives unchanged; the Extra MAINE branch never consumes it.
    resident_.end_sequence=EndSequence::extra;
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

void State::seed_maine_verdict_random() {
    require_program(Program::maine);
    // This is an explicit verdict event rather than an MAINE entry action:
    // Extra and score-only routes save while the new process is still at 1.
    process_random_.reseed(resident_.random_seed_source);
}
void State::publish_maine_verdict_completion(std::uint16_t frames) {
    require_program(Program::maine);
    // Good/Extra completion changes only the resident STD counter. Score,
    // cumulative frame counts and the resident menu seed stay unchanged.
    resident_.statistics.std_frames=frames;
}

void State::finish_maine() {
    require_program(Program::maine);
    enter(Program::op);
}

void State::exit_from_op() {
    require_program(Program::op);
    enter(Program::exited);
}

std::uint16_t State::next_process_random() {
    if (program_ == Program::exited) {
        throw std::logic_error("exited product has no process-local random state");
    }
    return process_random_.next15();
}

} // namespace th04::portable::application
