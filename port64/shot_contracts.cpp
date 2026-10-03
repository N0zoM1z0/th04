#include "player_shots.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

namespace s = th04::portable::shot;
namespace m = th04::portable::motion;
namespace a = th04::portable::application;
namespace r = th04::portable::randring;
namespace {
void require(bool ok, const char* text) { if (!ok) throw std::runtime_error(text); }
std::int64_t number(std::istream& in) {
    std::int64_t value;
    if (!(in >> value)) throw std::runtime_error("short shot checkpoint");
    return value;
}
m::Point point(std::istream& in) {
    const auto x = m::wrap(static_cast<std::int32_t>(number(in)));
    const auto y = m::wrap(static_cast<std::int32_t>(number(in)));
    return {x,y};
}
void print(const s::Snapshot& state, unsigned cursor, const s::HitResult& hit) {
    const auto value = [](auto v) { std::cout << +v << ' '; };
    const auto pt = [&](m::Point p) { value(p.x); value(p.y); };
    for (const auto& e : state.entities) {
        value(e.flag);value(e.age);pt(e.position.current);pt(e.position.previous);
        pt(e.position.velocity);value(e.pattern);value(e.damage);value(e.unused_angle);
    }
    value(state.alive_count);
    for (unsigned i=0; i<state.alive_count; ++i) {
        pt(state.collision_cache[i].position);value(state.collision_cache[i].index);
    }
    value(state.time);value(state.reimu_cycle);value(state.spark_cycle);
    value(state.laser.time);value(static_cast<unsigned>(state.laser.style));value(state.laser.ring_cycle);
    pt(state.laser.bottom.current);pt(state.laser.bottom.previous);pt(state.laser.bottom.velocity);
    pt(state.options);value(state.score_delta);value(cursor);value(hit.damage);value(hit.spark_count);
    for (unsigned i=0; i<hit.spark_count; ++i) pt(hit.sparks[i]);
    std::cout << '\n';
}
void vectors(const char* path) {
    std::ifstream in(path);
    require(bool(in),"cannot read shot fixture");
    char operation;
    while (in >> operation) {
        const auto character = static_cast<a::Playchar>(number(in));
        const auto type = static_cast<a::ShotType>(number(in));
        const auto level = static_cast<unsigned>(number(in));
        const bool target_present = number(in) != 0;
        const auto target = point(in), player = point(in), options = point(in);
        const auto center = point(in), radius = point(in);
        const s::HitContext context{number(in)!=0,number(in)!=0,
            static_cast<std::uint8_t>(number(in)),static_cast<std::uint8_t>(number(in))};
        s::Snapshot state;
        state.time = static_cast<std::uint8_t>(number(in));
        state.reimu_cycle = static_cast<std::uint8_t>(number(in));
        state.spark_cycle = static_cast<std::uint8_t>(number(in));
        state.laser.time = static_cast<std::uint16_t>(number(in));
        state.laser.style = static_cast<s::LaserStyle>(number(in));
        state.laser.ring_cycle = static_cast<std::uint8_t>(number(in));
        state.laser.bottom.current = point(in);state.laser.bottom.previous = point(in);
        state.laser.bottom.velocity = point(in);state.options = point(in);
        state.score_delta = static_cast<std::uint32_t>(number(in));
        for (auto& e : state.entities) {
            e.flag = static_cast<std::uint8_t>(number(in));e.age = static_cast<std::uint8_t>(number(in));
            e.position.current = point(in);e.position.previous = point(in);e.position.velocity = point(in);
            e.pattern = static_cast<std::uint16_t>(number(in));e.damage = static_cast<std::uint8_t>(number(in));
            e.unused_angle = static_cast<std::uint8_t>(number(in));
        }
        state.alive_count = static_cast<std::uint16_t>(number(in));
        require(state.alive_count<=s::pool_size,"invalid fixture cache count");
        for (unsigned i=0;i<state.alive_count;++i) {
            state.collision_cache[i].position = point(in);
            state.collision_cache[i].index = static_cast<std::uint16_t>(number(in));
        }
        s::System shots(state);
        r::SharedRandomRing random;
        unsigned draw=0;
        random.fill([&] { return static_cast<std::uint8_t>(draw++*73u+19u); });
        s::HitResult result;
        if (operation=='F') shots.fire(character,type,level,player,random,
            target_present ? std::optional<m::Point>{target} : std::nullopt);
        else if (operation=='U') shots.update_entities(options);
        else if (operation=='H') result=shots.hittest(center,radius,context);
        else if (operation=='D') { shots.hittest(center,radius,context);result=shots.hittest(center,radius,context); }
        else if (operation=='T') result.damage=shots.advance_trigger(target_present) ? 1 : 0;
        else throw std::runtime_error("unknown fixture operation");
        print(shots.snapshot(),random.cursor(),result);
    }
}
void contracts() {
    s::System shots;
    unsigned fires=0;
    for (unsigned frame=0;frame<20;++frame) fires+=shots.advance_trigger(frame==0);
    require(fires==3 && shots.snapshot().time==0,"release must finish the 18-frame cycle");
    require(s::level_for_power(5)==0 && s::level_for_power(6)==1 &&
            s::level_for_power(127)==8 && s::level_for_power(128)==9,"power boundaries");
    // A successful final-slot allocation is followed by another request in
    // this volley. The portable adapter must stop rather than touch slot 68.
    s::Snapshot full;
    for (auto& e : full.entities) e.flag=s::alive;
    full.entities.back().flag=s::free;
    s::System guarded(full);r::SharedRandomRing random;
    guarded.fire(a::Playchar::marisa,a::ShotType::b,9,{3000,5000},random);
    require(guarded.snapshot().entities.back().pattern==36,"last free slot is usable");
    require(guarded.snapshot().entities.back().flag==s::alive,"capacity guard");
    full.alive_count=69;
    bool rejected=false;
    try { s::System invalid(full); } catch(const std::invalid_argument&) { rejected=true; }
    require(rejected,"invalid collision checkpoint must be rejected");
    for (unsigned style=0;style<5;++style) {
        s::Laser laser;laser.style=static_cast<s::LaserStyle>(style);laser.time=192;
        require(laser.cel()==style,"laser full-width cel");
        laser.time=40;require(laser.dots()==0x18,"laser cooldown width");
    }
}
} // namespace
int main(int argc,char** argv) {
    try {
        static_assert(sizeof(void*)==8,"shots require x64");
        if (argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        require(argc==1,"usage: th04-port64-shot-contracts [--vectors FILE]");
        contracts();
        std::cout << "TH04 player shots: PASS routes=4 levels=10 pool=68 pointer_bits=64\n";
    } catch(const std::exception& error) { std::cerr<<error.what()<<'\n';return 1; }
}
