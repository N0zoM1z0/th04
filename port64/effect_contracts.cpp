#include "effects.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
namespace s=th04::portable::spark;
namespace g=th04::portable::gather;
namespace b=th04::portable::bullet;
namespace m=th04::portable::motion;
namespace r=th04::portable::randring;
namespace rng=th04::portable::rng;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool ok,const char* message) { if (!ok) throw std::runtime_error(message); }
std::int64_t number(std::istream& in) { std::int64_t n=0;require(bool(in>>n),"short effect fixture");return n; }
struct Wire {
    Bytes bytes;unsigned at=0;
    std::uint8_t byte() { return bytes.at(at++); }
    std::uint16_t word() { const unsigned a=byte(),c=byte();return static_cast<std::uint16_t>(a|(c<<8)); }
    m::Point point() { const auto x=m::wrap(word()),y=m::wrap(word());return {x,y}; }
};
Wire read(std::istream& in,unsigned count) { Wire w;while (count--) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));return w; }
void put(Bytes& bytes,unsigned v) { bytes.push_back(static_cast<std::uint8_t>(v)); }
void word(Bytes& bytes,unsigned v) { put(bytes,v);put(bytes,v>>8); }
void point(Bytes& bytes,m::Point p) { word(bytes,static_cast<std::uint16_t>(p.x));word(bytes,static_cast<std::uint16_t>(p.y)); }
b::Template template_read(Wire& w) {
    b::Template t;t.spawn_type=w.byte();t.pattern=w.byte();t.origin=w.point();t.velocity=w.point();
    t.group=w.byte();t.angle=w.byte();t.speed=w.byte();t.count=w.byte();t.delta=w.byte();t.unused_1=w.byte();t.special_motion=w.byte();t.unused_2=w.byte();return t;
}
void template_write(Bytes& bytes,const b::Template& t) {
    put(bytes,t.spawn_type);put(bytes,t.pattern);point(bytes,t.origin);point(bytes,t.velocity);
    for (auto v:{t.group,t.angle,t.speed,t.count,t.delta,t.unused_1,t.special_motion,t.unused_2}) put(bytes,v);
}
s::Entity spark_read(Wire w) {
    s::Entity e;e.flag=w.byte();e.age=w.byte();e.center.current=w.point();e.center.previous=w.point();e.center.velocity=w.point();e.angle=w.word();return e;
}
Bytes spark_write(const s::Entity& e) {
    Bytes bytes;put(bytes,e.flag);put(bytes,e.age);point(bytes,e.center.current);point(bytes,e.center.previous);point(bytes,e.center.velocity);word(bytes,e.angle);return bytes;
}
g::Template gather_template_read(Wire w) {
    g::Template t;t.center=w.point();t.velocity=w.point();t.radius=m::wrap(w.word());t.ring_points=m::wrap(w.word());t.color=w.byte();t.angle_delta=w.byte();return t;
}
g::Entity gather_read(Wire w) {
    g::Entity e;e.flag=w.byte();e.color=w.byte();e.center.current=w.point();e.center.previous=w.point();e.center.velocity=w.point();e.radius=m::wrap(w.word());e.ring_points=m::wrap(w.word());e.angle=w.byte();e.angle_delta=w.byte();e.bullet=template_read(w);e.previous_radius=m::wrap(w.word());e.radius_delta=m::wrap(w.word());return e;
}
Bytes gather_write(const g::Entity& e) {
    Bytes bytes;put(bytes,e.flag);put(bytes,e.color);point(bytes,e.center.current);point(bytes,e.center.previous);point(bytes,e.center.velocity);
    word(bytes,static_cast<std::uint16_t>(e.radius));word(bytes,static_cast<std::uint16_t>(e.ring_points));put(bytes,e.angle);put(bytes,e.angle_delta);
    template_write(bytes,e.bullet);word(bytes,static_cast<std::uint16_t>(e.previous_radius));word(bytes,static_cast<std::uint16_t>(e.radius_delta));return bytes;
}
void print(const Bytes& bytes) { for (auto v:bytes) std::cout << +v << ' '; }
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read effect vectors");char op;
    while (in>>op) {
        if (op=='I' || op=='R' || op=='C' || op=='S' || op=='D') {
            const auto seed=static_cast<std::uint32_t>(number(in));s::Snapshot initial;
            initial.ring_offset=static_cast<std::uint16_t>(number(in));const auto density=number(in),slot=number(in);
            auto record=spark_read(read(in,16));
            for (unsigned i=0;i<s::pool_size;++i) {
                auto e=record;e.angle=static_cast<std::uint16_t>(e.angle+i*19);e.flag=density ? (density==2 && i%2==0 ? 0 : 1) : 0;initial.entities[i]=e;
            }
            require(slot>=0 && slot<s::pool_size,"spark fixture slot");initial.entities[slot]=record;
            const auto x=m::wrap(static_cast<std::int32_t>(number(in))),y=m::wrap(static_cast<std::int32_t>(number(in)));
            const auto radius=m::wrap(static_cast<std::int32_t>(number(in)));const auto count=static_cast<std::uint16_t>(number(in));
            s::System system(initial);rng::Lcg32 generator(seed);r::SharedRandomRing random;unsigned draw=0;
            random.fill([&] { return static_cast<std::uint8_t>(draw++*73u+19u); });
            if (op=='I') system.initialize([&] { return generator.next_byte(); });
            if (op=='R') system.add_random({x,y},radius,count,random);
            if (op=='C') system.add_circle({x,y},radius,count);
            if (op=='S') system.update();
            if (op=='D') {
                for (const auto& e:system.snapshot().entities) if (e.flag==1) {
                    const int left=(e.center.current.x>=0 ? e.center.current.x/16 : -((-int(e.center.current.x)+15)/16))+28;
                    const auto cy=m::wrap(std::int32_t(e.center.current.y)+192);
                    const int top=(cy>=0 ? cy/16 : -((-int(cy)+15)/16));
                    std::cout << left << ' ' << (top<0 ? top+400 : top) << ' ' << (e.age&7u) << ' ';
                }
                std::cout << '\n';continue;
            }
            for (const auto& e:system.snapshot().entities) print(spark_write(e));
            std::cout << system.snapshot().ring_offset << ' ' << generator.state() << ' ' << random.cursor() << '\n';
        } else {
            const auto density=number(in),slot=number(in);auto record=gather_read(read(in,42));auto shape=gather_template_read(read(in,14));auto wire=read(in,18);const auto bullet=template_read(wire);
            g::Snapshot initial;initial.scratch=shape;
            for (unsigned i=0;i<g::pool_size;++i) { initial.entities[i]=record;initial.entities[i].flag=density ? (density==2 && i%2==0 ? 0 : 1) : 0; }
            require(slot>=0 && slot<g::pool_size,"gather fixture slot");initial.entities[slot]=record;
            g::System system(initial);std::vector<b::Template> releases;
            if (op=='G' || op=='O') system.add(shape,bullet,op=='O');
            else if (op=='U') system.update([&](const b::Template& saved) { releases.push_back(saved); });
            else if (op=='P') {
                for (const auto& p:system.points()) {
                    const int x=(p.position.x>=0 ? p.position.x/16 : -((-int(p.position.x)+15)/16))+28;
                    const auto cy=m::wrap(std::int32_t(p.position.y)+192);
                    const int y=(cy>=0 ? cy/16 : -((-int(cy)+15)/16));
                    std::cout << x << ' ' << (y<0 ? y+400 : y) << ' ' << +p.color << ' ';
                }
                std::cout << '\n';continue;
            } else throw std::runtime_error("unknown effect operation");
            for (const auto& e:system.snapshot().entities) print(gather_write(e));
            std::cout << releases.size() << ' ';for (const auto& t:releases) { Bytes bytes;template_write(bytes,t);print(bytes); }std::cout << '\n';
        }
    }
}
void contracts() {
    s::Snapshot full;for (auto& e:full.entities) e.flag=1;s::System sparks(full);r::SharedRandomRing random;
    sparks.add_random({1000,1000},32,8,random);require(random.cursor()==0 && sparks.snapshot().ring_offset==128,"occupied spark attempts advance without RNG");
    s::System zero;bool rejected=false;try { zero.add_circle({1000,1000},32,0); } catch(const std::domain_error&) { rejected=true; }require(rejected,"zero spark circle divisor guarded");
    g::System gather;b::Template bullet;bullet.spawn_type=1;g::Template shape;shape.center={2000,1000};gather.add(shape,bullet);unsigned releases=0;
    for (unsigned i=0;i<31;++i) gather.update([&](const b::Template&) { ++releases; });
    require(releases==0,"gather waits while radius at least2px");
    gather.update([&](const b::Template& t) { require(t.origin.x==2000,"release at current center");++releases; });require(releases==1 && gather.snapshot().entities[0].flag==2,"gather releases once and defers reclaim");
}
}
int main(int argc,char** argv) {
    try {
        static_assert(sizeof(void*)==8,"effects require x64");
        if (argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        if (argc==2 && std::string(argv[1])=="--pixels") {
            for (unsigned cel=0;cel<8;++cel) for (unsigned y=0;y<8;++y) for (unsigned x=0;x<8;++x) std::cout << s::pixel(cel,x,y) << ' ';
            for (unsigned y=0;y<8;++y) for (unsigned x=0;x<8;++x) std::cout << g::pixel(x,y) << ' ';
            std::cout << '\n';return 0;
        }
        require(argc==1,"usage: th04-port64-effect-contracts [--vectors FILE|--pixels]");contracts();
        std::cout << "TH04 effects: PASS sparks=96 gathers=16 pointer_bits=64\n";
    } catch(const std::exception& error) { std::cerr << error.what() << '\n';return 1; }
}
