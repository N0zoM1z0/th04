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

// Normal fixed-priority arbitration for one primary 8259. Requests survive
// masking; accepting a line leaves it in service until an explicit EOI.
// Cascade routing, special modes, CPU dispatch time and guest IF belong to
// their callers. The PC-98 keyboard uses primary line 1 (vector 09h).
class FixedPriorityPic {
public:
    struct State {std::uint8_t requests=0,mask=0xff,service=0;};
    FixedPriorityPic():state_{}{}
    explicit FixedPriorityPic(State state):state_(state){}
    const State& state() const {return state_;}
    void set_mask(std::uint8_t mask) {state_.mask=mask;}
    void request(unsigned line) {state_.requests|=bit(line);}
    bool pending(unsigned line) const {return (state_.requests&bit(line))!=0;}
    unsigned active() const {return first(state_.service);}
    std::optional<unsigned> eligible(bool interrupts_enabled) const {
        if(!interrupts_enabled)return {};
        const auto candidates=std::uint8_t(state_.requests&~state_.mask&~state_.service);
        const auto selected=first(candidates);
        if(selected<active())return selected;
        return {};
    }
    void accept(unsigned line,bool interrupts_enabled) {
        const auto selected=eligible(interrupts_enabled);
        if(!selected || *selected!=line)
            throw std::logic_error("CPU accepted an ineligible primary interrupt");
        state_.requests=std::uint8_t(state_.requests&~bit(line));state_.service|=bit(line);
    }
    void eoi(std::optional<unsigned> line={}) {
        const auto selected=line ? *line : active();
        if(line || selected<8)state_.service=std::uint8_t(state_.service&~bit(selected));
    }
    class Line {
    public:
        Line(const FixedPriorityPic& owner,unsigned line):owner_(owner),line_(line){}
        bool pending() const {return owner_.pending(line_);}
        bool eligible(bool interrupts_enabled) const {
            const auto next=owner_.eligible(interrupts_enabled);return next && *next==line_;
        }
    private:
        const FixedPriorityPic& owner_;unsigned line_;
    };
    Line line(unsigned value) const {bit(value);return {*this,value};}
private:
    State state_;
    static std::uint8_t bit(unsigned line) {
        if(line>=8)throw std::out_of_range("invalid primary interrupt line");
        return std::uint8_t(1u<<line);
    }
    static unsigned first(std::uint8_t bits) {
        for(unsigned i=0;i<8;++i)if(bits&(1u<<i))return i;
        return 8;
    }
};

// CPU availability and the PIC's delayed check are separate gates. These
// flags describe one dispatch opportunity, not an instruction-level CPU.
struct CpuAvailability {
    bool interrupts_enabled=true,trap=false,nmi_active=false,nmi_pending=false;
};
class PicDispatch {
public:
    explicit PicDispatch(Time delay=0):delay_(delay){}
    void signal(Time now) {
        if(pending_)return;
        if(now>std::numeric_limits<Time>::max()-delay_)
            throw std::overflow_error("PIC check deadline overflow");
        pending_=now+delay_;
    }
    void event(Time now) {
        if(!pending_ || now<*pending_)throw std::logic_error("unexpected PIC check callback");
        pending_.reset();check_=true;
    }
    std::optional<unsigned> select(const FixedPriorityPic& pic,CpuAvailability cpu) {
        if(!cpu.interrupts_enabled || !check_ || cpu.trap || cpu.nmi_active || cpu.nmi_pending)return {};
        check_=false;return pic.eligible(true);
    }
    void accepted(Time now) {check_=false;signal(now);}
    bool check() const {return check_;}
    std::optional<Time> next_event() const {return pending_;}
private:
    Time delay_;std::optional<Time> pending_;bool check_=false;
};

// A receive-ready request survives a masked CPU. IF is only a necessary
// condition: the caller still owns PIC masks, priority, in-service state and
// the actual CPU dispatch event. Accepting an IRQ does not read UART data or
// update BIOS memory, and enabling interrupts does not accept it automatically.
// This isolated latch remains for historical fixtures; Device uses the PIC.
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

