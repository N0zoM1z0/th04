#include "gengetsu.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
namespace k=th04::portable::gengetsu;
namespace o=th04::portable::orange;
namespace b=th04::portable::bullet;
namespace g=th04::portable::gather;
namespace sp=th04::portable::spark;
namespace m=th04::portable::motion;
namespace r=th04::portable::randring;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool condition,const char* why) { if (!condition) throw std::runtime_error(why); }
int number(std::istream& in) { int n=0;require(bool(in>>n),"short Gengetsu fixture");return n; }
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
    v.clear();word(v,owner.wave_target);v.push_back(owner.wave_amplitude);v.push_back(owner.flash);v.push_back(owner.bomb_invincibility);hex(v);
    v.clear();for(const auto& column:owner.columns) {
        v.insert(v.end(),column.unused.begin(),column.unused.end());point(v,column.position);
        v.insert(v.end(),column.padding.begin(),column.padding.end());
    }hex(v);v.clear();
    const auto beam=[&](const th04::portable::laser::Beam& e) {
        v.push_back(e.flag);v.push_back(e.unused_first);point(v,e.origin);v.insert(v.end(),e.unused_origin.begin(),e.unused_origin.end());
        word(v,e.phase_frame);word(v,e.line_frames);word(v,e.static_frames);v.push_back(e.outline);v.push_back(e.unused_color);
        word(v,e.maximum_radius);word(v,e.radius);word(v,e.radius_speed);
    };
    beam(owner.lasers.scratch);for(const auto& e:owner.lasers.beams)beam(e);hex(v);
    std::cout<<+owner.lasers.player_hit<<' '<<s.palette_tone<<' '<<s.big_frame<<' '<<+bullets.snapshot().special_parameter<<' '<<+bullets.snapshot().special_angle<<' '<<returned<<' '<<events.size()<<' ';
    for(const auto& e:events)std::cout<<int(e.type)<<' '<<e.position.x<<' '<<e.position.y<<' '<<e.value<<' '<<e.count<<' ';
    std::cout<<'\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read Gengetsu fixture");char op;
    while(in>>op) {
        const auto steps=number(in);require(steps>0 && steps<=30000,"invalid Gengetsu steps");k::Context c;
        c.bullets.rank=std::uint8_t(number(in));c.bullets.performance=std::uint8_t(number(in));c.frame=std::uint16_t(number(in));
        c.power=std::uint8_t(number(in));const auto damage=number(in),density=number(in),timed=number(in);
        k::Snapshot initial;initial.boss=read(in);initial.boss.timed_out=std::uint8_t(timed);initial.boss.hitbox_radius={384,768};
        initial.wave_target=m::wrap(number(in));initial.wave_amplitude=std::uint8_t(number(in));initial.flash=std::uint8_t(number(in));initial.bomb_invincibility=std::uint8_t(number(in));
        initial.boss.palette_tone=m::wrap(number(in));c.bombing=number(in)!=0;const auto selector=number(in);
        const auto px=m::wrap(number(in)),py=m::wrap(number(in));c.bullets.player={px,py};const auto beam_density=number(in);
        c.bullets.turbo=c.bullets.rank==4;c.hit=[damage](m::Point,m::Point){return std::uint16_t(damage);};
        for(unsigned i=0;i<initial.columns.size();++i) {
            auto& column=initial.columns[i];column.unused={std::uint8_t(i*11+9),std::uint8_t(i*17+19)};
            column.position={m::wrap(-32000+int(i)*113),m::wrap(32000-int(i)*117)};
            for(unsigned j=0;j<column.padding.size();++j)column.padding[j]=std::uint8_t(i*19+j*7+3);
        }
        const auto beam=[](unsigned marker) {
            th04::portable::laser::Beam e;e.unused_first=std::uint8_t(marker);e.origin={3072,1024};
            for(unsigned j=0;j<4;++j)e.unused_origin[j]=std::uint8_t(marker+37*j);
            e.phase_frame=19;e.line_frames=32;e.static_frames=144;e.outline=8;e.unused_color=std::uint8_t(marker+17);
            e.maximum_radius=160;e.radius=1;e.radius_speed=6;return e;
        };
        initial.lasers.scratch=beam(201);auto& scratch=initial.lasers.scratch;scratch.flag=1;scratch.origin={2048,1024};scratch.phase_frame=0;scratch.static_frames=48;scratch.maximum_radius=64;scratch.radius_speed=1;
        initial.lasers.beams={beam(19),beam(71)};
        if(beam_density==1)for(auto& e:initial.lasers.beams)e.flag=1;
        else if(beam_density==2){auto& e=initial.lasers.beams[0];e.flag=3;e.phase_frame=31;e.radius=16;}
        b::Snapshot bs;bs.scratch={1,52,{2048,1024},{17,-19},46,129,42,3,6,123,128,19};
        g::Snapshot gs;gs.scratch={{2048,1024},{17,-19},1024,8,13,129};sp::Snapshot ss;
        if(density) {
            for(unsigned i=0;i<bs.entities.size();++i)bs.entities[i].flag=std::uint8_t(density==1 || i%2);
            for(unsigned i=0;i<gs.entities.size();++i)gs.entities[i].flag=std::uint8_t(density==1 || i%2);
            for(unsigned i=0;i<ss.entities.size();++i)ss.entities[i].flag=std::uint8_t(density==1 || i%2);
        }
        if(op=='D'){initial.boss.small[0].alive=17;initial.boss.small[1].alive=31;}
        b::System bullets(bs);g::System gathers(gs);sp::System sparks(ss);k::System owner(initial);r::SharedRandomRing random;
        unsigned index=0;random.fill([&]{return std::uint8_t(index++*73+19);});
        for(int tick=0;tick<steps;++tick) {
            std::vector<o::Event> events;const auto sink=[&](const o::Event& e){events.push_back(e);};unsigned returned=0;
            c.bullets.frame_mod2=std::uint8_t(c.frame%2);
            if(op=='D') {auto reset=owner.snapshot();reset.boss.palette_tone=60;reset.boss.palette_changed=1;owner=k::System(k::prepare_after_dialog(reset));}
            else if(op=='G')owner.gather_intro(bullets,gathers,sink);
            else if(op=='W')returned=owner.wave_step();
            else if(op=='B')returned=owner.wave_bounce();
            else if(op=='T')returned=owner.phase_state(c,bullets,gathers,sink);
            else if(op=='H')returned=owner.hit(c,sink);
            else if(op=='P' || op=='A')owner.pattern(k::Attack(selector),c,bullets,gathers,random,sink);
            else owner.update(c,bullets,gathers,random,sink);
            print(owner,bullets,gathers,sparks,random,events,returned);
            if(op=='S' && owner.snapshot().boss.phase==255)break;
            if(op=='A') {
                auto next=owner.snapshot();next.boss.phase_frame=m::wrap(int(next.boss.phase_frame)+1);owner=k::System(next);
            }
            ++c.frame;
        }
    }
    require(in.eof(),"malformed Gengetsu fixture");
}
}
namespace {
o::Explosion read_explosion(std::istream& in) {
    Wire w;for(unsigned i=0;i<16;++i)w.bytes.push_back(std::uint8_t(number(in)));
    o::Explosion e;e.alive=std::uint8_t(w.byte());e.age=std::uint8_t(w.byte());e.center=w.point();e.radius=w.point();e.delta=w.point();
    const auto unused=w.byte();e.unused=std::int8_t(unused<128 ? int(unused) : int(unused)-256);e.angle_offset=std::uint8_t(w.byte());return e;
}
th04::portable::laser::Beam read_beam(std::istream& in) {
    Wire w;for(unsigned i=0;i<24;++i)w.bytes.push_back(std::uint8_t(number(in)));
    th04::portable::laser::Beam e;e.flag=std::uint8_t(w.byte());e.unused_first=std::uint8_t(w.byte());e.origin=w.point();
    for(auto& value:e.unused_origin)value=std::uint8_t(w.byte());
    e.phase_frame=m::wrap(w.word());e.line_frames=m::wrap(w.word());e.static_frames=m::wrap(w.word());
    e.outline=std::uint8_t(w.byte());e.unused_color=std::uint8_t(w.byte());e.maximum_radius=m::wrap(w.word());e.radius=m::wrap(w.word());e.radius_speed=m::wrap(w.word());return e;
}
}
void foreground_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read Gengetsu foreground fixture");
        int frame;
        while(in>>frame) {
            const auto big=number(in),tone=number(in),changed=number(in);k::Snapshot initial;initial.boss=read(in);
            initial.boss.big_frame=m::wrap(big);initial.boss.palette_tone=m::wrap(tone);initial.boss.palette_changed=std::uint8_t(changed);
            initial.wave_amplitude=std::uint8_t(number(in));const auto adjacent=std::uint8_t(number(in));initial.flash=std::uint8_t(number(in));initial.bomb_invincibility=std::uint8_t(number(in));
            for(auto& e:initial.boss.small)e=read_explosion(in);initial.boss.big=read_explosion(in);
            for(auto& column:initial.columns) {
                Wire w;for(unsigned i=0;i<26;++i)w.bytes.push_back(std::uint8_t(number(in)));
                for(auto& value:column.unused)value=std::uint8_t(w.byte());column.position=w.point();for(auto& value:column.padding)value=std::uint8_t(w.byte());
            }
            initial.lasers.scratch=read_beam(in);for(auto& e:initial.lasers.beams)e=read_beam(in);
            k::System owner(initial);owner.prepare_render(std::uint16_t(frame),adjacent);initial=owner.snapshot();const auto& draws=owner.draws();
            Bytes v;for(const auto& e:initial.boss.small)explosion(v,e);explosion(v,initial.boss.big);hex(v);
            std::cout<<initial.boss.big_frame<<' '<<initial.boss.palette_tone<<' '<<+initial.boss.palette_changed<<' '<<+initial.boss.damage<<' '<<+initial.boss.angle<<' '<<+initial.flash<<' '<<draws.size()<<' ';
            for(const auto& d:draws)std::cout<<d.kind<<' '<<d.x<<' '<<d.y<<' '<<d.value<<' '<<d.color<<' '<<d.end_x<<' '<<d.end_y<<' '<<d.mode<<' '<<d.wavelength<<' '<<d.amplitude<<' '<<d.phase<<' ';
            std::cout<<'\n';
        }
    require(in.eof(),"malformed Gengetsu foreground fixture");
}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--foreground-vectors"){foreground_vectors(argv[2]);return 0;}
        if(argc==3 && std::string(argv[1])=="--vectors"){vectors(argv[2]);return 0;}
        require(argc==1,"Gengetsu contracts take vector option");
        k::Snapshot s;s.boss.position.current={3072,1280};s.wave_target=-32768;s.boss.phase_frame=1;
        k::System owner(s);owner.wave_step();require(owner.snapshot().boss.position.velocity.x==464,"Gengetsu wave subtraction must wrap before signed division");
        k::Context c;b::System bullets;g::System gathers;r::SharedRandomRing random;
        auto pending=owner.snapshot();pending.boss.phase=255;k::System stopped(pending);
        try{stopped.update(c,bullets,gathers,random);throw std::runtime_error("Gengetsu crossed the post-dialog gate");}catch(const std::logic_error&){}
        std::cout<<"Gengetsu state contracts PASS\n";return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
