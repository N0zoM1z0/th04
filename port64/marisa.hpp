#pragma once
#include "orange.hpp"
#include "sprite_sheet.hpp"
namespace th04::portable::marisa {
// MAIN DATA:B204 contains32 retained26-byte custom records. Marisa owns
// only slots0..3; the remaining records still belong to the shared pool.
struct Bit {
    std::uint8_t flag=0,angle=0;
    motion::Point center{};
    std::int16_t pattern=0;
    std::array<std::uint8_t,8> padding{};
    std::int16_t distance=0,moveout_speed=0,hp=0,damage=0;
    std::uint8_t unused=0;
    std::int8_t angle_speed=0;
};
// A code address is retained as an explicit dispatch token, never converted
// into a host pointer. Unknown tokens fail if an active bit actually fires.
enum class Fire : std::uint16_t { none=0,spread=0x3494,single=0x35d1 };
struct Snapshot {
    orange::Snapshot boss{};
    std::array<Bit,32> bits{};
    std::array<std::int16_t,4> hp_table{{220,400,280,450}};
    std::array<std::int16_t,4> center_x{},center_y{};
    std::uint8_t previous_mode=0,previous_alive=0,palette_direction=0;
    std::uint8_t angle_speed=0,alive=0,bitless_cycle=0,variant=0,player_hit=0;
    Fire fire=Fire::none;
};
struct Context : orange::Context {
    // Raw unit collisions use against-boss=false and retain WORD damage.
    // The body wrapper truncates to BYTE before dividing by alive+1.
    std::function<std::uint16_t(motion::Point,motion::Point)> bit_hit;
    // Native gameplay may extend the two zero-divisor durations to14.
    // Original-state comparisons leave this policy disabled.
    bool repair_flystep_zero_divisor=false;
};
using Sink=orange::Sink;
Snapshot prepare_stage4(orange::Snapshot previous);
void raster_sprite(const sprite::Sheet&,unsigned image,int left,int top,orange::DrawKind,
                   const std::function<std::uint8_t(int,int)>& read,
                   const std::function<void(int,int,std::uint8_t)>& write);
std::vector<motion::Point> line_pixels(motion::Point first,motion::Point last);
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    void initialize_bits(randring::SharedRandomRing&);
    void update_bits(const Context&,spark::System&,randring::SharedRandomRing&,const Sink& sink={});
    void fire_bits(const Context&,bullet::System&,randring::SharedRandomRing&);
    unsigned phase_entry(gather::System&,const bullet::Template&,const Sink& sink={});
    void move(randring::SharedRandomRing&);
    bool flystep(std::int16_t duration);
    bool hittest_phase(const Context&,const Sink& sink={});
    void prepare_render();
    const std::vector<orange::Draw>& draws() const { return draws_; }
    void apply_departure(const transition::Departure&);
    void set_palette_zero(std::array<std::uint8_t,3> value) { state_.boss.palette_zero=value; }
    void set_invincibility(std::uint8_t value) { state_.boss.invincibility=value; }
    void pattern(const Context&,bullet::System&,gather::System&,randring::SharedRandomRing&,const Sink& sink={});
    void update(const Context&,bullet::System&,gather::System&,spark::System&,randring::SharedRandomRing&,const Sink& sink={});
private:
    Snapshot state_{};
    std::vector<orange::Draw> draws_;
};
} // namespace th04::portable::marisa
