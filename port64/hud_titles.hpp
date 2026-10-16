#pragma once
#include "registration_render.hpp"
#include "stage_transition.hpp"
#include <array>
#include <functional>
#include <string_view>

namespace th04::portable::titles {
struct Snapshot {
    std::uint8_t frame=0,boss_frame=0,sprite=0,stage_id=0,bgm_id=0;
    std::int16_t stage_length=0,bgm_length=0,boss_length=0;
};
struct Draw { std::uint16_t left=0,top=0;std::uint8_t sprite=0,color=0; };
std::string_view stage_name(unsigned);
std::string_view bgm_name(unsigned);
// Titles and boss BGM have separate BYTE clocks and one shared dissolve cel.
// The overlay callback, title strings and TRAM are retained across requests.
std::vector<Draw> update(Snapshot&,transition::Callback&,registration::TextPlane&,
    std::uint8_t stage,std::uint8_t character,std::int16_t scroll,bool scrolling);
void request_boss(Snapshot&,transition::Callback&,std::uint8_t stage,std::uint8_t character);
class Graphics {
public:
    Graphics(const score_file::Bytes& out,const score_file::Bytes& in);
    using Pixel=std::function<void(unsigned,unsigned,std::uint8_t)>;
    // Actual 32x32 masks, aligned down to eight pixels and rolling at400.
    // A set bit writes the GRCG color; an unset bit preserves the destination.
    void raster(const std::vector<Draw>&,unsigned display_line,const Pixel&) const;
private:
    std::array<std::uint8_t,3072> masks_{};
};
} // namespace th04::portable::titles
