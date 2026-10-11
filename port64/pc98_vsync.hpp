#pragma once
#include <cstdint>
#include <limits>
#include <stdexcept>

namespace th04::portable::vsync {
// OP decoded 0000:25C6 increments both unsigned words unless adding the
// cadence increment carries. START resets both counters even when installed,
// but preserves the cadence accumulator (OP decoded 0000:2552..25BB).
// frame_delay and Logo clear only Count1, at different points in their waits.
class Counter {
public:
    void start(std::uint16_t increment=0) {
        one_=two_=0;increment_=increment;active_=true;
    }
    void end() {active_=false;}
    void clear_wait() {one_=0;}
    bool interrupt() {
        if(!active_)return false;
        const std::uint32_t sum=std::uint32_t(accumulator_)+increment_;
        accumulator_=std::uint16_t(sum);
        if(sum>=65536)return false;
        one_=std::uint16_t(one_+1u);two_=std::uint16_t(two_+1u);return true;
    }
    // The same recurrence without per-IRQ observers. Split the product so
    // UINT64_MAX physical inputs cannot overflow an intermediate accumulator.
    std::uint64_t interrupts(std::uint64_t pulses) {
        if(!active_)return 0;
        const auto tail=std::uint64_t(accumulator_)+(pulses%65536)*increment_;
        const auto carries=(pulses/65536)*increment_+tail/65536;
        const auto counted=pulses-carries;
        accumulator_=std::uint16_t(tail);
        one_=std::uint16_t(one_+std::uint16_t(counted));
        two_=std::uint16_t(two_+std::uint16_t(counted));
        return counted;
    }
    std::uint16_t one() const {return one_;}
    std::uint16_t two() const {return two_;}
    std::uint16_t accumulator() const {return accumulator_;}
    std::uint16_t increment() const {return increment_;}
    bool active() const {return active_;}
    // Number of physical IRQ inputs needed for an unsigned Count1 threshold.
    // A closed integer search also handles increment65535 without billions
    // of simulated carry-skips. Count1 cannot wrap before reaching threshold.
    std::uint64_t interrupts_until(std::uint16_t threshold) const {
        if(one_>=threshold)return 0;
        return pulses_until(std::uint64_t(threshold-one_));
    }
    // VSYNC_WAIT snapshots Count1 and waits for a change without clearing it.
    // One counted IRQ also changes FFFFh to0000h.
    std::uint64_t interrupts_until_change() const {return pulses_until(1);}
private:
    std::uint64_t pulses_until(std::uint64_t remaining) const {
        if(!active_)throw std::logic_error("VSYNC wait has no IRQ owner");
        std::uint64_t low=1,high=remaining*65536;
        while(low<high) {
            const auto middle=low+(high-low)/2;
            const auto counted=middle-(accumulator_+middle*increment_)/65536;
            if(counted>=remaining)high=middle;else low=middle+1;
        }
        return low;
    }
    std::uint16_t one_=0,two_=0,accumulator_=0,increment_=0;
    bool active_=false;
};

// Explicit raster inputs, independent of PMD installation and CPU service.
// Defaults are the retained 24-kHz mode: master AW80, HS8/HFP10/HBP8,
// AL400, VS8/VFP7/VBP25 and integer 21,052,600/8 character clock.
struct Raster {
    std::uint32_t character_hz=2631575,horizontal_total=106,
                  vertical_total=440,retrace_start=407;
    std::uint64_t irq_adjustment_ns=0;
};
// Ideal raster-edge adapter with zero CPU ISR latency. A host supplies the
// display epoch and an optional explicit edge adjustment; measured ISR work
// remains separate. This is not the GDC blink callback or a physical timing
// claim. Resetting an IRQ counter never resets the global raster phase.
class RasterClock {
public:
    explicit RasterClock(std::uint64_t display_epoch_ns=0,Raster raster={})
        :raster_(raster),epoch_(display_epoch_ns),now_(display_epoch_ns) {
        if(!raster.character_hz || !raster.horizontal_total ||
           !raster.vertical_total || raster.retrace_start>=raster.vertical_total)
            throw std::invalid_argument("VSYNC raster geometry");
    }
    Counter& counter() {return counter_;}
    const Counter& counter() const {return counter_;}
    std::uint64_t now() const {return now_;}
    std::uint64_t next_edge() const {return edge(frame_);}
    std::uint64_t until_count(std::uint16_t threshold) const {
        const auto pulses=counter_.interrupts_until(threshold);
        if(!pulses)return 0;
        const auto at=edge(add(frame_,pulses-1));
        if(at<now_)throw std::logic_error("VSYNC raster phase moved backwards");
        return at-now_;
    }
    std::uint64_t until_change() const {
        return edge(add(frame_,counter_.interrupts_until_change()-1))-now_;
    }
    // Uninstalled VSYNC_WAIT polls a strict next GDC rising edge. ISR edge
    // adjustment and cadence skips do not move this physical status edge.
    std::uint64_t until_vblank() const {
        const auto after=[this](std::uint64_t frame) {
            try {return raster_edge(frame)>now_;}
            catch(const std::overflow_error&) {return true;}
        };
        std::uint64_t low=0,high=frame_ ? frame_ : 1;
        while(!after(high))high=add(high,high);
        while(low<high) {
            const auto middle=low+(high-low)/2;
            if(!after(middle))low=middle+1;else high=middle;
        }
        return raster_edge(low)-now_;
    }
    template<class Sink> void advance(std::uint64_t ns,Sink sink) {
        const auto finish=add(now_,ns);
        while(true) {
            std::uint64_t at;
            try {at=next_edge();}
            catch(const std::overflow_error&) {break;} // No representable future edge.
            if(at>finish)break;
            now_=at;const bool counted=counter_.interrupt();
            frame_=add(frame_,1);sink(now_,counted);
        }
        now_=finish;
    }
    void advance(std::uint64_t ns) {
        const auto finish=add(now_,ns);
        const auto after=[this,finish](std::uint64_t frame) {
            try {return edge(frame)>finish;}
            catch(const std::overflow_error&) {return true;}
        };
        auto low=frame_,high=frame_;std::uint64_t step=1;
        const auto maximum=std::numeric_limits<std::uint64_t>::max();
        while(!after(high)) {
            if(high==maximum)throw std::overflow_error("VSYNC frame overflow");
            high=step>maximum-high ? maximum : high+step;
            step=step>maximum/2 ? maximum : step*2;
        }
        while(low<high) {
            const auto middle=low+(high-low)/2;
            if(after(middle))high=middle;else low=middle+1;
        }
        counter_.interrupts(low-frame_);frame_=low;now_=finish;
    }
private:
    Raster raster_;std::uint64_t epoch_,now_,frame_=0;Counter counter_;
    static std::uint64_t add(std::uint64_t a,std::uint64_t b) {
        if(b>std::numeric_limits<std::uint64_t>::max()-a)
            throw std::overflow_error("VSYNC time overflow");
        return a+b;
    }
    static std::uint64_t multiply(std::uint64_t a,std::uint64_t b) {
        if(b && a>std::numeric_limits<std::uint64_t>::max()/b)
            throw std::overflow_error("VSYNC raster overflow");
        return a*b;
    }
    std::uint64_t edge(std::uint64_t frame) const {
        return add(raster_edge(frame),raster_.irq_adjustment_ns);
    }
    std::uint64_t raster_edge(std::uint64_t frame) const {
        const auto lines=add(multiply(frame,raster_.vertical_total),raster_.retrace_start);
        const auto cycles=multiply(lines,raster_.horizontal_total);
        // Quotient/remainder keeps hours of phase without multiplying a
        // complete uptime by1e9. Round the actual edge up to a nanosecond.
        const auto numerator=multiply(cycles%raster_.character_hz,1000000000);
        const auto elapsed=add(multiply(cycles/raster_.character_hz,1000000000),
            (numerator+raster_.character_hz-1)/raster_.character_hz);
        return add(epoch_,elapsed);
    }
};
// Original OP0000:2648 selects the installed Count1-change path at entry;
// otherwise it polls GDC status. Neither path clears either counter.
class Wait {
public:
    explicit Wait(RasterClock& clock):clock_(&clock),owned_(clock.counter().active()),
        initial_(clock.counter().one()),deadline_(owned_ ? 0 : clock.now()+clock.until_vblank()) {}
    bool ready() const {
        return owned_ ? clock_->counter().one()!=initial_ : clock_->now()>=deadline_;
    }
    std::uint64_t until_ready() const {
        if(ready())return 0;
        return owned_ ? clock_->until_change() : deadline_-clock_->now();
    }
    bool interrupt_owned() const {return owned_;}
private:
    RasterClock* clock_;bool owned_;std::uint16_t initial_;std::uint64_t deadline_;
};
// frame_delay clears only Count1, then polls an unsigned WORD threshold.
// It has no GDC fallback when the IRQ owner is absent. Other consumers can
// reset Count1 during the wait, so readiness is a live word comparison.
class Delay {
public:
    explicit Delay(RasterClock& clock,int minimum):clock_(&clock),
        minimum_(static_cast<std::uint16_t>(minimum)) {clock_->counter().clear_wait();}
    bool ready() const {return clock_->counter().one()>=minimum_;}
    std::uint64_t until_ready() const {return clock_->until_count(minimum_);}
    std::uint16_t minimum() const {return minimum_;}
private:
    RasterClock* clock_;std::uint16_t minimum_;
};
}