// A persistent peripheral, primary PIC and BIOS owner. External timer/RX
// callbacks, CPU acceptance, data reads and EOI remain distinct operations.
// Neither IF restoration nor elapsed time implicitly performs service; reading
// BIOS data does not end the PIC's in-service state.
class Device {
public:
    explicit Device(Time check_delay=0):dispatch_(check_delay){}
    void key(Key value,bool pressed,Time now) {
        check_time(now);keyboard_.key(value,pressed,[&](std::uint8_t byte){receiver_.enqueue(byte,now);});
    }
    void tick(Time now,bool enabled=true) {
        check_time(now);keyboard_.tick([&](std::uint8_t byte){receiver_.enqueue(byte,now);},enabled);
    }
    Receiver::Completion receive(Time now) {
        // The UART callback raises IRQ1 from its queued service index. Keep
        // that deadline separate from the CPU's possibly later observation.
        check_time(now);const auto scheduled=receiver_.next_event();
        const auto result=receiver_.complete(now);
        if(result==Receiver::Completion::ready)request_irq_at(*scheduled,1);
        return result;
    }
    void accept(Time now,bool interrupts_enabled) {
        accept_irq(now,1,interrupts_enabled);
    }
    void set_irq_mask(Time now,std::uint8_t mask) {
        check_time(now);const auto before=pic_.state();pic_.set_mask(mask);
        if((before.mask^mask)&before.requests&~before.service)
            if(pic_.eligible(true))dispatch_.signal(now);
    }
    void request_irq(Time now,unsigned line) {check_time(now);request_irq_at(now,line);}
    void dispatch_event(Time now) {check_time(now);dispatch_.event(now);}
    std::optional<unsigned> dispatch_irq(Time now,CpuAvailability cpu={}) {
        check_time(now);const auto selected=dispatch_.select(pic_,cpu);
        if(selected)accept_irq(now,*selected,cpu.interrupts_enabled);
        return selected;
    }
    void accept_irq(Time now,unsigned line,bool interrupts_enabled) {
        check_time(now);
        if(line==1 && admitted_)throw std::logic_error("keyboard ISR already owns an unread byte");
        pic_.accept(line,interrupts_enabled);if(line==1)admitted_=true;
        dispatch_.accepted(now);
    }
    void end_irq(Time now,std::optional<unsigned> line={}) {
        check_time(now);const bool command=line || pic_.active()<8;pic_.eoi(line);
        if(command && pic_.eligible(true))dispatch_.signal(now);
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
    FixedPriorityPic::Line irq() const {return pic_.line(1);}
    const FixedPriorityPic& pic() const {return pic_;}
    const PicDispatch& dispatcher() const {return dispatch_;}
    bool admitted() const {return admitted_;}
    const std::array<std::uint8_t,10>& matrix() const {return matrix_;}
    bool shift() const {return shift_;}
private:
    void request_irq_at(Time anchor,unsigned line) {
        const bool pending=pic_.pending(line);pic_.request(line);
        const auto state=pic_.state();const auto bit=std::uint8_t(1u<<line);
        if(!pending && !(state.mask&bit) && !(state.service&bit) && line<pic_.active())
            dispatch_.signal(anchor);
    }
    void check_time(Time now) {
        if(now<last_time_)throw std::logic_error("keyboard device clock moved backward");
        last_time_=now;
    }
    Typematic keyboard_;Receiver receiver_;
    // Portable keyboard-only mask, not the original boot PIC configuration.
    FixedPriorityPic pic_{FixedPriorityPic::State{0,0xfd,0}};
    PicDispatch dispatch_;
    std::array<std::uint8_t,10> matrix_{};
    Time last_time_=0;bool admitted_=false,shift_=false;
};
} // namespace th04::portable::pc98_keyboard
