#pragma once

#include <array>
#include <cstdint>
#include <functional>

#include "menu_state.hpp"
#include "random_lcg.hpp"

namespace th04::portable::application {

enum class Program : std::uint8_t {
    op,
    main,
    maine,
    exited,
};

enum class Playchar : std::uint8_t {
    reimu,
    marisa,
};

enum class ShotType : std::uint8_t {
    a,
    b,
};

// These values are part of the cross-executable resident contract. Keeping
// their historical byte values lets migrated Ending and score code classify a
// run without carrying the 16-bit resident structure into native code.
enum class EndSequence : std::uint8_t {
    score = 0x00,
    in_game = 0x37,
    extra = 0xfd,
    bad = 0xfe,
    good = 0xff,
};

enum class MaineRoute : std::uint8_t {
    score_registration,
    extra,
    ending,
};

struct RunStatistics {
    std::array<std::uint8_t, 8> score_digits{};
    std::uint16_t std_frames = 0;
    std::uint16_t items_spawned = 0;
    std::uint16_t items_collected = 0;
    std::uint16_t point_items_collected = 0;
    std::uint16_t max_valued_point_items_collected = 0;
    std::uint16_t enemies_gone = 0;
    std::uint16_t enemies_killed = 0;
    std::uint32_t slow_frames = 0;
    std::uint32_t frames = 0;
};

// Semantic replacement for the ZUN.COM paragraph block. This is deliberately
// ordinary fixed-width host state: it preserves values and lifetimes needed by
// the current migration slice, without preserving segment pointers or padding.
struct ResidentState {
    menu::Options config{};
    std::uint8_t remaining_lives = 0;
    std::uint8_t credit_lives = 0;
    std::uint8_t remaining_bombs = 0;
    std::uint8_t credit_bombs = 0;
    std::uint8_t stage = 0,stage_ascii = '0';
    std::uint16_t graze = 0;
    // These resident counters span Stages and are cleared for a new MAIN run.
    // Death/Bomb owners will increment them when those actions are migrated.
    std::uint8_t miss_count = 0,bombs_used = 0;
    std::uint8_t resource_stage = 0;
    Playchar playchar = Playchar::reimu;
    ShotType shot_type = ShotType::a;
    // Persistent OP menu-time accumulator. This seeds MAIN but never aliases
    // any executable generation's process-local LCG.
    std::uint32_t random_seed_source = 0;
    std::array<std::uint8_t, 8> score_digits{};
    EndSequence end_sequence = EndSequence::score;
    char end_type_ascii = '0';
    RunStatistics statistics{};
    std::uint8_t demo_stage = 0;
    std::uint8_t demo_number = 0;
    bool zunsoft_shown = false;
};

// DOS used execl() to replace OP, MAIN and MAINE around a resident paragraph
// block. The native product keeps one process and makes the same ownership
// boundaries explicit. A successful transition increments generation(), so
// host resource owners can reject stale executable-local state later.
class State {
public:
    Program program() const { return program_; }
    std::uint32_t generation() const { return generation_; }
    const ResidentState& resident() const { return resident_; }
    std::uint32_t process_random_state() const { return process_random_.state(); }

    void apply_options(const menu::Options& options);
    void advance_op_menu_frame();
    void start_normal(Playchar playchar, ShotType shot_type);
    void start_extra(Playchar playchar, ShotType shot_type);
    void start_next_demo();
    void prepare_next_demo();
    void start_prepared_demo();

    void publish_main_resources(std::uint8_t lives,std::uint8_t bombs);
    void publish_player_statistics(std::uint8_t misses,std::uint8_t bombs);
    void prepare_main_score();
    void add_stage_graze(std::uint16_t);
    void initialize_main_gameplay();
    // Original stage_session_init does this AFTER gameplay/high-score setup.
    void initialize_demo_stage();
    void advance_main_stage();
    // Resource replacement happens inside the current MAIN process.
    void publish_main_resource_stage(std::uint8_t stage);
    void return_from_main(const RunStatistics& statistics);
    void finish_main(
        const RunStatistics& statistics, EndSequence end_sequence,
        const std::function<void()>& release_main={}
    );
    void prepare_main_ending(EndSequence);
    void prepare_main_extra();
    MaineRoute maine_route() const;
    void seed_maine_verdict_random();
    void publish_maine_verdict_completion(std::uint16_t standard_frames);
    void finish_maine();
    void exit_from_op();
    std::uint16_t next_process_random();

private:
    bool demo_prepared_=false;
    void require_program(Program expected) const;
    void enter(Program next);
    void begin_main(
        std::uint8_t stage, std::uint8_t resource_stage,
        std::uint8_t lives, std::uint8_t bombs,
        Playchar playchar, ShotType shot_type, std::uint8_t demo_number
    );
    void publish_statistics(const RunStatistics& statistics);

    Program program_ = Program::op;
    std::uint32_t generation_ = 1;
    ResidentState resident_{};
    rng::Lcg32 process_random_{};
};

} // namespace th04::portable::application
