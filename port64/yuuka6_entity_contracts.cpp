#include "yuuka6_entities.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
namespace y=th04::portable::yuuka6;
namespace m=th04::portable::motion;
namespace b=th04::portable::bullet;
namespace sp=th04::portable::spark;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool c,const char* why) { if(!c) throw std::runtime_error(why); }
Bytes decode(const std::string& text,unsigned bytes) {
    require(text.size()==bytes*2,"invalid entity wire extent");Bytes raw;
    const auto nibble=[](char c)->unsigned { if(c>='0' && c<='9') return c-'0';if(c>='a' && c<='f') return c-'a'+10;throw std::runtime_error("invalid entity hex byte"); };
    for(unsigned i=0;i<bytes;++i) raw.push_back((nibble(text[i*2])<<4)|nibble(text[i*2+1]));
    return raw;
}
struct Wire {
    Bytes raw;unsigned at=0;
    unsigned byte() { return raw.at(at++); }
    unsigned word() { const auto lo=byte(),hi=byte();return lo|(hi<<8); }
    m::Point point() { const auto x=m::wrap(word()),yy=m::wrap(word());return {x,yy}; }
};
void word(Bytes& raw,unsigned n) { raw.push_back(n&255);raw.push_back((n>>8)&255); }
void point(Bytes& raw,m::Point p) { word(raw,static_cast<std::uint16_t>(p.x));word(raw,static_cast<std::uint16_t>(p.y)); }
void motion(Bytes& raw,const m::Motion& p) { point(raw,p.current);point(raw,p.previous);point(raw,p.velocity); }
void hex(const Bytes& raw) {
    constexpr char digits[]="0123456789abcdef";for(auto n:raw) std::cout << digits[n>>4] << digits[n&15];std::cout << ' ';
}
y::EntitySlot read_slot(Wire& w) {
    y::EntitySlot q;q.flag=w.byte();q.angle=w.byte();q.center=w.point();for(auto& n:q.unused_position) n=w.byte();q.velocity=w.point();q.age=w.word();
    q.filled_radius=m::wrap(w.word());q.ring_distance=m::wrap(w.word());q.hp=m::wrap(w.word());q.damage=m::wrap(w.word());q.speed=w.byte();q.padding=w.byte();return q;
}
void slot(Bytes& raw,const y::EntitySlot& q) {
    raw.push_back(q.flag);raw.push_back(q.angle);point(raw,q.center);raw.insert(raw.end(),q.unused_position.begin(),q.unused_position.end());point(raw,q.velocity);word(raw,q.age);
    word(raw,q.filled_radius);word(raw,q.ring_distance);word(raw,q.hp);word(raw,q.damage);raw.push_back(q.speed);raw.push_back(q.padding);
}
b::Template read_shot(Wire& w) {
    b::Template t;t.spawn_type=w.byte();t.pattern=w.byte();t.origin=w.point();t.velocity=w.point();
    t.group=w.byte();t.angle=w.byte();t.speed=w.byte();t.count=w.byte();t.delta=w.byte();t.unused_1=w.byte();t.special_motion=w.byte();t.unused_2=w.byte();return t;
}
void shot(Bytes& raw,const b::Template& t) {
    raw.push_back(t.spawn_type);raw.push_back(t.pattern);point(raw,t.origin);point(raw,t.velocity);
    for(auto n:{t.group,t.angle,t.speed,t.count,t.delta,t.unused_1,t.special_motion,t.unused_2}) raw.push_back(n);
}
void print(const y::Entities& entities,const b::System& bullets,const sp::System& sparks,
           const th04::portable::randring::SharedRandomRing& random,const std::vector<th04::portable::orange::Event>& events) {
    const auto& s=entities.snapshot();Bytes raw;for(const auto& q:s.slots) slot(raw,q);hex(raw);
    std::cout << s.hit_center.x << ' ' << s.hit_center.y << ' ' << s.hit_radius.x << ' ' << s.hit_radius.y << ' ' << +s.player_hit << ' ' << s.score_delta << ' ' << random.cursor() << ' ' << sparks.snapshot().ring_offset << ' ';
    const auto& bs=bullets.snapshot();std::cout << +bs.clear_time << ' ' << +bs.zap_frame << ' ' << +bs.special_parameter << ' ' << +bs.special_angle << ' ';
    raw.clear();shot(raw,bs.scratch);hex(raw);raw.clear();
    for(const auto& q:bs.entities) {
        raw.push_back(q.flag);raw.push_back(q.age);motion(raw,q.position);
        for(auto n:{q.group,q.unused,q.speed,q.angle,static_cast<std::uint8_t>(q.phase),static_cast<std::uint8_t>(q.movement),q.special,q.final_speed,q.timer_or_turns,q.delta_or_angle}) raw.push_back(n);
        word(raw,q.pattern);
    }
    hex(raw);raw.clear();for(const auto& q:sparks.snapshot().entities) { raw.push_back(q.flag);raw.push_back(q.age);motion(raw,q.center);word(raw,q.angle); }hex(raw);
    std::cout << events.size() << ' ';for(const auto& e:events) std::cout << int(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
    std::cout << entities.draws().size();for(const auto& d:entities.draws()) std::cout << ' ' << int(d.kind) << ' ' << d.position.x << ' ' << d.position.y << ' ' << d.value;std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open Yuuka6 entity fixtures");char op;
    while(in>>op) {
        int steps=0,rank=0,perf=0,frame=0,damage=0,density=0,hit=0,ring=0,cursor=0,angle=0,speed=0,bx=0,by=0,px=0,py=0,clear=0,zap=0;
        std::uint32_t score=0;std::string slots,scratch;
        require(bool(in>>steps>>rank>>perf>>frame>>damage>>density>>hit>>score>>ring>>cursor>>angle>>speed>>bx>>by>>px>>py>>clear>>zap>>slots>>scratch),"short entity fixture");
        require(op=='A' || op=='G' || op=='U' || op=='R' || op=='L',"unknown entity operation");
        require(steps>0 && steps<=1024 && rank>=0 && rank<=4 && perf>=0 && perf<=255,"invalid entity execution bounds");
        require(frame>=0 && frame<=65535 && damage>=0 && damage<=65535 && density>=0 && density<=2 && hit>=0 && hit<=255,"invalid entity context");
        require(ring>=0 && ring<1536 && ring%16==0 && cursor>=0 && cursor<=255 && angle>=0 && angle<=255 && speed>=0 && speed<=255,"invalid entity ring/angle");
        require(bx>=-32768 && bx<=32767 && by>=-32768 && by<=32767 && px>=-32768 && px<=32767 && py>=-32768 && py<=32767 && clear>=0 && clear<=255 && zap>=0 && zap<=255,"invalid entity coordinates/clear flags");
        y::EntitySnapshot initial;Wire w{decode(slots,832)};for(auto& q:initial.slots) q=read_slot(w);
        initial.hit_center={111,222};initial.hit_radius={333,444};initial.player_hit=hit;initial.score_delta=score;
        y::EntityContext c;c.frame=frame;c.boss_origin={m::wrap(bx),m::wrap(by)};c.bullets.player={m::wrap(px),m::wrap(py)};c.bullets.rank=rank;c.bullets.performance=perf;
        c.hit=[damage](m::Point,m::Point){return static_cast<std::uint16_t>(damage);};
        b::Snapshot bs;Wire tw{decode(scratch,18)};bs.scratch=read_shot(tw);bs.clear_time=clear;bs.zap_frame=zap;
        for(unsigned i=0;i<bs.entities.size();++i) bs.entities[i].flag=static_cast<std::uint8_t>(density==1 || (density==2 && i%2));
        sp::Snapshot ss;ss.ring_offset=ring;
        for(unsigned i=0;i<ss.entities.size();++i) { auto& q=ss.entities[i];q.flag=static_cast<std::uint8_t>(density==1 || (density==2 && i%2));q.age=37;q.center={{900,1200},{777,888},{17,-19}};q.angle=static_cast<std::uint16_t>(i*257u+0xab13u); }
        b::System bullets(bs);sp::System sparks(ss);y::Entities entities(initial);th04::portable::randring::SharedRandomRing random;unsigned index=0;
        random.fill([&]{return static_cast<std::uint8_t>(index++*73u+19u);});for(int i=0;i<cursor;++i) random.next16();
        for(int i=0;i<steps;++i) {
            std::vector<th04::portable::orange::Event> events;const auto sink=[&](const th04::portable::orange::Event& e){events.push_back(e);};c.bullets.frame_mod2=c.frame%2;
            if(op=='A') entities.add_cross(c.boss_origin,angle,speed);
            else if(op=='G') entities.add_safety_circle(c.bullets.player,sink);
            else if(op=='R') entities.prepare_render();
            else {
                if(op=='L' && i==0) entities.add_safety_circle(c.bullets.player,sink);
                entities.update(c,bullets,sparks,random,sink);
                if(op=='L') entities.prepare_render();
            }
            print(entities,bullets,sparks,random,events);++c.frame;
        }
    }
}
void contracts() {
    y::EntitySnapshot initial;for(unsigned i=0;i<31;++i) initial.slots[i].flag=1;
    initial.slots.back().filled_radius=77;initial.slots.back().padding=123;y::Entities entities(initial);
    require(entities.add_cross({3072,1280},64,16),"allocator skipped free final shared slot");
    require(entities.snapshot().slots.back().filled_radius==77 && entities.snapshot().slots.back().padding==123,"allocation erased retained circle metadata");
    entities.add_safety_circle({3072,5120});entities.prepare_render();
    const auto count=entities.draws().size();entities.draws();require(entities.draws().size()==count,"cached repaint changed draw list");
    require(entities.draws().back().kind==y::EntityDrawKind::filled_circle,"grow circle wrongly disables graphics mode");
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") {vectors(argv[2]);return 0;}
        require(argc==1,"usage: Yuuka6 entity contracts [--vectors FILE]");contracts();std::cout << "Stage 6 Yuuka entity contracts PASS\n";return 0;
    } catch(const std::exception& e) {std::cerr << "Yuuka6 entities: " << e.what() << '\n';return 1;}
}
