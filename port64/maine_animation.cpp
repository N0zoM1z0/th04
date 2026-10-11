#include "maine_animation.hpp"

namespace th04::portable::maine {
void Animation::advance(std::uint16_t held,const RequestSink& sink,const PaletteSink& palette) {
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
        if(fade_step_) {
            // Both black fades align once, show the initial tone, then use
            // signed WORD speed for each six-tone group. Nonpositive speed
            // still aligns, but all subsequent shows happen on this admission.
            if(!fade_aligned_) {
                fade_aligned_=true;
                if(palette)palette(tone_);
                if(fade_speed_) {left_=fade_speed_;return;}
            }
            do {
                tone_+=fade_step_;
                if((fade_step_>0 && tone_>=fade_end_) || (fade_step_<0 && tone_<=fade_end_)) {
                    tone_=fade_end_;fade_step_=0;
                }
                if(palette)palette(tone_);
                if(fade_step_ && fade_speed_) {left_=fade_speed_;return;}
            } while(fade_step_);
        }
        status_=AnimationStatus::running;
    }
    while(at_<requests_.size()) {
        const auto& e=requests_[at_++];
        if(e.kind==RequestKind::tone)tone_=e.a;
        else if(e.kind==RequestKind::fade) {
            tone_=e.b ? 0 : 100;fade_end_=e.b ? 100 : 0;
            const auto speed=static_cast<std::uint16_t>(e.c);
            fade_step_=e.b ? 6 : -6;fade_speed_=speed<0x8000 ? speed : 0;
            fade_aligned_=false;left_=1;status_=AnimationStatus::delay;
        } else if(e.kind==RequestKind::delay) {
            // frame_delay clears Count1 even for zero, then compares unsigned
            // WORDs. Zero returns in place; a negative int becomes a long wait.
            left_=static_cast<std::uint16_t>(e.a);
            if(left_)status_=AnimationStatus::delay;
        }
        else if(e.kind==RequestKind::wait) { previous_keys_=held;status_=AnimationStatus::release; }
        if(sink)sink(e);
        if(status_!=AnimationStatus::running)return;
    }
    status_=AnimationStatus::stopped;
}
} // namespace th04::portable::maine
