#pragma once
#include "sound_control.hpp"
#include <array>
#include <cstdint>
#include <functional>
#include <optional>
#include <vector>

namespace th04::portable::sound {
using Bytes=std::vector<std::uint8_t>;
struct BeepPort {std::uint16_t port;std::uint8_t value;};
using BeepSink=std::function<void(BeepPort)>;
struct Effect {std::array<std::uint16_t,257> words{};std::uint16_t cursor=0;};
struct BeepState {
    bool clock8=false;
    std::uint16_t enabled=1,count=0,selected=0,active=0,phase=0,tempo=120,timer_divisor=2458;
    std::array<Effect,16> effects{};
    bool gate=false;
    std::uint16_t divisor=1229;
    std::uint64_t reloads=0;
};
class Beeper {
public:
    explicit Beeper(bool clock8=false,BeepSink sink={});
    explicit Beeper(BeepState state,BeepSink sink={}):state_(std::move(state)),sink_(std::move(sink)){}
    const BeepState& state() const {return state_;}
    std::uint32_t clock_hz() const {return state_.clock8 ? 1996800u : 2457600u;}
    int read(const std::optional<Bytes>& bytes);
    int play(std::int16_t effect);
    int tempo(std::int16_t value);
    void enable(std::uint16_t value){state_.enabled=value;}
    void tick();
    using Reader=std::function<std::optional<Bytes>(const std::string&)>;
    // Unhandled requests still belong to the future FM/PMD owner.
    std::optional<int> consume(const Request&,const Reader&);
private:
    BeepState state_;BeepSink sink_;
    void out(std::uint16_t,std::uint8_t) const;
    void silence();
    void frequency(std::uint16_t);
};
// Digital PIT mode3 sampling at explicit host sample boundaries. Gain and
// sample phase are host policy, separate from analogue/audio-device claims.
class BeepPcm {
public:
    explicit BeepPcm(Beeper&,std::uint32_t rate=48000);
    std::vector<std::int16_t> render(std::size_t samples);
    std::uint64_t samples() const {return samples_;}
private:
    Beeper* beeper_;std::uint32_t rate_;
    std::uint64_t samples_=0,time_=0,next_irq_=0,reload_time_=0,generation_=0;
    void observe(std::uint64_t time);
};
}
