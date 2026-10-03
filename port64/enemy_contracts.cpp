#include "enemy_system.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

namespace e=th04::portable::enemy;
namespace s=th04::portable::stage;
namespace m=th04::portable::motion;
namespace r=th04::portable::randring;
using Bytes=s::Program::Bytes;
namespace {
void require(bool ok,const char* reason) { if (!ok) throw std::runtime_error(reason); }
Bytes read(const char* path) {
    std::ifstream file(path,std::ios::binary);require(bool(file),"cannot read enemy fixture");
    return Bytes(std::istreambuf_iterator<char>(file),{});
}
std::int64_t number(std::istream& in) { std::int64_t value;require(bool(in>>value),"short enemy fixture");return value; }
Bytes encode(const e::Entity& e) {
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
e::Entity decode(std::istream& in) {
    Bytes b(64);for (auto& v:b) v=static_cast<std::uint8_t>(number(in));unsigned at=0;
    const auto byte=[&] { return b[at++]; };
    const auto word=[&] { const unsigned low=byte(),high=byte();return low|(high<<8); };
    const auto signed_word=[&] { return m::wrap(word()); };
    const auto point=[&] { const auto x=signed_word(),y=signed_word();return m::Point{x,y}; };
    e::Entity e;
    e.flag=byte();e.age=byte();e.position.current=point();e.position.previous=point();e.position.velocity=point();
    e.pattern=byte();e.unused_1=byte();e.hp=signed_word();e.unused_2=signed_word();e.score=signed_word();
    e.script=static_cast<std::uint16_t>(word());e.ip=signed_word();e.instruction_frame=byte();e.loop=byte();e.speed=signed_word();
    e.angle=byte();e.angle_delta=byte();e.clip_x=byte();e.clip_y=byte();e.unused_3=byte();e.item=byte();e.damaged=byte();
    e.animation_cels=byte();e.frames_per_cel=byte();e.cel=byte();e.can_be_damaged=byte();e.autofire=byte();
    e.player_collision=byte();e.left_half=byte();e.bullet.spawn_type=byte();e.bullet.pattern=byte();
    e.bullet.origin=point();e.bullet.velocity=point();e.bullet.group=byte();e.bullet.angle=byte();e.bullet.speed=byte();
    e.bullet.count=byte();e.bullet.delta=byte();e.bullet.unused_1=byte();e.bullet.special_motion=byte();e.bullet.unused_2=byte();
    e.autofire_frame=byte();e.autofire_interval=byte();return e;
}
e::Context context(std::istream& in) {
    e::Context c;c.rank=static_cast<std::uint8_t>(number(in));c.performance=static_cast<std::int16_t>(number(in));
    c.scroll_delta=m::wrap(static_cast<std::int32_t>(number(in)));
    c.player.x=m::wrap(static_cast<std::int32_t>(number(in)));c.player.y=m::wrap(static_cast<std::int32_t>(number(in)));
    return c;
}
void print_events(const std::vector<e::Event>& events) {
    std::cout << events.size() << ' ';
    for (const auto& event:events) {
        std::cout << unsigned(event.type) << ' ';
        if (event.type==e::EventType::fire) {
            const auto& b=event.bullet;
            std::cout << +b.spawn_type << ' ' << +b.pattern << ' ' << b.origin.x << ' ' << b.origin.y << ' '
                << +b.group << ' ' << +b.angle << ' ' << +b.speed << ' ' << +b.count << ' ' << +b.delta << ' ';
        } else if (event.type==e::EventType::sound) std::cout << event.value << ' ';
        else std::cout << event.position.x << ' ' << event.position.y << ' ' << event.value << ' ';
        if (event.type==e::EventType::sparks) std::cout << event.count << ' ';
    }
}
void vm_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read VM vectors");
    while (in>>std::ws && in.peek()!=std::char_traits<char>::eof()) {
        const auto c=context(in);auto gone=static_cast<std::uint16_t>(number(in));auto entity=decode(in);
        const auto size=static_cast<unsigned>(number(in));require(size<=65536,"VM fixture extent");
        Bytes script(size);for (auto& v:script) v=static_cast<std::uint8_t>(number(in));
        r::SharedRandomRing ring;unsigned draw=0;ring.fill([&] { return static_cast<std::uint8_t>(draw++*73u+19u); });
        std::vector<e::Event> events;
        const auto killed=e::run_script(entity,script,c,ring,gone,[&](const e::Event& event) { events.push_back(event); });
        for (auto v:encode(entity)) std::cout << +v << ' ';
        std::cout << gone << ' ' << ring.cursor() << ' ' << killed << ' ';
        print_events(events);std::cout << '\n';
    }
}
std::uint32_t hash_pool(const e::System& pool) {
    std::uint32_t hash=2166136261u;
    for (const auto& entity:pool.snapshot().entities) for (auto b:encode(entity)) hash=(hash^b)*16777619u;
    return hash;
}
void stage_trace(const char* path,unsigned rank,unsigned frames) {
    s::Program program(read(path));e::System pool;r::SharedRandomRing ring;unsigned draw=0;
    ring.fill([&] { return static_cast<std::uint8_t>(draw++*73u+19u); });
    th04::portable::shot::System shots;
    for (unsigned frame=0;frame<frames;++frame) {
        e::Context c;c.player={3072,5120};c.rank=static_cast<std::uint8_t>(rank);
        c.scroll_delta=frame%3==0 ? 16 : 0;c.frame_mod2=frame%2;c.frame_mod4=frame%4;
        c.performance=static_cast<std::int16_t>(rank==3 ? 22 : 16);
        std::vector<e::Event> events;
        const bool midboss=frame>=2000 && frame<2400; // explicit skip fixture
        for (const auto& spawn:program.run(static_cast<std::uint16_t>(frame),midboss)) pool.add(spawn,c,ring);
        pool.update(program,c,ring,shots,[&](const e::Event& event) { events.push_back(event); });
        pool.prepare_render();
        const auto& state=pool.snapshot();const auto target=state.homing_target.value_or(m::Point{-15984,-15984});
        std::cout << frame << ' ' << program.original_cursor() << ' ' << program.stopped() << ' '
            << hash_pool(pool) << ' ' << ring.cursor() << ' ' << state.gone << ' ' << state.killed_count << ' '
            << state.score_delta << ' ' << state.player_hit << ' ' << target.x << ' ' << target.y << ' ';
        print_events(events);
        unsigned draw_count=0;for (const auto& draw:pool.render_sprites()) draw_count+=draw.visible;
        std::cout << draw_count << ' ';
        for (const auto& draw:pool.render_sprites()) if (draw.visible) {
            const auto pixels=[](std::int16_t v) { return v>=0 ? v/16 : -((-int(v)+15)/16); };
            std::cout << 16+pixels(draw.position.x) << ' ' << (pixels(draw.position.y)+400)%400
                      << ' ' << +draw.pattern << ' ' << draw.white << ' ';
        }
        std::cout << '\n';
    }
}
// A finite WAIT script isolates update/render branches from wave scheduling.
// These are explicit CPU-comparison fixtures, never product spawn data.
void pool_vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot read pool vectors");
    const s::Program program(Bytes{10,0,0,0,1,3,6,30,0,0,0,0});
    while (in>>std::ws && in.peek()!=std::char_traits<char>::eof()) {
        auto c=context(in);c.bombing=number(in)!=0;
        c.frame_mod2=static_cast<std::uint8_t>(number(in));c.frame_mod4=static_cast<std::uint8_t>(number(in));
        e::Snapshot initial;initial.entities[0]=decode(in);e::System pool(initial);
        th04::portable::shot::Snapshot shot_state;
        const auto damage=static_cast<std::uint8_t>(number(in));
        shot_state.spark_cycle=static_cast<std::uint8_t>(number(in));
        shot_state.laser.time=static_cast<std::uint16_t>(number(in));
        shot_state.laser.bottom.current={3072,5120};
        for (unsigned i=0;i<2;++i) {
            auto& shot=shot_state.entities[i];shot.flag=1;shot.damage=damage;
            shot.position.current={3072,1800};shot.position.velocity={-19,-128};
            shot_state.collision_cache[i]={shot.position.current,static_cast<std::uint16_t>(i)};
        }
        shot_state.alive_count=2;th04::portable::shot::System shots(shot_state);
        r::SharedRandomRing ring;unsigned draw=0;
        ring.fill([&] { return static_cast<std::uint8_t>(draw++*73u+19u); });
        std::vector<e::Event> events;
        pool.update(program,c,ring,shots,[&](const e::Event& event) { events.push_back(event); });
        pool.prepare_render();
        for (const auto byte:encode(pool.snapshot().entities[0])) std::cout << +byte << ' ';
        const auto& state=pool.snapshot();const auto target=state.homing_target.value_or(m::Point{-15984,-15984});
        std::cout << state.gone << ' ' << state.killed_count << ' ' << state.score_delta << ' '
                  << state.player_hit << ' ' << target.x << ' ' << target.y << ' ';
        for (unsigned i=0;i<2;++i) {
            const auto& shot=shots.snapshot().entities[i];
            std::cout << +shot.flag << ' ' << shot.pattern << ' ' << shot.position.velocity.x << ' ' << shot.position.velocity.y << ' ';
        }
        std::cout << +shots.snapshot().spark_cycle << ' ';print_events(events);std::cout << '\n';
    }
}
void contracts() {
    e::Entity entity;entity.flag=e::alive;entity.speed=16;entity.angle=64;
    r::SharedRandomRing random;std::uint16_t gone=0;
    const Bytes script{2,1,0};
    require(!e::run_script(entity,script,{},random,gone,{}) && entity.position.current.y==16 && entity.ip==0,"timed movement first update");
    require(!e::run_script(entity,script,{},random,gone,{}) && entity.position.current.y==32 && entity.ip==2,"inclusive final movement update");
    require(e::run_script(entity,script,{},random,gone,{}) && entity.flag==e::killed,"script kill");
    bool rejected=false;try { e::run_script(entity,Bytes{0xff},{},random,gone,{}); } catch(const std::exception&) { rejected=true; }
    require(rejected,"undefined opcode must be rejected");
    e::Snapshot full;for (auto& item:full.entities) item.flag=e::alive;
    e::System pool(full);const auto cursor=random.cursor();
    require(!pool.add({0,{15984,15984},255},{},random) && cursor==random.cursor(),"full enemy pool consumes no RNG");
}
void schedule(const char* path) {
    s::Program program(read(path));
    std::cout << program.script_count() << ' ';
    for (unsigned i=0;i<program.script_count();++i) {
        std::cout << program.original_script_offset(i) << ' ' << program.script(i).size() << ' ';
    }
    std::cout << '\n';
    unsigned wave=0;
    while (!program.stopped()) {
        const auto frame=program.pending_frame();
        const bool midboss=wave++%3==1;
        const auto spawns=program.run(frame,midboss);
        std::cout << frame << ' ' << program.original_cursor() << ' ' << program.stopped() << ' ' << spawns.size() << ' ';
        for (const auto& spawn:spawns) std::cout << +spawn.script << ' ' << spawn.position.x << ' ' << spawn.position.y << ' ' << +spawn.item << ' ';
        std::cout << '\n';
    }
}
} // namespace
int main(int argc,char** argv) {
    try {
        static_assert(sizeof(void*)==8,"enemy port requires x64");
        if (argc==3 && std::string(argv[1])=="--vm-vectors") { vm_vectors(argv[2]);return 0; }
        if (argc==3 && std::string(argv[1])=="--pool-vectors") { pool_vectors(argv[2]);return 0; }
        if (argc==3 && std::string(argv[1])=="--schedule") { schedule(argv[2]);return 0; }
        if (argc==5 && std::string(argv[1])=="--stage-trace") {
            stage_trace(argv[2],static_cast<unsigned>(std::stoul(argv[3])),static_cast<unsigned>(std::stoul(argv[4])));return 0;
        }
        require(argc==1,"usage: th04-port64-enemy-contracts [--vm-vectors FILE | --stage-trace STD RANK FRAMES]");
        contracts();std::cout << "TH04 stage/enemy contracts: PASS pool=32 opcodes=52 pointer_bits=64\n";
    } catch(const std::exception& error) { std::cerr << error.what() << '\n';return 1; }
}
