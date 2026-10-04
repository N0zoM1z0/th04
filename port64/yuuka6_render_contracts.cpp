#include "yuuka6.hpp"
#include "yuuka6_foreground.hpp"
#include "yuuka6_entities.hpp"
#include "thick_lasers.hpp"
#include "sprite_sheet.hpp"
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
namespace y=th04::portable::yuuka6;
namespace m=th04::portable::motion;
namespace b=th04::portable::bullet;
namespace g=th04::portable::gather;
namespace l=th04::portable::laser;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool ok,const char* why) { if(!ok) throw std::runtime_error(why); }
struct Wire {
    Bytes raw;unsigned at=0;
    unsigned byte() { return raw.at(at++); }
    unsigned word() { const auto lo=byte(),hi=byte();return lo|(hi<<8); }
    m::Point point() { const auto x=m::wrap(word()),yy=m::wrap(word());return {x,yy}; }
    m::Motion movement() { m::Motion p;p.current=point();p.previous=point();p.velocity=point();return p; }
};
Wire read(const std::string& hex,unsigned size) {
    require(hex.size()==size*2,"invalid attack wire extent");Wire w;
    const auto nibble=[](char c)->unsigned { if(c>='0' && c<='9') return c-'0';if(c>='a' && c<='f') return c-'a'+10;throw std::runtime_error("invalid attack hex byte"); };
    for(unsigned i=0;i<size;++i) w.raw.push_back((nibble(hex[i*2])<<4)|nibble(hex[i*2+1]));
    return w;
}
void word(Bytes& v,unsigned n) { v.push_back(n&255);v.push_back((n>>8)&255); }
void point(Bytes& v,m::Point p) { word(v,p.x);word(v,p.y); }
void movement(Bytes& v,const m::Motion& p) { point(v,p.current);point(v,p.previous);point(v,p.velocity); }
void hex(const Bytes& v) { constexpr char d[]="0123456789abcdef";for(auto n:v) std::cout << d[n>>4] << d[n&15];std::cout << ' '; }
y::Snapshot boss(Wire& w) {
    y::Snapshot s;auto& q=s.boss;q.position=w.movement();q.hp=m::wrap(w.word());q.sprite=w.byte();q.phase=w.byte();q.phase_frame=m::wrap(w.word());
    q.damage=w.byte();q.mode=w.byte();q.angle=w.byte();q.patterns_or_bonus=w.byte();q.end_hp=m::wrap(w.word());
    s.sprite_flag=w.byte();s.fly_path=w.byte();s.aux_flag=w.byte();s.unused_animation=w.byte();s.animation_frame=m::wrap(w.word());s.mirror=w.point();s.mirror_state=w.byte();return s;
}
void boss(Bytes& v,const y::Snapshot& s) {
    const auto& q=s.boss;movement(v,q.position);word(v,q.hp);v.push_back(q.sprite);v.push_back(q.phase);word(v,q.phase_frame);
    for(auto n:{q.damage,q.mode,q.angle,q.patterns_or_bonus}) v.push_back(n);
    word(v,q.end_hp);for(auto n:{s.sprite_flag,s.fly_path,s.aux_flag,s.unused_animation}) v.push_back(n);
    word(v,s.animation_frame);point(v,s.mirror);v.push_back(s.mirror_state);
}
l::Beam beam(Wire& w) {
    l::Beam q;q.flag=w.byte();q.unused_first=w.byte();q.origin=w.point();for(auto& n:q.unused_origin) n=w.byte();q.phase_frame=m::wrap(w.word());q.line_frames=m::wrap(w.word());q.static_frames=m::wrap(w.word());q.outline=w.byte();q.unused_color=w.byte();q.maximum_radius=m::wrap(w.word());q.radius=m::wrap(w.word());q.radius_speed=m::wrap(w.word());return q;
}
void beam(Bytes& v,const l::Beam& q) {
    v.push_back(q.flag);v.push_back(q.unused_first);point(v,q.origin);v.insert(v.end(),q.unused_origin.begin(),q.unused_origin.end());word(v,q.phase_frame);word(v,q.line_frames);word(v,q.static_frames);v.push_back(q.outline);v.push_back(q.unused_color);word(v,q.maximum_radius);word(v,q.radius);word(v,q.radius_speed);
}
y::EntitySlot custom(Wire& w) {
    y::EntitySlot q;q.flag=w.byte();q.angle=w.byte();q.center=w.point();for(auto& n:q.unused_position) n=w.byte();q.velocity=w.point();q.age=w.word();q.filled_radius=m::wrap(w.word());q.ring_distance=m::wrap(w.word());q.hp=m::wrap(w.word());q.damage=m::wrap(w.word());q.speed=w.byte();q.padding=w.byte();return q;
}
void custom(Bytes& v,const y::EntitySlot& q) {
    v.push_back(q.flag);v.push_back(q.angle);point(v,q.center);v.insert(v.end(),q.unused_position.begin(),q.unused_position.end());point(v,q.velocity);word(v,q.age);word(v,q.filled_radius);word(v,q.ring_distance);word(v,q.hp);word(v,q.damage);v.push_back(q.speed);v.push_back(q.padding);
}
void explosion(Bytes& v,const th04::portable::orange::Explosion& e) {
    v.push_back(e.alive);v.push_back(e.age);point(v,e.center);point(v,e.radius);point(v,e.delta);v.push_back(static_cast<std::uint8_t>(e.unused));v.push_back(e.angle_offset);
}
th04::portable::orange::Explosion explosion(Wire& w) {
    th04::portable::orange::Explosion e;e.alive=w.byte();e.age=w.byte();e.center=w.point();e.radius=w.point();e.delta=w.point();e.unused=static_cast<std::int8_t>(w.byte());e.angle_offset=w.byte();return e;
}
void print(const y::System& system,const y::Foreground& fg,const l::System& lasers,const y::Entities& entities) {
    const auto& s=system.snapshot();const auto& z=s.boss;Bytes raw;boss(raw,s);hex(raw);hex(Bytes(z.additional.begin(),z.additional.end()));
    raw.clear();for(const auto& e:z.small) explosion(raw,e);explosion(raw,z.big);hex(raw);
    raw.clear();beam(raw,lasers.snapshot().scratch);for(const auto& q:lasers.snapshot().beams) beam(raw,q);hex(raw);
    raw.clear();for(const auto& q:entities.snapshot().slots) custom(raw,q);hex(raw);
    std::cout << +fg.state().body_flash << ' ' << +fg.state().mirror_flash << ' ' << +s.mirror_damage << ' ' << z.big_frame << ' ' << z.palette_tone << ' ' << +z.palette_changed << ' ' << +lasers.snapshot().player_hit << ' ';
    std::cout << fg.draws().size();for(const auto& d:fg.draws()) std::cout << ' ' << int(d.kind) << ' ' << d.x << ' ' << d.y << ' ' << d.value << ' ' << d.color << ' ' << d.end_x << ' ' << d.end_y << ' ' << d.mode;std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Yuuka6 foreground fixtures");int steps=0;
    while(in>>steps) {
        int frame=0,bigclock=0,tone=0,changed=0,bodycycle=0,mirrorcycle=0,damage=0,hit=0,rehit=0;
        std::string raw,additional,exp,lasershex,customhex;
        require(bool(in>>frame>>bigclock>>tone>>changed>>bodycycle>>mirrorcycle>>damage>>hit>>rehit>>raw>>additional>>exp>>lasershex>>customhex),"short foreground fixture");
        require(steps>0 && steps<=64 && frame>=0 && frame<=65535 && rehit>=0 && rehit<=1,"invalid foreground execution bounds");
        auto bw=read(raw,35);auto initial=boss(bw);auto aw=read(additional,16);for(auto& n:initial.boss.additional) n=aw.byte();
        initial.mirror_damage=damage;initial.boss.big_frame=m::wrap(bigclock);initial.boss.palette_tone=m::wrap(tone);initial.boss.palette_changed=changed;
        auto ew=read(exp,48);for(auto& e:initial.boss.small) e=explosion(ew);initial.boss.big=explosion(ew);
        l::Snapshot ls;auto lw=read(lasershex,72);ls.scratch=beam(lw);for(auto& q:ls.beams) q=beam(lw);ls.player_hit=hit;
        y::EntitySnapshot es;auto cw=read(customhex,832);for(auto& q:es.slots) q=custom(cw);
        y::System system(initial);y::Foreground fg({static_cast<std::uint8_t>(bodycycle),static_cast<std::uint8_t>(mirrorcycle)});l::System lasers(ls);y::Entities entities(es);
        for(int i=0;i<steps;++i) {
            if(rehit) { auto s=system.snapshot();s.boss.damage=initial.boss.damage;s.mirror_damage=initial.mirror_damage;system=y::System(s); }
            fg.prepare_render(system,static_cast<std::uint16_t>(frame+i),lasers,entities);
            print(system,fg,lasers,entities);
        }
    }
    require(in.eof(),"malformed foreground fixture");
}
void contracts() {
    y::Snapshot s;s.boss.phase=2;s.boss.sprite=128;s.boss.damage=1;s.mirror_state=2;s.mirror_damage=255;
    y::EntitySnapshot es;es.slots[0].flag=16;es.slots.back().flag=1;es.slots.back().filled_radius=8;
    y::System system(s);y::Entities entities(es);l::System lasers;y::Foreground fg({254,255});
    fg.prepare_render(system,0,lasers,entities);
    require(fg.draws().at(0).kind==y::DrawKind::red_sprite && fg.draws().at(2).kind==y::DrawKind::sprite,"independent body/mirror flash differs");
    require(fg.state().body_flash==255 && fg.state().mirror_flash==0,"flash BYTE wrap differs");
    require(system.snapshot().boss.damage==0 && system.snapshot().mirror_damage==0,"visible hit bytes not consumed");
    const auto size=fg.draws().size();fg.draws();fg.draws();require(fg.draws().size()==size && entities.snapshot().slots[0].flag==17,"cached repaint aged a cross");
    s.boss.phase=254;s.boss.damage=19;s.boss.small[0].alive=1;system=y::System(s);
    fg.prepare_render(system,1,lasers,entities);
    require(fg.draws().size()==1 && fg.draws()[0].kind==y::DrawKind::zoom_sprite && system.snapshot().boss.damage==19 && system.snapshot().boss.small[0].age==0 && entities.snapshot().slots[0].flag==17,"death phase advanced an ordinary render owner");
}
void pixels(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Yuuka6 pixel fixtures");
    const std::string fixture_path(path);
    const auto split=fixture_path.find_last_of("/\\");
    const auto directory=split==std::string::npos ? std::string{} : fixture_path.substr(0,split+1);
    std::map<std::string,std::unique_ptr<th04::portable::sprite::Sheet>> sheets;
    unsigned seed=0,count=0;
    while(in>>seed>>count) {
        require(seed<16 && count<=8,"invalid Yuuka6 screen fixture bounds");
        Bytes screen(640*400);
        for(unsigned i=0;i<screen.size();++i) screen[i]=static_cast<std::uint8_t>((i*73+seed)&15);
        for(unsigned i=0;i<count;++i) {
            std::string name;unsigned image=0,kind=0;int x=0,yy=0;
            require(bool(in>>name>>image>>x>>yy>>kind),"short Yuuka6 sprite fixture");
            if(!sheets.count(name)) {
                std::ifstream file(directory+name,std::ios::binary);require(bool(file),"cannot open Yuuka6 sprite asset");
                const Bytes raw{std::istreambuf_iterator<char>(file),{}};
                sheets.emplace(name,std::make_unique<th04::portable::sprite::Sheet>(raw));
            }
            y::raster_sprite(*sheets.at(name),image,m::wrap(x),m::wrap(yy),static_cast<y::DrawKind>(kind),
                [&](int px,int py){return screen[unsigned(py)*640+unsigned(px)];},
                [&](int px,int py,std::uint8_t color){screen[unsigned(py)*640+unsigned(px)]=color;});
        }
        std::cout.write(reinterpret_cast<const char*>(screen.data()),static_cast<std::streamsize>(screen.size()));
    }
    require(in.eof(),"malformed Yuuka6 pixel fixture");
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--pixels") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            pixels(argv[2]);return 0;
        }
        require(argc==1,"usage: Yuuka6 foreground contracts [--vectors FILE]");contracts();std::cout << "Stage 6 Yuuka foreground contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr << "Yuuka6 foreground: " << e.what() << '\n';return 1; }
}
