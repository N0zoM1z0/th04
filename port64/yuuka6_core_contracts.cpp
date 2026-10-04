#include "yuuka6.hpp"
#include "yuuka6_entities.hpp"
#include "thick_lasers.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
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
b::Template shot(Wire& w) {
    b::Template t;t.spawn_type=w.byte();t.pattern=w.byte();t.origin=w.point();t.velocity=w.point();
    t.group=w.byte();t.angle=w.byte();t.speed=w.byte();t.count=w.byte();t.delta=w.byte();t.unused_1=w.byte();t.special_motion=w.byte();t.unused_2=w.byte();return t;
}
void shot(Bytes& v,const b::Template& t) {
    v.push_back(t.spawn_type);v.push_back(t.pattern);point(v,t.origin);point(v,t.velocity);
    for(auto n:{t.group,t.angle,t.speed,t.count,t.delta,t.unused_1,t.special_motion,t.unused_2}) v.push_back(n);
}
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
g::Template shape(Wire& w) { g::Template s;s.center=w.point();s.velocity=w.point();s.radius=m::wrap(w.word());s.ring_points=m::wrap(w.word());s.color=w.byte();s.angle_delta=w.byte();return s; }
void shape(Bytes& v,const g::Template& s) { point(v,s.center);point(v,s.velocity);word(v,s.radius);word(v,s.ring_points);v.push_back(s.color);v.push_back(s.angle_delta); }
g::Entity gather(Wire& w) {
    g::Entity q;q.flag=w.byte();q.color=w.byte();q.center=w.movement();q.radius=m::wrap(w.word());q.ring_points=m::wrap(w.word());q.angle=w.byte();q.angle_delta=w.byte();q.bullet=shot(w);q.previous_radius=m::wrap(w.word());q.radius_delta=m::wrap(w.word());return q;
}
void gather(Bytes& v,const g::Entity& q) {
    v.push_back(q.flag);v.push_back(q.color);movement(v,q.center);word(v,q.radius);word(v,q.ring_points);v.push_back(q.angle);v.push_back(q.angle_delta);shot(v,q.bullet);word(v,q.previous_radius);word(v,q.radius_delta);
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
void print(const y::System& system,const b::System& bullets,const g::System& gathers,
           const l::System& lasers,const y::Entities& entities,const th04::portable::spark::System& sparks,bool returned,
           const th04::portable::randring::SharedRandomRing& random,
           const std::vector<th04::portable::orange::Event>& events) {
    const auto& s=system.snapshot();Bytes v;boss(v,s);hex(v);hex(Bytes(s.boss.additional.begin(),s.boss.additional.end()));
    std::cout << +s.boss.circle_color << ' ' << +lasers.snapshot().player_hit << ' ' << random.cursor() << ' ';
    const auto& bs=bullets.snapshot();std::cout << +bs.clear_time << ' ' << +bs.zap_frame << ' ' << +bs.special_parameter << ' ' << +bs.special_angle << ' ';
    v.clear();shot(v,bs.scratch);hex(v);v.clear();
    for(const auto& q:bs.entities) {
        v.push_back(q.flag);v.push_back(q.age);movement(v,q.position);
        for(auto n:{q.group,q.unused,q.speed,q.angle,static_cast<std::uint8_t>(q.phase),static_cast<std::uint8_t>(q.movement),q.special,q.final_speed,q.timer_or_turns,q.delta_or_angle}) v.push_back(n);
        word(v,q.pattern);
    }
    hex(v);v.clear();shape(v,gathers.snapshot().scratch);hex(v);v.clear();for(const auto& q:gathers.snapshot().entities) gather(v,q);hex(v);v.clear();
    beam(v,lasers.snapshot().scratch);for(const auto& q:lasers.snapshot().beams) beam(v,q);hex(v);v.clear();for(const auto& q:entities.snapshot().slots) custom(v,q);hex(v);
    const auto& q=s.boss;
    for(auto n:{int(s.mirror_damage),int(s.pattern_previous),int(s.stage_vm_disabled),int(s.midboss_frames_until),int(q.timed_out),int(q.palette_changed),int(q.tile_column),int(q.invincibility),int(q.background),int(q.shake_x),int(q.shake_y),int(q.slowdown),int(q.bombing_disabled),int(q.point_times_two),int(q.big_frame),int(q.palette_tone)}) std::cout << n << ' ';
    std::cout << q.score_delta << ' ' << q.homing.x << ' ' << q.homing.y << ' ' << s.shot_center.x << ' ' << s.shot_center.y << ' ' << s.shot_radius.x << ' ' << s.shot_radius.y << ' ';
    for(auto n:q.palette_zero) std::cout << +n << ' ';
    v.clear();const auto exp=[&](const th04::portable::orange::Explosion& e) { v.push_back(e.alive);v.push_back(e.age);point(v,e.center);point(v,e.radius);point(v,e.delta);v.push_back(static_cast<std::uint8_t>(e.unused));v.push_back(e.angle_offset); };
    for(const auto& e:q.small) exp(e);
    exp(q.big);hex(v);v.clear();
    for(const auto& e:sparks.snapshot().entities) { v.push_back(e.flag);v.push_back(e.age);movement(v,e.center);word(v,e.angle); }
    hex(v);std::cout << sparks.snapshot().ring_offset << ' ' << returned << ' ';
    std::cout << events.size();for(const auto& e:events) std::cout << ' ' << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count;std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Yuuka6 core fixtures");char op;
    while(in>>op) {
        unsigned score=0;int power=0,damage=0,ordinary=0,previous=0,mirror_damage=0,vm=0,midboss=0,timed=0,tone=0;
        int steps=0,selector=0,rank=0,perf=0,frame=0,density=0,cursor=0,hit=0,clear=0,zap=0,px=0,py=0;std::string raw,additional,scratch,shapehex,gathershex,lasershex,customhex;
        require(bool(in>>steps>>selector>>rank>>perf>>frame>>density>>cursor>>hit>>clear>>zap>>px>>py>>raw>>additional>>scratch>>shapehex>>gathershex>>lasershex>>customhex>>power>>damage>>ordinary>>previous>>mirror_damage>>vm>>midboss>>score>>timed>>tone),"short core fixture");
        require((op=='M' || op=='N' || op=='U' || op=='S') && steps>0 && steps<=20000,"invalid attack operation/steps");
        require(selector>=0 && selector<=65535 && rank>=0 && rank<=4 && perf>=0 && perf<=255,"invalid attack selector/rank");
        require(px>=-32768 && px<=32767 && py>=-32768 && py<=32767,"invalid player coordinates");
        require(frame>=0 && frame<=65535 && density>=0 && density<=2 && cursor>=0 && cursor<=255 && hit>=0 && hit<=255 && clear>=0 && clear<=255 && zap>=0 && zap<=255,"invalid attack context");
        auto bw=read(raw,35);auto initial=boss(bw);initial.boss.circle_color=13;auto aw=read(additional,16);for(auto& n:initial.boss.additional) n=aw.byte();initial.mirror_damage=mirror_damage;initial.pattern_previous=previous;initial.stage_vm_disabled=vm;initial.midboss_frames_until=m::wrap(midboss);initial.shot_center={111,222};initial.shot_radius={333,444};
        auto& z=initial.boss;z.homing={111,222};z.hitbox_radius={384,768};z.timed_out=timed;z.palette_zero={17,29,41};z.tile_column=7;z.invincibility=77;z.shake_x=17;z.shake_y=-19;z.slowdown=3;z.point_times_two=1;z.score_delta=score;z.palette_tone=m::wrap(tone);z.small[0].unused=-7;z.small[1].unused=19;z.big.unused=61;y::System system(initial);
        b::Snapshot bs;auto tw=read(scratch,18);bs.scratch=shot(tw);bs.clear_time=clear;bs.zap_frame=zap;
        for(unsigned i=0;i<bs.entities.size();++i) bs.entities[i].flag=static_cast<std::uint8_t>(density==1 || (density==2 && i%2));
        g::Snapshot gs;auto gw=read(shapehex,14);gs.scratch=shape(gw);gw=read(gathershex,672);for(auto& q:gs.entities) q=gather(gw);
        l::Snapshot ls;auto lw=read(lasershex,72);ls.scratch=beam(lw);for(auto& q:ls.beams) q=beam(lw);ls.player_hit=hit;
        y::EntitySnapshot es;auto ew=read(customhex,832);for(auto& q:es.slots) q=custom(ew);
        b::System bullets(bs);g::System gathers(gs);l::System lasers(ls);y::Entities entities(es);th04::portable::spark::System sparks;
        th04::portable::randring::SharedRandomRing random;unsigned draw=0;random.fill([&]{return static_cast<std::uint8_t>(draw++*73u+19u);});for(int i=0;i<cursor;++i) random.next16();
        y::Context c;c.power=power;c.hit=[&](m::Point,m::Point){return static_cast<std::uint16_t>(damage);};c.ordinary_hit=[&](m::Point,m::Point){return static_cast<std::uint16_t>(ordinary);};c.frame=frame;c.bullets.rank=rank;c.bullets.performance=perf;c.bullets.player={m::wrap(px),m::wrap(py)};
        for(int i=0;i<steps;++i) {
            std::vector<th04::portable::orange::Event> events;auto sink=[&](const th04::portable::orange::Event& e){events.push_back(e);};c.bullets.frame_mod2=c.frame%2;
            bool returned=false;
            if(op=='M') returned=system.mirror_hittest(c,sink);
            else if(op=='N') system.phase_next(selector,m::wrap(damage),bullets,sink);
            else system.update(c,bullets,gathers,sparks,lasers,entities,random,sink);
            print(system,bullets,gathers,lasers,entities,sparks,returned,random,events);
            if(op=='S' && system.snapshot().boss.phase==254) break;
            ++c.frame;
        }
    }
}
void contracts() {
    y::Snapshot s;s.mirror_state=2;s.boss.hp=2;s.mirror={2048,1280};y::System system(s);y::Context c;
    c.ordinary_hit=[](m::Point,m::Point){return std::uint16_t{257};};
    require(!system.mirror_hittest(c) && system.snapshot().boss.hp==1,"mirror damage did not truncate to BYTE");
    require(system.snapshot().shot_radius.y==768,"mirror hitbox height differs");
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        require(argc==1,"usage: Yuuka6 core contracts [--vectors FILE]");contracts();std::cout << "Stage 6 Yuuka core contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr << "Yuuka6 cores: " << e.what() << '\n';return 1; }
}
