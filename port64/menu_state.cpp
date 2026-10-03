#include "menu_state.hpp"

namespace th04::portable::menu {
namespace {

template <typename Value>
void increment_wrapped(Value& value, Value first, Value last) {
    value = (value == last) ? first : Value(value + 1);
}

template <typename Value>
void decrement_wrapped(Value& value, Value first, Value last) {
    value = (value == first) ? last : Value(value - 1);
}

} // namespace

bool Options::operator==(const Options& other) const {
    return rank == other.rank && lives == other.lives &&
        bombs == other.bombs && bgm_mode == other.bgm_mode &&
        se_mode == other.se_mode && turbo == other.turbo;
}

State::State(bool extra_unlocked) : extra_unlocked_(extra_unlocked) {}

void State::move_vertical(int direction) {
    const int count = (screen_ == Screen::main)
        ? int(MainChoice::count)
        : int(OptionChoice::count);
    int next = (int(selection_) + direction + count) % count;
    if (
        screen_ == Screen::main && !extra_unlocked_ &&
        next == int(MainChoice::extra)
    ) {
        next += direction;
    }
    selection_ = std::uint8_t((next + count) % count);
}

void State::change_option(int direction) {
    switch (OptionChoice(selection_)) {
    case OptionChoice::rank:
        (direction > 0)
            ? increment_wrapped(options_.rank, std::uint8_t(0), std::uint8_t(3))
            : decrement_wrapped(options_.rank, std::uint8_t(0), std::uint8_t(3));
        break;
    case OptionChoice::lives:
        (direction > 0)
            ? increment_wrapped(options_.lives, std::uint8_t(1), std::uint8_t(6))
            : decrement_wrapped(options_.lives, std::uint8_t(1), std::uint8_t(6));
        break;
    case OptionChoice::bombs:
        (direction > 0)
            ? increment_wrapped(options_.bombs, std::uint8_t(0), std::uint8_t(2))
            : decrement_wrapped(options_.bombs, std::uint8_t(0), std::uint8_t(2));
        break;
    case OptionChoice::bgm:
        (direction > 0)
            ? increment_wrapped(options_.bgm_mode, std::uint8_t(0), std::uint8_t(2))
            : decrement_wrapped(options_.bgm_mode, std::uint8_t(0), std::uint8_t(2));
        break;
    case OptionChoice::sound_effects:
        // OP's visual order is OFF -> BEEP -> FM when moving right, and the
        // reverse when moving left. The stored values are OFF=0, FM=1, BEEP=2.
        if (direction > 0) {
            options_.se_mode = (options_.se_mode == 0)
                ? std::uint8_t(2)
                : std::uint8_t(options_.se_mode - 1);
        } else {
            increment_wrapped(
                options_.se_mode, std::uint8_t(0), std::uint8_t(2)
            );
        }
        break;
    case OptionChoice::turbo:
        options_.turbo = !options_.turbo;
        break;
    case OptionChoice::reset:
    case OptionChoice::quit:
    case OptionChoice::count:
        break;
    }
}

void State::return_to_main() {
    screen_ = Screen::main;
    selection_ = std::uint8_t(MainChoice::options);
}

Result State::handle(Input input) {
    if (input == Input::up || input == Input::down) {
        move_vertical(input == Input::up ? -1 : 1);
        return {};
    }

    if (screen_ == Screen::main) {
        if (input == Input::cancel) {
            return {ResultKind::quit, MainChoice::quit};
        }
        if (input != Input::confirm) {
            return {};
        }
        const MainChoice choice = MainChoice(selection_);
        if (choice == MainChoice::options) {
            screen_ = Screen::options;
            selection_ = std::uint8_t(OptionChoice::rank);
            return {};
        }
        if (choice == MainChoice::quit) {
            return {ResultKind::quit, choice};
        }
        return {ResultKind::choose_main, choice};
    }

    if (input == Input::cancel) {
        return_to_main();
        return {};
    }
    if (input == Input::left || input == Input::right) {
        change_option(input == Input::right ? 1 : -1);
        return {};
    }
    if (input != Input::confirm) {
        return {};
    }

    switch (OptionChoice(selection_)) {
    case OptionChoice::reset:
        options_ = Options{};
        break;
    case OptionChoice::quit:
        return_to_main();
        break;
    default:
        // OP treats OK/Shot on an adjustable row like a right press.
        change_option(1);
        break;
    }
    return {};
}

} // namespace th04::portable::menu
