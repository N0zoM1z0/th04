#include "pc98_vsync.hpp"
#include <fstream>
#include <iostream>
#include <string>
using namespace th04::portable::vsync;
void state(const Counter& c) {std::cout<<c.one()<<' '<<c.two()<<' '<<c.accumulator()<<' ';}
int main(int argc,char** argv) {
 try {
    if(argc==1) {
        for(unsigned inc:{0,1,13311,65535}) {
            Counter bulk,scalar;bulk.start(std::uint16_t(inc));scalar.start(std::uint16_t(inc));
            auto n=bulk.interrupts(131072);std::uint64_t counted=0;
            for(unsigned i=0;i<131072;++i)counted+=scalar.interrupt();
            if(n!=counted || bulk.one()!=scalar.one() || bulk.two()!=scalar.two() || bulk.accumulator()!=scalar.accumulator())throw std::runtime_error("bulk recurrence");
        }
        RasterClock fast,observed;fast.counter().start(13311);observed.counter().start(13311);
        unsigned callbacks=0;fast.advance(1000000000);observed.advance(1000000000,[&](auto,bool){++callbacks;});
        if(!callbacks || fast.now()!=observed.now() || fast.next_edge()!=observed.next_edge() || fast.counter().one()!=observed.counter().one() || fast.counter().two()!=observed.counter().two() || fast.counter().accumulator()!=observed.counter().accumulator())throw std::runtime_error("observed raster parity");
        auto previous=fast.counter().two();Delay zero(fast,65536);
        if(!zero.ready() || zero.until_ready() || fast.counter().one() || fast.counter().two()!=previous)throw std::runtime_error("zero WORD delay");
        Delay negative(fast,-1);fast.advance(negative.until_ready());
        if(!negative.ready() || fast.counter().one()!=65535)throw std::runtime_error("negative WORD delay");
        RasterClock inactive;Delay blocked(inactive,1);inactive.advance(1000000000);
        bool rejected=false;try {blocked.until_ready();}catch(const std::logic_error&){rejected=true;}
        if(blocked.ready() || !rejected)throw std::runtime_error("unowned delay used GDC fallback");
        Delay live(fast,3);fast.advance(live.until_ready());fast.counter().clear_wait();
        if(live.ready())throw std::runtime_error("delay cached an old completion");
        fast.advance(live.until_ready());if(!live.ready())throw std::runtime_error("delay after external clear");
        std::cout<<"Counter bulk, raster observers and live WORD delay PASS\n";return 0;
    }
    if(argc!=3 || std::string(argv[1])!="--vectors")throw std::invalid_argument("use --vectors FILE");
    std::ifstream in(argv[2]);if(!in)throw std::runtime_error("vector input");std::string mode;
    while(in>>mode) {
        unsigned active,inc;std::uint64_t pre,n,epoch,phase,adjust;int minimum;
        if(mode=="B") {
            if(!(in>>active>>inc>>pre>>n) || active>1 || inc>65535)throw std::invalid_argument("bulk row");
            Counter c;c.start(std::uint16_t(inc));c.interrupts(pre);if(!active)c.end();state(c);auto count=c.interrupts(n);state(c);std::cout<<count<<' '<<c.active()<<'\n';
        } else if(mode=="D") {
            if(!(in>>active>>inc>>epoch>>phase>>adjust>>pre>>minimum) || active>1 || inc>65535)throw std::invalid_argument("delay row");
            Raster r;r.irq_adjustment_ns=adjust;RasterClock c(epoch,r);c.counter().start(std::uint16_t(inc));c.counter().interrupts(pre);c.advance(phase);if(!active)c.counter().end();state(c.counter());
            Delay delay(c,minimum);state(c.counter());std::cout<<c.now()<<' '<<delay.minimum()<<' '<<delay.ready()<<' ';
            try {auto dt=delay.until_ready();c.advance(dt);std::cout<<dt<<' '<<c.now()<<' ';state(c.counter());std::cout<<delay.ready()<<'\n';}
            catch(const std::logic_error&){std::cout<<"BLOCKED\n";}
        } else throw std::invalid_argument("vector kind");
    }
    if(!in.eof())throw std::invalid_argument("partial vector");
 } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
