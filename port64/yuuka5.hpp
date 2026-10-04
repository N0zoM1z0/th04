#pragma once
#include "orange.hpp"
#include "thick_lasers.hpp"
#include "sprite_sheet.hpp"
namespace th04::portable::yuuka5 {
// MAIN13A9:AD4D..AD6C: Stage5 Easy or any Continue-used byte enters
// the separately loaded bad dialogue, then end_game_bad before clear bonus.
constexpr bool bad_ending_after_defeat(std::uint8_t stage_id,std::uint8_t rank,std::uint8_t continues_used) {
    return stage_id==4 && (continues_used!=0 || rank==0);
}
enum class Attack : std::uint8_t { sweep,clouds,gather,speedup_ring,aimed_spread,laser_burst,mirrored_streams };
struct Snapshot {
    orange::Snapshot boss{};
    std::int16_t sweep_x=0,midboss_frames_until=0;
    std::uint8_t cloud_step=0,cloud_accumulator=0,palette_tone=0,move_state=0;
    // The original writes a FAR nullfunc token, never a host-address pointer.
    // The game loop consumes this dispatch state to disable the STD VM.
    bool stage_vm_disabled=false;
};
enum class DrawKind : std::uint8_t { sprite,white_sprite,large_sprite,tiny_sprite,circle,color,disc,rectangle,vertical_line,disable,zoom_sprite };
struct Draw {
    DrawKind kind{};
    std::int16_t x=0,y=0;
    std::uint16_t value=0,color=0;
    std::int16_t end_x=0,end_y=0;
    std::uint16_t mode=0;
};
enum class BackdropKind : std::uint8_t { all_tiles,dirty_tiles,picture,tiles_and_mask,picture_and_mask };
struct Backdrop { BackdropKind kind=BackdropKind::all_tiles;std::uint8_t cel=0; };
struct BackgroundDraw { unsigned kind=0;std::int16_t x=0,y=0;unsigned value=0; };
Backdrop backdrop(std::uint8_t phase,std::int16_t clock);
std::vector<BackgroundDraw> backdrop_requests(std::uint8_t phase,std::int16_t clock);
std::vector<motion::Point> disc_pixels(motion::Point center,std::uint16_t radius);
std::vector<motion::Point> rectangle_pixels(motion::Point first,motion::Point last);
std::vector<motion::Point> vertical_line_pixels(std::int16_t x,std::int16_t first,std::int16_t last);
std::vector<motion::Point> filler_pixels();
void raster_sprite(const sprite::Sheet&,unsigned image,int left,int top,DrawKind,
                   const std::function<std::uint8_t(int,int)>& read,
                   const std::function<void(int,int,std::uint8_t)>& write);
using Context=orange::Context;
using Sink=orange::Sink;
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    bool move(std::uint16_t centered,randring::SharedRandomRing&);
    void pattern(Attack,const Context&,bullet::System&,gather::System&,laser::System&,
                 randring::SharedRandomRing&,const Sink& sink={});
    void update(const Context&,bullet::System&,gather::System&,laser::System&,
                randring::SharedRandomRing&,const Sink& sink={});
    void prepare_render(std::uint16_t frame,const laser::System&);
    const std::vector<Draw>& draws() const { return draws_; }
    void apply_departure(const transition::Departure& departure);
    void set_invincibility(std::uint8_t value) { state_.boss.invincibility=value; }
private:
    Snapshot state_{};
    std::vector<Draw> draws_;
};
} // namespace th04::portable::yuuka5
