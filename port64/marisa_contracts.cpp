#include "marisa.hpp"
#include "reimu.hpp"
#include "player_motion.hpp"
#include <algorithm>
namespace k=th04::portable::marisa;
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
int number(std::istream& in) { int n=0;require(bool(in>>n),"short Marisa fixture");return n; }
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
void bit(Bytes& v,const k::Bit& q) {
    v.push_back(q.flag);v.push_back(q.angle);point(v,q.center);word(v,q.pattern);
    for(auto n:q.padding) v.push_back(n);
    for(auto n:{q.distance,q.moveout_speed,q.hp,q.damage}) word(v,static_cast<std::uint16_t>(n));
    v.push_back(q.unused);v.push_back(static_cast<std::uint8_t>(q.angle_speed));
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
k::Bit read_bit(std::istream& in) {
    Wire w;for(unsigned i=0;i<26;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
    k::Bit q;q.flag=static_cast<std::uint8_t>(w.byte());q.angle=static_cast<std::uint8_t>(w.byte());q.center=w.point();q.pattern=m::wrap(w.word());
    for(auto& n:q.padding) n=static_cast<std::uint8_t>(w.byte());
    q.distance=m::wrap(w.word());q.moveout_speed=m::wrap(w.word());q.hp=m::wrap(w.word());q.damage=m::wrap(w.word());
    q.unused=static_cast<std::uint8_t>(w.byte());q.angle_speed=signed_byte(w.byte());return q;
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
           const sp::System& sparks,const r::SharedRandomRing& random,const std::vector<o::Event>& events,int result) {
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
    const auto& a=system.snapshot();v.clear();
    for(auto n:{a.previous_mode,a.previous_alive,a.palette_direction,a.angle_speed,a.alive,a.bitless_cycle,a.variant,a.player_hit}) v.push_back(n);
    word(v,static_cast<std::uint16_t>(a.fire));for(auto n:a.center_x) word(v,n);for(auto n:a.center_y) word(v,n);for(auto n:a.hp_table) word(v,n);hex(v);
    v.clear();for(const auto& q:a.bits) bit(v,q);hex(v);
    std::cout<<+bullets.snapshot().special_parameter<<' '<<+bullets.snapshot().special_angle<<' '<<result<<' '<<events.size()<<' ';
    for(const auto& e:events) std::cout<<int(e.type)<<' '<<e.position.x<<' '<<e.position.y<<' '<<e.value<<' '<<e.count<<' ';
    std::cout<<'\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Marisa fixtures");char op;
    while(in>>op) {
        const unsigned steps=static_cast<unsigned>(number(in));k::Context c;
        c.bullets.rank=static_cast<std::uint8_t>(number(in));c.bullets.performance=static_cast<std::uint8_t>(number(in));
        c.frame=static_cast<std::uint16_t>(number(in));c.power=static_cast<std::uint8_t>(number(in));
        const auto damage=number(in),density=number(in),timed_out=number(in);k::Snapshot initial;
        initial.boss=read(in);initial.boss.timed_out=static_cast<std::uint8_t>(timed_out);
        for(auto* n:{&initial.previous_mode,&initial.previous_alive,&initial.palette_direction,&initial.angle_speed,&initial.alive,&initial.bitless_cycle,&initial.variant,&initial.player_hit}) *n=static_cast<std::uint8_t>(number(in));
        initial.fire=static_cast<k::Fire>(number(in));for(auto& n:initial.center_x) n=m::wrap(number(in));for(auto& n:initial.center_y) n=m::wrap(number(in));for(auto& n:initial.hp_table) n=m::wrap(number(in));
        for(auto& q:initial.bits) q=read_bit(in);
        c.bullets.player={m::wrap(number(in)),m::wrap(number(in))};const auto duration=m::wrap(number(in));
        c.hit=[damage](m::Point,m::Point) {return static_cast<std::uint16_t>(damage);};c.bit_hit=c.hit;
        b::Snapshot bs;bs.scratch={1,52,{2048,1024},{17,-19},46,129,42,3,6,123,128,19};
        g::Snapshot gs;gs.scratch={{2048,1024},{17,-19},1024,8,13,129};sp::Snapshot ss;
        if(density) {
            for(unsigned i=0;i<bs.entities.size();++i) bs.entities[i].flag=static_cast<std::uint8_t>(density==1 || (i&1));
            for(unsigned i=0;i<gs.entities.size();++i) gs.entities[i].flag=static_cast<std::uint8_t>(density==1 || (i&1));
            for(unsigned i=0;i<ss.entities.size();++i) ss.entities[i].flag=static_cast<std::uint8_t>(density==1 || (i&1));
        }
        b::System bullets(bs);g::System gathers(gs);sp::System sparks(ss);r::SharedRandomRing random;k::System system(initial);
        unsigned index=0;random.fill([&] {return static_cast<std::uint8_t>(index++*73+19);});
        for(unsigned step=0;step<steps;++step) {
            std::vector<o::Event> events;const auto sink=[&](const o::Event& e){events.push_back(e);};int result=0;
            if(op=='U' || op=='S' || op=='P') system.update(c,bullets,gathers,sparks,random,sink);
            else if(op=='A') system.pattern(c,bullets,gathers,random,sink);
            else if(op=='I') system.initialize_bits(random);
            else if(op=='O') system.update_bits(c,sparks,random,sink);
            else if(op=='F') system.fire_bits(c,bullets,random);
            else if(op=='E') result=system.phase_entry(gathers,bullets.scratch(),sink);
            else if(op=='M') system.move(random);
            else if(op=='Y') result=system.flystep(duration);
            else if(op=='H') result=system.hittest_phase(c,sink);
            else throw std::runtime_error("unknown Marisa fixture");
            print(system,bullets,gathers,sparks,random,events,result);++c.frame;
            if(op=='P' && system.snapshot().boss.mode==255) break;
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

Bytes private_bytes(const k::Snapshot& a,std::uint8_t padding) {
    Bytes v;for(auto n:{a.previous_mode,a.previous_alive,a.palette_direction,a.angle_speed,a.alive,a.bitless_cycle,a.variant,padding}) v.push_back(n);
    word(v,static_cast<std::uint16_t>(a.fire));for(auto n:a.center_x) word(v,n);for(auto n:a.center_y) word(v,n);return v;
}
void render_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Marisa render fixtures");int frame;
    while(in>>frame) {
        (void)frame;const auto clock=m::wrap(number(in)),tone=m::wrap(number(in));const auto changed=static_cast<std::uint8_t>(number(in));
        k::Snapshot initial;initial.boss=read(in);read_explosions(in,initial.boss);
        initial.boss.big_frame=clock;initial.boss.palette_tone=tone;initial.boss.palette_changed=changed;
        for(auto* n:{&initial.previous_mode,&initial.previous_alive,&initial.palette_direction,&initial.angle_speed,&initial.alive,&initial.bitless_cycle,&initial.variant}) *n=static_cast<std::uint8_t>(number(in));
        const auto padding=static_cast<std::uint8_t>(number(in));Wire w;for(unsigned i=0;i<18;++i) w.bytes.push_back(static_cast<std::uint8_t>(number(in)));
        initial.fire=static_cast<k::Fire>(w.word());for(auto& n:initial.center_x) n=m::wrap(w.word());for(auto& n:initial.center_y) n=m::wrap(w.word());
        for(auto& q:initial.bits) q=read_bit(in);
        k::System system(initial);system.prepare_render();const auto& a=system.snapshot();const auto& b=a.boss;Bytes v;
        for(const auto& e:b.small) explosion(v,e);
        explosion(v,b.big);hex(v);
        std::cout<<b.big_frame<<' '<<b.palette_tone<<' '<<+b.palette_changed<<' '<<+b.damage<<' ';
        hex(private_bytes(a,padding));v.clear();for(const auto& q:a.bits) bit(v,q);hex(v);
        std::cout<<system.draws().size()<<' ';for(const auto& d:system.draws()) std::cout<<int(d.kind)<<' '<<d.left<<' '<<d.top<<' '<<d.pattern_or_radius<<' '<<+d.color<<' '<<d.end_left<<' '<<d.end_top<<' ';
        std::cout<<'\n';
    }
}
void line_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Marisa line fixtures");int x;
    while(in>>x) {
        const auto y=number(in),ex=number(in),ey=number(in);Bytes mask(32000);
        for(auto p:k::line_pixels({m::wrap(x),m::wrap(y)},{m::wrap(ex),m::wrap(ey)})) {
            const unsigned at=unsigned(p.y)*640+unsigned(p.x);mask[at/8]|=static_cast<std::uint8_t>(128>>(at%8));
        }
        hex(mask);std::cout<<'\n';
    }
}
void background_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open NPC backdrop fixtures");int phase;
    while(in>>phase) {
        const auto plan=th04::portable::reimu::backdrop(static_cast<std::uint8_t>(phase),m::wrap(number(in)));
        std::vector<std::array<int,4>> events;
        using Kind=th04::portable::reimu::BackdropKind;
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
    std::ifstream in(path);require(bool(in),"cannot open Marisa pixel fixtures");std::string file;
    while(in>>file) {
        const auto image=static_cast<unsigned>(number(in));const auto left=number(in),top=number(in),rolling=number(in),seed=number(in);
        std::ifstream asset(file,std::ios::binary);require(bool(asset),"cannot open pixel fixture BFNT");
        const Bytes bytes{std::istreambuf_iterator<char>(asset),{}};th04::portable::sprite::Sheet sheet(bytes);
        Bytes pixels(640*400);for(unsigned i=0;i<pixels.size();++i) pixels[i]=static_cast<std::uint8_t>((i*73+unsigned(seed))&15);
        k::raster_sprite(sheet,image,left,top,static_cast<o::DrawKind>(rolling),
            [&](int x,int y) { return pixels[unsigned(y)*640+unsigned(x)]; },
            [&](int x,int y,std::uint8_t color) { pixels[unsigned(y)*640+unsigned(x)]=color; });
        std::cout.write(reinterpret_cast<const char*>(pixels.data()),static_cast<std::streamsize>(pixels.size()));
    }
}
void setup_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open retained Marisa setup fixtures");int marker;
    while(in>>marker) {
        (void)marker;auto previous=read(in);read_explosions(in,previous);
        const auto state=k::prepare_stage4(previous);const auto& a=state.boss;Bytes v;
        motion(v,a.position);word(v,static_cast<std::uint16_t>(a.hp));v.push_back(a.sprite);v.push_back(a.phase);word(v,static_cast<std::uint16_t>(a.phase_frame));
        for(auto n:{a.damage,a.mode,a.angle,a.patterns_or_bonus}) v.push_back(n);
        word(v,static_cast<std::uint16_t>(a.end_hp));hex(v);hex(Bytes(a.additional.begin(),a.additional.end()));v.clear();
        for(const auto& e:a.small) explosion(v,e);
        explosion(v,a.big);hex(v);std::cout<<a.hitbox_radius.x<<' '<<a.hitbox_radius.y<<' '<<+a.timed_out<<'\n';
    }
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--line-vectors") {line_vectors(argv[2]);return 0;}
        if(argc==3 && std::string(argv[1])=="--pixel-vectors") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            pixel_vectors(argv[2]);return 0;
        }
        if(argc==3 && std::string(argv[1])=="--render-vectors") {render_vectors(argv[2]);return 0;}
        if(argc==3 && std::string(argv[1])=="--background-vectors") {background_vectors(argv[2]);return 0;}
        if(argc==3 && std::string(argv[1])=="--setup-vectors") {setup_vectors(argv[2]);return 0;}
        if(argc==3 && std::string(argv[1])=="--vectors") {vectors(argv[2]);return 0;}
        k::Snapshot initial;k::System system(initial);r::SharedRandomRing random;system.initialize_bits(random);
        require(system.snapshot().bits[0].hp==220 && system.snapshot().bits[3].hp==450,"Marisa bit HP");
        for(auto duration:{12,13}) {
            k::System bad(initial);try {bad.flystep(static_cast<std::int16_t>(duration));throw std::runtime_error("flystep divide failure swallowed");} catch(const std::domain_error&) {}
            require(bad.snapshot().boss.additional[13]==0,"flystep pre-IDIV state");
        }
        k::Snapshot collision;collision.boss.phase=2;collision.boss.hp=1000;collision.alive=3;
        k::System body(collision);k::Context c;c.hit=[](m::Point,m::Point){return std::uint16_t{257};};
        body.hittest_phase(c);require(body.snapshot().boss.damage==1 && body.snapshot().boss.hp==1000,"BYTE damage then shared divisor");
        for(unsigned index=0;index<2;++index) {
            k::Snapshot overflow;overflow.boss.position.current=index ? m::Point{3072,-30976} : m::Point{-29696,1024};
            overflow.boss.position.velocity={17,-19};k::System bad(overflow);
            try {bad.flystep(10);throw std::runtime_error("flystep quotient overflow swallowed");} catch(const std::domain_error&) {}
            require(bad.snapshot().boss.position.velocity.x==(index ? 0 : 17) && bad.snapshot().boss.position.velocity.y==-19 && bad.snapshot().boss.additional[13]==0,"flystep sequential pre-overflow writes");
        }
        // Native-only policy controls are deliberately separate from original
        // equality fixtures. Both attack callers must survive the known gap.
        for(unsigned mode:{1u,2u}) {
            k::Snapshot gap;gap.boss.mode=static_cast<std::uint8_t>(mode);gap.boss.phase_frame=152;
            gap.boss.additional[15]=148;gap.boss.position.current={3000,1700};
            b::System gap_bullets;g::System gap_gathers;k::Context portable;
            portable.repair_flystep_zero_divisor=true;k::System repaired(gap);
            repaired.pattern(portable,gap_bullets,gap_gathers,random);
            require(repaired.snapshot().boss.additional[13]==1 && repaired.snapshot().boss.position.current.x==3072 && repaired.snapshot().boss.position.current.y==1792,"portable gap repair is explicit duration14");
        }
        b::System bullets;g::System gathers;sp::System sparks;
        k::Snapshot empty;empty.fire=static_cast<k::Fire>(65535);k::System no_callback(empty);no_callback.fire_bits(c,bullets,random);
        empty.bits[0].flag=1;k::System bad_callback(empty);
        try {bad_callback.fire_bits(c,bullets,random);throw std::runtime_error("invalid callback swallowed");} catch(const std::domain_error&) {}
        std::cout<<"Stage 4 Marisa core contracts PASS\n";return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
