#pragma once

#include <array>
#include <cstdint>

#include "application_state.hpp"
#include "menu_state.hpp"

namespace th04::portable::selection {

enum class Screen : std::uint8_t {
    playchar,
    shot_type,
};

enum class ResultKind : std::uint8_t {
    none,
    canceled,
    chosen,
};

struct Result {
    ResultKind kind = ResultKind::none;
    application::Playchar playchar = application::Playchar::reimu;
    application::ShotType shot_type = application::ShotType::a;
};

using Availability = std::array<std::array<bool, 2>, 2>;

// Portable state for OP's two-step character and shot-type menu. The mask is
// explicit because Extra unlocks each character/shot combination separately.
class State {
public:
    explicit State(Availability available = all_available());

    static constexpr Availability all_available() {
        return {{{true, true}, {true, true}}};
    }

    Screen screen() const { return screen_; }
    application::Playchar playchar() const { return playchar_; }
    application::ShotType shot_type() const { return shot_type_; }
    bool available(
        application::Playchar playchar, application::ShotType shot_type
    ) const;

    Result handle(menu::Input input);

private:
    bool playchar_available(application::Playchar playchar) const;

    Availability available_{};
    Screen screen_ = Screen::playchar;
    application::Playchar playchar_ = application::Playchar::reimu;
    application::ShotType shot_type_ = application::ShotType::a;
};

} // namespace th04::portable::selection
