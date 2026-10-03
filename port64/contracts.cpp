#include "bullet_geometry.hpp"
#include "menu_state.hpp"

#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>

namespace bullet = th04::portable::bullet;
namespace menu = th04::portable::menu;

namespace {

void require(bool condition, const char* message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

template <size_t Size>
void require_spread(
    std::uint8_t count, bullet::Angle step,
    const std::array<unsigned, Size>& expected
) {
    require(count == Size, "spread fixture count mismatch");
    for (std::uint16_t member = 0; member < count; ++member) {
        require(
            bullet::spread_member_angle(member, count, step) == expected[member],
            "spread angle mismatch"
        );
    }
}

} // namespace

int main() {
    static_assert(sizeof(void*) == 8, "portable build must be 64-bit");
    static_assert(sizeof(bullet::Angle) == 1, "bullet angle storage must be one byte");
    static_assert(sizeof(bullet::GroupCode) == 1, "spawn group storage must be one byte");
    static_assert(BG_RING == 0x26 && BG_RING_AIMED == 0x2c);
    static_assert(BG_SPREAD == 0x2d && BG_SPREAD_AIMED == 0x2e);

    require_spread<5>(5, 0x10, {0x00, 0xf0, 0x10, 0xe0, 0x20});
    require_spread<4>(4, 0x10, {0x08, 0xf8, 0x18, 0xe8});
    require_spread<5>(5, 0x90, {0x00, 0x70, 0x90, 0xe0, 0x20});

    const std::array<unsigned, 8> ring{
        0x00, 0x20, 0x40, 0x60, 0x80, 0xa0, 0xc0, 0xe0
    };
    for (std::uint16_t member = 0; member < ring.size(); ++member) {
        require(
            bullet::ring_member_angle(member, std::uint8_t(ring.size())) ==
                ring[member],
            "ring angle mismatch"
        );
    }
    require(
        bullet::apply_aim_and_rotation(0xf0, true, 0x20, 0x08) == 0x18,
        "aim/template rotation wrap mismatch"
    );
    require(
        bullet::apply_aim_and_rotation(0xf0, false, 0x20, 0x08) == 0xf8,
        "un-aimed template rotation mismatch"
    );

    require(bullet::directional_sprite_cel(0x00) == 0, "right-facing cel mismatch");
    require(bullet::directional_sprite_cel(0x04) == 0, "rounded cel mismatch");
    require(bullet::directional_sprite_cel(0x05) == 1, "next cel mismatch");
    require(bullet::directional_sprite_cel(0x7c) == 15, "last cel mismatch");
    require(bullet::directional_sprite_cel(0x80) == 0, "half-turn reuse mismatch");

    bool rejected = false;
    try {
        (void)bullet::ring_member_angle(0, 0);
    } catch (const std::out_of_range&) {
        rejected = true;
    }
    require(rejected, "portable ring must reject count zero");

    menu::State locked_menu;
    locked_menu.handle(menu::Input::down);
    require(
        locked_menu.selection() == std::uint8_t(menu::MainChoice::scores),
        "locked Extra must be skipped moving down"
    );
    locked_menu.handle(menu::Input::up);
    require(
        locked_menu.selection() == std::uint8_t(menu::MainChoice::game),
        "locked Extra must be skipped moving up"
    );

    menu::State unlocked_menu(true);
    unlocked_menu.handle(menu::Input::down);
    require(
        unlocked_menu.selection() == std::uint8_t(menu::MainChoice::extra),
        "unlocked Extra must remain selectable"
    );

    menu::State option_menu;
    for (unsigned i = 0; i < 3; ++i) {
        option_menu.handle(menu::Input::down);
    }
    option_menu.handle(menu::Input::confirm);
    require(
        option_menu.screen() == menu::Screen::options &&
            option_menu.selection() == std::uint8_t(menu::OptionChoice::rank),
        "Option must enter at the Rank row"
    );
    option_menu.handle(menu::Input::left);
    require(option_menu.options().rank == 0, "rank left transition mismatch");
    option_menu.handle(menu::Input::left);
    require(option_menu.options().rank == 3, "rank wrap mismatch");
    option_menu.handle(menu::Input::down);
    option_menu.handle(menu::Input::left);
    option_menu.handle(menu::Input::left);
    option_menu.handle(menu::Input::left);
    require(option_menu.options().lives == 6, "lives wrap mismatch");
    option_menu.handle(menu::Input::down);
    option_menu.handle(menu::Input::right);
    require(option_menu.options().bombs == 0, "bombs wrap mismatch");
    option_menu.handle(menu::Input::down);
    option_menu.handle(menu::Input::right);
    require(option_menu.options().bgm_mode == 0, "BGM wrap mismatch");
    option_menu.handle(menu::Input::down);
    option_menu.handle(menu::Input::right);
    require(option_menu.options().se_mode == 0, "SE right order mismatch");
    option_menu.handle(menu::Input::right);
    require(option_menu.options().se_mode == 2, "SE right BEEP transition mismatch");
    option_menu.handle(menu::Input::left);
    require(option_menu.options().se_mode == 0, "SE left order mismatch");
    option_menu.handle(menu::Input::down);
    option_menu.handle(menu::Input::confirm);
    require(!option_menu.options().turbo, "confirm must toggle Turbo");
    option_menu.handle(menu::Input::down);
    option_menu.handle(menu::Input::confirm);
    require(option_menu.options() == menu::Options{}, "Reset defaults mismatch");
    option_menu.handle(menu::Input::down);
    option_menu.handle(menu::Input::confirm);
    require(
        option_menu.screen() == menu::Screen::main &&
            option_menu.selection() == std::uint8_t(menu::MainChoice::options),
        "Option Quit must return to the Option command"
    );
    const auto quit = option_menu.handle(menu::Input::cancel);
    require(quit.kind == menu::ResultKind::quit, "main Cancel must quit");

    std::cout << "TH04 portable contracts: PASS pointer_bits="
              << sizeof(void*) * 8 << " angle_bits=" << sizeof(bullet::Angle) * 8
              << " menu_state=OP" << std::endl;
    return 0;
}
