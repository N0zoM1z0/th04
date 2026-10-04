#include "yuuka5.hpp"
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
namespace k=th04::portable::yuuka5;
namespace l=th04::portable::laser;
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
int number(std::istream& in) { int n=0;require(bool(in>>n),"short Yuuka fixture");return n; }
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
    s.homing={111,222};s.palette_zero={17,29,41};s.circle_color=13;s.tile_column=7;s.invincibility=77;
    s.shake_x=17;s.shake_y=-19;s.slowdown=3;s.point_times_two=1;
    s.small[0].unused=-7;s.small[1].unused=19;s.big.unused=61;return s;
}
l::Beam read_beam(std::istream& in) {
    Wire w;for(unsigned i=0;i<24;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
    l::Beam q;q.flag=w.byte();q.unused_first=w.byte();q.origin=w.point();
    for(auto& n:q.unused_origin) n=w.byte();
    q.phase_frame=m::wrap(w.word());q.line_frames=m::wrap(w.word());q.static_frames=m::wrap(w.word());
    q.outline=w.byte();q.unused_color=w.byte();q.maximum_radius=m::wrap(w.word());q.radius=m::wrap(w.word());q.radius_speed=m::wrap(w.word());return q;
}
void beam(Bytes& v,const l::Beam& q) {
    v.push_back(q.flag);v.push_back(q.unused_first);point(v,q.origin);v.insert(v.end(),q.unused_origin.begin(),q.unused_origin.end());
    word(v,q.phase_frame);word(v,q.line_frames);word(v,q.static_frames);v.push_back(q.outline);v.push_back(q.unused_color);
    word(v,q.maximum_radius);word(v,q.radius);word(v,q.radius_speed);
}
void print(const k::System& system,const b::System& bullets,const g::System& gathers,
           const sp::System& sparks,const l::System& lasers,const r::SharedRandomRing& random,const std::vector<o::Event>& events,bool returned) {
    const auto& owner=system.snapshot();const auto& s=owner.boss;Bytes v;motion(v,s.position);word(v,static_cast<std::uint16_t>(s.hp));
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
    v.clear();word(v,owner.sweep_x);v.push_back(owner.cloud_step);v.push_back(owner.cloud_accumulator);v.push_back(owner.palette_tone);v.push_back(owner.move_state);hex(v);
    std::cout << s.palette_tone << ' ' << owner.stage_vm_disabled << ' ' << owner.midboss_frames_until << ' ';
    v.clear();beam(v,lasers.snapshot().scratch);for(const auto& q:lasers.snapshot().beams) beam(v,q);hex(v);
    std::cout << +lasers.snapshot().player_hit << ' ' << +bullets.snapshot().special_parameter << ' ' << +bullets.snapshot().special_angle << ' ' << returned << ' ';
    std::cout << events.size() << ' ';
    for (const auto& e:events) std::cout << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
    std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Yuuka fixtures");char op;
    while(in>>op) {
        require(op=='U' || op=='S' || op=='M' || op=='P' || op=='A',"unknown Yuuka operation");
        const auto steps=number(in);require(steps>0 && steps<=20000,"invalid Yuuka step count");o::Context c;
        c.bullets.rank=static_cast<std::uint8_t>(number(in));c.bullets.performance=static_cast<std::uint8_t>(number(in));
        require(c.bullets.rank<=4,"invalid Yuuka rank");c.frame=static_cast<std::uint16_t>(number(in));c.power=static_cast<std::uint8_t>(number(in));
        const auto damage=number(in),density=number(in),timed_out=number(in);require(density>=0 && density<=2,"invalid pool density");
        k::Snapshot initial;initial.boss=read(in);initial.boss.timed_out=static_cast<std::uint8_t>(timed_out);initial.boss.hitbox_radius={416,416};
        initial.sweep_x=m::wrap(number(in));initial.cloud_step=static_cast<std::uint8_t>(number(in));initial.cloud_accumulator=static_cast<std::uint8_t>(number(in));
        initial.palette_tone=static_cast<std::uint8_t>(number(in));initial.move_state=static_cast<std::uint8_t>(number(in));
        initial.stage_vm_disabled=number(in)!=0;initial.midboss_frames_until=m::wrap(number(in));initial.boss.palette_tone=m::wrap(number(in));
        l::Snapshot ls;ls.scratch=read_beam(in);for(auto& q:ls.beams) q=read_beam(in);ls.player_hit=static_cast<std::uint8_t>(number(in));
        c.bullets.player.x=m::wrap(number(in));c.bullets.player.y=m::wrap(number(in));const auto selector=number(in);
        require((op!='P' && op!='A') || (selector>=0 && selector<7),"invalid Yuuka attack");
        c.hit=[damage](m::Point,m::Point) { return static_cast<std::uint16_t>(damage); };
        b::Snapshot bs;bs.scratch={1,52,{2048,1024},{17,-19},46,129,42,3,6,123,128,19};
        g::Snapshot gs;gs.scratch={{2048,1024},{17,-19},1024,8,13,129};sp::Snapshot ss;
        if(density) {
            for(unsigned i=0;i<bs.entities.size();++i) bs.entities[i].flag=static_cast<std::uint8_t>(density==1 || i%2);
            for(unsigned i=0;i<gs.entities.size();++i) gs.entities[i].flag=static_cast<std::uint8_t>(density==1 || i%2);
            for(unsigned i=0;i<ss.entities.size();++i) ss.entities[i].flag=static_cast<std::uint8_t>(density==1 || i%2);
        }
        b::System bullets(bs);g::System gathers(gs);sp::System sparks(ss);l::System lasers(ls);k::System system(initial);r::SharedRandomRing random;
        unsigned index=0;random.fill([&] { return static_cast<std::uint8_t>(index++*73+19); });
        for(int i=0;i<steps;++i) {
            std::vector<o::Event> events;bool returned=false;c.bullets.frame_mod2=static_cast<std::uint8_t>(c.frame%2);
            const auto sink=[&](const o::Event& e) { events.push_back(e); };
            if(op=='M') returned=system.move(static_cast<std::uint16_t>(selector),random);
            else if(op=='P' || op=='A') system.pattern(static_cast<k::Attack>(selector),c,bullets,gathers,lasers,random,sink);
            else system.update(c,bullets,gathers,lasers,random,sink);
            print(system,bullets,gathers,sparks,lasers,random,events,returned);++c.frame;
            bool finished=false;for(const auto& e:events) if(e.type==o::EventType::next_stage) finished=true;
            if(finished && op=='S') break;
            if(op=='A') {
                auto state=system.snapshot();state.boss.phase_frame=m::wrap(int(state.boss.phase_frame)+1);system=k::System(state);
            }
        }
    }
    require(in.eof(),"malformed Yuuka fixture");
}
} // namespace
int main(int argc,char** argv) {
    try {
#ifdef _WIN32
        _setmode(_fileno(stdout),_O_BINARY);
#endif
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        require(argc==1,"unknown Yuuka arguments");
        k::Snapshot state;state.boss.phase=3;state.boss.phase_frame=7;state.move_state=3;
        k::System owner(state);b::System bullets;g::System gathers;l::System lasers;r::SharedRandomRing random;o::Context context;
        unsigned hits=0;context.hit=[&](m::Point,m::Point) { ++hits;return 1; };
        owner.update(context,bullets,gathers,lasers,random);
        require(owner.snapshot().boss.phase==4 && owner.snapshot().move_state==0 && hits==0,"centered move transition");
        bool rejected=false;try { owner.pattern(static_cast<k::Attack>(7),context,bullets,gathers,lasers,random); } catch(const std::invalid_argument&) { rejected=true; }
        require(rejected,"invalid attack accepted");std::cout<<"Stage 5 Yuuka contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
