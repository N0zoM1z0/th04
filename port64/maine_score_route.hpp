#pragma once
#include "application_state.hpp"
#include "registration_scene.hpp"
#include "host_score.hpp"
#include "verdict_scene.hpp"
#include <memory>
#include "sound_scenes.hpp"

namespace th04::portable::maine {
enum class ScorePhase { registration_delay,registration,verdict,stopped };
enum class ScoreFlow { delay100,registration,verdict,sound_fade4,exec_op };
struct ScoreBoundary { ScoreFlow kind;unsigned tick; };
// Game Over already blacked out MAIN. ES_SCORE enters fresh MAINE directly:
// delay100 -> regist_menu -> verdict -> song fade4 -> fresh OP.
// The host score store has separate writer-close commits. This owner opens no
// audio device and cannot complete after a failed writer.
class ScoreRoute {
public:
    ScoreRoute(application::State&,const application::RunStatistics&,
               const registration::GraphicsAssets&,const cutscene::Assets&,
               score_file::HostStore&,std::function<void()> release_main={},sound::Timeline* audio=nullptr);
    void advance(std::uint16_t host_keys);
    ScorePhase phase() const {return phase_;}
    bool finished() const {return phase_==ScorePhase::stopped;}
    bool failed() const {return failed_;}
    unsigned ticks() const {return ticks_;}
    const registration::Scene* registration_scene() const {return registration_.get();}
    const verdict::Scene* verdict_scene() const {return verdict_.get();}
    const std::vector<ScoreBoundary>& boundaries() const {return boundaries_;}
    const std::vector<cutscene::Event>& sound_requests() const {return sound_;}
    void set_verdict_observer(verdict::Sink sink) {observer_=std::move(sink);}
private:
    void start_registration(std::uint16_t);
    sound::Timeline* audio_;
    application::State* application_;
    score_file::HostStore* store_;
    registration::GraphicsAssets registration_assets_;
    const cutscene::Assets* assets_;
    std::unique_ptr<registration::Scene> registration_;
    std::unique_ptr<verdict::Scene> verdict_;
    verdict::Sink observer_;
    ScorePhase phase_=ScorePhase::registration_delay;
    unsigned ticks_=0,delay_left_=100;
    bool completion_published_=false,random_published_=false,failed_=false;
    std::vector<ScoreBoundary> boundaries_{{ScoreFlow::delay100,0}};
    std::vector<cutscene::Event> sound_;
};
} // namespace th04::portable::maine
