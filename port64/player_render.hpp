#pragma once
#include "player_lifecycle.hpp"
#include "sprite_sheet.hpp"

namespace th04::portable::player {
enum class RenderKind {sprite,white,option};
struct RenderDraw {
    RenderKind kind{};
    std::int16_t left=0,top=0;
    std::uint16_t pattern=0;
};
// MAIN relative0AAF:610D. Coordinates name physical rolling VRAM rows;
// scroll conversion adjusts by400 once, as the original helper does.
std::vector<RenderDraw> render_requests(const LifeState&,const motion::Motion&,
    std::uint8_t shot_level,std::uint16_t option_pattern,
    std::uint8_t frame_mod4,std::uint16_t scroll_line);
// Visible640x400 GRCG/sprite consumer. Input sheets remain separately owned.
void render_pixels(const std::vector<RenderDraw>&,const sprite::Sheet& player,
    const sprite::Sheet& explosion,const sprite::Sheet& options,
    std::vector<std::uint8_t>& indexed);
} // namespace th04::portable::player
