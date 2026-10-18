#pragma once
#include "pc98_input.hpp"
#include <memory>
#include <stdexcept>

namespace th04::portable::host_joystick {
// Host policy, not PC-98 electrical timing: first two axes/first hat, first
// button Shot, second button Bomb, and a half-range analog dead zone.
constexpr int axis_threshold=16384;
constexpr std::uint8_t axis_actions(int x,int y) {
    return std::uint8_t((y<=-axis_threshold?1:0)|(y>=axis_threshold?2:0)|
        (x<=-axis_threshold?4:0)|(x>=axis_threshold?8:0));
}
struct Sample {std::int64_t identity=-1;std::uint8_t pins=0xff;};
class Device {
public:
    virtual ~Device()=default;
    virtual Sample read()=0;
};
std::unique_ptr<Device> platform_device();

// Keep host levels, UI edges and the game's Reset/Sense latch separate.
// A newly connected controller, or a focus regain, must first be neutral.
class Joystick {
public:
    explicit Joystick(std::unique_ptr<Device> device):device_(std::move(device)) {
        if(!device_)throw std::invalid_argument("missing host joystick device");
    }
    void update(bool focused) {
        held_=read_actions(focused);edges_=std::uint8_t(held_&~previous_);previous_=held_;
    }
    std::uint8_t edges() const {return edges_;}
    std::uint16_t host_actions() const {
        return std::uint16_t((held_&0x0f)|(held_&0x20)|((held_&0x10)?0x800:0));
    }
    pc98_input::ByteSource source(pc98_input::ByteSource keyboard,std::function<bool()> focused) {
        if(!keyboard || keyboard.joystick_enabled || keyboard.joystick_pins || !focused)
            throw std::invalid_argument("invalid host joystick byte composition");
        auto focus=std::make_shared<std::function<bool()>>(std::move(focused));
        keyboard.joystick_enabled=[this,focus] {
            if(!(*focus)()){release();return false;}
            return identity_>=0;
        };
        keyboard.joystick_pins=[this,focus] {
            held_=read_actions((*focus)());return std::uint8_t(0xff^held_);
        };
        return keyboard;
    }
private:
    void release(){identity_=-1;armed_=false;held_=edges_=previous_=0;}
    std::uint8_t read_actions(bool focused) {
        if(!focused){release();return 0;}
        const auto sample=device_->read();
        if(sample.identity<0){release();return 0;}
        if(identity_!=sample.identity){release();identity_=sample.identity;}
        const auto actions=std::uint8_t((~sample.pins)&0x3f);
        if(!actions)armed_=true;
        return armed_?actions:0;
    }
    std::unique_ptr<Device> device_;
    std::int64_t identity_=-1;
    bool armed_=false;
    std::uint8_t held_=0,edges_=0,previous_=0;
};
} // namespace th04::portable::host_joystick
