#pragma once
#include "motion.hpp"
#include "random_ring.hpp"
#include <array>
#include <functional>
#include <vector>

namespace th04::portable::yuuka6 {
struct CheckerboardState {
    // Original DATA1EFA..1F01. These are virtual PC98 paragraph/WORD offsets,
    // never host pointers. Bottom and top fragments scroll independently.
    std::uint16_t segment=0xAF30,bottom=0x04B0,top=0x09B0;
    std::uint8_t dark_x=4,passes=2;
};
struct CheckerStore { std::int32_t offset=0;std::uint8_t color=0; };
class Checkerboard {
public:
    explicit Checkerboard(CheckerboardState initial={}):state_(initial) {}
    void prepare_render();
    const CheckerboardState& state() const { return state_; }
    // Each store overwrites four planar bytes with the TDW color. Keep flat
    // addressing, including writes just below the playfield; consumers clip
    // only against the attested visible32000-byte plane, not a host rectangle.
    const std::vector<CheckerStore>& stores() const { return stores_; }
private:
    CheckerboardState state_{};
    std::vector<CheckerStore> stores_;
};
struct BackgroundShape {
    motion::Point position{};
    std::uint8_t angle=0,speed=0;
};
enum class ShapeClip : std::uint8_t { none,center,wrap };
struct BackgroundState {
    // Original BA92:56 active records plus one retained sentinel. Do not
    // clear/animate the sentinel or replace a retained clip at every state.
    std::array<BackgroundShape,57> shapes{};
    std::uint16_t pattern=120,flyout_speed=16;
    std::uint8_t state=0,fade=0,palette_latch=0,palette_changed=0;
    std::array<std::uint8_t,3> palette_zero{};
    ShapeClip clip=ShapeClip::none;
    // Opaque DOS resource tokens, retained for BB handoff state. A host
    // consumer resolves an asset handle separately, never dereferences these.
    std::uint16_t boss_bb=0,current_bb=0;
};
enum class BackgroundKind : std::uint8_t { mode,color,fill,checkerboard,entrance,mono,disable };
struct BackgroundDraw { BackgroundKind kind{};motion::Point position{};std::uint16_t value=0; };
class Background {
public:
    explicit Background(BackgroundState initial={},CheckerboardState board={}):state_(initial),board_(board) {}
    // MAIN0AAF:7DC9..7E88 prefix plus7971..7D8B particle update. Call once
    // per simulated frame; redraw the cached request/store lists thereafter.
    // Use the same ring as attacks and entities, including the index255 seam.
    void prepare_render(std::uint8_t phase,std::int16_t phase_frame,randring::SharedRandomRing&);
    void update_particles(std::uint8_t phase,randring::SharedRandomRing&);
    static void clip_shape(BackgroundShape&,ShapeClip,std::uint16_t flyout_speed);
    const BackgroundState& state() const { return state_; }
    const Checkerboard& checkerboard() const { return board_; }
    const std::vector<BackgroundDraw>& draws() const { return draws_; }
private:
    void particles(std::uint8_t,randring::SharedRandomRing&);
    void draw(BackgroundKind kind,std::uint16_t value=0,motion::Point position={}) { draws_.push_back({kind,position,value}); }
    BackgroundState state_{};
    Checkerboard board_;
    std::vector<BackgroundDraw> draws_;
};
// MAIN0AAF:152A. The mono blitter reads the first32 alpha bytes of a16x16
// sprite, ignores color planes, and uses unsigned X/WORD row addressing.
void raster_mono(const std::array<std::uint8_t,32>& mask,std::int16_t left,
                 std::int16_t top,std::uint8_t color,
                 const std::function<void(int,int,std::uint8_t)>& write);
} // namespace th04::portable::yuuka6
