#include "enemy_bullets.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

namespace b=th04::portable::bullet;
namespace m=th04::portable::motion;
namespace r=th04::portable::randring;
namespace enemy=th04::portable::enemy;
namespace stage=th04::portable::stage;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool ok,const char* why) { if (!ok) throw std::runtime_error(why); }
std::int64_t number(std::istream& in) { std::int64_t v;require(bool(in>>v),"short bullet fixture");return v; }
Bytes encode(const b::Entity& e) {
    Bytes bytes;
    const auto byte=[&](auto v) { bytes.push_back(static_cast<std::uint8_t>(v)); };
    const auto word=[&](auto v) { byte(v);byte(static_cast<std::uint16_t>(v)>>8); };
    const auto point=[&](m::Point p) { word(p.x);word(p.y); };
    byte(e.flag);byte(e.age);point(e.position.current);point(e.position.previous);point(e.position.velocity);
    byte(e.group);byte(e.unused);byte(e.speed);byte(e.angle);byte(e.phase);byte(e.movement);byte(e.special);
    byte(e.final_speed);byte(e.timer_or_turns);byte(e.delta_or_angle);word(e.pattern);
    return bytes;
}
b::Entity entity(std::istream& in) {
    Bytes bytes(26);for (auto& v:bytes) v=static_cast<std::uint8_t>(number(in));unsigned at=0;
    const auto byte=[&] { return bytes[at++]; };
    const auto word=[&] { const unsigned low=byte(),high=byte();return low|(high<<8); };
    const auto point=[&] { const auto x=m::wrap(word()),y=m::wrap(word());return m::Point{x,y}; };
    b::Entity e;e.flag=byte();e.age=byte();e.position.current=point();e.position.previous=point();e.position.velocity=point();
    e.group=byte();e.unused=byte();e.speed=byte();e.angle=byte();e.phase=static_cast<b::Phase>(byte());
    e.movement=static_cast<b::Movement>(byte());e.special=byte();e.final_speed=byte();e.timer_or_turns=byte();e.delta_or_angle=byte();e.pattern=static_cast<std::uint16_t>(word());return e;
}
b::Template read_template(std::istream& in) {
    const auto byte=[&] { return static_cast<std::uint8_t>(number(in)); };
    const auto point=[&] { const auto x=m::wrap(static_cast<std::int32_t>(number(in))),y=m::wrap(static_cast<std::int32_t>(number(in)));return m::Point{x,y}; };
    b::Template t;t.spawn_type=byte();t.pattern=byte();t.origin=point();t.velocity=point();
    t.group=byte();t.angle=byte();t.speed=byte();t.count=byte();t.delta=byte();t.unused_1=byte();t.special_motion=byte();t.unused_2=byte();return t;
}
void print_template(const b::Template& t) {
    std::cout << +t.spawn_type << ' ' << +t.pattern << ' ' << t.origin.x << ' ' << t.origin.y << ' '
        << t.velocity.x << ' ' << t.velocity.y << ' ' << +t.group << ' ' << +t.angle << ' ' << +t.speed << ' '
        << +t.count << ' ' << +t.delta << ' ' << +t.unused_1 << ' ' << +t.special_motion << ' ' << +t.unused_2 << ' ';
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read bullet vectors");char operation;
    while (in>>operation) {
        b::Context c;c.rank=static_cast<std::uint8_t>(number(in));c.performance=static_cast<std::uint8_t>(number(in));
        c.player.x=m::wrap(static_cast<std::int32_t>(number(in)));c.player.y=m::wrap(static_cast<std::int32_t>(number(in)));
        c.frame_mod2=static_cast<std::uint8_t>(number(in));c.invincibility=static_cast<std::uint8_t>(number(in));c.turbo=number(in)!=0;c.graze_score=static_cast<std::uint16_t>(number(in));
        auto t=read_template(in);
        if (operation=='T') { b::tune(t,c.rank,c.performance);print_template(t);std::cout << '\n';continue; }
        b::Snapshot initial;initial.clear_time=static_cast<std::uint8_t>(number(in));initial.zap_frame=static_cast<std::uint8_t>(number(in));
        initial.special_parameter=static_cast<std::uint8_t>(number(in));initial.special_angle=static_cast<std::uint8_t>(number(in));initial.graze=static_cast<std::uint16_t>(number(in));initial.slowdown=static_cast<std::uint16_t>(number(in));
        const unsigned density=static_cast<unsigned>(number(in)),slot=static_cast<unsigned>(number(in));require(slot<b::pool_size,"bullet slot outside pool");
        const auto seed=entity(in);
        for (unsigned i=0;i<b::pool_size;++i) if (density && (density!=3 || i%2)) { initial.entities[i]=seed;initial.entities[i].flag=1; }
        initial.entities[slot]=seed;
        b::System pool(initial);r::SharedRandomRing ring;unsigned draw=0;
        ring.fill([&] { return static_cast<std::uint8_t>(draw++*73u+19u); });
        std::vector<b::Event> events;const auto sink=[&](const b::Event& event) { events.push_back(event); };
        if (operation=='A') { const bool special=number(in)!=0,fixed=number(in)!=0;pool.add(t,c,ring,special,fixed,sink); }
        else if (operation=='U') pool.update(c,sink);
        else throw std::runtime_error("unknown bullet fixture operation");
        print_template(t);std::uint32_t hash=2166136261u;
        for (const auto& e:pool.snapshot().entities) for (const auto byte:encode(e)) hash=(hash^byte)*16777619u;
        const auto& s=pool.snapshot();std::cout << hash << ' ' << ring.cursor() << ' ' << s.score_delta << ' ' << s.graze << ' ' << s.slowdown << ' '
            << +s.clear_time << ' ' << +s.zap_frame << ' ' << s.bonus << ' ' << s.player_hit << ' ' << events.size() << ' ';
        for (const auto& e:events) {
            std::cout << unsigned(e.type) << ' ' << e.position.x << ' ' << e.position.y << ' ' << e.value << ' ' << e.count << ' ';
            if (e.type==b::EventType::gather) print_template(e.bullet);
        }
        std::cout << '\n';
    }
}
std::uint32_t entity_hash(const b::System& pool) {
    std::uint32_t hash=2166136261u;
    for (const auto& e:pool.snapshot().entities) for (const auto v:encode(e)) hash=(hash^v)*16777619u;
    return hash;
}
Bytes enemy_encode(const enemy::Entity& e) {
    Bytes b;
    const auto byte=[&](auto v) { b.push_back(static_cast<std::uint8_t>(v)); };
    const auto word=[&](auto v) { byte(v);byte(static_cast<std::uint16_t>(v)>>8); };
    const auto point=[&](m::Point p) { word(p.x);word(p.y); };
    byte(e.flag);byte(e.age);point(e.position.current);point(e.position.previous);point(e.position.velocity);
    byte(e.pattern);byte(e.unused_1);word(e.hp);word(e.unused_2);word(e.score);word(e.script);word(e.ip);
    byte(e.instruction_frame);byte(e.loop);word(e.speed);byte(e.angle);byte(e.angle_delta);
    byte(e.clip_x);byte(e.clip_y);byte(e.unused_3);byte(e.item);byte(e.damaged);
    byte(e.animation_cels);byte(e.frames_per_cel);byte(e.cel);byte(e.can_be_damaged);byte(e.autofire);
    byte(e.player_collision);byte(e.left_half);
    byte(e.bullet.spawn_type);byte(e.bullet.pattern);point(e.bullet.origin);point(e.bullet.velocity);
    byte(e.bullet.group);byte(e.bullet.angle);byte(e.bullet.speed);byte(e.bullet.count);
    byte(e.bullet.delta);byte(e.bullet.unused_1);byte(e.bullet.special_motion);byte(e.bullet.unused_2);
    byte(e.autofire_frame);byte(e.autofire_interval);require(b.size()==64,"enemy wire size");return b;
}
std::uint32_t enemy_hash(const enemy::System& pool) {
    std::uint32_t hash=2166136261u;
    for (const auto& e:pool.snapshot().entities) for (const auto v:enemy_encode(e)) hash=(hash^v)*16777619u;
    return hash;
}
void joint_stage(const char* path,unsigned rank,unsigned frames) {
    std::ifstream file(path,std::ios::binary);require(bool(file),"cannot read joint STD");
    const stage::Program program_template(Bytes(std::istreambuf_iterator<char>(file),{}));
    auto program=program_template;enemy::System enemies;b::System bullets;
    th04::portable::shot::System shots;r::SharedRandomRing ring;unsigned draw=0;
    ring.fill([&] { return static_cast<std::uint8_t>(draw++*73u+19u); });
    for (unsigned frame=0;frame<frames;++frame) {
        enemy::Context ec;ec.player={3072,5120};ec.rank=static_cast<std::uint8_t>(rank);ec.performance=rank==3 ? 22 : 16;
        ec.scroll_delta=frame%3==0 ? 16 : 0;ec.frame_mod2=frame%2;ec.frame_mod4=frame%4;
        b::Context bc;bc.player=ec.player;bc.rank=ec.rank;bc.performance=static_cast<std::uint8_t>(ec.performance);
        bc.frame_mod2=ec.frame_mod2;bc.invincibility=1;bc.turbo=true;
        for (const auto& spawn:program.run(static_cast<std::uint16_t>(frame))) enemies.add(spawn,ec,ring);
        bullets.begin_frame();bullets.update(bc);
        enemies.update(program,ec,ring,shots,[&](const enemy::Event& event) {
            if (event.type==enemy::EventType::fire) bullets.fire(event,bc,ring);
        });
        enemies.prepare_render();
        const auto& state=enemies.snapshot();
        std::cout << frame << ' ' << enemy_hash(enemies) << ' ' << entity_hash(bullets) << ' ' << ring.cursor() << ' '
            << state.gone << ' ' << state.killed_count << ' ' << state.score_delta+bullets.snapshot().score_delta << ' '
            << (state.player_hit || bullets.snapshot().player_hit) << ' ';
        print_template(bullets.snapshot().scratch);std::cout << '\n';
    }
}
void contracts() {
    b::Snapshot initial;for (auto& e:initial.entities) e.flag=1;
    b::System full(initial);b::Template t;t.spawn_type=1;t.origin={2048,1024};t.group=BG_RANDOM_ANGLE;t.count=10;t.speed=42;
    r::SharedRandomRing ring;full.add(t,{},ring);require(ring.cursor()==0 && t.speed==42,"full pool consumes no random draws and restores speed");
    b::System empty;t.group=BG_RING;t.count=0;empty.add(t,{},ring);require(ring.cursor()==0,"empty ring is skipped safely");
    b::Snapshot state;auto& e=state.entities[0];e.flag=1;e.movement=b::Movement::regular;e.position.current={3072,5120};
    b::System collision(state);b::Context c;c.player={3072,5120};collision.update(c);
    require(collision.snapshot().graze==1 && !collision.snapshot().player_hit,"first close frame only grazes");
    collision.update(c);require(collision.snapshot().player_hit,"next close frame can collide");
}
}
int main(int argc,char** argv) {
    try {
        static_assert(sizeof(void*)==8,"bullet port requires x64");
        if (argc==2 && std::string(argv[1])=="--pellet-pixels") {
            for (unsigned y=0;y<8;++y) for (unsigned x=0;x<8;++x) std::cout << +b::pellet_pixel(x,y) << ' ';
            std::cout << '\n';return 0;
        }
        if (argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        if (argc==5 && std::string(argv[1])=="--stage") { joint_stage(argv[2],static_cast<unsigned>(std::stoul(argv[3])),static_cast<unsigned>(std::stoul(argv[4])));return 0; }
        require(argc==1,"usage: th04-port64-bullet-contracts [--vectors FILE]");contracts();
        std::cout << "TH04 enemy bullets: PASS pellets=240 large=200 motions=9 pointer_bits=64\n";
    } catch (const std::exception& error) { std::cerr << error.what() << '\n';return 1; }
}
