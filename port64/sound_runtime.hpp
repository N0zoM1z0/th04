#pragma once
#include "beeper.hpp"
#include "pmd_resident.hpp"
#include <memory>
#include <exception>

namespace th04::portable::sound {
// MAIN call sites retain their order. Refresh time is an explicit muted host
// adapter, separate from original hardware timing and audio device playback.
enum class ActionKind { play,update,force,command,load,reset,immediate_update };
struct Action {ActionKind kind;std::uint16_t value=0;std::string name;};
using ActionSink=std::function<void(const Action&)>;
class Runtime {
public:
    using Samples=std::function<void(const std::vector<std::int16_t>&)>;
    using StereoSamples=std::function<void(const std::vector<pmd::StereoSample>&)>;
    Runtime(Beeper::Reader reader,ActionSink actions={},Sink requests={},Samples samples={},bool clock8=false,
            std::shared_ptr<ResidentPmd> resident={},StereoSamples stereo={});
    Runtime(const Runtime&)=delete;Runtime& operator=(const Runtime&)=delete;
    void configure(std::uint16_t bgm,std::uint16_t se,Drivers drivers={});
    void handle(const Action&);
    void begin_refresh(std::uint64_t nanoseconds);
    void end_refresh();
    void advance(std::uint64_t nanoseconds);
    void flush_refresh();
    void cancel_refresh() noexcept {pending_=0;refreshing_=false;}
    std::uint16_t command(std::uint16_t argument,std::uint16_t incoming_ax=0);
    std::optional<std::uint16_t> song_measure();
    const std::shared_ptr<ResidentPmd>& resident() const {return resident_;}
    const State& control() const {return control_.state();}
    const BeepState& beeper() const {return beeper_.state();}
    std::uint64_t samples() const {return pcm_.samples();}
    std::uint64_t unsupported() const {return unsupported_;}
    int resource_result() const {return resource_result_;}
private:
    Beeper::Reader reader_;ActionSink actions_;Sink requests_;Samples samples_;
    std::shared_ptr<ResidentPmd> resident_;StereoSamples stereo_;
    Beeper beeper_;BeepPcm pcm_;Control control_;
    std::uint64_t fraction_=0,pending_=0,unsupported_=0;bool refreshing_=false;
    int resource_result_=0;
    std::uint16_t reply_=0;
    void consume(const Request&);
};
// The caller retains its process owner until this refresh guard finishes.
class Refresh {
public:
    Refresh(Runtime* runtime,std::uint64_t ns):runtime_(runtime),exceptions_(std::uncaught_exceptions()){if(runtime_)runtime_->begin_refresh(ns);}
    ~Refresh() noexcept(false){if(runtime_){if(std::uncaught_exceptions()>exceptions_)runtime_->cancel_refresh();else runtime_->end_refresh();}}
    Refresh(const Refresh&)=delete;Refresh& operator=(const Refresh&)=delete;
private:Runtime* runtime_;int exceptions_;
};
}
