#pragma once
#include "maine_animation.hpp"
#include "pc98_input.hpp"
namespace th04::portable::pause {
enum class Kind {gaiji,ank,wait};
struct Event {Kind kind;int row=0,attribute=0;std::string text;};
using Sink=std::function<void(const Event&)>;
enum class Result {pending,resume,quit};
// MAIN pause has no actor tick or sound command. Initial/final reset-sense
// spins use an explicit counted-edge observation cadence, without clearing
// Count1. This cadence is an adapter, not a recovered CPU polling cost.
class Scene {
public:
    Scene(vsync::RasterClock&,std::uint16_t initial_keys,Sink={});
    std::uint64_t advance_elapsed(std::uint64_t,const maine::KeySource&,const maine::ElapsedSink& service={});
    std::uint64_t advance_elapsed_sampled(std::uint64_t,const pc98_input::Poll&,const maine::ElapsedSink& service={});
    Result result() const {return result_;}
    unsigned selected() const {return selected_;}
    std::uint16_t key_det() const {return key_det_;}
    unsigned ticks() const {return ticks_;}
private:
    std::uint64_t advance_impl(std::uint64_t,const maine::KeySource&,const pc98_input::Poll&,const maine::ElapsedSink&);
    void labels();
    enum class Phase {initial_release,menu,final_release};
    vsync::RasterClock* clock_;Sink sink_;Phase phase_=Phase::initial_release;
    Result result_=Result::pending;unsigned selected_=0,ticks_=0;
    std::uint16_t key_det_,previous_=0,pair_=0;
    bool reset_sample_=true;
    std::optional<vsync::Wait> poll_;
    std::optional<maine::Animation> wait_;
};
std::uint16_t input_from_host(std::uint16_t);
std::uint16_t input_to_host(std::uint16_t);
}
