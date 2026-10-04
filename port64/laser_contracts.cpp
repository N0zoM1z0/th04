#include "thick_lasers.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
namespace l=th04::portable::laser;
namespace m=th04::portable::motion;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool v,const char* why) { if(!v) throw std::runtime_error(why); }
struct Wire {
    Bytes bytes;unsigned at=0;
    explicit Wire(std::istream& in) { for(unsigned i=0;i<24;++i) { int n;require(bool(in>>n),"short laser fixture");bytes.push_back(static_cast<std::uint8_t>(n)); } }
    unsigned byte() { return bytes.at(at++); }
    std::int16_t word() { const auto lo=byte(),hi=byte();return m::wrap(lo|(hi<<8)); }
    l::Beam beam() {
        l::Beam b;b.flag=byte();b.unused_first=byte();b.origin={word(),word()};
        for(auto& n:b.unused_origin) n=byte();
        b.phase_frame=word();b.line_frames=word();b.static_frames=word();b.outline=byte();b.unused_color=byte();
        b.maximum_radius=word();b.radius=word();b.radius_speed=word();return b;
    }
};
void word(Bytes& bytes,int n) { const auto w=static_cast<std::uint16_t>(n);bytes.push_back(w&255);bytes.push_back(w>>8); }
void beam(Bytes& bytes,const l::Beam& b) {
    bytes.push_back(b.flag);bytes.push_back(b.unused_first);word(bytes,b.origin.x);word(bytes,b.origin.y);
    bytes.insert(bytes.end(),b.unused_origin.begin(),b.unused_origin.end());word(bytes,b.phase_frame);word(bytes,b.line_frames);word(bytes,b.static_frames);
    bytes.push_back(b.outline);bytes.push_back(b.unused_color);word(bytes,b.maximum_radius);word(bytes,b.radius);word(bytes,b.radius_speed);
}
void checkpoint(const l::System& system,const std::vector<l::Draw>& events) {
    const auto& s=system.snapshot();Bytes bytes;beam(bytes,s.scratch);for(const auto& b:s.beams) beam(bytes,b);
    constexpr char digits[]="0123456789abcdef";
    for(auto n:bytes) std::cout<<digits[n>>4]<<digits[n&15];
    std::cout<<' '<<+s.player_hit<<' '<<events.size();
    for(const auto& d:events) std::cout<<' '<<unsigned(d.kind)<<' '<<d.mode<<' '<<d.color<<' '<<d.x<<' '<<d.y<<' '<<d.end_x<<' '<<d.end_y<<' '<<d.radius;
    std::cout<<'\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"missing laser fixture file");char op;unsigned steps,index,hit;int x,y;
    while(in>>op>>steps>>index>>x>>y>>hit) {
        l::Snapshot s;s.player_hit=static_cast<std::uint8_t>(hit);s.scratch=Wire(in).beam();for(auto& b:s.beams) b=Wire(in).beam();
        l::System system(s);std::vector<l::Draw> events;
        const auto sound=[&](std::uint16_t value) { events.push_back({static_cast<l::DrawKind>(0),0,value}); };
        for(unsigned frame=0;frame<steps;++frame) {
            events.clear();
            if(op=='I') system.initialize();
            else if(op=='P') system.pull(index);
            else if(op=='A') system.add(sound);
            else if(op=='U' || op=='S') system.update({m::wrap(x),m::wrap(y)},sound);
            else if(op=='D') events=system.draws();
            else if(op=='L') { if(frame==0) { system.initialize();system.add(sound); } else system.update({m::wrap(x),m::wrap(y)},sound); }
            else throw std::runtime_error("unknown laser fixture operation");
            checkpoint(system,events);
        }
    }
    require(in.eof(),"malformed laser fixture header");
}
void contracts() {
    l::System system;system.initialize();auto& b=system.scratch();b.line_frames=0;b.static_frames=0;b.maximum_radius=7;b.radius_speed=6;b.origin={3072,1024};
    unsigned se=0;const auto sound=[&](unsigned n) { se=se*10+n; };
    require(system.add(sound),"first beam missing");system.update({3072,5120},sound);
    require(system.snapshot().beams[0].flag==2 && system.snapshot().beams[0].phase_frame==1 && se==56,"line transition order");
    system.update({3072,5120});require(system.snapshot().beams[0].flag==3 && system.snapshot().beams[0].radius==7,"growth clamp");
    system.update({3072,5120});system.update({3072,5120});
    require(system.snapshot().beams[0].flag==0 && system.snapshot().beams[0].phase_frame==2,"last shrinking clock");
    require(system.draws().size()==1 && system.draws()[0].kind==l::DrawKind::disable,"empty graphics disable");
    bool rejected=false;try { system.pull(2); } catch(const std::out_of_range&) { rejected=true; }
    require(rejected,"invalid host slot accepted");
}
}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        require(argc==1,"unknown laser contract arguments");contracts();std::cout<<"Thick laser contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
