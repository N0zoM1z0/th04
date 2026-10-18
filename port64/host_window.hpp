#pragma once
#include <cstdint>
#include "pc98_input.hpp"
#include "pc98_keyboard.hpp"
#include <fstream>
#include <string>

namespace th04::portable::host_window {
// Recorded 640x400/24 kHz GDC mode: 106 character clocks * 440 lines,
// with a 21.0526 MHz oscillator divided by 8. Round to the nearest ns.
// This calibrates cadence; the original boot/process epoch is separate.
constexpr std::int64_t period_ns=17723227;
constexpr unsigned catchup_limit=4;
std::int64_t now_ns();

// Portable host admission policy, independent of simulation and sound clocks.
class Schedule {
public:
    explicit Schedule(std::int64_t now):next_(now+period_ns){}
    void wake(){steps_=0;}
    bool due(std::int64_t now)const{return steps_<catchup_limit && now>=next_;}
    void completed(unsigned next_slowdown);
    std::int64_t resync(std::int64_t now,unsigned next_slowdown);
    std::int64_t next()const{return next_;}
    std::uint64_t total()const{return total_;}
private:
    std::int64_t next_;unsigned steps_=0;std::uint64_t total_=0;
};
struct Keys {bool up=false,down=false,left=false,right=false,shot=false,
    enter=false,bomb=false,escape=false,quit=false,shift=false;
    bool up_left=false,up_right=false,down_left=false,down_right=false,space=false;
    bool keypad_up=false,keypad_down=false,keypad_left=false,keypad_right=false,
        keypad_enter=false,right_shift=false;};
// Physical identities stay distinct even when two keys emit the same scan.
enum class HostKey : unsigned {up,down,left,right,shot,enter,bomb,escape,quit,shift,
    up_left,up_right,down_left,down_right,space,keypad_up,keypad_down,keypad_left,
    keypad_right,keypad_enter,right_shift,count};
struct Input {std::uint16_t held=0;bool shift=false;};
Input input(const Keys&,bool focused);
pc98_input::Sample bios_input(const Keys&,bool focused);

struct KeySample {Keys keys;bool focused;std::int64_t time_ns;};
// Host elapsed time drives a persistent keyboard across process generations.
// The pinned original observer measures a configured 406 ns PIC check delay.
// Round that event deadline upward to the first representable peripheral
// quantum. CPU service after the check remains the explicit available_cpu
// policy; no original instruction cost or boot epoch is implied.
constexpr pc98_keyboard::Time pic_check_delay=(406*72+124)/125;
class Keyboard {
public:
    using Dispatch=std::function<void(pc98_keyboard::Device&,pc98_keyboard::Time)>;
    using KeySource=std::function<KeySample()>;
    Keyboard(std::int64_t epoch,Dispatch dispatch);
    static void available_cpu(pc98_keyboard::Device&,pc98_keyboard::Time);
    void key(HostKey,bool down,std::int64_t now);
    void focus(bool focused,std::int64_t now);
    Keys keys() const;
    void observe(const KeySample&);
    void advance(std::int64_t now);
    pc98_input::ByteSource source(KeySource,std::function<void(pc98_input::Operation)> begin={});
    pc98_input::ByteSource elapsed_source(std::function<std::int64_t()> clock,
        std::function<void(pc98_input::Operation)> begin={});
    const pc98_keyboard::Device& device() const {return device_;}
private:
    pc98_keyboard::Device device_{pic_check_delay};Dispatch dispatch_;
    std::int64_t last_ns_;pc98_keyboard::Time time_=0,next_tick_=pc98_keyboard::quanta_per_ms;
    unsigned remainder_=0;
    std::array<bool,unsigned(HostKey::count)> held_{};
    bool focused_=true;
    void set_key(unsigned,bool);
};

struct Snapshot {
    const char* scene="unknown";
    unsigned program=0,generation=0,frame=0,stage=0,rank=0,character=0,shot_type=0;
    int x=0,y=0;
    unsigned bullets=0,shots=0,lives=0,bombs=0,misses=0,invincibility=0;
    std::uint64_t audio_frames=0,audio_opens=0;bool audio_failed=false;
    unsigned score_units=0,credits=0,power=0,bombing=0,respawn=0;
    unsigned slow_frames=0,run_frames=0,score_digits_units=0,score_delta=0;
    std::uint16_t advice_held=0;bool advice_shift=false;
};
// Optional read-only observer. It never supplies input or changes game state.
class Trace {
public:
    Trace(const std::string& directory,bool muted);
    explicit operator bool()const{return enabled_;}
    void refresh(std::uint64_t sequence,std::int64_t begin,std::int64_t end,
        std::int64_t deadline,Input,bool focused,unsigned before,unsigned after,const Snapshot&);
    void input_poll(std::uint64_t sequence,std::int64_t begin,std::int64_t end,
        const pc98_input::Observation&,bool focused,const Snapshot&);
    void present(std::uint64_t sequence,std::int64_t begin,std::int64_t end,bool updated);
    void resync(std::int64_t now,std::int64_t discarded,unsigned slowdown);
    void finish(const Snapshot&);
private:
    bool enabled_=false,finished_=false;std::int64_t epoch_=0;
    std::ofstream stream_,input_stream_;std::uint64_t refreshes_=0,presents_=0,resyncs_=0,input_polls_=0;
};
}
