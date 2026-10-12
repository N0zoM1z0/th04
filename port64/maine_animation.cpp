#include "maine_animation.hpp"
#include <algorithm>

namespace th04::portable::maine {
void Animation::advance(std::uint16_t held,const RequestSink& sink,const PaletteSink& palette) {
    if(clock_)throw std::logic_error("timed MAINE requires elapsed admission");
    if(status_==AnimationStatus::stopped)return;
    ++ticks_;
    if(status_==AnimationStatus::release || status_==AnimationStatus::press) {
        // input_reset_sense samples before frame_delay(1); input_sense then
        // ORs the post-refresh sample. A one-refresh release between two
        // held samples cannot satisfy the original release loop.
        const auto sampled=static_cast<std::uint16_t>(previous_keys_|held);
        previous_keys_=held;
        if(status_==AnimationStatus::release) {
            if(sampled)return;
            status_=AnimationStatus::press;
            if(press_budget_>0)return;
        } else if(!sampled) {
            if(press_budget_==9999 || ++press_elapsed_<press_budget_)return;
        }
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
            tone_=e.a ? (e.b ? 200 : 100) : (e.b ? 0 : 100);
            fade_end_=e.b ? 100 : (e.a ? 200 : 0);
            const auto speed=static_cast<std::uint16_t>(e.c);
            fade_step_=tone_<fade_end_ ? 6 : -6;fade_speed_=speed<0x8000 ? speed : 0;
            fade_aligned_=false;left_=1;status_=AnimationStatus::delay;
        } else if(e.kind==RequestKind::delay) {
            // frame_delay clears Count1 even for zero, then compares unsigned
            // WORDs. Zero returns in place; a negative int becomes a long wait.
            left_=static_cast<std::uint16_t>(e.a);
            if(left_)status_=AnimationStatus::delay;
        }
        else if(e.kind==RequestKind::wait) {
            const auto budget=static_cast<std::uint16_t>(e.a);
            press_budget_=budget>=0x8000 ? int(budget)-65536 : budget;
            if(!press_budget_)press_budget_=9999;
            press_elapsed_=0;previous_keys_=held;status_=AnimationStatus::release;
        }
        if(sink)sink(e);
        if(status_!=AnimationStatus::running)return;
    }
    status_=AnimationStatus::stopped;
}
std::uint64_t Animation::advance_elapsed(std::uint64_t ns,const KeySource& keys,
        const RequestSink& sink,const PaletteSink& palette,const ElapsedSink& service) {
    if(!clock_ || !keys)throw std::logic_error("elapsed MAINE requires clock and keys");
    const auto sample_before=[&] {
        previous_keys_=keys();count_wait_.emplace(*clock_,1);
    };
    for(;;) {
        if(status_==AnimationStatus::stopped)return ns;
        if(status_==AnimationStatus::running) {
            while(at_<requests_.size()) {
                const auto& e=requests_[at_++];
                if(e.kind==RequestKind::tone)tone_=e.a;
                else if(e.kind==RequestKind::fade) {
                    const auto speed=static_cast<std::uint16_t>(e.c);
                    tone_=e.a ? (e.b ? 200 : 100) : (e.b ? 0 : 100);
            fade_end_=e.b ? 100 : (e.a ? 200 : 0);fade_step_=tone_<fade_end_ ? 6 : -6;
                    fade_speed_=speed<0x8000 ? speed : 0;fade_aligned_=false;
                    fade_waits_=0;sync_wait_.emplace(*clock_);status_=AnimationStatus::delay;
                } else if(e.kind==RequestKind::delay) {
                    count_wait_.emplace(*clock_,e.a);left_=count_wait_->minimum();status_=AnimationStatus::delay;
                } else if(e.kind==RequestKind::wait) {
                    const auto word=static_cast<std::uint16_t>(e.a);
                    press_budget_=word>=0x8000 ? int(word)-65536 : word;
                    if(!press_budget_)press_budget_=9999;
                    press_elapsed_=0;status_=AnimationStatus::release;
                }
                if(sink)sink(e);
                if(e.kind==RequestKind::wait)sample_before();
                if(status_!=AnimationStatus::running)break;
            }
            if(status_==AnimationStatus::running){status_=AnimationStatus::stopped;return ns;}
        }
        const bool ready=sync_wait_ ? sync_wait_->ready() : count_wait_->ready();
        if(ready) {
            if(status_==AnimationStatus::release || status_==AnimationStatus::press) {
                ++ticks_;count_wait_.reset();
                const auto sensed=static_cast<std::uint16_t>(previous_keys_|keys());
                if(status_==AnimationStatus::release) {
                    if(sensed){sample_before();continue;}
                    if(press_budget_<=0){status_=AnimationStatus::running;continue;}
                    status_=AnimationStatus::press;sample_before();continue;
                }
                if(sensed || (press_budget_!=9999 && ++press_elapsed_>=press_budget_)) {
                    status_=AnimationStatus::running;continue;
                }
                sample_before();continue;
            }
            if(count_wait_) {
                ticks_+=static_cast<unsigned>(left_);count_wait_.reset();status_=AnimationStatus::running;continue;
            }
            ++ticks_;sync_wait_.reset();
            if(!fade_aligned_) {
                fade_aligned_=true;if(palette)palette(tone_);fade_waits_=static_cast<unsigned>(fade_speed_);
            } else --fade_waits_;
            while(!fade_waits_) {
                tone_+=fade_step_;
                if((fade_step_>0 && tone_>=fade_end_) || (fade_step_<0 && tone_<=fade_end_)) {
                    tone_=fade_end_;fade_step_=0;
                }
                if(palette)palette(tone_);
                if(!fade_step_){status_=AnimationStatus::running;break;}
                fade_waits_=static_cast<unsigned>(fade_speed_);
            }
            if(status_==AnimationStatus::running)continue;
            sync_wait_.emplace(*clock_);continue;
        }
        if(!ns)return 0;
        auto step=ns;
        const bool needs_irq=count_wait_ || sync_wait_->interrupt_owned();
        if(!needs_irq || clock_->counter().active())
            step=std::min(step,sync_wait_ ? sync_wait_->until_ready() : count_wait_->until_ready());
        if(!step)throw std::logic_error("elapsed MAINE wait made no progress");
        clock_->advance(step);if(service)service(step);ns-=step;
    }
}
} // namespace th04::portable::maine
