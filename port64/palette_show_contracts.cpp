#include "pc98_palette.hpp"
#include "op_startup.hpp"
#include <array>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace p=th04::portable::pc98_palette;
namespace startup=th04::portable::op_startup;
void require(bool value,const char* message) {if(!value)throw std::runtime_error(message);}
template<class Range> void numbers(const Range& values) {
    std::cout<<'[';bool comma=false;
    for(auto value:values) {if(comma)std::cout<<',';std::cout<<unsigned(value);comma=true;}
    std::cout<<']';
}
#ifndef TH04_PALETTE_PREDECESSOR
void self_test() {
    std::array<std::uint8_t,48> raw;raw.fill(255);
    const auto black=p::show(raw,65535),white=p::show(raw,65736);
    for(unsigned at=0;at<48;++at)require(black[at]==0 && white[at]==15,"WORD tone boundary");
    startup::Assets assets;startup::Renderer renderer(assets);
    startup::Event event{startup::Kind::palette_show};event.a=65535;
    event.data.assign(raw.begin(),raw.end());renderer.apply(event);
    require(renderer.dac()==black,"startup must consume signed WORD tone");
    std::vector<unsigned> reads;
    const auto lcd=p::show(raw,100,1,[&](unsigned port){reads.push_back(port);return port==0x871e ? 255 : 4;},[](unsigned,unsigned){});
    require(reads==std::vector<unsigned>{0x871e,0xae8e},"notebook fallback query");
    require(lcd[0]==0 && lcd[1]==15 && lcd[2]==0,"original LCD green weighting");
    std::cout<<"Palette show input PASS\n";
}
#endif
int main(int argc,char** argv) {
    try {
#ifndef TH04_PALETTE_PREDECESSOR
        if(argc==1 || (argc==2 && std::string(argv[1])=="--self-test")) {self_test();return 0;}
#endif
        require(argc==2 && std::string(argv[1])=="--rows","usage: --rows");
        int tone,note,q0,q1;
        while(std::cin>>tone>>note>>q0>>q1) {
            std::array<std::uint8_t,48> raw;for(auto& channel:raw) {unsigned value;require(bool(std::cin>>value) && value<=255,"palette input");channel=std::uint8_t(value);}
            startup::Assets assets;std::vector<unsigned> startup_reads;
#ifdef TH04_PALETTE_PREDECESSOR
            startup::Renderer renderer(assets);
#else
            std::vector<std::array<unsigned,3>> io;
            const auto query=[&](unsigned port) {require(port==0x871e || port==0xae8e,"unexpected query port");return std::uint8_t(port==0x871e ? q0 : q1);};
            const auto dac=p::show(raw,tone,std::uint16_t(note),[&](unsigned port) {
                const auto value=query(port);io.push_back({1,port,value});return value;
            },[&](unsigned port,unsigned value){io.push_back({0,port,value});});
            startup::Renderer renderer(assets,std::uint16_t(note),[&](unsigned port){startup_reads.push_back(port);return query(port);});
#endif
            startup::Event event{startup::Kind::palette_show};event.a=tone;
            event.data.assign(raw.begin(),raw.end());renderer.apply(event);
            std::cout<<"{\"startup\":";numbers(renderer.dac());
#ifndef TH04_PALETTE_PREDECESSOR
            std::cout<<",\"dac\":";numbers(dac);
            std::cout<<",\"io\":[";
            for(unsigned at=0;at<io.size();++at) {if(at)std::cout<<',';const auto& op=io[at];std::cout<<"[\""<<(op[0] ? "in" : "out")<<"\","<<op[1]<<','<<op[2]<<']';}
            std::cout<<']';
#endif
            std::cout<<",\"startup_reads\":";numbers(startup_reads);std::cout<<"}\n";
        }
        require(std::cin.eof(),"incomplete palette row");
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
