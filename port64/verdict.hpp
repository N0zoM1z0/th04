#pragma once
#include "application_state.hpp"
#include "cutscene.hpp"
#include "maine_animation.hpp"
#include <vector>

namespace th04::portable::verdict {
using Bytes=cutscene::Bytes;
using Kind=maine::RequestKind;
using Event=maine::Request;
const char* kind_name(Kind);
using Sink=maine::RequestSink;

struct Input {
    application::ResidentState resident;
    std::uint8_t misses=0,bombs_used=0;
    // Fresh MAINE BSS starts skill at zero. These explicit inputs also allow
    // an independent original-CPU control to exercise arithmetic wrap and
    // the initialized percentage subtraction byte at DATA0E53:071A.
    std::uint32_t initial_skill=0;
    bool subtract_percentages=false;
};
struct Result {
    std::uint32_t skill=0,cap=0,random_state=0;
    std::uint16_t std_frames=0;
    std::uint8_t rank=0;
    int commentary_line=-1;
    bool score_visible=false;
    bool random_drawn=false;
};

// Full recovered MAINE0A05:1737..20F8 calculation and consumer requests.
// This plan owns no borrowed resident pointer or DOS file handle. The caller
// publishes std_frames and the continued MAINE RNG at the calculation phase,
// then a graphics/timing owner consumes these requests in their original order.
class Plan {
public:
    Plan(const Input&,const Bytes& commentary);
    const Result& result() const { return result_; }
    const std::vector<Event>& requests() const { return events_; }
private:
    void emit(Kind,int=0,int=0,int=0,int=0,int=0,std::string={});
    void text(int,int,const std::string&,int color=14);
    void gaiji(int,int,const std::string&);
    void number(int,int,std::uint16_t,bool fixed_two=false);
    void fraction(int,int,std::uint32_t);
    void percentage(int,int,std::uint16_t,std::uint16_t,bool);
    Result result_;
    std::vector<Event> events_;
};

using Status=maine::AnimationStatus;
// Palette and key waits remain independent of repaint and wall-clock time.
// wait(0) releases held keys first, then waits indefinitely for a fresh press.
class Script:public maine::Animation {
public:
    explicit Script(Plan plan):Animation(plan.requests()),result_(plan.result()) {}
    const Result& result() const { return result_; }
private:
    Result result_;
};
} // namespace th04::portable::verdict
