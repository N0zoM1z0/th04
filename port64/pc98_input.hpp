#pragma once
#include <array>
#include <cstdint>

namespace th04::portable::pc98_input {
// Original MAIN 130E:06BC resets, then falls through to 06C4; sense ORs
// new samples into the existing game latch. Sampling time belongs to the
// caller; this component owns neither physical delivery nor the game clock.
// The ten bytes beginning at PC-98 BIOS 0000:052A. Keypad diagonals are
// distinct high-byte actions; they are not two arrow actions combined.
using BiosKeys = std::array<std::uint8_t,10>;
constexpr std::uint16_t keyboard_actions(const BiosKeys& keys) {
    std::uint16_t result=0;
    const auto add=[&](unsigned group,unsigned mask,std::uint16_t action) {
        if(keys[group]&mask)result|=action;
    };
    add(7,0x04,0x0001);add(7,0x20,0x0002);
    add(7,0x08,0x0004);add(7,0x10,0x0008);
    add(9,0x01,0x0008);add(9,0x04,0x0400);
    add(9,0x08,0x0002);add(9,0x10,0x0800);
    add(8,0x40,0x0004);add(8,0x04,0x0100);
    add(8,0x08,0x0001);add(8,0x10,0x0200);
    add(5,0x02,0x0020);add(5,0x04,0x0010);
    add(2,0x01,0x4000);add(0,0x01,0x1000);
    add(3,0x10,0x2000);add(6,0x10,0x0020);
    return result;
}
struct Sample {
    BiosKeys keys{};
    bool shift=false;
    bool joystick_enabled=false;
    // Active-low OPNA input pins. The original wrapper inverts AL and masks AX.
    std::uint8_t joystick_pins=0xff;
};
class Latch {
public:
    void reset_sense(const Sample& sample) { actions_=0;sense(sample); }
    void sense(const Sample& sample) {
        actions_|=keyboard_actions(sample.keys);
        if(sample.joystick_enabled)actions_|=std::uint16_t((~sample.joystick_pins)&0x3f);
        shift_=sample.shift;
    }
    std::uint16_t actions() const { return actions_; }
    bool shift() const { return shift_; }
private:
    std::uint16_t actions_=0;
    bool shift_=false;
};
} // namespace th04::portable::pc98_input
