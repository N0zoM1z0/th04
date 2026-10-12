#pragma once
#include "registration_render.hpp"
#include "maine_animation.hpp"
#include <functional>

namespace th04::portable::registration {
enum class Status { fade_in,editing,release,press,fade_out,stopped };
using Sink=std::function<void(const Event&)>;
using FileSink=std::function<void(const score_file::Operation&)>;

// Owns the blocking clock and consumes Menu commands in order. Construction
// draws the initial table and starts black-in; advance consumes ONE refresh.
// All sound requests are retained; this owner never opens an audio device.
class Scene {
public:
    Scene(const GraphicsAssets&,Run,score_file::File&,const score_file::Random&,
          std::uint16_t inherited_keys=0,FileSink={},Sink={},vsync::RasterClock* clock=nullptr);
    void advance(std::uint16_t held);
    std::uint64_t advance_elapsed(std::uint64_t,const maine::KeySource&,
        const maine::ElapsedSink& service={},const std::function<void()>& loop={},const maine::PaletteSink& palette={});
    bool timed() const {return clock_!=nullptr;}
    Status status() const { return status_; }
    bool finished() const { return status_==Status::stopped; }
    bool failed() const {return failed_;}
    int tone() const { return tone_; }
    unsigned ticks() const { return ticks_; }
    const Menu& menu() const { return menu_; }
    const Renderer& renderer() const { return renderer_; }
    const std::vector<Event>& sound_requests() const { return sound_; }
    std::size_t event_count() const { return at_; }
private:
    void drain(std::uint16_t held);
    vsync::RasterClock* clock_;
    std::optional<maine::Animation> animation_;
    std::optional<vsync::Delay> count_wait_;
    bool editing_reset_=false,editing_iteration_=false;
    Menu menu_;
    Renderer renderer_;
    FileSink file_sink_;
    Sink observer_;
    std::vector<Event> sound_;
    std::size_t at_=0;
    Status status_=Status::editing;
    unsigned ticks_=0;
    int tone_=0,left_=0,step_=0,goal_=0,speed_=0;
    std::uint16_t previous_keys_=0;
    bool startup_pending_=true;
    bool failed_=false;
};

// MAIN host actions deliberately have different masks from MAINE key_det.
// Translate each action; an any-key bridge would turn Esc into a typed glyph.
std::uint16_t input_from_main_actions(std::uint16_t);
} // namespace th04::portable::registration
