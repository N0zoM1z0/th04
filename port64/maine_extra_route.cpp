#include "maine_extra_route.hpp"
#include "maine_ending.hpp"
#include <stdexcept>

namespace th04::portable::maine {
ExtraRoute::ExtraRoute(application::State& app,application::RunStatistics statistics,
                      const registration::GraphicsAssets& registration_assets,
                      const cutscene::Assets& assets,score_file::HostStore& store,
                      std::function<void()> release_main,sound::Timeline* audio)
    :audio_(audio),application_(&app),statistics_(statistics),store_(&store),
     registration_assets_(registration_assets),assets_(&assets),release_main_(std::move(release_main)) {
    if(app.program()!=application::Program::main || app.resident().stage!=6 || app.resident().resource_stage!=6)
        throw std::logic_error("Extra MAINE requires an outgoing Extra MAIN");
    std::string picture="CONG04.PI";picture[4]=char('0'+unsigned(app.resident().playchar));
    if(!assets.scripts.count("_UDE.TXT") || !assets.pictures.count("UDE.PI") || !assets.pictures.count(picture))
        throw std::invalid_argument("Extra MAINE resources are missing");
    registration_assets_.text_weight=0;
    app.prepare_main_extra();
    main_sound_.push_back({cutscene::Kind::bgm_control,0x204});
    if(audio_)audio_->handle({sound::ActionKind::command,0x204});
}
void ExtraRoute::start_registration(std::uint16_t held) {
    const auto& r=application_->resident();
    registration::Run run{r.stage,r.config.rank,std::uint8_t('0'+unsigned(r.playchar)),
        std::uint8_t(r.shot_type),std::uint8_t(r.config.turbo),std::uint8_t(r.end_sequence),r.score_digits};
    registration_=std::make_unique<registration::Scene>(registration_assets_,run,store_->file(),
        [this]{return application_->next_process_random();},registration::input_from_main_actions(held),
        [this](const score_file::Operation& operation){store_->apply(operation);},
        [this](const registration::Event& e){if(audio_)audio_->registration(e);});
    phase_=ExtraPhase::registration;boundaries_.push_back({ExtraFlow::registration,ticks_});
}
void ExtraRoute::start_verdict() {
    const auto& r=application_->resident();
    verdict::Input input;input.resident=r;input.misses=r.miss_count;input.bombs_used=r.bombs_used;
    const auto& canvas=congratulations_->canvas();
    verdict_=std::make_unique<verdict::Scene>(*assets_,input,
        std::array<cutscene::Bytes,2>{canvas.page(0),canvas.page(1)},canvas.shown_page());
    congratulations_.reset();phase_=ExtraPhase::verdict;
    boundaries_.push_back({ExtraFlow::verdict,ticks_});
}
void ExtraRoute::advance(std::uint16_t held) {
    if(finished() || failed_)return;
    ++ticks_;
    try {
        if(phase_==ExtraPhase::main_fade) {
            ++fade_ticks_;
            if(--fade_left_)return;
            tone_-=6;
            if(tone_>0) {fade_left_=16;return;}
            tone_=0;
            application_->finish_main(statistics_,application::EndSequence::extra,release_main_);
            release_main_={};
            if(audio_)audio_->enter(application::Program::maine,application_->generation(),application_->resident().config);
            phase_=ExtraPhase::registration_delay;
            boundaries_.push_back({ExtraFlow::exec_maine,ticks_});
            boundaries_.push_back({ExtraFlow::delay100,ticks_});return;
        }
        if(phase_==ExtraPhase::registration_delay) {
            if(--delay_left_==0)start_registration(held);
            return;
        }
        if(phase_==ExtraPhase::registration) {
            registration_->advance(registration::input_from_main_actions(held));
            if(registration_->finished()) {
                const auto& canvas=registration_->renderer().canvas();
                congratulations_=std::make_unique<Congratulations>(*assets_,unsigned(application_->resident().playchar),4,
                    std::array<cutscene::Bytes,2>{canvas.page(0),canvas.page(1)},canvas.shown_page());
                registration_.reset();phase_=ExtraPhase::congratulations;
                boundaries_.push_back({ExtraFlow::tone0,ticks_});
                boundaries_.push_back({ExtraFlow::congratulations,ticks_});
            }
            return;
        }
        if(phase_==ExtraPhase::congratulations) {
            congratulations_->advance(input_from_main_actions(held));
            if(congratulations_->animation().status()==AnimationStatus::stopped)start_verdict();
            return;
        }
        verdict_->advance(input_from_main_actions(held),[&](const verdict::Event& e) {
            const auto& result=verdict_->result();
            if(e.kind==verdict::Kind::gaiji && e.a==192 && e.b==168 && !completion_published_) {
                application_->publish_maine_verdict_completion(result.std_frames);completion_published_=true;
            }
            if(e.kind==verdict::Kind::gaiji && e.a==192 && e.b==264 && !random_published_) {
                application_->seed_maine_verdict_random();
                if(result.random_drawn)application_->next_process_random();
                if(application_->process_random_state()!=result.random_state)
                    throw std::logic_error("Extra-route verdict process RNG differs");
                random_published_=true;
            }
            if(observer_)observer_(e);
        });
        if(verdict_->status()==verdict::Status::stopped) {
            sound_.push_back({cutscene::Kind::bgm_control,0x204});
            if(audio_)audio_->handle({sound::ActionKind::command,0x204});
            boundaries_.push_back({ExtraFlow::sound_fade4,ticks_});
            application_->finish_maine();phase_=ExtraPhase::stopped;
            boundaries_.push_back({ExtraFlow::exec_op,ticks_});
        }
    } catch(...) {failed_=true;throw;}
}
}
