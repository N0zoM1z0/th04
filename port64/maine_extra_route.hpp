#pragma once
#include "application_state.hpp"
#include "registration_scene.hpp"
#include "host_score.hpp"
#include "verdict_scene.hpp"
#include "congratulations.hpp"
#include <memory>
#include "sound_scenes.hpp"

namespace th04::portable::maine {
enum class ExtraPhase { main_fade,registration_delay,registration,congratulations,verdict,stopped };
enum class ExtraFlow { main_sound_fade4,main_fade16,exec_maine,delay100,registration,
                       tone0,congratulations,verdict,sound_fade4,exec_op };
struct ExtraBoundary {ExtraFlow kind;unsigned tick;};
// MAIN end_extra -> blackout16 -> fresh MAINE -> delay100 -> registration
// -> Extra congratulations -> verdict -> fade4 -> fresh OP. No Ending/Staff.
// Writer failures retain MAINE and are never retried on subsequent refreshes.
class ExtraRoute {
public:
    ExtraRoute(application::State&,application::RunStatistics,
               const registration::GraphicsAssets&,const cutscene::Assets&,
               score_file::HostStore&,std::function<void()> release_main={},sound::Timeline* audio=nullptr);
    void advance(std::uint16_t host_keys);
    ExtraPhase phase() const {return phase_;}
    bool finished() const {return phase_==ExtraPhase::stopped;}
    bool failed() const {return failed_;}
    unsigned ticks() const {return ticks_;}
    unsigned fade_ticks() const {return fade_ticks_;}
    int main_tone() const {return tone_;}
    const registration::Scene* registration_scene() const {return registration_.get();}
    const Congratulations* congratulations_scene() const {return congratulations_.get();}
    const verdict::Scene* verdict_scene() const {return verdict_.get();}
    const std::vector<ExtraBoundary>& boundaries() const {return boundaries_;}
    const std::vector<cutscene::Event>& main_sound_requests() const {return main_sound_;}
    const std::vector<cutscene::Event>& sound_requests() const {return sound_;}
    void set_verdict_observer(verdict::Sink sink) {observer_=std::move(sink);}
private:
    void start_registration(std::uint16_t);
    void start_verdict();
    sound::Timeline* audio_;
    application::State* application_;
    application::RunStatistics statistics_;
    score_file::HostStore* store_;
    registration::GraphicsAssets registration_assets_;
    const cutscene::Assets* assets_;
    std::function<void()> release_main_;
    std::unique_ptr<registration::Scene> registration_;
    std::unique_ptr<Congratulations> congratulations_;
    std::unique_ptr<verdict::Scene> verdict_;
    verdict::Sink observer_;
    ExtraPhase phase_=ExtraPhase::main_fade;
    unsigned ticks_=0,fade_ticks_=0,delay_left_=100;
    int tone_=100,fade_left_=17;
    bool completion_published_=false,random_published_=false,failed_=false;
    std::vector<ExtraBoundary> boundaries_{{ExtraFlow::main_sound_fade4,0},{ExtraFlow::main_fade16,0}};
    std::vector<cutscene::Event> main_sound_,sound_;
};
}
