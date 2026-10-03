#include "midboss.hpp"
#include "stage_background.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
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
void print(const mb::System& system,const b::System& bullets,const r::SharedRandomRing& random,const std::vector<mb::Event>& events) {
    const auto& s=system.snapshot();hex(wire(s));
    std::cout << s.active << ' ' << s.hp_bar << ' ' << s.vram_y << ' ' << +s.pattern_angle << ' ' << +s.defeat_angle << ' ' << system.score_delta() << ' ' << random.cursor() << ' ' << +bullets.snapshot().zap_frame << ' ';
    const auto& t=bullets.snapshot().scratch;
    std::cout << +t.spawn_type << ' ' << +t.pattern << ' ' << t.origin.x << ' ' << t.origin.y << ' ' << t.velocity.x << ' ' << t.velocity.y << ' ';
    for (auto v:{t.group,t.angle,t.speed,t.count,t.delta,t.unused_1,t.special_motion,t.unused_2}) std::cout << +v << ' ';
    hex(pool(bullets.snapshot()));std::cout << events.size() << ' ';
    for (const auto& e:events) std::cout << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
    std::cout << system.draws().size() << ' ';
    for (const auto& d:system.draws()) std::cout << d.left << ' ' << d.vram_top << ' ' << d.pattern << ' ' << d.white << ' ';
    std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read midboss fixtures");char op;
    while (in>>op) {
        mb::Context c;c.bullets.rank=static_cast<std::uint8_t>(number(in));c.bullets.performance=static_cast<std::uint8_t>(number(in));
        c.bullets.player={3072,5120};c.frame=static_cast<std::uint16_t>(number(in));c.scroll_delta=m::wrap(number(in));
        c.scroll_line=m::wrap(number(in));c.scroll_speed=static_cast<std::uint8_t>(number(in));
        const bool active=number(in)!=0;c.scroll_active=number(in)!=0;
        const auto hpbar=m::wrap(number(in)),vram=m::wrap(number(in));const auto angle=number(in),defeat_angle=number(in),density=number(in),damage=number(in);
        auto s=read(in);s.active=active;s.hp_bar=hpbar;s.vram_y=vram;s.pattern_angle=static_cast<std::uint8_t>(angle);s.defeat_angle=static_cast<std::uint8_t>(defeat_angle);
        c.hit=[damage](m::Point,m::Point) { return static_cast<std::uint16_t>(damage); };
        b::Snapshot initial;initial.scratch={1,52,{2048,1024},{17,-19},46,129,42,3,6,123,128,19};
        if (density) for (auto& e:initial.entities) e.flag=1;
        b::System bullets(initial);mb::System system(s);r::SharedRandomRing random;unsigned index=0;
        random.fill([&] { return static_cast<std::uint8_t>(index++*73+19); });
        std::vector<mb::Event> events;
        if (op=='U') system.update(c,bullets,random,[&](const mb::Event& e) { events.push_back(e); });
        else if (op=='A') system.activate(c.frame);
        else if (op=='R') system.reset();
        else if (op=='D') system.prepare_render(c);
        else throw std::runtime_error("unknown midboss fixture");
        print(system,bullets,random,events);
    }
}
Bytes file(const char* path) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"cannot read stage asset");
    return Bytes(std::istreambuf_iterator<char>(in),std::istreambuf_iterator<char>());
}
void tiles(const char* map_path,const char* std_path,const char* fixtures) {
    const auto map=file(map_path),standard=file(std_path);
    std::ifstream in(fixtures);require(bool(in),"cannot read tile fixtures");unsigned frames=0;
    while (in>>frames) {
        const auto x=m::wrap(number(in)),y=m::wrap(number(in));const auto image=number(in);
        th04::portable::stage::Background background(map,standard);
        for (unsigned i=0;i<frames;++i) background.update();
        background.set_tile(x,y,unsigned(image));Bytes bytes;
        for (const auto& row:background.ring()) for (auto tile:row) word(bytes,tile);
        std::cout << background.scroll_line() << ' ';hex(bytes);std::cout << '\n';
    }
}
} // namespace
int main(int argc,char** argv) {
    try {
        if (argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        if (argc==5 && std::string(argv[1])=="--tile-vectors") { tiles(argv[2],argv[3],argv[4]);return 0; }
        mb::System system;
        require(system.snapshot().position.current.y==5888 && system.snapshot().hp==800,"stage1 setup");
        system.activate(3099);require(!system.snapshot().active,"early activation");
        system.activate(3100);require(system.snapshot().active,"activation frame");
        std::cout << "Stage 1 midboss contracts PASS\n";return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n';return 1; }
}
