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
    if(phase_==Phase::verdict_pending || phase_==Phase::congratulations_pending || phase_==Phase::registration_pending)return;
    if(phase_==Phase::registration_delay) {
        if(--registration_delay_left_==0)phase_=Phase::registration_pending;
        return;
    }
    if(phase_==Phase::congratulations) {
        congratulations_->advance(keys);
        if(congratulations_->animation().status()==AnimationStatus::stopped)begin_registration_delay();
        return;
    }
    if(phase_==Phase::verdict) {
        verdict_->advance(keys,[&](const verdict::Event& e) {
            const auto& result=verdict_->result();
            // STD and LCG writes occur at different points in the original
            // nonblocking calculation. Publish each at its first digit
            // request, after the complete UDE background fade has finished.
            if(e.kind==verdict::Kind::gaiji && e.a==192 && e.b==168 && !completion_published_) {
                application_->publish_maine_verdict_completion(result.std_frames);
                completion_published_=true;
            }
            if(e.kind==verdict::Kind::gaiji && e.a==192 && e.b==264 && !random_published_) {
                application_->seed_maine_verdict_random();
                if(result.random_drawn)application_->next_process_random();
                if(application_->process_random_state()!=result.random_state)
                    throw std::logic_error("verdict process RNG differs from its original-controlled calculation");
                random_published_=true;
            }
            if(verdict_observer_)verdict_observer_(e);
        });
        if(verdict_->status()==verdict::Status::stopped) {
            const auto& r=application_->resident();
            if(r.end_sequence==application::EndSequence::good || r.config.rank==0)
                phase_=Phase::congratulations_pending;
            else begin_registration_delay();
        }
        return;
    }
    if(phase_==Phase::staff_roll) {
        staff_->advance();
        if(staff_->status()==staff::Status::stopped)phase_=Phase::verdict_pending;
        return;
    }
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
void Ending::start_staff_roll(const staff::Assets& assets) {
    if(phase_!=Phase::staff_roll_pending || !scene_)throw std::logic_error("Staff Roll requires a completed Ending");
    staff_=std::make_unique<staff::Scene>(assets,std::array<Bytes,2>{scene_->page(0),scene_->page(1)},scene_->shown_page());
    staff_->set_audio_active(bgm_active_);
    // A new song owns measure progress; the previous Ending song cannot
    // satisfy STAFF's waits. Its PI/script/text-box owner is now released.
    text_weight_=scene_->text_weight();
    song_measure_.reset();scene_.reset();phase_=Phase::staff_roll;
}
void Ending::start_verdict() {
    if(phase_!=Phase::verdict_pending || !staff_)throw std::logic_error("verdict requires a completed Staff Roll");
    const auto& resident=application_->resident();
    verdict::Input input;input.resident=resident;input.misses=resident.miss_count;input.bombs_used=resident.bombs_used;
    verdict_=std::make_unique<verdict::Scene>(*assets_,input,
        std::array<Bytes,2>{staff_->page(0),staff_->page(1)},staff_->shown_page());
    // Transfer both pages once, then release the whole Staff Roll graphics
    // owner. A new process is not entered; the MAINE RNG remains untouched.
    staff_.reset();song_measure_.reset();phase_=Phase::verdict;
}
void Ending::start_congratulations() {
    if(phase_!=Phase::congratulations_pending || !verdict_)
        throw std::logic_error("congratulations requires a completed verdict");
    const auto& r=application_->resident();const auto& old=verdict_->canvas();
    text_weight_=old.text_weight();
    congratulations_=std::make_unique<Congratulations>(*assets_,unsigned(r.playchar),r.config.rank,
        std::array<Bytes,2>{old.page(0),old.page(1)},old.shown_page());
    // Retain pages, not the old scoring/clock owner. MAINE and its continued
    // LCG remain the same process while this picture waits for a fresh press.
    verdict_.reset();phase_=Phase::congratulations;
}
void Ending::begin_registration_delay() {
    // Recovered _main requests song fade(4), then frame_delay(100), before
    // regist_menu. This delay consumes refreshes even when Enter stays held.
    maine_sound_requests_.push_back({cutscene::Kind::bgm_control,0x204});
    registration_delay_left_=100;phase_=Phase::registration_delay;
}
} // namespace th04::portable::maine
