#include "thick_lasers.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::laser {
namespace {
using motion::wrap;
constexpr std::uint8_t free=0,line=1,grow=2,hold=3,shrink=4;
std::int16_t screen(std::int16_t value,int offset) {
    // SAR by four floors negative Q12.4 coordinates. C++ signed division
    // truncates toward zero, so it needs the explicit negative remainder fix.
    return wrap(value/16-(value<0 && value%16!=0)+offset);
}
void emit(const Sound& sound,unsigned value) { if(sound) sound(value); }
}
void System::initialize() {
    // Original stage initialization retains every actor byte except its flag,
    // and retains scratch origin/durations/color/maximum and unused bytes.
    for(auto& b:state_.beams) b.flag=free;
    auto& b=state_.scratch;
    b.phase_frame=0;b.flag=line;b.radius=1;b.radius_speed=1;
}
void System::pull(unsigned slot) {
    // REP MOVSW copies all 24 bytes, including the four retained origin bytes.
    if(slot>=state_.beams.size()) throw std::out_of_range("thick laser slot");
    state_.beams[slot]=state_.scratch;
}
bool System::add(const Sound& sound) {
    for(unsigned i=0;i<state_.beams.size();++i) {
        if(state_.beams[i].flag!=free) continue;
        pull(i);emit(sound,5);return true;
    }
    return false; // A full two-slot pool neither replaces a beam nor plays SE5.
}
void System::update(motion::Point player,const Sound& sound) {
    for(auto& b:state_.beams) {
        if(b.flag==free) continue;
        switch(b.flag) {
        case line:
            if(b.phase_frame>=b.line_frames) {
                b.flag=grow;b.phase_frame=0;emit(sound,6);
            }
            break;
        case grow:
            b.radius=wrap(int(b.radius)+b.radius_speed);
            if(b.radius>=b.maximum_radius) {
                b.flag=hold;b.phase_frame=0;b.radius=b.maximum_radius;
            }
            break;
        case hold:
            if(b.phase_frame>=b.static_frames) { b.flag=shrink;b.phase_frame=0; }
            break;
        case shrink:
            b.radius=wrap(int(b.radius)-b.radius_speed);
            if(b.radius<=1) b.flag=free;
            break;
        default:
            // Unknown nonzero BYTE states still advance their clock and use
            // the original unsigned flag>1 collision gate; do not normalize.
            break;
        }
        // Reset-to-zero transitions end their frame at one. Even the last
        // shrinking frame increments before the now-free collision gate.
        b.phase_frame=wrap(int(b.phase_frame)+1);
        if(b.flag<=line) continue;

        // Preserve each 16-bit SHL/add/sub before the signed comparisons.
        // The rounded cap is one half-radius below the origin; the horizontal
        // box subtracts min(radius*4,16px) from radius*16 in subpixel units.
        auto r=wrap(int(b.radius)*8);
        if(wrap(int(b.origin.y)+r)>player.y) continue;
        r=wrap(int(b.radius)*4);
        if(r>=256) r=256;
        r=wrap(int(b.radius)*16-r);
        if(wrap(int(b.origin.x)-r)>player.x) continue;
        if(wrap(int(b.origin.x)+r)<player.x) continue;
        state_.player_hit=1;
    }
}
std::vector<Draw> System::draws() const {
    std::vector<Draw> result;
    const auto color=[&](unsigned c) { result.push_back({DrawKind::color,192,static_cast<std::uint16_t>(c)}); };
    const auto disc=[&](int x,int y,int r) { result.push_back({DrawKind::disc,0,0,wrap(x),wrap(y),0,0,wrap(r)}); };
    const auto box=[&](int left,int top,int right) { result.push_back({DrawKind::rectangle,0,0,wrap(left),wrap(top),wrap(right),383}); };
    for(const auto& b:state_.beams) {
        if(b.flag==free) continue;
        const auto x=screen(b.origin.x,32);
        if(b.flag==line) {
            color(15);result.push_back({DrawKind::line,0,0,x,screen(b.origin.y,16),0,383});continue;
        }
        const auto y=wrap(int(screen(b.origin.y,16))+b.radius);
        auto left=wrap(int(x)-b.radius),right=wrap(int(x)+b.radius);
        // IDIV truncates toward zero. Only positive quarter widths are capped;
        // this is intentionally not an absolute value or a lower clamp.
        const int quarter=std::min(int(b.radius)/4,16),half=quarter/2;
        if(half!=0) {
            color(b.outline);disc(x,y,b.radius);
            box(left,y,wrap(int(left)+half));box(wrap(int(right)-half),y,right);
        }
        if(quarter!=0) {
            // Outline+1 is a WORD argument. Color255 produces256, not BYTE0.
            color(unsigned(b.outline)+1);disc(x,y,wrap(int(b.radius)-half));
            box(wrap(int(left)+half),y,wrap(int(left)+quarter));
            box(wrap(int(right)-quarter),y,wrap(int(right)-half));
        }
        left=wrap(int(left)+quarter);right=wrap(int(right)-quarter);
        color(15);disc(x,y,wrap(int(b.radius)-quarter));box(left,y,right);
    }
    result.push_back({DrawKind::disable});return result;
}
} // namespace th04::portable::laser
