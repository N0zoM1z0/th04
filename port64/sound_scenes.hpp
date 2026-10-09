#pragma once
#include "sound_runtime.hpp"
#include "application_state.hpp"
#include "cutscene.hpp"
#include "staff_roll.hpp"
#include "registration.hpp"
#include "op_ranking.hpp"
#include "op_music.hpp"
#include <memory>

namespace th04::portable::sound {
enum class SceneKind {enter,leave,configure,action,measure};
struct SceneEvent {
    SceneKind kind;application::Program program;std::uint32_t generation;
    Action action{ActionKind::update};menu::Options options{};
    std::uint16_t goal=0,fallback=0;
};
using SceneSink=std::function<void(const SceneEvent&)>;
// Process-local beeper/control ownership with an independently resident PMD.
// An absent injected driver remains absent; no fictional measure is reported.
class Timeline {
public:
    using Samples=std::function<void(application::Program,std::uint32_t,const std::vector<std::int16_t>&)>;
    using StereoSamples=std::function<void(application::Program,std::uint32_t,const std::vector<pmd::StereoSample>&)>;
    using Requests=std::function<void(application::Program,std::uint32_t,const Request&)>;
    Timeline(Beeper::Reader reader={},SceneSink observer={},Samples samples={},
             std::shared_ptr<ResidentPmd> resident={},StereoSamples stereo={},Requests requests={})
        :reader_(std::move(reader)),observer_(std::move(observer)),samples_(std::move(samples)),
         resident_(std::move(resident)),stereo_(std::move(stereo)),requests_(std::move(requests)) {}
    void enter(application::Program,std::uint32_t,const menu::Options&);
    void leave();
    void configure(const menu::Options&);
    void op_title(bool demo);
    void op_restart(const menu::Options&);
    void handle(const Action&);
    void cutscene(const cutscene::Event&);
    void staff(const staff::Event&);
    void registration(const registration::Event&);
    void ranking(const op_ranking::Event&);
    void music(const op_music::Event&);
    const std::shared_ptr<Runtime>& runtime() const {return runtime_;}
    bool bgm_active() const {return runtime_ && runtime_->control().bgm!=0;}
    std::optional<std::uint16_t> song_measure() {return runtime_ ? runtime_->song_measure() : std::nullopt;}
    const std::shared_ptr<ResidentPmd>& resident() const {return resident_;}
    application::Program program() const {return program_;}
    std::uint32_t generation() const {return generation_;}
private:
    Beeper::Reader reader_;SceneSink observer_;Samples samples_;
    std::shared_ptr<ResidentPmd> resident_;StereoSamples stereo_;
    Requests requests_;
    std::shared_ptr<Runtime> runtime_;
    application::Program program_=application::Program::exited;
    std::uint32_t generation_=0;
    void emit(SceneEvent) const;
    void measure(int goal,int fallback);
};
}
