#include "reimu.hpp"
#include "player_motion.hpp"
#include <algorithm>
namespace k=th04::portable::reimu;
#include "circles.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
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
int number(std::istream& in) { int n=0;require(bool(in>>n),"short Reimu fixture");return n; }
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
void orb(Bytes& v,const k::Orb& q) {
    v.push_back(q.flag);v.push_back(q.angle);point(v,q.center);point(v,q.origin);point(v,q.velocity);
    word(v,q.spin_time);word(v,static_cast<std::uint16_t>(q.distance));word(v,static_cast<std::uint16_t>(q.unknown));
    for(auto n:q.padding) v.push_back(n);
    v.push_back(q.move_speed);v.push_back(static_cast<std::uint8_t>(q.angle_speed));
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
std::int8_t signed_byte(unsigned n) { return static_cast<std::int8_t>(n<128 ? n : int(n)-256); }
k::Orb read_orb(std::istream& in) {
    Wire w;for(unsigned i=0;i<26;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
    k::Orb q;q.flag=static_cast<std::uint8_t>(w.byte());q.angle=static_cast<std::uint8_t>(w.byte());
    q.center=w.point();q.origin=w.point();q.velocity=w.point();q.spin_time=static_cast<std::uint16_t>(w.word());
    q.distance=m::wrap(w.word());q.unknown=m::wrap(w.word());
    for(auto& n:q.padding) n=static_cast<std::uint8_t>(w.byte());
    q.move_speed=static_cast<std::uint8_t>(w.byte());q.angle_speed=signed_byte(w.byte());return q;
}
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
    const auto& state=system.snapshot();v.clear();v.push_back(static_cast<std::uint8_t>(state.angle_delta));v.push_back(state.orb_pattern);v.push_back(state.trail_visible);hex(v);
    v.clear();orb(v,state.scratch);hex(v);v.clear();for(const auto& q:state.orbs) orb(v,q);hex(v);
    std::cout<<+state.pattern8_angle<<' '<<int(state.pulse_direction)<<' '<<+state.player_hit<<' '<<+bullets.snapshot().special_parameter<<' '<<+bullets.snapshot().special_angle<<' ';
    std::cout << events.size() << ' ';
    for (const auto& e:events) std::cout << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
    std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Reimu fixtures");char op;
    while(in>>op) {
        const unsigned steps=static_cast<unsigned>(number(in));k::Context c;
        c.bullets.rank=static_cast<std::uint8_t>(number(in));c.bullets.performance=static_cast<std::uint8_t>(number(in));
        c.bullets.player={3072,5120};c.frame=static_cast<std::uint16_t>(number(in));c.power=static_cast<std::uint8_t>(number(in));
        const auto damage=number(in),density=number(in),timed_out=number(in);k::Snapshot initial;
        initial.boss=read(in);initial.boss.timed_out=static_cast<std::uint8_t>(timed_out);
        initial.angle_delta=signed_byte(static_cast<unsigned>(number(in)));
        initial.orb_pattern=static_cast<std::uint8_t>(number(in));initial.trail_visible=static_cast<std::uint8_t>(number(in));
        initial.scratch=read_orb(in);for(auto& q:initial.orbs) q=read_orb(in);
        initial.pattern8_angle=static_cast<std::uint8_t>(number(in));initial.pulse_direction=signed_byte(static_cast<unsigned>(number(in)));
        initial.player_hit=static_cast<std::uint8_t>(number(in));c.bullets.player={m::wrap(number(in)),m::wrap(number(in))};
        const auto offset=static_cast<std::uint8_t>(number(in));const auto count=m::wrap(number(in));
        if(op=='P') initial.boss.palette_zero[0]=static_cast<std::uint8_t>(number(in));
        c.hit=[damage](m::Point,m::Point) { return static_cast<std::uint16_t>(damage); };
        c.orb_hit=[damage](m::Point,m::Point) { return static_cast<std::uint16_t>(damage); };
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
            std::vector<o::Event> events;const auto sink=[&](const o::Event& e){events.push_back(e);};
            if(op=='U' || op=='S') system.update(c,bullets,gathers,sparks,random,sink);
            else if(op=='M') system.add_moving();
            else if(op=='I') system.add_spinning(offset,count);
            else if(op=='O') system.update_orbs(c,sink);
            else if(op=='P') system.pulse();
            else throw std::runtime_error("unknown Reimu fixture");
            print(system,bullets,gathers,sparks,random,events);++c.frame;
            if(op=='S' && std::any_of(events.begin(),events.end(),[](const o::Event& e){return e.type==o::EventType::next_stage;})) break;
        }
    }
}
void read_explosions(std::istream& in,o::Snapshot& s) {
    for(auto* e:{&s.small[0],&s.small[1],&s.big}) {
        Wire w;for(unsigned i=0;i<16;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
        e->alive=static_cast<std::uint8_t>(w.byte());e->age=static_cast<std::uint8_t>(w.byte());
        e->center=w.point();e->radius=w.point();e->delta=w.point();
        e->unused=signed_byte(w.byte());e->angle_offset=static_cast<std::uint8_t>(w.byte());
    }
}
void render_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Reimu render fixtures");int frame;
    while(in>>frame) {
        const auto clock=m::wrap(number(in)),tone=m::wrap(number(in));const auto changed=static_cast<std::uint8_t>(number(in));
        k::Snapshot initial;initial.boss=read(in);read_explosions(in,initial.boss);
        initial.boss.big_frame=clock;initial.boss.palette_tone=tone;initial.boss.palette_changed=changed;
        initial.angle_delta=signed_byte(static_cast<unsigned>(number(in)));initial.orb_pattern=static_cast<std::uint8_t>(number(in));initial.trail_visible=static_cast<std::uint8_t>(number(in));
        initial.scratch=read_orb(in);for(auto& q:initial.orbs) q=read_orb(in);
        k::System system(initial);system.prepare_render(static_cast<std::uint16_t>(frame));const auto& s=system.snapshot();Bytes v;
        for(const auto& e:s.boss.small) explosion(v,e);
        explosion(v,s.boss.big);hex(v);
        std::cout<<s.boss.big_frame<<' '<<s.boss.palette_tone<<' '<<+s.boss.palette_changed<<' '<<+s.boss.damage<<' ';
        v.clear();v.push_back(static_cast<std::uint8_t>(s.angle_delta));v.push_back(s.orb_pattern);v.push_back(s.trail_visible);hex(v);
        v.clear();orb(v,s.scratch);hex(v);v.clear();for(const auto& q:s.orbs) orb(v,q);hex(v);
        std::cout<<system.draws().size()<<' ';
        for(const auto& d:system.draws()) std::cout<<int(d.kind)<<' '<<d.left<<' '<<d.top<<' '<<d.pattern_or_radius<<' '<<+d.color<<' ';
        std::cout<<'\n';
    }
}
void background_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open NPC backdrop fixtures");int phase;
    while(in>>phase) {
        const auto plan=k::backdrop(static_cast<std::uint8_t>(phase),m::wrap(number(in)));
        std::vector<std::array<int,4>> events;
        using Kind=k::BackdropKind;
        if(plan.kind==Kind::all_tiles || plan.kind==Kind::tiles_and_mask) events.push_back({0,0,0,0});
        if(plan.kind==Kind::dirty_tiles) events.push_back({1,0,0,0});
        if(plan.kind==Kind::picture_and_mask) events.push_back({4,1,0,0});
        if(plan.kind==Kind::picture || plan.kind==Kind::picture_and_mask) events.push_back({2,96,72,16});
        if(plan.kind==Kind::picture) events.push_back({4,1,0,0});
        if(plan.kind==Kind::tiles_and_mask || plan.kind==Kind::picture_and_mask) events.push_back({3,plan.cel,0,0});
        std::cout<<events.size()<<' ';for(const auto& e:events) for(auto n:e) std::cout<<n<<' ';std::cout<<'\n';
    }
}
void pixel_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Reimu pixel fixtures");std::string file;
    while(in>>file) {
        const auto image=static_cast<unsigned>(number(in));const auto left=number(in),top=number(in),rolling=number(in),seed=number(in);
        std::ifstream asset(file,std::ios::binary);require(bool(asset),"cannot open pixel fixture BFNT");
        const Bytes bytes{std::istreambuf_iterator<char>(asset),{}};th04::portable::sprite::Sheet sheet(bytes);
        Bytes pixels(640*400);for(unsigned i=0;i<pixels.size();++i) pixels[i]=static_cast<std::uint8_t>((i*73+unsigned(seed))&15);
        k::raster_sprite(sheet,image,left,top,rolling ? o::DrawKind::rolling_sprite : o::DrawKind::plane_sprite,
            [&](int x,int y) { return pixels[unsigned(y)*640+unsigned(x)]; },
            [&](int x,int y,std::uint8_t color) { pixels[unsigned(y)*640+unsigned(x)]=color; });
        std::cout.write(reinterpret_cast<const char*>(pixels.data()),static_cast<std::streamsize>(pixels.size()));
    }
}
void setup_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open retained Reimu setup fixtures");int marker;
    while(in>>marker) {
        (void)marker;
        auto previous=read(in);
        for(auto* e:{&previous.small[0],&previous.small[1],&previous.big}) {
            Wire w;for(unsigned i=0;i<16;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
            e->alive=static_cast<std::uint8_t>(w.byte());e->age=static_cast<std::uint8_t>(w.byte());
            e->center=w.point();e->radius=w.point();e->delta=w.point();
            const auto unused=w.byte();e->unused=static_cast<std::int8_t>(unused<128 ? int(unused) : int(unused)-256);
            e->angle_offset=static_cast<std::uint8_t>(w.byte());
        }
        const auto state=k::prepare_stage4(previous,static_cast<unsigned>(marker));const auto& s=state.boss;Bytes v;
        motion(v,s.position);word(v,static_cast<std::uint16_t>(s.hp));v.push_back(s.sprite);v.push_back(s.phase);
        word(v,static_cast<std::uint16_t>(s.phase_frame));for(auto n:{s.damage,s.mode,s.angle,s.patterns_or_bonus}) v.push_back(n);
        word(v,static_cast<std::uint16_t>(s.end_hp));hex(v);hex(Bytes(s.additional.begin(),s.additional.end()));
        v.clear();for(const auto& e:s.small) explosion(v,e);explosion(v,s.big);hex(v);
        std::cout<<s.hitbox_radius.x<<' '<<s.hitbox_radius.y<<' '<<+s.timed_out<<'\n';
    }
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--pixel-vectors") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            pixel_vectors(argv[2]);return 0;
        }
        if(argc==3 && std::string(argv[1])=="--render-vectors") { render_vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--background-vectors") { background_vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--setup-vectors") { setup_vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        auto initial=k::prepare_stage4({},3);require(initial.boss.additional[0]==12 && initial.boss.additional[1]==6,"Reimu Lunatic setup");
        k::System system(initial);k::Context c;b::System bullets;g::System gathers;sp::System sparks;r::SharedRandomRing random;
        system.update(c,bullets,gathers,sparks,random);require(system.snapshot().boss.phase_frame==1,"Reimu entrance clock");
        unsigned body=0,raw=0;k::Snapshot collision;collision.boss.phase=0;collision.orbs[0].flag=3;
        c.hit=[&](m::Point,m::Point) { ++body;return std::uint16_t{19}; };
        c.orb_hit=[&](m::Point,m::Point) { ++raw;return std::uint16_t{257}; };
        k::System distinct(collision);distinct.update(c,bullets,gathers,sparks,random);
        require(body==1 && raw==1 && distinct.snapshot().boss.hp==0,"separate Reimu body and orb hit adapters");
        k::Snapshot full;for(auto& q:full.orbs) q.flag=1;k::System exhausted(full);exhausted.add_spinning(0,0);
        k::Snapshot zero;zero.scratch.spin_time=173;zero.orbs[0].angle=96;k::System zero_divisor(zero);
        try { zero_divisor.add_spinning(19,0);throw std::runtime_error("zero count was swallowed"); }
        catch(const std::domain_error&) {}
        require(zero_divisor.snapshot().orbs[0].flag==1 && zero_divisor.snapshot().orbs[0].spin_time==173 && zero_divisor.snapshot().orbs[0].angle==96,"original pre-IDIV writes");
        std::cout<<"Stage 4 Reimu core contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
