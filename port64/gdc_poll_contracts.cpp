#include "op_startup.hpp"
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
using namespace th04::portable;
namespace {void require(bool yes,const char* why) {if(!yes)throw std::runtime_error(why);}}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") {
            std::ifstream in(argv[2]);std::uint64_t epoch,phase,adjust;unsigned mode,increment,seed,steps;
            while(in>>epoch>>phase>>adjust>>mode>>increment>>seed>>steps) {
                require(mode<2 && increment<=65535 && seed<=65535 && steps<=8,"VSync vector input");
                vsync::Raster raster;raster.irq_adjustment_ns=adjust;
                vsync::RasterClock clock(epoch,raster);clock.counter().start(std::uint16_t(increment));
                for(unsigned i=0;i<seed;++i)clock.counter().interrupt();
                if(!mode)clock.counter().end();clock.advance(phase);
                for(unsigned i=0;i<steps;++i) {
                    vsync::Wait wait(clock);const auto delay=wait.until_ready();
                    require(!wait.ready() && delay,"new VSync wait returned immediately");
                    clock.advance(delay-1);require(!wait.ready(),"VSync wait before source edge");
                    clock.advance(1);require(wait.ready(),"VSync wait missed source edge");
                    std::cout<<clock.now()<<' '<<delay<<' '<<clock.counter().one()<<' '
                        <<clock.counter().two()<<' '<<clock.counter().accumulator()<<' '
                        <<wait.interrupt_owned()<<'\n';
                }
            }
            require(in.eof() && bool(std::cout),"VSync vector stream");return 0;
        }
        require(argc==1,"GDC poll contracts CLI");
        vsync::RasterClock wrap;wrap.counter().start();
        for(unsigned i=0;i<65535;++i)wrap.counter().interrupt();
        vsync::Wait change(wrap);require(wrap.counter().one()==65535,"wait cleared Count1");
        wrap.advance(change.until_ready());require(change.ready() && wrap.counter().one()==0 &&
            wrap.counter().two()==0,"VSync change fails FFFF-to-zero wrap");
        vsync::RasterClock external;external.counter().start();external.counter().interrupt();
        vsync::Wait cleared(external);external.counter().clear_wait();
        require(cleared.ready() && external.counter().two()==1,"VSync compares change, not increase");
        vsync::RasterClock off;off.counter().start();off.counter().interrupt();off.counter().end();
        vsync::Wait polled(off);off.advance(polled.until_ready());
        require(polled.ready() && off.counter().one()==1 && off.counter().two()==1,
            "uninstalled GDC wait clears or requires IRQ");
        vsync::RasterClock title_clock;title_clock.counter().start();
        for(unsigned i=0;i<100;++i)title_clock.counter().interrupt();
        op_startup::Assets assets;op_startup::Scene title(assets,false,false,{}, {},1,0,{},&title_clock);
        require(title_clock.counter().one()==100 && title_clock.counter().two()==100,
            "startup palette wait clears Count1");
        const auto silence=[](std::uint64_t){};const auto timer=[]{return 1ull;};
        title.advance_elapsed(title_clock.until_change(),0,silence,timer);
        require(title_clock.counter().one()==101 && title_clock.counter().two()==101,
            "successive palette waits retain both IRQ words");
        vsync::RasterClock whole_clock,split_clock;whole_clock.counter().start(13311);split_clock.counter().start(13311);
        op_startup::Scene whole(assets,false,false,{}, {},1,0,{},&whole_clock);
        op_startup::Scene split(assets,false,false,{}, {},1,0,{},&split_clock);
        whole.advance_elapsed(1000000000,0,silence,timer);
        for(unsigned i=0;i<1000;++i)split.advance_elapsed(1000000,0,silence,timer);
        require(whole.palette()==split.palette() && whole.tone()==split.tone() &&
            whole_clock.counter().one()==split_clock.counter().one() &&
            whole_clock.counter().two()==split_clock.counter().two() &&
            whole_clock.now()==split_clock.now(),"palette wait partition dependence");
        vsync::RasterClock near_limit(std::numeric_limits<std::uint64_t>::max()-20000000);
        vsync::Wait near(near_limit);near_limit.advance(near.until_ready());require(near.ready(),"valid final edge overflow");
        std::cout<<"GDC/owned VSync wait contracts PASS\n";return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
