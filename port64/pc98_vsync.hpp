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
        if(!active_)throw std::logic_error("VSYNC wait has no IRQ owner");
        const auto remaining=std::uint64_t(threshold-one_);
        std::uint64_t low=1,high=remaining*65536;
        while(low<high) {
            const auto middle=low+(high-low)/2;
            const auto counted=middle-(accumulator_+middle*increment_)/65536;
            if(counted>=remaining)high=middle;else low=middle+1;
        }
        return low;
    }
private:
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
    template<class Sink> void advance(std::uint64_t ns,Sink sink) {
        const auto finish=add(now_,ns);
        while(next_edge()<=finish) {
            now_=next_edge();const bool counted=counter_.interrupt();
            frame_=add(frame_,1);sink(now_,counted);
        }
        now_=finish;
    }
    void advance(std::uint64_t ns) {advance(ns,[](std::uint64_t,bool){});}
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
        const auto lines=add(multiply(frame,raster_.vertical_total),raster_.retrace_start);
        const auto cycles=multiply(lines,raster_.horizontal_total);
        // Quotient/remainder keeps hours of phase without multiplying a
        // complete uptime by1e9. Round the actual edge up to a nanosecond.
        const auto numerator=multiply(cycles%raster_.character_hz,1000000000);
        const auto elapsed=add(multiply(cycles/raster_.character_hz,1000000000),
            (numerator+raster_.character_hz-1)/raster_.character_hz);
        return add(add(epoch_,elapsed),raster_.irq_adjustment_ns);
    }
};
}
