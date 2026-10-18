#pragma once
#include <array>
#include <cstdint>
#include <functional>

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
// A value read from the game latch, after sampling. This is a different domain
// from the frontend's host key encoding and from a fresh physical sample.
struct Snapshot {
    std::uint16_t actions=0;
    bool shift=false;
};
enum class Operation {reset,sense};
using SampleSource=std::function<Sample(Operation)>;
// A live sampler consumes these bytes independently, in original instruction
// order. begin runs after a reset has cleared the game latch. Whole-sample
// movies retain their separate SampleSource entry and observation contract.
struct ByteSource {
    std::function<void(Operation)> begin;
    std::function<std::uint8_t(unsigned)> key;
    std::function<bool()> shift;
    explicit operator bool() const {return bool(key) && bool(shift);}
};
using Poll=std::function<Snapshot(Operation)>;
// Observation values never supply samples or modify the game latch.
struct Observation {Operation operation;Sample physical;Snapshot before,after;};
using Observer=std::function<void(const Observation&)>;
class Latch {
public:
    Sample poll(Operation operation,const ByteSource& source) {
        if(operation==Operation::reset)actions_=0;
        if(source.begin)source.begin(operation);
        Sample sample;
        for(const auto group:std::array<unsigned,8>{{7,9,8,5,2,0,3,6}}) {
            const auto value=source.key(group);sample.keys[group]=value;
            BiosKeys single{};single[group]=value;actions_|=keyboard_actions(single);
        }
        sample.shift=source.shift();shift_=sample.shift;
        return sample;
    }
    void reset_sense(const Sample& sample) { actions_=0;sense(sample); }
    void sense(const Sample& sample) {
        actions_|=keyboard_actions(sample.keys);
        if(sample.joystick_enabled)actions_|=std::uint16_t((~sample.joystick_pins)&0x3f);
        shift_=sample.shift;
    }
    std::uint16_t actions() const { return actions_; }
    bool shift() const { return shift_; }
    Snapshot snapshot() const { return {actions_,shift_}; }
    // The real DEMO callback writes the input globals from its replay banks.
    // Keyboard polling never uses this explicit game-write entry.
    void replay_input(Snapshot value) { actions_=value.actions;shift_=value.shift; }
private:
    std::uint16_t actions_=0;
    bool shift_=false;
};
} // namespace th04::portable::pc98_input
