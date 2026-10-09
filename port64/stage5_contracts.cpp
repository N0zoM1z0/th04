#include "stage5.hpp"
#include "stage6.hpp"
#include "stagex.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
namespace s=th04::portable::stage5;
namespace o=th04::portable::orange;
namespace m=th04::portable::motion;
namespace mb=th04::portable::midboss;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool b,const char* why) { if(!b) throw std::runtime_error(why); }
int number(std::istream& in) { int n;require(bool(in>>n),"short Stage5 fixture");return n; }
struct Wire {
    Bytes data;unsigned at=0;
    Wire(std::istream& in,unsigned count) { while(count--) data.push_back(static_cast<std::uint8_t>(number(in))); }
    unsigned byte() { return data.at(at++); }
    unsigned word() { const auto lo=byte(),hi=byte();return lo|(hi<<8); }
    m::Point point() { const auto x=m::wrap(word()),y=m::wrap(word());return {x,y}; }
    m::Motion motion() { const auto c=point(),p=point(),v=point();return {c,p,v}; }
};
void word(Bytes& v,int n) { const auto w=static_cast<std::uint16_t>(n);v.push_back(static_cast<std::uint8_t>(w));v.push_back(static_cast<std::uint8_t>(w>>8)); }
void point(Bytes& v,m::Point p) { word(v,p.x);word(v,p.y); }
void motion(Bytes& v,const m::Motion& p) { point(v,p.current);point(v,p.previous);point(v,p.velocity); }
void hex(const Bytes& v) { constexpr char d[]="0123456789abcdef";for(auto n:v) std::cout<<d[n>>4]<<d[n&15];std::cout<<' '; }
o::Snapshot read_boss(std::istream& in) {
    Wire w(in,24);o::Snapshot b;b.position=w.motion();b.hp=m::wrap(w.word());b.sprite=w.byte();b.phase=w.byte();b.phase_frame=m::wrap(w.word());
    b.damage=w.byte();b.mode=w.byte();b.angle=w.byte();b.patterns_or_bonus=w.byte();b.end_hp=m::wrap(w.word());
    for(auto& n:b.additional) n=static_cast<std::uint8_t>(number(in));
    for(auto* e:{&b.small[0],&b.small[1],&b.big}) {
        Wire q(in,16);e->alive=q.byte();e->age=q.byte();e->center=q.point();e->radius=q.point();e->delta=q.point();
        const auto n=q.byte();e->unused=static_cast<std::int8_t>(n<128 ? int(n) : int(n)-256);e->angle_offset=q.byte();
    }return b;
}
void print_boss(const o::Snapshot& b) {
    Bytes v;motion(v,b.position);word(v,b.hp);v.push_back(b.sprite);v.push_back(b.phase);word(v,b.phase_frame);
    for(auto n:{b.damage,b.mode,b.angle,b.patterns_or_bonus}) { v.push_back(n); }
    word(v,b.end_hp);hex(v);hex(Bytes(b.additional.begin(),b.additional.end()));v.clear();
    for(const auto* e:{&b.small[0],&b.small[1],&b.big}) {
        v.push_back(e->alive);v.push_back(e->age);point(v,e->center);point(v,e->radius);point(v,e->delta);v.push_back(static_cast<std::uint8_t>(e->unused));v.push_back(e->angle_offset);
    }hex(v);
}
void setup_vectors(const char* path,bool sixth=false,bool extra=false) {
    std::ifstream in(path);require(bool(in),"cannot read Stage5 setups");unsigned rank;
    while(in>>rank) {
        const auto boss=read_boss(in);Wire w(in,22);mb::Snapshot mid;mid.position=w.motion();mid.start_frame=w.word();mid.hp=m::wrap(w.word());mid.sprite=w.byte();mid.phase=w.byte();mid.phase_frame=m::wrap(w.word());mid.damaged=w.byte();mid.unused_angle=w.byte();
        mid.active=number(in)!=0;mid.hp_bar=m::wrap(number(in));mid.pattern_angle=static_cast<std::uint8_t>(number(in));
        auto next_boss=boss;auto next_mid=mid;std::array<m::Subpixel,3> centers{};
        if(extra) {const auto next=th04::portable::stagex::prepare(boss,mid);next_boss=next.boss;next_mid=next.midboss;}
        else if(sixth) {const auto next=th04::portable::stage6::prepare(boss,mid,rank);next_boss=next.boss;next_mid=next.midboss;}
        else {const auto next=s::prepare(boss,mid,rank);next_boss=next.boss;next_mid=next.midboss;centers=next.centers;}
        print_boss(next_boss);Bytes v;motion(v,next_mid.position);word(v,next_mid.start_frame);word(v,next_mid.hp);v.push_back(next_mid.sprite);v.push_back(next_mid.phase);word(v,next_mid.phase_frame);v.push_back(next_mid.damaged);v.push_back(next_mid.unused_angle);hex(v);
        std::cout<<next_mid.active<<' '<<next_mid.hp_bar<<' '<<+next_mid.pattern_angle<<' '<<next_boss.hitbox_radius.x<<' '<<next_boss.hitbox_radius.y<<' '<<+next_boss.timed_out;
        if(!sixth && !extra) for(auto c:centers) { std::cout<<' '<<c; }
        std::cout<<'\n';
    }
}
void star_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read star fixtures");unsigned phase;
    while(in>>phase) {
        const int line=number(in);const bool scrolling=number(in)!=0;s::Stars stars;for(auto& c:stars.centers)c=m::wrap(number(in));
        const auto draws=stars.update(static_cast<std::uint8_t>(phase),line,scrolling);
        for(auto c:stars.centers) { std::cout<<c<<' '; }
        std::cout<<draws.size();for(auto d:draws) std::cout<<' '<<d.left<<' '<<d.physical_top;
        for(auto r:stars.invalidations()) { std::cout<<' '<<r.center.x<<' '<<r.center.y<<' '<<r.width<<' '<<r.height; }
        std::cout<<'\n';
    }
}
void pixels(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read star pixel fixtures");std::string file;int left,top;unsigned display,seed;
    while(in>>file>>left>>top>>display>>seed) {
        std::ifstream f(file,std::ios::binary);require(bool(f),"cannot read star CDG");const Bytes raw{std::istreambuf_iterator<char>(f),{}};s::StarPlane plane(raw);
        Bytes indices(640*400);for(unsigned i=0;i<indices.size();++i)indices[i]=static_cast<std::uint8_t>((i*73+seed)&15);
        const auto initial=indices;
        plane.raster(left,top,display,[&](unsigned x,unsigned y){return indices[y*640+x];},[&](unsigned x,unsigned y,std::uint8_t c){indices[y*640+x]=c;});
        Bytes packed(32000);
        for(unsigned i=0;i<indices.size();++i) {
            require((indices[i]&7)==(initial[i]&7) && (indices[i]|initial[i])==indices[i],"star OR changed retained colors");
            if(indices[i]&8)packed[i/8]|=static_cast<std::uint8_t>(0x80u>>(i%8));
        }
        std::cout.write(reinterpret_cast<const char*>(packed.data()),static_cast<std::streamsize>(packed.size()));
    }
}
}
int main(int argc,char** argv) {
 try {
    if(argc==3) {
        const std::string op=argv[1];if(op=="--setup-vectors")setup_vectors(argv[2]);else if(op=="--extra-setup-vectors")setup_vectors(argv[2],false,true);else if(op=="--stage6-setup-vectors")setup_vectors(argv[2],true);else if(op=="--star-vectors")star_vectors(argv[2]);else if(op=="--pixel-vectors") {
#ifdef _WIN32
            require(_setmode(_fileno(stdout),_O_BINARY)!=-1,"cannot set binary star stream");
#endif
            pixels(argv[2]);
        } else throw std::runtime_error("unknown Stage5 contract option");return 0;
    }
    require(argc==1,"Stage5 contracts take a mode and fixture path");s::Stars stars;const auto before=stars.centers;
    require(stars.update(1,399,true).empty() && stars.centers==before,"battle phase advanced stars");
    require(stars.update(0,399,true).size()==3,"ordinary phase failed to draw stars");
    o::Snapshot boss;boss.hp=123;boss.additional[7]=99;mb::Snapshot mid;mid.hp=1200;mid.phase=7;mid.active=true;
    const auto next=s::prepare(boss,mid,3);require(next.boss.hp==123 && next.boss.additional[7]==99 && next.boss.additional[0]==180 && !next.midboss.active && next.midboss.hp==0 && next.midboss.phase==7 && next.midboss.start_frame==60000,"Stage5 retained setup");
    const auto final=th04::portable::stage6::prepare(next.boss,next.midboss,3);
    require(final.boss.hp==123 && final.boss.additional[7]==99 && final.boss.additional[0]==96 && final.boss.additional[1]==4 && final.boss.position.current.y==1280 && final.boss.hitbox_radius.y==768 && final.midboss.phase==7 && !final.midboss.active && final.midboss.start_frame==60000,"Stage6 retained setup");
    std::cout<<"Stage5 retained setup and star ownership: PASS\n";return 0;
 } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
