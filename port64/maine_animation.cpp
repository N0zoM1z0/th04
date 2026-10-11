#include "maine_animation.hpp"

namespace th04::portable::maine {
void Animation::advance(std::uint16_t held,const RequestSink& sink) {
    if(status_==AnimationStatus::stopped)return;
    ++ticks_;
    if(status_==AnimationStatus::release || status_==AnimationStatus::press) {
        // input_reset_sense samples before frame_delay(1); input_sense then
        // ORs the post-refresh sample. A one-refresh release between two
        // held samples cannot satisfy the original release loop.
        const auto sampled=static_cast<std::uint16_t>(previous_keys_|held);
        previous_keys_=held;
        if(status_==AnimationStatus::release) { if(!sampled)status_=AnimationStatus::press;return; }
        if(!sampled)return;
        status_=AnimationStatus::running;
    }
    if(status_==AnimationStatus::delay) {
        if(left_>0 && --left_>0)return;
        while(fade_step_) {
            tone_+=fade_step_;
            if((fade_step_>0 && tone_>=fade_end_) || (fade_step_<0 && tone_<=fade_end_)) {
                tone_=fade_end_;fade_step_=0;
            } else if(fade_speed_) { left_=fade_speed_;return; }
        }
        status_=AnimationStatus::running;
    }
    while(at_<requests_.size()) {
        const auto& e=requests_[at_++];
        if(e.kind==RequestKind::tone)tone_=e.a;
        else if(e.kind==RequestKind::fade) {
            tone_=e.b ? 0 : 100;fade_end_=e.b ? 100 : 0;
            // The far argument is a WORD, but the original loop tests its
            // signed value. Nonpositive speeds retain only the initial wait.
            const auto speed=static_cast<std::uint16_t>(e.c);
            fade_step_=e.b ? 6 : -6;fade_speed_=speed<0x8000u ? int(speed) : 0;
            left_=1+fade_speed_;status_=AnimationStatus::delay;
        } else if(e.kind==RequestKind::delay) { left_=e.a;status_=AnimationStatus::delay; }
        else if(e.kind==RequestKind::wait) { previous_keys_=held;status_=AnimationStatus::release; }
        if(sink)sink(e);
        if(status_!=AnimationStatus::running)return;
    }
    status_=AnimationStatus::stopped;
}
} // namespace th04::portable::maine
