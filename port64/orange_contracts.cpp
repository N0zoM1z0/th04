#include "orange.hpp"
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
    s.homing={111,222};s.palette_zero={17,29,41};s.circle_color=13;s.tile_column=7;s.invincibility=77;
    s.shake_x=17;s.shake_y=-19;s.slowdown=3;s.point_times_two=1;
    s.small[0].unused=-7;s.small[1].unused=19;s.big.unused=61;return s;
}
void print(const o::System& system,const b::System& bullets,const g::System& gathers,
           const sp::System& sparks,const r::SharedRandomRing& random,const std::vector<o::Event>& events) {
    const auto& s=system.snapshot();Bytes v;motion(v,s.position);word(v,static_cast<std::uint16_t>(s.hp));
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
    std::cout << events.size() << ' ';
    for (const auto& e:events) std::cout << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
    std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Orange fixtures");char op;
    while (in>>op) {
        const unsigned steps=static_cast<unsigned>(number(in));o::Context c;
        c.bullets.rank=static_cast<std::uint8_t>(number(in));c.bullets.performance=static_cast<std::uint8_t>(number(in));
        c.bullets.player={3072,5120};c.frame=static_cast<std::uint16_t>(number(in));c.power=static_cast<std::uint8_t>(number(in));
        const auto damage=number(in),density=number(in),timed_out=number(in);auto initial=read(in);initial.timed_out=static_cast<std::uint8_t>(timed_out);
        c.hit=[damage](m::Point,m::Point) { return static_cast<std::uint16_t>(damage); };
        b::Snapshot bs;bs.scratch={1,52,{2048,1024},{17,-19},46,129,42,3,6,123,128,19};
        g::Snapshot gs;gs.scratch={{2048,1024},{17,-19},1024,8,13,129};
        sp::Snapshot ss;
        if (density) {
            for (unsigned i=0;i<bs.entities.size();++i) bs.entities[i].flag=static_cast<std::uint8_t>(density==1 || i%2);
            for (unsigned i=0;i<gs.entities.size();++i) gs.entities[i].flag=static_cast<std::uint8_t>(density==1 || i%2);
            for (unsigned i=0;i<ss.entities.size();++i) ss.entities[i].flag=static_cast<std::uint8_t>(density==1 || i%2);
        }
        b::System bullets(bs);g::System gathers(gs);sp::System sparks(ss);o::System system(initial);r::SharedRandomRing random;
        unsigned index=0;random.fill([&] { return static_cast<std::uint8_t>(index++*73+19); });
        require(op=='U' || op=='S' || op=='P',"unknown Orange fixture");
        for (unsigned i=0;i<steps;++i) {
            std::vector<o::Event> events;
            system.update(c,bullets,gathers,sparks,random,[&](const o::Event& e) { events.push_back(e); });
            print(system,bullets,gathers,sparks,random,events);++c.frame;
            bool finished=false;
            for (const auto& e:events) if (e.type==o::EventType::next_stage) finished=true;
            if (finished && op=='S') break;
        }
    }
}
void render_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open render fixtures");int frame;
    while (in>>frame) {
        const auto big_frame=m::wrap(number(in)),tone=m::wrap(number(in));const auto changed=number(in);
        auto initial=read(in);initial.big_frame=big_frame;initial.palette_tone=tone;initial.palette_changed=static_cast<std::uint8_t>(changed);
        for (auto* e:{&initial.small[0],&initial.small[1],&initial.big}) {
            Wire w;for (unsigned i=0;i<16;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
            e->alive=static_cast<std::uint8_t>(w.byte());e->age=static_cast<std::uint8_t>(w.byte());
            e->center=w.point();e->radius=w.point();e->delta=w.point();
            const auto unused=w.byte();e->unused=static_cast<std::int8_t>(unused<128 ? int(unused) : int(unused)-256);
            e->angle_offset=static_cast<std::uint8_t>(w.byte());
        }
        o::System system(initial);system.prepare_render(static_cast<std::uint16_t>(frame));const auto& s=system.snapshot();
        Bytes bytes;for (const auto& e:s.small) explosion(bytes,e);explosion(bytes,s.big);hex(bytes);
        std::cout << s.big_frame << ' ' << s.palette_tone << ' ' << +s.palette_changed << ' ' << +s.damage << ' ' << system.draws().size() << ' ';
        for (const auto& d:system.draws()) std::cout << int(d.kind) << ' ' << d.left << ' ' << d.top << ' ' << d.pattern_or_radius << ' ' << +d.color << ' ';
        std::cout << '\n';
    }
}
void circle_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open circle fixtures");char op;
    while (in>>op) {
        const auto x=m::wrap(number(in)),y=m::wrap(number(in)),radius=m::wrap(number(in));
        if (op=='P') {
            Bytes bits(32000);
            for (auto p:ci::raster({x,y},static_cast<std::uint16_t>(radius))) bits[unsigned(p.y)*80+unsigned(p.x)/8]|=static_cast<std::uint8_t>(0x80u>>(p.x&7));
            hex(bits);std::cout << '\n';continue;
        }
        const auto color=number(in),density=number(in),slot=number(in);
        Wire w;for (unsigned i=0;i<10;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
        ci::Entity entity;entity.flag=static_cast<std::uint8_t>(w.byte());entity.age=static_cast<std::uint8_t>(w.byte());entity.center=w.point();entity.radius=m::wrap(w.word());entity.delta=m::wrap(w.word());
        ci::Snapshot initial;initial.color=static_cast<std::uint8_t>(color);
        for (unsigned i=0;i<initial.entities.size();++i) { initial.entities[i]=entity;initial.entities[i].flag=static_cast<std::uint8_t>(density==1 || (density==2 && i%2)); }
        initial.entities.at(unsigned(slot))=entity;ci::System system(initial);
        if (op=='G' || op=='S') system.add({x,y},op=='G');
        else if (op=='U') system.update();
        else require(op=='R',"unknown circle fixture");
        Bytes bytes;for (const auto& e:system.snapshot().entities) {
            bytes.push_back(e.flag);bytes.push_back(e.age);point(bytes,e.center);word(bytes,static_cast<std::uint16_t>(e.radius));word(bytes,static_cast<std::uint16_t>(e.delta));
        }
        hex(bytes);std::cout << +system.snapshot().color << ' ';unsigned count=0;
        if (op=='R') for (const auto& e:system.snapshot().entities) count+=e.flag==1;
        std::cout << count << ' ';
        if (op=='R') for (const auto& e:system.snapshot().entities) if (e.flag==1) std::cout << e.center.x << ' ' << e.center.y << ' ' << static_cast<std::uint16_t>(e.radius) << ' ' << +system.snapshot().color << ' ';
        std::cout << '\n';
    }
}
} // namespace
int main(int argc,char** argv) {
    try {
        if (argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        if (argc==3 && std::string(argv[1])=="--render-vectors") { render_vectors(argv[2]);return 0; }
        if (argc==3 && std::string(argv[1])=="--circle-vectors") { circle_vectors(argv[2]);return 0; }
        o::System s;require(s.snapshot().position.current.x==3072 && s.snapshot().position.current.y==640,"Orange initial center");
        require(s.snapshot().sprite==128 && s.snapshot().hitbox_radius.x==384,"Orange initial sprite/hitbox");
        std::cout << "Stage 1 Orange contracts PASS\n";return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n';return 1; }
}
