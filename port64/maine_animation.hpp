#pragma once
#include <cstddef>
#include <cstdint>
#include <functional>
#include <string>
#include <utility>
#include <vector>
#include <optional>
#include "pc98_vsync.hpp"

namespace th04::portable::maine {
enum class RequestKind {
    tone,access,show,pi_load,pi_palette,pi_put,pi_free,copy_page,fade,
    text,gaiji,file_open,file_seek,file_read,file_close,delay,wait
};
struct Request {
    RequestKind kind;
    int a=0,b=0,c=0,d=0,e=0;
    std::string data{};
};
using RequestSink=std::function<void(const Request&)>;
using PaletteSink=std::function<void(int)>;
using KeySource=std::function<std::uint16_t()>;
using ElapsedSink=std::function<void(std::uint64_t)>;
enum class AnimationStatus { running,delay,release,press,stopped };

// MAINE's palette fades, frame_delay and input_wait are shared by verdict and
// congratulations. This owner consumes real request sequences; it neither
// computes a score nor parses a synthetic Ending script. A repaint cannot
// consume a refresh or release a held key.
class Animation {
public:
    explicit Animation(std::vector<Request> requests,vsync::RasterClock* clock=nullptr)
        :requests_(std::move(requests)),clock_(clock) {}
    void advance(std::uint16_t held,const RequestSink& sink={},const PaletteSink& palette={});
    // Returns unconsumed time at STOP so the process owner can establish its
    // next wait at this event's actual time, rather than at the admission end.
    std::uint64_t advance_elapsed(std::uint64_t ns,const KeySource& keys,
        const RequestSink& sink={},const PaletteSink& palette={},const ElapsedSink& service={});
    bool timed() const {return clock_!=nullptr;}
    AnimationStatus status() const { return status_; }
    int tone() const { return tone_; }
    unsigned ticks() const { return ticks_; }
    std::size_t event_count() const { return at_; }
private:
    std::vector<Request> requests_;
    AnimationStatus status_=AnimationStatus::running;
    std::size_t at_=0;
    unsigned ticks_=0;
    std::uint16_t previous_keys_=0;
    int tone_=0,left_=0,fade_step_=0,fade_end_=0,fade_speed_=0;
    bool fade_aligned_=false;
    int press_budget_=9999,press_elapsed_=0;
    vsync::RasterClock* clock_=nullptr;
    std::optional<vsync::Wait> sync_wait_;
    std::optional<vsync::Delay> count_wait_;
    unsigned fade_waits_=0;
};
} // namespace th04::portable::maine
