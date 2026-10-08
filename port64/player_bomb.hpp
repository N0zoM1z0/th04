#pragma once
#include "player_lifecycle.hpp"
#include "random_ring.hpp"
#include "circles.hpp"
#include "sprite_sheet.hpp"
#include "cdg_image.hpp"

namespace th04::portable::bomb {
struct Star { motion::Point center{};std::uint8_t angle=0,speed=0; };
struct Snapshot { std::array<Star,48> stars{}; };
enum class Kind { fill_bands,picture,circle,sound,star };
struct Draw { Kind kind{};motion::Point position{};int value=0; };
struct Context {
    player::LifeState& life;
    randring::SharedRandomRing& random;
    circle::System& circles;
    std::uint16_t stage_frame=0;
    std::uint8_t stage_frame_mod4=0;
};
// Called by the character-Bomb render dispatch once per gameplay frame.
// Repainting consumes cached draws and must not consume RNG or move stars.
class Effect {
public:
    explicit Effect(Snapshot initial={}):state_(initial) {}
    void render(application::Playchar,Context&);
    void render_stars(application::Playchar,Context&);
    const Snapshot& snapshot() const {return state_;}
    const std::vector<Draw>& draws() const {return draws_;}
private:
    void stars(application::Playchar,Context&);
    Snapshot state_;
    std::vector<Draw> draws_;
};
// Indexed graphics consumer. Tiles use physical scroll-line addressing;
// character graphics execute after the Bomb owner disables hardware scroll.
class Graphics {
public:
    using Bytes=std::vector<std::uint8_t>;
    Graphics(Bytes bb,Bytes cdg,const Bytes& sprite_sheet);
    Graphics(const Graphics&)=delete;
    Graphics& operator=(const Graphics&)=delete;
    void tiles(unsigned cel,unsigned scroll_line,std::uint8_t color,Bytes&) const;
    void apply(const std::vector<Draw>&,Bytes&) const;
private:
    Bytes bb_,cdg_bytes_;
    CdgSheet picture_;
    sprite::Sheet sprites_;
    std::array<std::uint8_t,32> star_mask_{};
};
} // namespace th04::portable::bomb
