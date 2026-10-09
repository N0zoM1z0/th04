#include "mugetsu.hpp"
#include "extra_dialog.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
namespace k=th04::portable::mugetsu;
namespace o=th04::portable::orange;
namespace b=th04::portable::bullet;
namespace g=th04::portable::gather;
namespace sp=th04::portable::spark;
namespace m=th04::portable::motion;
namespace r=th04::portable::randring;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool condition,const char* why) { if (!condition) throw std::runtime_error(why); }
int number(std::istream& in) { int n=0;require(bool(in>>n),"short Mugetsu fixture");return n; }
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
void print(const k::System& system,const b::System& bullets,const g::System& gathers,
           const sp::System& sparks,const r::SharedRandomRing& random,const std::vector<o::Event>& events,unsigned returned) {
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
    v.clear();point(v,owner.anchor);word(v,owner.gather_offset);v.push_back(owner.cycle);v.push_back(owner.flash);v.push_back(owner.bomb_invincibility);v.push_back(std::uint8_t(owner.transition));hex(v);
    std::cout << s.palette_tone << ' ' << owner.stage_vm_disabled << ' ' << owner.midboss_frames_until << ' ';
    std::cout << +bullets.snapshot().special_parameter << ' ' << +bullets.snapshot().special_angle << ' ' << returned << ' ';
    std::cout << events.size() << ' ';
    for (const auto& e:events) std::cout << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
    std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read Mugetsu fixtures");char op;
    while(in>>op) {
        const auto steps=number(in);require(steps>0 && steps<=12000,"invalid Mugetsu steps");k::Context c;
        c.bullets.rank=std::uint8_t(number(in));c.bullets.performance=std::uint8_t(number(in));c.frame=std::uint16_t(number(in));c.power=std::uint8_t(number(in));
        const auto damage=number(in),density=number(in),timed=number(in);k::Snapshot initial;initial.boss=read(in);
        initial.boss.timed_out=std::uint8_t(timed);initial.boss.hitbox_radius={384,768};
        initial.anchor={m::wrap(number(in)),m::wrap(number(in))};initial.gather_offset=m::wrap(number(in));
        initial.cycle=std::uint8_t(number(in));initial.flash=std::uint8_t(number(in));initial.bomb_invincibility=std::uint8_t(number(in));
        initial.transition=k::Transition(number(in));initial.stage_vm_disabled=number(in)!=0;initial.midboss_frames_until=m::wrap(number(in));
        initial.boss.palette_tone=m::wrap(number(in));c.bombing=number(in)!=0;const auto selector=number(in);
        c.bullets.player={3072,5120};c.bullets.turbo=c.bullets.rank==4;c.hit=[damage](m::Point,m::Point){return std::uint16_t(damage);};
        b::Snapshot bs;bs.scratch={1,52,{2048,1024},{17,-19},46,129,42,3,6,123,128,19};
        g::Snapshot gs;gs.scratch={{2048,1024},{17,-19},1024,8,13,129};sp::Snapshot ss;
        if(density) {
            for(unsigned i=0;i<bs.entities.size();++i)bs.entities[i].flag=std::uint8_t(density==1 || i%2);
            for(unsigned i=0;i<gs.entities.size();++i)gs.entities[i].flag=std::uint8_t(density==1 || i%2);
            for(unsigned i=0;i<ss.entities.size();++i)ss.entities[i].flag=std::uint8_t(density==1 || i%2);
        }
        b::System bullets(bs);g::System gathers(gs);sp::System sparks(ss);k::System owner(initial);r::SharedRandomRing random;
        unsigned index=0;random.fill([&]{return std::uint8_t(index++*73+19);});
        for(int tick=0;tick<steps;++tick) {
            std::vector<o::Event> events;const auto sink=[&](const o::Event& e){events.push_back(e);};unsigned returned=0;
            c.bullets.frame_mod2=std::uint8_t(c.frame%2);
            if(op=='T')returned=owner.transition(c,bullets,gathers,sink);
            else if(op=='P' || op=='A')owner.pattern(k::Attack(selector),c,bullets,gathers,random,sink);
            else owner.update(c,bullets,gathers,random,sink);
            print(owner,bullets,gathers,sparks,random,events,returned);++c.frame;
            if(op=='S' && owner.snapshot().boss.phase==255)break;
            if(op=='A'){auto q=owner.snapshot();q.boss.phase_frame=m::wrap(int(q.boss.phase_frame)+1);owner=k::System(q);}
        }
    }
    require(in.eof(),"malformed Mugetsu fixture");
}
void graphics_vectors(const char* path,bool background) {
    std::ifstream in(path);require(bool(in),"cannot read Mugetsu graphics fixtures");
    while(in.peek()!=EOF) {
        in>>std::ws;if(in.peek()==EOF)break;
        if(background) {
            const auto phase=std::uint8_t(number(in));const auto clock=m::wrap(number(in));
            const auto draws=k::background(phase,clock);
            std::cout<<draws.size()<<' ';
            for(const auto& d:draws)std::cout<<d.kind<<' '<<d.x<<' '<<d.y<<' '<<d.value<<' ';
            std::cout<<'\n';continue;
        }
        k::Snapshot s;s.boss=read(in);s.flash=std::uint8_t(number(in));s.bomb_invincibility=std::uint8_t(number(in));
        Wire w;for(unsigned i=0;i<48;++i)w.bytes.push_back(std::uint8_t(number(in)));
        for(auto* e:{&s.boss.small[0],&s.boss.small[1],&s.boss.big}) {
            e->alive=std::uint8_t(w.byte());e->age=std::uint8_t(w.byte());e->center=w.point();e->radius=w.point();e->delta=w.point();
            e->unused=static_cast<std::int8_t>(w.byte());e->angle_offset=std::uint8_t(w.byte());
        }
        s.boss.big_frame=m::wrap(number(in));s.boss.palette_tone=m::wrap(number(in));s.boss.palette_changed=std::uint8_t(number(in));
        k::System owner(s);owner.prepare_render();const auto& q=owner.snapshot();const auto& boss=q.boss;
        Bytes v;for(const auto& e:boss.small)explosion(v,e);explosion(v,boss.big);hex(v);
        std::cout<<boss.big_frame<<' '<<boss.palette_tone<<' '<<+boss.palette_changed<<' '<<+boss.damage<<' '<<+q.flash<<' '<<owner.draws().size()<<' ';
        for(const auto& d:owner.draws())std::cout<<int(d.kind)<<' '<<d.left<<' '<<d.top<<' '<<d.pattern_or_radius<<' '<<+d.color<<' ';
        std::cout<<'\n';
    }
    require(in.eof(),"malformed Mugetsu graphics fixture");
}
void resource_vectors(const char* path) {
    std::ifstream in(path);unsigned character,calls;require(bool(in),"cannot read Extra resource fixtures");
    while(in>>character>>calls) {
        th04::portable::extra_dialog::Resources owner{std::uint8_t(calls)};
        auto requests=owner.begin(character);const auto exit=owner.finish(character);requests.insert(requests.end(),exit.begin(),exit.end());
        std::cout<<+owner.calls()<<' '<<requests.size()<<' ';
        for(const auto& e:requests)std::cout<<int(e.kind)<<' '<<e.slot<<' '<<(e.name.empty() ? "-" : e.name)<<' '<<e.image<<' ';
        std::cout<<'\n';
    }
    require(in.eof(),"malformed Extra resource fixture");
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors"){vectors(argv[2]);return 0;}
        if(argc==3 && std::string(argv[1])=="--foreground-vectors"){graphics_vectors(argv[2],false);return 0;}
        if(argc==3 && std::string(argv[1])=="--background-vectors"){graphics_vectors(argv[2],true);return 0;}
        if(argc==3 && std::string(argv[1])=="--resource-vectors"){resource_vectors(argv[2]);return 0;}
        require(argc==1,"Mugetsu contracts take vector options");
        k::Snapshot s;s.boss.position.current={3072,1280};s.boss.sprite=128;s.boss.hitbox_radius={384,768};
        k::System owner(s);b::System bullets;g::System gathers;r::SharedRandomRing random;unsigned index=0;random.fill([&]{return std::uint8_t(index++*73+19);});
        k::Context c;c.bullets.rank=4;c.bullets.turbo=true;c.bullets.performance=16;c.bullets.player={3072,5120};
        unsigned ticks=0;
        for(;ticks<12000 && owner.snapshot().boss.phase!=255;++ticks){c.frame=std::uint16_t(ticks);owner.update(c,bullets,gathers,random);owner.prepare_render();}
        require(owner.snapshot().boss.phase==255 && ticks>6000,"Mugetsu full timeout missed Gengetsu frontier");
        try{owner.update(c,bullets,gathers,random);throw std::runtime_error("Mugetsu used ordinary stage departure at Extra dialog");}
        catch(const std::logic_error&){}
        std::cout<<"Mugetsu full timeout to Gengetsu dialog: PASS ticks="<<ticks<<'\n';return 0;
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
