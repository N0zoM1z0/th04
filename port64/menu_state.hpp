#pragma once

#include <cstdint>

namespace th04::portable::menu {

enum class Screen : std::uint8_t {
    main,
    options,
};

enum class MainChoice : std::uint8_t {
    game,
    extra,
    scores,
    music_room,
    options,
    quit,
    count,
};

enum class OptionChoice : std::uint8_t {
    rank,
    lives,
    bombs,
    bgm,
    sound_effects,
    turbo,
    reset,
    quit,
    count,
};

enum class Input : std::uint8_t {
    up,
    down,
    left,
    right,
    confirm,
    cancel,
};

enum class ResultKind : std::uint8_t {
    none,
    choose_main,
    quit,
};

struct Options {
    std::uint8_t rank = 1;
    std::uint8_t lives = 3;
    std::uint8_t bombs = 2;
    std::uint8_t bgm_mode = 2;
    std::uint8_t se_mode = 1;
    bool turbo = true;

    bool operator==(const Options& other) const;
};

struct Result {
    ResultKind kind = ResultKind::none;
    MainChoice choice = MainChoice::game;
};

// Host input drives this state one discrete press at a time. The transitions
// retain OP's menu order, locked-Extra skip, option wrap directions and reset
// defaults without importing 16-bit resident pointers into portable state.
class State {
public:
    explicit State(bool extra_unlocked = false);

    Screen screen() const { return screen_; }
    std::uint8_t selection() const { return selection_; }
    bool extra_unlocked() const { return extra_unlocked_; }
    const Options& options() const { return options_; }

    Result handle(Input input);

private:
    void move_vertical(int direction);
    void change_option(int direction);
    void return_to_main();

    Screen screen_ = Screen::main;
    std::uint8_t selection_ = 0;
    bool extra_unlocked_ = false;
    Options options_{};
};

} // namespace th04::portable::menu
