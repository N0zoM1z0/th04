#include "pc98_vsync.hpp"
#include <iostream>
#include <cstdlib>
using namespace th04::portable::vsync;
void require(bool yes,const char* why) {if(!yes)throw std::runtime_error(why);}
int main() {
    try {
        Counter counter;require(!counter.interrupt(),"uninstalled IRQ");
        counter.start();for(unsigned i=0;i<104;++i)counter.interrupt();
        require(counter.one()==104 && counter.two()==104 && counter.interrupts_until(2)==0,
                "first Logo inherits sufficient counter");
        counter.clear_wait();require(counter.one()==0 && counter.two()==104 &&
                counter.interrupts_until(2)==2,"Logo reset preserves Count2");
        counter.interrupt();counter.interrupt();counter.clear_wait();
        require(counter.two()==106,"second Logo wait");
        counter.start();for(unsigned i=0;i<10;++i)counter.interrupt();counter.clear_wait();
        require(counter.one()==0 && counter.two()==10 && counter.interrupts_until(0)==0,
                "zero frame_delay still clears Count1");
        counter.end();counter.interrupt();require(counter.two()==10,"END preserves counters");
        counter.start();for(unsigned i=0;i<65536;++i)counter.interrupt();
        require(counter.one()==0 && counter.two()==0,"unsigned counter wrap");
        counter.start(13311);unsigned counted=0;
        for(unsigned i=0;i<65536;++i)counted+=counter.interrupt();
        require(counted==65536-13311 && counter.two()==counted && counter.accumulator()==0,
                "31kHz carry skips both words");
        for(unsigned increment: {0u,13311u,65535u}) {
            counter.start(std::uint16_t(increment));
            for(unsigned i=0;i<17;++i)counter.interrupt();counter.clear_wait();
            const auto predicted=counter.interrupts_until(2);
            for(std::uint64_t i=0;i<predicted;++i) {
                require(counter.one()<2,"threshold predicted too late");counter.interrupt();
            }
            require(counter.one()==2,"threshold predicted too early");
        }
        RasterClock clock;clock.counter().start();
        const auto first=clock.next_edge();require(first==16393985,"raster formula");
        clock.advance(first-1);require(clock.counter().two()==0,"before retrace");
        clock.advance(1);require(clock.counter().two()==1,"at retrace");
        clock.advance(4000000);clock.counter().clear_wait();
        const auto delay=clock.until_count(2);clock.advance(delay-1);
        require(clock.counter().one()==1,"inherited physical phase");clock.advance(1);
        require(clock.counter().one()==2,"unsigned awaited threshold");
        const auto phase=clock.next_edge();clock.counter().start();
        require(clock.next_edge()==phase && clock.counter().two()==0,"START retains raster phase");
        RasterClock split,whole;split.counter().start();whole.counter().start();
        split.advance(1);split.advance(123456789);whole.advance(123456790);
        require(split.next_edge()==whole.next_edge() && split.counter().two()==whole.counter().two(),
                "elapsed batching retains fractional phase");
        bool rejected=false;try {RasterClock bad(0,{0,106,440,407});}catch(const std::invalid_argument&){rejected=true;}
        require(rejected,"invalid raster accepted");
        rejected=false;try {RasterClock bad(std::uint64_t(-1));bad.advance(1);}
        catch(const std::overflow_error&){rejected=true;}
        require(rejected,"time overflow accepted");
        std::cout<<"VSYNC counter/raster contracts PASS\n";return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
