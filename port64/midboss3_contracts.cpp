#include "midboss3.hpp"
#include "stage_session.hpp"
#include "stage_background.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
namespace mb3=th04::portable::midboss3;
namespace g=th04::portable::gather;
namespace mb=th04::portable::midboss;
namespace b=th04::portable::bullet;
namespace m=th04::portable::motion;
namespace r=th04::portable::randring;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool ok,const char* why) { if (!ok) throw std::runtime_error(why); }
int number(std::istream& in) { int n=0;require(bool(in>>n),"short midboss fixture");return n; }
struct Wire {
    Bytes bytes;unsigned at=0;
    unsigned byte() { return bytes.at(at++); }
    unsigned word() { const auto low=byte(),high=byte();return low|(high<<8); }
    m::Point point() { const auto x=m::wrap(word()),y=m::wrap(word());return {x,y}; }
};
mb::Snapshot read(std::istream& in) {
    Wire w;for (unsigned i=0;i<22;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
    mb::Snapshot s;s.position.current=w.point();s.position.previous=w.point();s.position.velocity=w.point();
    s.start_frame=static_cast<std::uint16_t>(w.word());s.hp=m::wrap(w.word());s.sprite=static_cast<std::uint8_t>(w.byte());
    s.phase=static_cast<std::uint8_t>(w.byte());s.phase_frame=m::wrap(w.word());s.damaged=static_cast<std::uint8_t>(w.byte());s.unused_angle=static_cast<std::uint8_t>(w.byte());return s;
}
void word(Bytes& bytes,unsigned v) { bytes.push_back(static_cast<std::uint8_t>(v));bytes.push_back(static_cast<std::uint8_t>(v>>8)); }
void point(Bytes& bytes,m::Point p) { word(bytes,static_cast<std::uint16_t>(p.x));word(bytes,static_cast<std::uint16_t>(p.y)); }
Bytes wire(const mb::Snapshot& s) {
    Bytes bytes;point(bytes,s.position.current);point(bytes,s.position.previous);point(bytes,s.position.velocity);
    word(bytes,s.start_frame);word(bytes,static_cast<std::uint16_t>(s.hp));bytes.push_back(s.sprite);bytes.push_back(s.phase);
    word(bytes,static_cast<std::uint16_t>(s.phase_frame));bytes.push_back(s.damaged);bytes.push_back(s.unused_angle);return bytes;
}
void hex(const Bytes& bytes) {
    constexpr char digits[]="0123456789abcdef";
    for (auto v:bytes) std::cout << digits[v>>4] << digits[v&15];
    std::cout << ' ';
}
Bytes pool(const b::Snapshot& s) {
    Bytes bytes;
    for (const auto& e:s.entities) {
        bytes.push_back(e.flag);bytes.push_back(e.age);
        point(bytes,e.position.current);point(bytes,e.position.previous);point(bytes,e.position.velocity);
        for (auto v:{e.group,e.unused,e.speed,e.angle,static_cast<std::uint8_t>(e.phase),static_cast<std::uint8_t>(e.movement),e.special,e.final_speed,e.timer_or_turns,e.delta_or_angle}) bytes.push_back(v);
        word(bytes,e.pattern);
    }
    return bytes;
}

Bytes gathers_wire(const g::Snapshot& s) {
    Bytes bytes;
    for(const auto& e:s.entities) {
        bytes.push_back(e.flag);bytes.push_back(e.color);point(bytes,e.center.current);point(bytes,e.center.previous);point(bytes,e.center.velocity);
        word(bytes,e.radius);word(bytes,e.ring_points);bytes.push_back(e.angle);bytes.push_back(e.angle_delta);
        const auto& t=e.bullet;
        bytes.push_back(t.spawn_type);bytes.push_back(t.pattern);point(bytes,t.origin);point(bytes,t.velocity);
        for(auto v:{t.group,t.angle,t.speed,t.count,t.delta,t.unused_1,t.special_motion,t.unused_2}) bytes.push_back(v);
        word(bytes,e.previous_radius);word(bytes,e.radius_delta);
    }
    return bytes;
}
void print(const mb3::System& system,const b::System& bullets,const g::System& gathers,const r::SharedRandomRing& random,const std::vector<mb::Event>& events) {
    const auto& s=system.snapshot();hex(wire(s.actor));
    std::cout << s.actor.active << ' ' << s.actor.hp_bar << ' ' << +s.pattern << ' ' << +s.mirror << ' ' << +s.patterns_done << ' ' << +s.actor.defeat_angle << ' ' << system.score_delta() << ' ' << random.cursor() << ' ' << +bullets.snapshot().zap_frame << ' ';
    const auto& t=bullets.snapshot().scratch;
    std::cout << +t.spawn_type << ' ' << +t.pattern << ' ' << t.origin.x << ' ' << t.origin.y << ' ' << t.velocity.x << ' ' << t.velocity.y << ' ';
    for(auto v:{t.group,t.angle,t.speed,t.count,t.delta,t.unused_1,t.special_motion,t.unused_2}) std::cout << +v << ' ';
    hex(pool(bullets.snapshot()));hex(gathers_wire(gathers.snapshot()));
    const auto& gt=gathers.snapshot().scratch;
    std::cout << gt.center.x << ' ' << gt.center.y << ' ' << gt.velocity.x << ' ' << gt.velocity.y << ' ' << gt.radius << ' ' << gt.ring_points << ' ' << +gt.color << ' ' << +gt.angle_delta << ' ';
    std::cout << events.size() << ' ';
    for(const auto& e:events) std::cout << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
    std::cout << system.draws().size() << ' ';
    for(const auto& d:system.draws()) std::cout << d.left << ' ' << d.vram_top << ' ' << d.pattern << ' ' << d.white << ' ';
    std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read Stage3 midboss fixtures");char op;
    while(in>>op) {
        mb::Context c;c.bullets.rank=static_cast<std::uint8_t>(number(in));c.bullets.performance=static_cast<std::uint8_t>(number(in));
        c.frame=static_cast<std::uint16_t>(number(in));c.scroll_line=m::wrap(number(in));c.scroll_active=number(in)!=0;
        mb3::Snapshot s;s.actor.active=number(in)!=0;s.actor.hp_bar=m::wrap(number(in));
        s.pattern=static_cast<std::uint8_t>(number(in));s.mirror=static_cast<std::uint8_t>(number(in));s.patterns_done=static_cast<std::uint8_t>(number(in));
        const int density=number(in),damage=number(in),zap=number(in),clear=number(in);
        c.bullets.player.x=m::wrap(number(in));c.bullets.player.y=m::wrap(number(in));const int cursor=number(in),gather_density=number(in);
        const auto metadata=s.actor;s.actor=read(in);s.actor.active=metadata.active;s.actor.hp_bar=metadata.hp_bar;s.actor.defeat_angle=static_cast<std::uint8_t>(number(in));
        c.hit=[damage](m::Point,m::Point) { return static_cast<std::uint16_t>(damage); };
        b::Snapshot bs;bs.scratch={1,52,{2048,1024},{17,-19},46,129,42,3,6,123,128,19};
        if(density) for(auto& e:bs.entities) e.flag=1;
        bs.zap_frame=static_cast<std::uint8_t>(zap);bs.clear_time=static_cast<std::uint8_t>(clear);b::System bullets(bs);
        g::Snapshot gs;gs.scratch={{2048,1024},{17,-19},1024,8,9,2};
        if(gather_density) for(auto& e:gs.entities) e.flag=1;
        g::System gathers(gs);mb3::System system(s);r::SharedRandomRing random;unsigned index=0;
        random.fill([&] { return static_cast<std::uint8_t>(index++*73+19); });for(int i=0;i<cursor;++i) random.next16();
        std::vector<mb::Event> events;
        if(op=='S') {
            const auto steps=number(in);
            for(int tick=0;tick<steps && system.snapshot().actor.active;++tick) {
                events.clear();system.update(c,bullets,gathers,random,[&](const mb::Event& e) { events.push_back(e); });
                system.prepare_render(c);print(system,bullets,gathers,random,events);++c.frame;
            }
            continue;
        }
        if(op=='U') system.update(c,bullets,gathers,random,[&](const mb::Event& e) { events.push_back(e); });
        else if(op=='A') system.activate(c.frame);
        else if(op=='R') system.reset();
        else if(op=='D') system.prepare_render(c);
        else throw std::runtime_error("unknown Stage3 midboss fixture");
        print(system,bullets,gathers,random,events);
    }
}
void setup_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read Stage3 retained setup fixtures");int rank;
    while(in>>rank) {
        require(rank>=0 && rank<5,"invalid setup rank");
        auto actor=read(in);actor.active=number(in)!=0;actor.hp_bar=m::wrap(number(in));
        actor.defeat_angle=static_cast<std::uint8_t>(number(in));
        const auto prepared=th04::portable::session::prepare_stage3_midboss(actor);
        hex(wire(prepared));std::cout << prepared.active << ' ' << prepared.hp_bar << ' ' << +prepared.defeat_angle << '\n';
    }
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--setup-vectors") { setup_vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        mb3::Snapshot s;s.actor=th04::portable::session::prepare_stage3_midboss({});mb3::System system(s);
        system.activate(1599);require(!system.snapshot().actor.active,"early Stage3 activation");
        system.activate(1600);require(system.snapshot().actor.active,"Stage3 activation missing");
        mb::Context c;b::System bullets;g::System gathers;r::SharedRandomRing random;
        for(unsigned i=0;i<20;++i) system.update(c,bullets,gathers,random);
        require(system.snapshot().actor.phase==1 && system.snapshot().actor.position.current.y==768,"Stage3 entry differs");
        std::cout<<"Stage 3 midboss contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
