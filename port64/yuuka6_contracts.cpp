#include "yuuka6.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
namespace y=th04::portable::yuuka6;
namespace m=th04::portable::motion;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool ok,const char* why) { if(!ok) throw std::runtime_error(why); }
unsigned byte(std::istream& in) { unsigned v=0;require(bool(in>>v) && v<=255,"invalid Yuuka6 state byte");return v; }
struct Wire {
    Bytes raw;unsigned at=0;
    unsigned byte() { return raw.at(at++); }
    unsigned word() { const auto lo=byte(),hi=byte();return lo|(hi<<8); }
    m::Point point() { const auto x=m::wrap(word()),yy=m::wrap(word());return {x,yy}; }
};
void word(Bytes& raw,int n) { const auto w=static_cast<std::uint16_t>(n);raw.push_back(w&255);raw.push_back(w>>8); }
void point(Bytes& raw,m::Point p) { word(raw,p.x);word(raw,p.y); }
y::Snapshot read(std::istream& in) {
    Wire w;for(unsigned i=0;i<35;++i) w.raw.push_back(byte(in));y::Snapshot s;auto& b=s.boss;
    b.position.current=w.point();b.position.previous=w.point();b.position.velocity=w.point();b.hp=m::wrap(w.word());
    b.sprite=w.byte();b.phase=w.byte();b.phase_frame=m::wrap(w.word());
    b.damage=w.byte();b.mode=w.byte();b.angle=w.byte();b.patterns_or_bonus=w.byte();b.end_hp=m::wrap(w.word());
    s.sprite_flag=w.byte();s.fly_path=w.byte();s.aux_flag=w.byte();s.unused_animation=w.byte();
    s.animation_frame=m::wrap(w.word());s.mirror=w.point();s.mirror_state=w.byte();return s;
}
void print(const y::Snapshot& s,bool returned) {
    const auto& b=s.boss;Bytes raw;point(raw,b.position.current);point(raw,b.position.previous);point(raw,b.position.velocity);word(raw,b.hp);
    raw.push_back(b.sprite);raw.push_back(b.phase);word(raw,b.phase_frame);
    for(auto n:{b.damage,b.mode,b.angle,b.patterns_or_bonus}) raw.push_back(n);
    word(raw,b.end_hp);for(auto n:{s.sprite_flag,s.fly_path,s.aux_flag,s.unused_animation}) raw.push_back(n);
    word(raw,s.animation_frame);point(raw,s.mirror);raw.push_back(s.mirror_state);
    constexpr char digits[]="0123456789abcdef";
    std::cout << returned << ' ';for(auto n:raw) std::cout << digits[n>>4] << digits[n&15];std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Yuuka6 fixtures");char op;
    while(in>>op) {
        int steps=0,selector=0,x=0,yy=0;require(bool(in>>steps>>selector>>x>>yy),"short Yuuka6 fixture");
        require(steps>0 && steps<=2048,"invalid Yuuka6 step count");
        require(op=='A' || op=='M' || op=='F' || op=='W' || op=='C',"unknown Yuuka6 operation");
        require(selector>=0 && selector<8,"invalid Yuuka6 animation selector");
        require(x>=-32768 && x<=32767 && yy>=-32768 && yy<=32767,"invalid Yuuka6 destination");
        y::System system(read(in));
        for(int i=0;i<steps;++i) {
            bool returned=false;
            if(op=='A') returned=system.animate(static_cast<y::Animation>(selector));
            else if(op=='M') returned=system.move_towards({m::wrap(x),m::wrap(yy)});
            else if(op=='F') returned=system.phase2_fly();
            else if(op=='W') system.horizontal_wave();
            else if(op=='C') returned=system.move_to_center();
            print(system.snapshot(),returned);
            if(op!='A' && op!='C') {
                auto s=system.snapshot();s.boss.phase_frame=m::wrap(std::int32_t(s.boss.phase_frame)+1);
                system=y::System(s);
            }
        }
    }
}
void contracts() {
    y::Snapshot s;s.sprite_flag=0;s.animation_frame=35;s.boss.position.current={3072,1280};
    s.aux_flag=17;y::System system(s);
    require(!system.move_to_center(),"appearance completed and centered in same call");
    require(system.snapshot().aux_flag==17,"hidden center movement cleared auxiliary flag");
    require(system.move_to_center() && system.snapshot().aux_flag==0,"center follow-up failed");
    s.fly_path=2;s.boss.phase_frame=1;y::System malformed(s);
    bool rejected=false;try { malformed.phase2_fly(); } catch(const std::invalid_argument&) { rejected=true; }
    require(rejected,"invalid flight path accepted");
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        require(argc==1,"usage: Yuuka6 contracts [--vectors FILE]");contracts();std::cout << "Stage 6 Yuuka movement contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr << "Yuuka6 contracts: " << e.what() << '\n';return 1; }
}
