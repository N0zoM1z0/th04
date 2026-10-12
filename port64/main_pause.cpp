#include "main_pause.hpp"
#include "player_lifecycle.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::pause {
std::uint16_t input_from_host(std::uint16_t held){return std::uint16_t(player::input_from_host_actions(held)|(held&0x4000u));}
std::uint16_t input_to_host(std::uint16_t key){return std::uint16_t((key&0x402fu)|(key&0x10u ? 0x800u : 0)|(key&0x1000u ? 0x2000u : 0)|(key&0x2000u ? 0x1000u : 0));}
Scene::Scene(vsync::RasterClock& clock,std::uint16_t initial,Sink sink)
    :clock_(&clock),sink_(std::move(sink)),key_det_(initial) {}
void Scene::labels() {
    if(sink_){sink_({Kind::gaiji,14,selected_ ? 0xc1 : 0xe9,"\xf2\xf3"});sink_({Kind::gaiji,15,selected_ ? 0xe9 : 0xc1,"\xf4\xf5"});}
}
std::uint64_t Scene::advance_elapsed(std::uint64_t ns,const maine::KeySource& keys,const maine::ElapsedSink& service) {
    if(!keys)throw std::invalid_argument("pause keyboard provider missing");
    for(;;) {
        if(result_!=Result::pending)return ns;
        if(phase_!=Phase::menu) {
            if(poll_ && !poll_->ready()) {
                const auto step=std::min(ns,poll_->until_ready());if(!step)return 0;
                clock_->advance(step);if(service)service(step);ns-=step;continue;
            }
            poll_.reset();
            if(key_det_) {
                key_det_=keys();
                if(key_det_){poll_.emplace(*clock_);continue;}
            }
            if(phase_==Phase::final_release) {
                if(sink_)for(int row:{12,14,15})sink_({Kind::ank,row,0xe1,std::string(4,' ')});
                result_=selected_ ? Result::quit : Result::resume;return ns;
            }
            if(sink_)sink_({Kind::gaiji,12,0xc1,"\xf0\xf1"});labels();phase_=Phase::menu;
        }
        if(!wait_){reset_sample_=true;wait_.emplace(std::vector<maine::Request>{{maine::RequestKind::wait,0}},clock_);}
        const auto sample=[&]{const auto value=keys();key_det_=reset_sample_ ? value : std::uint16_t(key_det_|value);reset_sample_=!reset_sample_;pair_=std::uint16_t(previous_|value);previous_=value;return value;};
        const auto sink=[&](const maine::Request& event){if(event.kind==maine::RequestKind::wait && sink_)sink_({Kind::wait});};
        const auto before=wait_->ticks();ns=wait_->advance_elapsed(ns,sample,sink,{},service);ticks_+=wait_->ticks()-before;
        if(wait_->status()!=maine::AnimationStatus::stopped)return 0;
        wait_.reset();key_det_=pair_;
        if(key_det_&3u){selected_=1-selected_;labels();}
        if(key_det_&0x4000u){result_=Result::quit;return ns;}
        if(key_det_&0x1000u){selected_=0;phase_=Phase::final_release;}
        else if(key_det_&(0x20u|0x2000u))phase_=Phase::final_release;
    }
}
}
