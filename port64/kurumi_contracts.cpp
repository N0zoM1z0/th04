#include "kurumi.hpp"
#include "player_motion.hpp"
#include <algorithm>
namespace k=th04::portable::kurumi;
#include "circles.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
namespace o=th04::portable::orange;
namespace b=th04::portable::bullet;
namespace g=th04::portable::gather;
namespace sp=th04::portable::spark;
namespace m=th04::portable::motion;
namespace r=th04::portable::randring;
namespace ci=th04::portable::circle;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool condition,const char* why) { if (!condition) throw std::runtime_error(why); }
int number(std::istream& in) { int n=0;require(bool(in>>n),"short Orange fixture");return n; }
void word(Bytes& v,unsigned x) { v.push_back(static_cast<std::uint8_t>(x));v.push_back(static_cast<std::uint8_t>(x>>8)); }
void point(Bytes& v,m::Point p) { word(v,static_cast<std::uint16_t>(p.x));word(v,static_cast<std::uint16_t>(p.y)); }
void motion(Bytes& v,const m::Motion& p) { point(v,p.current);point(v,p.previous);point(v,p.velocity); }
void shot(Bytes& v,const b::Template& t) {
    v.push_back(t.spawn_type);v.push_back(t.pattern);point(v,t.origin);point(v,t.velocity);
    for (auto n:{t.group,t.angle,t.speed,t.count,t.delta,t.unused_1,t.special_motion,t.unused_2}) v.push_back(n);
}
void explosion(Bytes& v,const o::Explosion& e) {
    v.push_back(e.alive);v.push_back(e.age);point(v,e.center);point(v,e.radius);point(v,e.delta);
    v.push_back(static_cast<std::uint8_t>(e.unused));v.push_back(e.angle_offset);
}
void hex(const Bytes& v) {
    constexpr char digits[]="0123456789abcdef";
    for (auto n:v) std::cout << digits[n>>4] << digits[n&15];
    std::cout << ' ';
}
struct Wire {
    Bytes bytes;unsigned at=0;
    unsigned byte() { return bytes.at(at++); }
    unsigned word() { const auto lo=byte(),hi=byte();return lo|(hi<<8); }
    m::Point point() { const auto x=m::wrap(word()),y=m::wrap(word());return {x,y}; }
};
o::Snapshot read(std::istream& in) {
    Wire w;for (unsigned i=0;i<24;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
    o::Snapshot s;s.position.current=w.point();s.position.previous=w.point();s.position.velocity=w.point();
    s.hp=m::wrap(w.word());s.sprite=static_cast<std::uint8_t>(w.byte());s.phase=static_cast<std::uint8_t>(w.byte());
    s.phase_frame=m::wrap(w.word());s.damage=static_cast<std::uint8_t>(w.byte());s.mode=static_cast<std::uint8_t>(w.byte());
    s.angle=static_cast<std::uint8_t>(w.byte());s.patterns_or_bonus=static_cast<std::uint8_t>(w.byte());s.end_hp=m::wrap(w.word());
    for (auto& x:s.additional) x=static_cast<std::uint8_t>(number(in));
    s.hitbox_radius={384,384};s.homing={111,222};s.palette_zero={17,29,41};s.circle_color=13;s.tile_column=7;s.invincibility=77;
    s.shake_x=17;s.shake_y=-19;s.slowdown=3;s.point_times_two=1;
    s.small[0].unused=-7;s.small[1].unused=19;s.big.unused=61;return s;
}
void print(const k::System& system,const b::System& bullets,const g::System& gathers,
           const sp::System& sparks,const r::SharedRandomRing& random,const std::vector<o::Event>& events) {
    const auto& s=system.snapshot().boss;Bytes v;motion(v,s.position);word(v,static_cast<std::uint16_t>(s.hp));
    v.push_back(s.sprite);v.push_back(s.phase);word(v,static_cast<std::uint16_t>(s.phase_frame));
    for (auto n:{s.damage,s.mode,s.angle,s.patterns_or_bonus}) v.push_back(n);
    word(v,static_cast<std::uint16_t>(s.end_hp));hex(v);hex(Bytes(s.additional.begin(),s.additional.end()));
    std::cout << s.hitbox_radius.x << ' ' << s.hitbox_radius.y << ' ' << s.homing.x << ' ' << s.homing.y << ' ' << +s.timed_out << ' ';
    for (auto n:s.palette_zero) std::cout << +n << ' ';
    std::cout << +s.palette_changed << ' ' << +s.circle_color << ' ' << +s.tile_column << ' ' << +s.invincibility << ' ' << int(s.background) << ' ' << s.shake_x << ' ' << s.shake_y << ' ' << s.slowdown << ' ' << +s.bombing_disabled << ' ' << +s.point_times_two << ' ' << s.score_delta << ' ' << random.cursor() << ' ' << +bullets.snapshot().clear_time << ' ' << +bullets.snapshot().zap_frame << ' ';
    v.clear();shot(v,bullets.snapshot().scratch);hex(v);v.clear();
    for (const auto& e:bullets.snapshot().entities) {
        v.push_back(e.flag);v.push_back(e.age);motion(v,e.position);
        for (auto n:{e.group,e.unused,e.speed,e.angle,static_cast<std::uint8_t>(e.phase),static_cast<std::uint8_t>(e.movement),e.special,e.final_speed,e.timer_or_turns,e.delta_or_angle}) v.push_back(n);
        word(v,e.pattern);
    }
    hex(v);v.clear();const auto& shape=gathers.snapshot().scratch;
    point(v,shape.center);point(v,shape.velocity);word(v,static_cast<std::uint16_t>(shape.radius));word(v,static_cast<std::uint16_t>(shape.ring_points));v.push_back(shape.color);v.push_back(shape.angle_delta);hex(v);v.clear();
    for (const auto& e:gathers.snapshot().entities) {
        v.push_back(e.flag);v.push_back(e.color);motion(v,e.center);word(v,static_cast<std::uint16_t>(e.radius));word(v,static_cast<std::uint16_t>(e.ring_points));
        v.push_back(e.angle);v.push_back(e.angle_delta);shot(v,e.bullet);word(v,static_cast<std::uint16_t>(e.previous_radius));word(v,static_cast<std::uint16_t>(e.radius_delta));
    }
    hex(v);v.clear();
    for (const auto& e:sparks.snapshot().entities) { v.push_back(e.flag);v.push_back(e.age);motion(v,e.center);word(v,e.angle); }
    hex(v);std::cout << sparks.snapshot().ring_offset << ' ';v.clear();
    for (const auto& e:s.small) explosion(v,e);
    explosion(v,s.big);hex(v);
    v.clear();
    for(const auto& ray:system.snapshot().rays) {
        v.push_back(ray.flag);v.push_back(ray.unused);point(v,ray.target);point(v,ray.origin);point(v,ray.velocity);
        v.insert(v.end(),ray.padding.begin(),ray.padding.end());
    }
    hex(v);std::cout<<+system.snapshot().turn_toggle<<' '<<+system.snapshot().unknown_state<<' '<<+bullets.snapshot().special_parameter<<' '<<+bullets.snapshot().special_angle<<' ';
    std::cout << events.size() << ' ';
    for (const auto& e:events) std::cout << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
    std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Kurumi fixtures");char op;
    while(in>>op) {
        const unsigned steps=static_cast<unsigned>(number(in));k::Context c;
        c.bullets.rank=static_cast<std::uint8_t>(number(in));c.bullets.performance=static_cast<std::uint8_t>(number(in));
        c.bullets.player={3072,5120};c.frame=static_cast<std::uint16_t>(number(in));c.power=static_cast<std::uint8_t>(number(in));
        const auto damage=number(in),density=number(in),timed_out=number(in);k::Snapshot initial;
        initial.boss=read(in);initial.boss.timed_out=static_cast<std::uint8_t>(timed_out);
        initial.turn_toggle=static_cast<std::uint8_t>(number(in));initial.unknown_state=static_cast<std::uint8_t>(number(in));
        for(auto& ray:initial.rays) {
            Wire w;for(unsigned i=0;i<26;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
            ray.flag=static_cast<std::uint8_t>(w.byte());ray.unused=static_cast<std::uint8_t>(w.byte());
            ray.target=w.point();ray.origin=w.point();ray.velocity=w.point();for(auto& v:ray.padding) v=static_cast<std::uint8_t>(w.byte());
        }
        c.hit=[damage](m::Point,m::Point) { return static_cast<std::uint16_t>(damage); };
        b::Snapshot bs;bs.scratch={1,52,{2048,1024},{17,-19},46,129,42,3,6,123,128,19};
        g::Snapshot gs;gs.scratch={{2048,1024},{17,-19},1024,8,13,129};sp::Snapshot ss;
        if(density) {
            for(unsigned i=0;i<bs.entities.size();++i) bs.entities[i].flag=static_cast<std::uint8_t>(density==1 || (i&1));
            for(unsigned i=0;i<gs.entities.size();++i) gs.entities[i].flag=static_cast<std::uint8_t>(density==1 || (i&1));
            for(unsigned i=0;i<ss.entities.size();++i) ss.entities[i].flag=static_cast<std::uint8_t>(density==1 || (i&1));
        }
        b::System bullets(bs);g::System gathers(gs);sp::System sparks(ss);r::SharedRandomRing random;k::System system(initial);
        unsigned index=0;random.fill([&] { return static_cast<std::uint8_t>(index++*73+19); });
        for(unsigned step=0;step<steps;++step) {
            std::vector<o::Event> events;system.update(c,bullets,gathers,sparks,random,[&](const o::Event& e){events.push_back(e);});
            print(system,bullets,gathers,sparks,random,events);++c.frame;
            if(op=='S' && std::any_of(events.begin(),events.end(),[](const o::Event& e){return e.type==o::EventType::next_stage;})) break;
        }
    }
}
void render_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Kurumi render fixtures");int frame;
    while(in>>frame) {
        const auto big_frame=m::wrap(number(in)),tone=m::wrap(number(in));const auto changed=number(in);
        k::Snapshot initial;initial.boss=read(in);auto& s=initial.boss;
        s.big_frame=big_frame;s.palette_tone=tone;s.palette_changed=static_cast<std::uint8_t>(changed);
        for(auto* e:{&s.small[0],&s.small[1],&s.big}) {
            Wire w;for(unsigned i=0;i<16;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
            e->alive=static_cast<std::uint8_t>(w.byte());e->age=static_cast<std::uint8_t>(w.byte());
            e->center=w.point();e->radius=w.point();e->delta=w.point();
            e->unused=static_cast<std::int8_t>(w.byte());e->angle_offset=static_cast<std::uint8_t>(w.byte());
        }
        for(auto& ray:initial.rays) {
            Wire w;for(unsigned i=0;i<26;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
            ray.flag=static_cast<std::uint8_t>(w.byte());ray.unused=static_cast<std::uint8_t>(w.byte());
            ray.target=w.point();ray.origin=w.point();ray.velocity=w.point();
            for(auto& x:ray.padding) x=static_cast<std::uint8_t>(w.byte());
        }
        k::System system(initial);system.prepare_render(static_cast<std::uint16_t>(frame));const auto& state=system.snapshot();
        Bytes bytes;for(const auto& e:state.boss.small) explosion(bytes,e);explosion(bytes,state.boss.big);hex(bytes);
        std::cout<<state.boss.big_frame<<' '<<state.boss.palette_tone<<' '<<+state.boss.palette_changed<<' '<<+state.boss.damage<<' ';
        bytes.clear();for(const auto& ray:state.rays) {
            bytes.push_back(ray.flag);bytes.push_back(ray.unused);point(bytes,ray.target);point(bytes,ray.origin);point(bytes,ray.velocity);
            bytes.insert(bytes.end(),ray.padding.begin(),ray.padding.end());
        }
        hex(bytes);std::cout<<system.draws().size()<<' ';
        for(const auto& d:system.draws()) std::cout<<int(d.kind)<<' '<<d.left<<' '<<d.top<<' '<<d.pattern_or_radius<<' '<<+d.color<<' '<<d.end_left<<' '<<d.end_top<<' ';
        std::cout<<'\n';
    }
}
void background_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Kurumi background fixtures");int phase;
    while(in>>phase) {
        o::Snapshot s;s.phase=static_cast<std::uint8_t>(phase);s.phase_frame=m::wrap(number(in));const auto plan=k::backdrop(s);
        const auto event=[](int kind,int x=0,int y=0,int value=0) { std::cout<<kind<<' '<<x<<' '<<y<<' '<<value<<' '; };
        if(plan.kind==k::BackdropKind::all_tiles) { std::cout<<1<<' ';event(0); }
        else if(plan.kind==k::BackdropKind::dirty_tiles) { std::cout<<1<<' ';event(1); }
        else if(plan.kind==k::BackdropKind::picture) { std::cout<<1<<' ';event(2,32,96,0); }
        else { std::cout<<3<<' ';event(2,32,96,0);event(3,plan.mask_cel);event(4); }
        std::cout<<'\n';
    }
}
void line_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Kurumi line fixtures");int x;
    while(in>>x) {
        const auto y=m::wrap(number(in)),end_x=m::wrap(number(in)),end_y=m::wrap(number(in));Bytes bits(32000);
        for(auto pixel:k::ray_pixels({m::wrap(x),y},{end_x,end_y})) bits[unsigned(pixel.y)*80+unsigned(pixel.x)/8]|=static_cast<std::uint8_t>(0x80u>>(pixel.x&7));
        hex(bits);std::cout<<'\n';
    }
}

void setup_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open retained Kurumi setup fixtures");int rank;
    while(in>>rank) {
        auto previous=read(in);
        for(auto* e:{&previous.small[0],&previous.small[1],&previous.big}) {
            Wire w;for(unsigned i=0;i<16;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
            e->alive=static_cast<std::uint8_t>(w.byte());e->age=static_cast<std::uint8_t>(w.byte());
            e->center=w.point();e->radius=w.point();e->delta=w.point();
            const auto unused=w.byte();e->unused=static_cast<std::int8_t>(unused<128 ? int(unused) : int(unused)-256);
            e->angle_offset=static_cast<std::uint8_t>(w.byte());
        }
        const auto state=k::prepare_stage2(previous,unsigned(rank));const auto& s=state.boss;Bytes v;
        motion(v,s.position);word(v,static_cast<std::uint16_t>(s.hp));v.push_back(s.sprite);v.push_back(s.phase);
        word(v,static_cast<std::uint16_t>(s.phase_frame));for(auto n:{s.damage,s.mode,s.angle,s.patterns_or_bonus}) v.push_back(n);
        word(v,static_cast<std::uint16_t>(s.end_hp));hex(v);hex(Bytes(s.additional.begin(),s.additional.end()));
        v.clear();for(const auto& e:s.small) explosion(v,e);explosion(v,s.big);hex(v);
        std::cout<<s.hitbox_radius.x<<' '<<s.hitbox_radius.y<<' '<<+s.timed_out<<'\n';
    }
}

}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--setup-vectors") { setup_vectors(argv[2]);return 0; }
        if(argc==2 && std::string(argv[1])=="--invincibility-vectors") {
            for(unsigned i=0;i<256;++i) std::cout<<+th04::portable::player::invincibility_after_tick(static_cast<std::uint8_t>(i))<<'\n';
            return 0;
        }
        if(argc==2 && std::string(argv[1])=="--setup") {
            for(unsigned rank=0;rank<4;++rank) {
                k::System system(rank);const auto& s=system.snapshot().boss;Bytes v;
                motion(v,s.position);word(v,static_cast<std::uint16_t>(s.hp));v.push_back(s.sprite);v.push_back(s.phase);
                word(v,static_cast<std::uint16_t>(s.phase_frame));for(auto n:{s.damage,s.mode,s.angle,s.patterns_or_bonus}) v.push_back(n);
                word(v,static_cast<std::uint16_t>(s.end_hp));hex(v);
                std::cout<<s.hitbox_radius.x<<' '<<s.hitbox_radius.y<<' '<<+s.additional[0]<<'\n';
            }
            return 0;
        }
        if(argc==3 && std::string(argv[1])=="--render-vectors") { render_vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--background-vectors") { background_vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--line-vectors") { line_vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        require(argc==1,"usage: th04-port64-kurumi-contracts [--vectors FILE]");
        for(unsigned rank=0;rank<4;++rank) {
            k::System system(rank);b::System bullets;g::System gathers;sp::System sparks;r::SharedRandomRing random;k::Context c;
            c.bullets.rank=static_cast<std::uint8_t>(rank);c.bullets.player={3072,5120};
            for(unsigned i=0;i<352;++i) { system.update(c,bullets,gathers,sparks,random);++c.frame; }
            require(system.snapshot().boss.phase==2 && system.snapshot().boss.hp==4800,"Kurumi invulnerable entry differs");
        }
        try { k::System invalid(4);throw std::logic_error("Extra incorrectly accepted Kurumi setup"); }
        catch(const std::invalid_argument&) {}
        k::Snapshot bad_period;bad_period.boss.phase=5;bad_period.boss.mode=1;bad_period.boss.phase_frame=16;
        k::System invalid_period(bad_period);b::System bullets;g::System gathers;sp::System sparks;r::SharedRandomRing random;k::Context c;
        try { invalid_period.update(c,bullets,gathers,sparks,random);throw std::logic_error("zero stack period accepted"); }
        catch(const std::domain_error&) {}
        std::cout<<"Stage 2 Kurumi contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
