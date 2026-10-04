#include "maine_ending.hpp"
#include <stdexcept>

namespace th04::portable::maine {
Ending::Ending(application::State& app,application::RunStatistics statistics,
               application::EndSequence sequence,const cutscene::Assets& assets,
               std::function<void()> release_main,bool bgm_active)
    :application_(&app),statistics_(statistics),end_sequence_(sequence),assets_(&assets),
     release_main_(std::move(release_main)),bgm_active_(bgm_active) {
    const auto& resident=app.resident();
    name_=cutscene::script_name(unsigned(resident.playchar),unsigned(resident.shot_type),
        sequence==application::EndSequence::bad);
    if(!assets.scripts.count(name_)) throw std::invalid_argument("MAINE Ending script is missing");
    app.prepare_main_ending(sequence);
    main_sound_requests_.emplace_back(cutscene::Kind::bgm_control,0x204);
}
void Ending::advance(std::uint16_t keys,const cutscene::Sink& observer) {
    if(phase_==Phase::staff_roll_pending) return;
    if(phase_==Phase::main_fade) {
        // end_game_* always performs palette_black_out(16): initial VSync,
        // then seventeen six-tone steps. Escape does not bypass this fade.
        ++fade_ticks_;
        if(--fade_left_) return;
        tone_-=6;
        if(tone_>0) { fade_left_=16;return; }
        tone_=0;
        application_->finish_main(statistics_,end_sequence_,release_main_);
        release_main_={};
        scene_=std::make_unique<cutscene::Scene>(*assets_,name_);
        phase_=Phase::cutscene;
        return;
    }
    const auto& script=scene_->script();
    if(script.status()==cutscene::Status::measure) {
        const auto& events=scene_->pending_sound_requests();
        if(events.empty() || events.back().kind!=cutscene::Kind::measure)
            throw std::logic_error("MAINE measure wait lacks a sound request");
        const auto wait=events.back();
        if(bgm_active_) {
            if(!song_measure_ || *song_measure_<static_cast<std::uint16_t>(wait.a)) return;
        } else if(measure_left_>0 && --measure_left_>0) return;
        scene_->script().complete_measure_wait();
    }
    for(;;) {
        scene_->advance(keys,observer);
        if(script.status()!=cutscene::Status::measure) break;
        // Original snd_delay_until_measure executes frame_delay(fallback)
        // only when BGM is inactive. Active sound must report actual progress.
        const auto wait=scene_->pending_sound_requests().back();
        if(bgm_active_) {
            if(!song_measure_ || *song_measure_<static_cast<std::uint16_t>(wait.a)) return;
            scene_->script().complete_measure_wait();continue;
        }
        measure_left_=static_cast<std::uint16_t>(wait.b);
        if(measure_left_>0) return;
        scene_->script().complete_measure_wait();
    }
    if(script.status()==cutscene::Status::stopped) phase_=Phase::staff_roll_pending;
}
} // namespace th04::portable::maine
