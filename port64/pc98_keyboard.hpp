#pragma once
#include <array>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>

namespace th04::portable::pc98_keyboard {
// These owners reproduce the locally observed DOSBox-X keyboard path. They do
// not establish real keyboard firmware behavior or choose the native game clock.
// The caller supplies timer ticks, transport time and CPU data reads separately.
struct Key {
    std::uint16_t physical;
    std::uint8_t make;
};

class Typematic {
public:
    template<class Send> void key(Key value, bool pressed, Send&& send) {
        if(value.make & 0x80)throw std::invalid_argument("make code contains break bit");
        const bool same=key_ && key_->physical==value.physical;
        if(same && key_->make!=value.make)
            throw std::invalid_argument("physical key changed scan mapping");
        if(pressed) {
            if(same)send(std::uint8_t(value.make|0x80));
            wait_=same ? rate_ticks : pause_ticks;
            key_=value;
        } else if(same) {
            key_.reset();wait_=0;
        }
        send(std::uint8_t(value.make|(pressed ? 0 : 0x80)));
    }
    template<class Send> void tick(Send&& send, bool enabled=true) {
        // reset/active/scanning and a pending input slot belong to the caller.
        if(enabled && wait_ && !--wait_)key(*key_,true,send);
    }
    std::optional<Key> repeating_key() const { return key_; }
    unsigned wait_ticks() const { return wait_; }
    static constexpr unsigned pause_ticks=500,rate_ticks=33;
private:
    std::optional<Key> key_;
    unsigned wait_=0;
};

// Exact common units for the measured 55/96 ms serial character and the
// recorded 1/36000 ms CPU observations. This is a representation, not a claim
// that a host frame or wall-clock instant has a particular guest PIC phase.
using Time=std::uint64_t;
constexpr Time quanta_per_ms=576000;
constexpr Time character_time=330000;

// A receive-ready request survives a masked CPU. IF is only a necessary
// condition: the caller still owns PIC masks, priority, in-service state and
// the actual CPU dispatch event. Accepting an IRQ does not read UART data or
// update BIOS memory, and enabling interrupts does not accept it automatically.
class InterruptRequest {
public:
    void request() {pending_=true;}
    bool pending() const {return pending_;}
    bool eligible(bool interrupts_enabled) const {
        return pending_ && interrupts_enabled;
    }
    void accept(bool interrupts_enabled) {
        if(!eligible(interrupts_enabled))
            throw std::logic_error("CPU accepted an ineligible keyboard interrupt");
        pending_=false;
    }
private:
    bool pending_=false;
};

class Receiver {
public:
    enum class Completion {ready,overrun};
    bool enqueue(std::uint8_t code,Time now) {
        check_time(now);
        const auto next=std::uint8_t((in_+1)%buffer_.size());
        const bool accepted=next!=out_;
        if(accepted) {buffer_[in_]=code;in_=next;}
        if(!busy_)schedule(now);
        return accepted;
    }
    Completion complete(Time callback_time) {
        if(callback_time<last_time_)
            throw std::logic_error("transport callback clock moved backward");
        if(!due_ || callback_time<*due_)
            throw std::logic_error("receive callback precedes its scheduled event");
        const auto scheduled=*due_;
        last_time_=callback_time;due_.reset();
        if(ready_) {busy_=false;return Completion::overrun;}
        if(in_==out_)throw std::logic_error("scheduled receive has no queued byte");
        data_=buffer_[out_];out_=std::uint8_t((out_+1)%buffer_.size());ready_=true;
        // The pinned PIC schedules a chained event from its service index,
        // even when the CPU reached the callback after the nominal deadline.
        if(in_!=out_)schedule(scheduled);
        else busy_=false;
        return Completion::ready;
    }
    std::uint8_t read_data(Time now) {
        check_time(now);ready_=false;
        if(in_!=out_ && !busy_)schedule(now);
        return data_;
    }
    void reset() {
        in_=out_=0;busy_=ready_=false;due_.reset();
        // A UART reset in the pinned source leaves the last data byte intact.
    }
    std::optional<Time> next_event() const {return due_;}
    bool busy() const {return busy_;}
    bool ready() const {return ready_;}
    std::uint8_t data() const {return data_;}
    unsigned queued() const {return unsigned((in_+buffer_.size()-out_)%buffer_.size());}
    std::uint8_t input_index() const {return in_;}
    std::uint8_t output_index() const {return out_;}
private:
    void check_time(Time now) {
        if(now<last_time_)throw std::logic_error("transport clock moved backward");
        if(due_ && *due_<now)
            throw std::logic_error("process the pending receive event first");
        last_time_=now;
    }
    void schedule(Time anchor) {
        if(anchor>std::numeric_limits<Time>::max()-character_time)
            throw std::overflow_error("transport deadline overflow");
        due_=anchor+character_time;busy_=true;
    }
    std::array<std::uint8_t,32> buffer_{};
    std::uint8_t in_=0,out_=0,data_=0xff;
    bool busy_=false,ready_=false;
    std::optional<Time> due_;
    Time last_time_=0;
};

// Nonmodifier scan bytes update the ten-byte BIOS matrix only when the CPU
// admits the receive byte. Modifier processing and interrupt policy are separate.
inline bool update_matrix(std::array<std::uint8_t,10>& matrix,std::uint8_t code) {
    const auto make=unsigned(code&0x7f);
    if(make>=matrix.size()*8)return false;
    auto& byte=matrix[make/8];const auto bit=std::uint8_t(1u<<(make%8));
    if(code&0x80)byte=std::uint8_t(byte&~bit);
    else byte=std::uint8_t(byte|bit);
    return true;
}

// A persistent peripheral and BIOS owner. External timer callbacks, receive
// callbacks, CPU acceptance and data reads remain distinct operations. Neither
// IF restoration nor elapsed time implicitly performs an interrupt service.
class Device {
public:
    void key(Key value,bool pressed,Time now) {
        check_time(now);keyboard_.key(value,pressed,[&](std::uint8_t byte){receiver_.enqueue(byte,now);});
    }
    void tick(Time now,bool enabled=true) {
        check_time(now);keyboard_.tick([&](std::uint8_t byte){receiver_.enqueue(byte,now);},enabled);
    }
    Receiver::Completion receive(Time now) {
        check_time(now);const auto result=receiver_.complete(now);
        if(result==Receiver::Completion::ready)irq_.request();
        return result;
    }
    void accept(Time now,bool interrupts_enabled) {
        check_time(now);
        if(admitted_)throw std::logic_error("keyboard ISR already owns an unread byte");
        irq_.accept(interrupts_enabled);admitted_=true;
    }
    std::uint8_t read_bios(Time now) {
        check_time(now);
        if(!admitted_ || !receiver_.ready())throw std::logic_error("BIOS read without CPU acceptance");
        const auto byte=receiver_.read_data(now);admitted_=false;
        if((byte&0x7f)==0x70)shift_=(byte&0x80)==0;
        else if(!update_matrix(matrix_,byte))throw std::logic_error("unsupported BIOS modifier scan");
        return byte;
    }
    const Typematic& keyboard() const {return keyboard_;}
    const Receiver& receiver() const {return receiver_;}
    const InterruptRequest& irq() const {return irq_;}
    bool admitted() const {return admitted_;}
    const std::array<std::uint8_t,10>& matrix() const {return matrix_;}
    bool shift() const {return shift_;}
private:
    void check_time(Time now) {
        if(now<last_time_)throw std::logic_error("keyboard device clock moved backward");
        last_time_=now;
    }
    Typematic keyboard_;Receiver receiver_;InterruptRequest irq_;
    std::array<std::uint8_t,10> matrix_{};
    Time last_time_=0;bool admitted_=false,shift_=false;
};
} // namespace th04::portable::pc98_keyboard
