#include "selection_state.hpp"

#include <stdexcept>

namespace th04::portable::selection {
namespace {

constexpr std::size_t index(application::Playchar playchar) {
    return static_cast<std::size_t>(playchar);
}

constexpr std::size_t index(application::ShotType shot_type) {
    return static_cast<std::size_t>(shot_type);
}

application::Playchar other(application::Playchar playchar) {
    return (playchar == application::Playchar::reimu)
        ? application::Playchar::marisa
        : application::Playchar::reimu;
}

application::ShotType other(application::ShotType shot_type) {
    return (shot_type == application::ShotType::a)
        ? application::ShotType::b
        : application::ShotType::a;
}

} // namespace

State::State(Availability available) : available_(available) {
    if (!playchar_available(playchar_)) {
        playchar_ = application::Playchar::marisa;
    }
    if (!playchar_available(playchar_)) {
        throw std::invalid_argument("selection menu has no available combination");
    }
}

bool State::available(
    application::Playchar playchar, application::ShotType shot_type
) const {
    return available_[index(playchar)][index(shot_type)];
}

bool State::playchar_available(application::Playchar playchar) const {
    return available(playchar, application::ShotType::a) ||
        available(playchar, application::ShotType::b);
}

Result State::handle(menu::Input input) {
    if (screen_ == Screen::playchar) {
        if (input == menu::Input::left || input == menu::Input::right) {
            const auto candidate = other(playchar_);
            if (playchar_available(candidate)) {
                playchar_ = candidate;
            }
        } else if (input == menu::Input::confirm) {
            shot_type_ = available(playchar_, application::ShotType::a)
                ? application::ShotType::a
                : application::ShotType::b;
            screen_ = Screen::shot_type;
        } else if (input == menu::Input::cancel) {
            return {ResultKind::canceled, playchar_, shot_type_};
        }
        return {};
    }

    if (input == menu::Input::up || input == menu::Input::down) {
        const auto candidate = other(shot_type_);
        if (available(playchar_, candidate)) {
            shot_type_ = candidate;
        }
    } else if (input == menu::Input::confirm) {
        return {ResultKind::chosen, playchar_, shot_type_};
    } else if (input == menu::Input::cancel) {
        screen_ = Screen::playchar;
    }
    return {};
}

} // namespace th04::portable::selection
