#include "maine_animation.hpp"
#include <fstream>
#include <iostream>
#include <string>
using namespace th04::portable;
constexpr std::uint64_t hz=2631575,h=106,v=440,r=407;
std::uint64_t edges(std::uint64_t now) {
    if(now*hz<r*h*1000000000)return 0;
    return (now*hz-r*h*1000000000)/(v*h*1000000000)+1;
}
std::uint16_t held(unsigned profile,std::uint64_t now) {
    const auto n=edges(now)%16;
    return (profile==1 ? (n<5 || n>=10) : profile==2 ? n!=6 : false) ? 0x20 : 0;
}
int main(int argc,char** argv) {
 try {
    if(argc==1) {
        vsync::RasterClock clock;clock.counter().start();clock.counter().interrupts(5);
        maine::Animation a({{maine::RequestKind::fade,0,1,0},{maine::RequestKind::delay,0},
            {maine::RequestKind::wait,1},{maine::RequestKind::text,99}},&clock);
        auto keys=[]{return std::uint16_t(0);};const auto first=clock.until_change();
        a.advance_elapsed(first-1,keys);
        if(a.status()!=maine::AnimationStatus::delay || clock.counter().one()!=5)throw std::runtime_error("fade released before IRQ");
        a.advance_elapsed(1,keys);
        if(a.status()!=maine::AnimationStatus::release || clock.counter().one() || clock.counter().two()!=6)throw std::runtime_error("zero delay/key reset order");
        a.advance_elapsed(clock.until_count(2),keys);
        if(a.status()!=maine::AnimationStatus::stopped || clock.counter().one()!=1 || clock.counter().two()!=8)throw std::runtime_error("finite key timeout");
        std::cout<<"Elapsed MAINE shared counter and input boundaries PASS\n";return 0;
    }
    if(argc!=3 || std::string(argv[1])!="--vectors")throw std::invalid_argument("use --vectors FILE");
    std::ifstream in(argv[2]);unsigned inc,profile;std::uint64_t seed,phase,horizon,chunk;int speed,delay,budget;unsigned index=0;
    while(in>>inc>>seed>>phase>>speed>>delay>>budget>>profile>>horizon>>chunk) {
        vsync::RasterClock clock;clock.counter().start(std::uint16_t(inc));clock.counter().interrupts(seed);clock.advance(phase);
        maine::Animation a({{maine::RequestKind::fade,0,1,speed},{maine::RequestKind::delay,delay},
            {maine::RequestKind::wait,budget},{maine::RequestKind::fade,0,0,0},{maine::RequestKind::text,99}},&clock);
        std::cout<<"CASE "<<index++<<'\n';auto left=horizon;
        auto keys=[&]{auto k=held(profile,clock.now());std::cout<<"K "<<clock.now()<<' '<<k<<'\n';return k;};
        auto event=[&](const maine::Request& e){std::cout<<"E "<<clock.now()<<' '<<int(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<'\n';};
        auto palette=[&](int tone){std::cout<<"P "<<clock.now()<<' '<<tone<<'\n';};
        do {
            const auto step=chunk ? std::min(chunk,left) : left;
            const auto unused=a.advance_elapsed(step,keys,event,palette);left-=step-unused;
            if(a.status()==maine::AnimationStatus::stopped || !left)break;
        } while(true);
        std::cout<<"STOP "<<clock.now()<<' '<<left<<' '<<int(a.status())<<' '<<clock.counter().one()<<' '<<clock.counter().two()<<' '<<clock.counter().accumulator()<<'\n';
    }
    if(!in.eof())throw std::invalid_argument("incomplete row");
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
