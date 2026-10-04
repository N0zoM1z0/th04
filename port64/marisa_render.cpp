#include "marisa.hpp"
#include "reimu.hpp"
#include "kurumi.hpp"
#include <stdexcept>

namespace th04::portable::marisa {
namespace {
int pixels(motion::Subpixel n) { return n>=0 ? n/16 : -((-int(n)+15)/16); }
unsigned outcode(motion::Point p) {
    return (p.x<32 ? 1u : (p.x>415 ? 2u : 0u))|(p.y<0 ? 8u : (p.y>367 ? 4u : 0u));
}
std::int16_t intersection(int border,int other,int delta,int divisor) {
    if(!divisor) throw std::domain_error("original Marisa line clip division by zero");
    const int quotient=(border-other)*delta/divisor;
    if(quotient<-32768 || quotient>32767) throw std::domain_error("original Marisa line clip quotient overflow");
    return motion::wrap(quotient);
}
void clip_endpoint(motion::Point& a,motion::Point b,unsigned& code) {
    if(!code) return;
    int border=0;
    // Original0000:079A clips X before Y, with signed IDIV toward zero.
    // Relative Y is measured from ClipYT; the stage rectangle is32..415,
    // 16..383 inclusive. Clipping after rasterizing changes edge rounding.
    if(code&3) {
        border=(code&1) ? 32 : 415;
        const int dx=int(a.x)-b.x;if(!dx) return;
        a.y=motion::wrap(int(intersection(border,b.x,int(a.y)-b.y,dx))+b.y);a.x=static_cast<std::int16_t>(border);
        if(a.y>=0 && a.y<=367) {code=0;return;}
        border=a.y<0 ? 0 : 367;
    } else border=(code&4) ? 367 : 0;
    const int dy=int(a.y)-b.y;if(!dy) return;
    a.x=motion::wrap(int(intersection(border,b.y,int(a.x)-b.x,dy))+b.x);a.y=static_cast<std::int16_t>(border);
    code=a.x<32 ? 1 : (a.x>415 ? 2 : 0);
}
}
std::vector<motion::Point> line_pixels(motion::Point a,motion::Point b) {
    a.y=motion::wrap(int(a.y)-16);b.y=motion::wrap(int(b.y)-16);
    unsigned first=outcode(a),last=outcode(b);
    if(first&last) return {};
    if(first|last) {
        clip_endpoint(a,b,first);
        if(first|last) clip_endpoint(b,a,last);
        if(first|last) return {};
    }
    a.y=motion::wrap(int(a.y)+16);b.y=motion::wrap(int(b.y)+16);
    return kurumi::ray_pixels(a,b);
}
void raster_sprite(const sprite::Sheet& sheet,unsigned image,int left,int top,orange::DrawKind kind,
                   const std::function<std::uint8_t(int,int)>& read,
                   const std::function<void(int,int,std::uint8_t)>& write) {
    // SUPER_ROLL_PUT_1PLANE uses alpha plane0 and FFC0 (all planes white).
    // Share the attested signed-top/bottom-wrap geometry with Reimu's normal
    // rolling put. RGB conversion remains the framebuffer consumer's job.
    const bool white=kind==orange::DrawKind::white_sprite || kind==orange::DrawKind::white_rolling_sprite;
    if(kind==orange::DrawKind::white_rolling_sprite) kind=orange::DrawKind::rolling_sprite;
    reimu::raster_sprite(sheet,image,left,top,kind,read,
        [&](int x,int y,std::uint8_t color) { write(x,y,white ? 15 : color); });
}
void System::prepare_render() {
    draws_.clear();auto& s=state_.boss;
    const auto draw=[&](orange::DrawKind kind,int x,int y,unsigned pattern) {
        draws_.push_back({kind,motion::wrap(x),motion::wrap(y),static_cast<std::uint16_t>(pattern),0});
    };
    const int left=pixels(s.position.current.x),top=pixels(s.position.current.y)-16;
    if(s.phase<254) {
        draw(s.damage ? orange::DrawKind::white_sprite : orange::DrawKind::sprite,left,top,s.sprite);
        if(s.damage) s.damage=0;
        // These are packed centers from the preceding update, in screen
        // pixels. Lines precede all sprite slots; two centers stay open,
        // three/four close the polygon. Impossible counts fail explicitly.
        if(state_.alive>4) throw std::domain_error("Marisa render alive count exceeds four owned bits");
        const auto line=[&](unsigned a,unsigned b) {
            draws_.push_back({orange::DrawKind::line,state_.center_x[a],state_.center_y[a],0,9,state_.center_x[b],state_.center_y[b]});
        };
        for(unsigned i=1;i<state_.alive;++i) line(i-1,i);
        if(state_.alive>=3) line(state_.alive-1,0);
        for(unsigned i=0;i<4;++i) {
            auto& q=state_.bits[i];
            // MAIN0AAF:419E clips signed centers BEFORE converting to pixels.
            // A hidden bit retains damage until it is actually painted.
            if(!q.flag || q.center.x<=-256 || q.center.x>=6144 || q.center.y<=-256 || q.center.y>=5888) continue;
            draw(q.damage ? orange::DrawKind::white_rolling_sprite : orange::DrawKind::rolling_sprite,
                 pixels(q.center.x)+16,pixels(q.center.y),static_cast<std::uint16_t>(q.pattern));
            if(q.damage) q.damage=0;
        }
    } else if(s.phase==254) draw(orange::DrawKind::large_sprite,left,top,s.sprite);
    orange::prepare_explosions(s,draws_);
}
void System::apply_departure(const transition::Departure& d) {
    auto& s=state_.boss;s.phase_frame=d.frame;s.homing=d.homing;s.palette_tone=d.palette_tone;s.palette_changed=d.palette_changed;
}
} // namespace th04::portable::marisa
