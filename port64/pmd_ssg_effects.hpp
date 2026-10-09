#pragma once
#include <array>
#include <cstdint>
#include <functional>
#include <vector>
#include <utility>

namespace th04::portable::pmd {
// One semantic segment of a built-in PMD SSG effect. Tone/envelope periods
// are chip counts; duration and noise interval count Timer A interrupts.
struct EffectFrame {
    std::uint8_t ticks;
    std::uint16_t tone;
    std::uint8_t noise;
    bool tone_enabled,noise_enabled;
    std::uint8_t volume;
    std::uint16_t envelope;
    std::uint8_t shape;
    std::int16_t tone_step;
    std::int8_t noise_step;
    std::uint8_t noise_interval;
};
struct Effect {std::uint8_t priority;std::vector<EffectFrame> frames;};
struct SsgWrite {std::uint8_t address,value;};
using SsgSink=std::function<void(SsgWrite)>;
struct EffectState {
    int resource=-1;
    unsigned next_frame=0;
    std::uint16_t tone=0;
    std::int16_t tone_step=0;
    std::uint8_t ticks=0,noise=0,noise_interval=0,noise_counter=0;
    std::int8_t noise_step=0;
    std::uint8_t priority=0,effect=255;
};
class SsgEffects {
public:
    explicit SsgEffects(SsgSink sink={}):sink_(std::move(sink)){}
    bool start(unsigned effect);
    void stop();
    void timer_a();
    // The music/chip owner supplies its register mirror. Effects preserve
    // other channels' mixer bits; no port or audio device is opened here.
    void mirror(std::uint8_t address,std::uint8_t value);
    const std::array<std::uint8_t,14>& registers() const {return registers_;}
    const EffectState& state() const {return state_;}
    static const std::array<Effect,40>& bank();
private:
    SsgSink sink_;EffectState state_{};
    std::array<std::uint8_t,14> registers_{};
    void write(std::uint8_t address,std::uint8_t value);
    void frame();
};
}
