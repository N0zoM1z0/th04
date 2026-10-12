#include "registration_scene.hpp"
#include <algorithm>

namespace th04::portable::registration {
std::uint16_t input_from_main_actions(std::uint16_t keys) {
    return std::uint16_t((keys&15u) | (keys&0x20u ? shot : 0) |
        (keys&0x800u ? bomb : 0) | (keys&0x1000u ? ok : 0) |
        (keys&0x2000u ? cancel : 0));
}
Scene::Scene(const GraphicsAssets& assets,Run run,score_file::File& file,
             const score_file::Random& random,std::uint16_t held,FileSink io,Sink observer,vsync::RasterClock* clock)
    :clock_(clock),menu_(run,file,random,held,true),
     renderer_(assets,menu_.character(),menu_.place()),
     file_sink_(std::move(io)),observer_(std::move(observer)) {
    drain(held);
}
void Scene::drain(std::uint16_t held) {
    while(at_<menu_.events().size()) {
        const auto& e=menu_.events()[at_];
        // Persist only the operation being consumed, never the Menu's future
        // final file buffer. A failed host write cannot return to fresh OP.
        if(e.kind==Kind::file && file_sink_) {
            try {file_sink_(e.io);}catch(...) {failed_=true;throw;}
        }
        renderer_.apply(e);
        if(e.kind==Kind::tone)tone_=e.a;
        else if(e.kind==Kind::sound || e.kind==Kind::song)sound_.push_back(e);
        if(observer_)observer_(e);
        ++at_;
        if(e.kind==Kind::fade) {
            status_=e.a ? Status::fade_in : Status::fade_out;
            tone_=e.a ? 0 : 100;goal_=e.a ? 100 : 0;
            step_=e.a ? 6 : -6;speed_=e.b;
            // Original palette fade: align at one VBlank, then 17 groups of
            // speed waits. Black-in(2)=35 refreshes; black-out(1)=18.
            left_=1+speed_;
            if(clock_)animation_.emplace(std::vector<maine::Request>{{maine::RequestKind::fade,0,e.a,e.b}},clock_);
            return;
        }
        if(e.kind==Kind::wait) {
            previous_keys_=held;status_=Status::release;
            if(clock_)animation_.emplace(std::vector<maine::Request>{{maine::RequestKind::wait,0}},clock_);
            return;
        }
    }
    if(menu_.finished())status_=Status::stopped;
}
void Scene::advance(std::uint16_t held) {
    if(finished() || failed_)return;
    if(clock_)throw std::logic_error("timed registration requires elapsed admission");
    ++ticks_;
    if(status_==Status::fade_in || status_==Status::fade_out) {
        if(--left_>0)return;
        tone_+=step_;
        if((step_>0 && tone_<goal_) || (step_<0 && tone_>goal_)) {left_=speed_;return;}
        tone_=goal_;status_=Status::editing;
        if(startup_pending_) {
            startup_pending_=false;
            menu_.complete_startup(held);
            // The first input_sense iteration follows input_reset_sense
            // immediately. The frame delay is at the bottom of that loop.
            if(!menu_.finished())menu_.advance(held);
        }
        drain(held);return;
    }
    if(status_==Status::release || status_==Status::press) {
        const auto sample=std::uint16_t(previous_keys_|held);previous_keys_=held;
        if(status_==Status::release) {
            if(!sample)status_=Status::press;
            return;
        }
        if(!sample)return;
        status_=Status::editing;drain(held);return;
    }
    menu_.advance(held);drain(held);
}
std::uint64_t Scene::advance_elapsed(std::uint64_t ns,const maine::KeySource& keys,
        const maine::ElapsedSink& service,const std::function<void()>& loop,const maine::PaletteSink& palette) {
    if(!clock_ || !keys)throw std::logic_error("elapsed registration requires clock and keys");
    if(failed_)return ns;
    for(;;) {
        if(finished())return ns;
        if(animation_) {
            const auto before=animation_->ticks();
            ns=animation_->advance_elapsed(ns,keys,{},[&](int tone){tone_=tone;if(palette)palette(tone);},service);
            ticks_+=animation_->ticks()-before;
            if(animation_->status()!=maine::AnimationStatus::stopped) {
                if(status_==Status::release || status_==Status::press)
                    status_=animation_->status()==maine::AnimationStatus::release ? Status::release : Status::press;
                return 0;
            }
            animation_.reset();status_=Status::editing;
            if(startup_pending_) {
                startup_pending_=false;menu_.complete_startup(0);
                editing_reset_=!menu_.finished();
            }
            drain(0);continue;
        }
        if(count_wait_) {
            if(!count_wait_->ready()) {
                if(!ns)return 0;
                const auto step=clock_->counter().active() ? std::min(ns,count_wait_->until_ready()) : ns;
                clock_->advance(step);if(service)service(step);ns-=step;continue;
            }
            count_wait_.reset();++ticks_;
        }
        drain(0);
        if(animation_ || finished())continue;
        if(editing_reset_) {menu_.reset_sample(keys());editing_reset_=false;}
        if(!editing_iteration_) {
            menu_.advance_sensed(keys());editing_iteration_=true;
            drain(0);if(animation_ || finished()){editing_iteration_=false;continue;}
        }
        menu_.reset_sample(keys());if(loop)loop();
        count_wait_.emplace(*clock_,1);editing_iteration_=false;
    }
}
} // namespace th04::portable::registration
