#include "maine_score_route.hpp"
#include "maine_ending.hpp"
#include <stdexcept>

namespace th04::portable::maine {
ScoreRoute::ScoreRoute(application::State& app,const application::RunStatistics& statistics,
                      const registration::GraphicsAssets& registration_assets,
                      const cutscene::Assets& assets,score_file::HostStore& store,
                      std::function<void()> release_main,sound::Timeline* audio)
    :audio_(audio),application_(&app),store_(&store),registration_assets_(registration_assets),assets_(&assets) {
    if(app.program()!=application::Program::main ||
       app.resident().end_sequence!=application::EndSequence::score)
        throw std::logic_error("score-only MAINE requires the completed MAIN Quit request");
    if(!assets.scripts.count("_UDE.TXT") || !assets.pictures.count("UDE.PI"))
        throw std::invalid_argument("score-only MAINE verdict resources are missing");
    // A new MAINE owns a fresh graph_putsa_fx value, not the Ending text box's
    // retained weight. Do not issue the normal Ending's pre-registration fade.
    registration_assets_.text_weight=0;
    app.finish_main(statistics,application::EndSequence::score,release_main);
    if(audio_)audio_->enter(application::Program::maine,app.generation(),app.resident().config);
}
void ScoreRoute::start_registration(std::uint16_t held) {
    const auto& r=application_->resident();
    registration::Run run{r.stage,r.config.rank,std::uint8_t('0'+unsigned(r.playchar)),
        std::uint8_t(r.shot_type),std::uint8_t(r.config.turbo),
        std::uint8_t(r.end_sequence),r.score_digits};
    registration_=std::make_unique<registration::Scene>(registration_assets_,run,store_->file(),
        [this]{return application_->next_process_random();},
        registration::input_from_main_actions(held),
        [this](const score_file::Operation& operation){store_->apply(operation);},
        [this](const registration::Event& e){if(audio_)audio_->registration(e);});
    boundaries_.push_back({ScoreFlow::registration,ticks_});
    phase_=ScorePhase::registration;
}
void ScoreRoute::advance(std::uint16_t held) {
    if(finished() || failed_)return;
    ++ticks_;
    try {
        if(phase_==ScorePhase::registration_delay) {
            if(--delay_left_==0)start_registration(held);
            return;
        }
        if(phase_==ScorePhase::registration) {
            registration_->advance(registration::input_from_main_actions(held));
            if(registration_->finished()) {
                const auto& r=application_->resident();
                verdict::Input input;input.resident=r;input.misses=r.miss_count;input.bombs_used=r.bombs_used;
                const auto& canvas=registration_->renderer().canvas();
                verdict_=std::make_unique<verdict::Scene>(*assets_,input,
                    std::array<cutscene::Bytes,2>{canvas.page(0),canvas.page(1)},canvas.shown_page());
                registration_.reset();phase_=ScorePhase::verdict;
                boundaries_.push_back({ScoreFlow::verdict,ticks_});
            }
            return;
        }
        verdict_->advance(input_from_main_actions(held),[&](const verdict::Event& e) {
            const auto& result=verdict_->result();
            if(e.kind==verdict::Kind::gaiji && e.a==192 && e.b==168 && !completion_published_) {
                application_->publish_maine_verdict_completion(result.std_frames);
                completion_published_=true;
            }
            if(e.kind==verdict::Kind::gaiji && e.a==192 && e.b==264 && !random_published_) {
                application_->seed_maine_verdict_random();
                if(result.random_drawn)application_->next_process_random();
                if(application_->process_random_state()!=result.random_state)
                    throw std::logic_error("score-route verdict process RNG differs");
                random_published_=true;
            }
            if(observer_)observer_(e);
        });
        if(verdict_->status()==verdict::Status::stopped) {
            sound_.push_back({cutscene::Kind::bgm_control,0x204});
            if(audio_)audio_->handle({sound::ActionKind::command,0x204});
            boundaries_.push_back({ScoreFlow::sound_fade4,ticks_});
            application_->finish_maine();phase_=ScorePhase::stopped;
            boundaries_.push_back({ScoreFlow::exec_op,ticks_});
        }
    } catch(...) {
        // A constructor may already have consumed RNG or file operations.
        // Preserve the failed MAINE state; repeated refreshes never retry it.
        failed_=true;throw;
    }
}
} // namespace th04::portable::maine
