#pragma once
#include "pmd_timer_player.hpp"
#include <array>

namespace th04::portable::pmd {
// Ideal OPN/OPNA master-cycle timeline at the installed default prescaler.
// The first FM clock is at quantum(), not at epoch zero. Coincident timer
// expirations latch together before a zero-latency CPU IRQ callback.
// This is an explicit adapter convention, not a measured PC-98 bus phase.
class OpnTimers {
public:
    explicit OpnTimers(Board board);
    void write(std::uint8_t address,std::uint8_t value);
    void advance(std::uint64_t cycles,const std::function<void(std::uint8_t)>& irq);
    std::uint64_t cycles() const {return cycles_;}
    std::uint64_t deadline(unsigned timer) const {return deadlines_.at(timer);}
    unsigned quantum() const {return quantum_;}
    std::uint8_t status() const {return status_;}
private:
    unsigned quantum_;bool opna_;
    std::uint64_t cycles_=0;
    std::array<std::uint64_t,2> deadlines_{}; // zero means stopped
    std::array<std::uint8_t,4> registers_{};
    std::uint8_t status_=0,irq_mask_=3;
    std::uint64_t period(unsigned timer,bool initial) const;
};

// Resident timers outlive individual song stop/start operations. Frequency
// must be supplied by the host scenario; no frame-to-measure approximation.
// PCM synthesis and an audio backend remain separate owners.
class ClockedPlayer {
public:
    ClockedPlayer(Board board,std::uint32_t master_hz,FmSink sink={},SsgSink ssg={});
    ClockedPlayer(const ClockedPlayer&)=delete;ClockedPlayer& operator=(const ClockedPlayer&)=delete;
    void load_music(const Bytes& b) {player_.load_music(b);}
    void load_effects(const Bytes& b) {player_.load_effects(b);}
    void start_music() {player_.start_music();}
    void stop_music() {player_.stop_music();}
    void fade(std::int8_t v) {player_.fade(v);}
    void start_effect(unsigned v) {player_.start_effect(v);}
    void stop_effect() {player_.stop_effect();}
    void start_ssg_effect(unsigned v) {player_.start_ssg_effect(v);}
    void stop_ssg_effect() {player_.stop_ssg_effect();}
    void mirror(std::uint8_t bank,std::uint8_t a,std::uint8_t v) {player_.mirror(bank,a,v);}
    void advance_cycles(std::uint64_t cycles);
    void advance_ns(std::uint64_t nanoseconds);
    void on_interrupt(std::function<void(std::uint64_t,std::uint8_t)> action) {interrupt_=std::move(action);}
    const FmPlayer& player() const {return player_.player();}
    const OpnTimers& timers() const {return timers_;}
    std::uint64_t interrupts() const {return interrupts_;}
    std::uint32_t fraction() const {return fraction_;} // billionths of a master cycle
private:
    OpnTimers timers_;std::uint32_t master_hz_,fraction_=0;
    TimerPlayer player_;std::uint64_t interrupts_=0;
    std::function<void(std::uint64_t,std::uint8_t)> interrupt_;
};
}
