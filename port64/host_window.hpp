#pragma once
#include <cstdint>
#include <fstream>
#include <string>

namespace th04::portable::host_window {
constexpr std::int64_t period_ns=17730496;
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
    enter=false,bomb=false,escape=false,quit=false,shift=false;};
struct Input {std::uint16_t held=0;bool shift=false;};
Input input(const Keys&,bool focused);

struct Snapshot {
    const char* scene="unknown";
    unsigned program=0,generation=0,frame=0,stage=0,rank=0,character=0,shot_type=0;
    int x=0,y=0;
    unsigned bullets=0,shots=0,lives=0,bombs=0,misses=0,invincibility=0;
    std::uint64_t audio_frames=0,audio_opens=0;bool audio_failed=false;
    unsigned score_units=0,credits=0,power=0,bombing=0,respawn=0;
    unsigned slow_frames=0,run_frames=0,score_digits_units=0,score_delta=0;
};
// Optional read-only observer. It never supplies input or changes game state.
class Trace {
public:
    Trace(const std::string& directory,bool muted);
    explicit operator bool()const{return enabled_;}
    void refresh(std::uint64_t sequence,std::int64_t begin,std::int64_t end,
        std::int64_t deadline,Input,bool focused,unsigned before,unsigned after,const Snapshot&);
    void present(std::uint64_t sequence,std::int64_t begin,std::int64_t end,bool updated);
    void resync(std::int64_t now,std::int64_t discarded,unsigned slowdown);
    void finish(const Snapshot&);
private:
    bool enabled_=false,finished_=false;std::int64_t epoch_=0;
    std::ofstream stream_;std::uint64_t refreshes_=0,presents_=0,resyncs_=0;
};
}
