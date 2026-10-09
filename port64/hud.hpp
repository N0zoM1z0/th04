#pragma once
#include "score.hpp"
#include "registration_render.hpp"

namespace th04::portable::hud {
enum class Kind {gaiji,gaiji_string,sjis};
struct Request {
    Kind kind=Kind::gaiji;
    int column=0,row=0;
    std::uint16_t attribute=0;
    std::uint8_t glyph=0;
    std::string text;
};
using Requests=std::vector<Request>;
struct Values {
    std::uint8_t character=0,rank=1,lives=3,bombs=2,points=0,power=1,shot_level=0;
    std::uint16_t dream=0,graze=0;
    score::Snapshot score;
};
Requests lives(std::uint8_t);
Requests bombs(std::uint8_t);
Requests points(std::uint8_t);
Requests dream(std::uint16_t);
Requests graze(std::uint16_t);
Requests power(std::uint8_t,std::uint8_t shot_level);
Requests bar(std::uint16_t row,std::int16_t value,std::uint16_t attribute);
// Only indices within the observed five-entry color table are defined.
Requests hp(std::int16_t bar_value);
Requests hp_update(std::int16_t& previous,std::int16_t current,std::int16_t maximum);
// hud_put clears the displayed HP bar without resetting hp_update's previous.
Requests initialize(Values&);
void apply(registration::TextPlane&,const Requests&);
} // namespace th04::portable::hud
