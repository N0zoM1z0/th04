#pragma once
#include "application_state.hpp"
#include "cutscene_scene.hpp"
#include "staff_roll.hpp"
#include "verdict_scene.hpp"
#include <memory>
#include <optional>

namespace th04::portable::maine {
enum class Phase { main_fade,cutscene,staff_roll_pending,staff_roll,verdict_pending,
                   verdict,congratulations_pending,registration_pending };
inline std::uint16_t input_from_main_actions(std::uint16_t input) {
    // MAIN's host Z/Enter masks can overlap MAINE's Escape bit. Translate
    // cancellation explicitly; all other held actions only affect wait input.
    return (input&0x2000 ? cutscene::input_cancel : 0) | (input&~0x2000u ? 0x20 : 0);
}
// MAIN's nonreturning end_game call and MAINE's first animation owner.
// Resources borrowed by Scene must outlive this owner. MAIN's release callback
// runs after publication and before a fresh MAINE process/generator is entered.
class Ending {
public:
    Ending(application::State&,application::RunStatistics,application::EndSequence,
           const cutscene::Assets&,std::function<void()> release_main={},bool bgm_active=false);
    void advance(std::uint16_t maine_keys,const cutscene::Sink& observer={});
    void report_song_measure(std::uint16_t measure) {
        if(staff_)staff_->report_song_measure(measure);else song_measure_=measure;
    }
    void start_staff_roll(const staff::Assets&);
    void start_verdict();
    void set_verdict_observer(verdict::Sink sink) { verdict_observer_=std::move(sink); }
    Phase phase() const { return phase_; }
    int main_tone() const { return tone_; }
    const cutscene::Scene* scene() const { return scene_.get(); }
    const staff::Scene* staff_scene() const { return staff_.get(); }
    const verdict::Scene* verdict_scene() const { return verdict_.get(); }
    const std::string& script_name() const { return name_; }
    unsigned fade_ticks() const { return fade_ticks_; }
    const std::vector<cutscene::Event>& main_sound_requests() const { return main_sound_requests_; }
private:
    application::State* application_;
    application::RunStatistics statistics_;
    application::EndSequence end_sequence_;
    const cutscene::Assets* assets_;
    std::function<void()> release_main_;
    std::unique_ptr<cutscene::Scene> scene_;
    std::unique_ptr<staff::Scene> staff_;
    std::unique_ptr<verdict::Scene> verdict_;
    verdict::Sink verdict_observer_;
    bool completion_published_=false,random_published_=false;
    std::string name_;
    Phase phase_=Phase::main_fade;
    int tone_=100,fade_left_=17,measure_left_=0;
    unsigned fade_ticks_=0;
    bool bgm_active_;
    std::optional<std::uint16_t> song_measure_;
    // The current host audio backend is inactive, but preserve the request
    // issued before MAIN's fade so a real backend can consume it later.
    std::vector<cutscene::Event> main_sound_requests_;
};
} // namespace th04::portable::maine
