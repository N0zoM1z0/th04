#include "kurumi.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::kurumi {
namespace {
int shifted_pixels(std::int16_t n) { return n>=0 ? n/16 : -((-int(n)+15)/16); }
}
void System::prepare_render(std::uint16_t frame) {
    draws_.clear();auto& s=state_.boss;
    const auto draw=[&](DrawKind kind,int x,int y,unsigned pattern,unsigned color=0) {
        draws_.push_back({kind,motion::wrap(x),motion::wrap(y),static_cast<std::uint16_t>(pattern),static_cast<std::uint8_t>(color)});
    };
    const int left=shifted_pixels(s.position.current.x),top=shifted_pixels(s.position.current.y)-16;
    if(s.phase<2) {
        draw(DrawKind::sprite,left,top,146+s.sprite+(frame%16)/4);
        if(s.phase==0 && s.phase_frame>128) {
            const auto radius=motion::wrap((320-int(s.phase_frame))*2);
            draw(DrawKind::circle,left+32,top+24,static_cast<std::uint16_t>(radius),7);
            draw(DrawKind::circle,left+32,top+24,static_cast<std::uint16_t>(motion::wrap(int(radius)+6)),6);
            draw(DrawKind::circle,left+32,top+24,static_cast<std::uint16_t>(motion::wrap(int(radius)+12)),6);
        }
    } else if(s.phase<254) {
        unsigned pattern=146+s.sprite;
        if(s.sprite==0 || s.sprite==12) pattern+=(frame%16)/4;
        if(s.sprite==4 || s.sprite==6) pattern+=(frame%8)/4;
        draw(s.damage ? DrawKind::white_sprite : DrawKind::sprite,left,top,pattern);
        // Flash is read, not consumed. All nonfree flags draw a ray, even
        // values other than the grow/shrink states understood by the updater.
        for(const auto& ray:state_.rays) if(ray.flag) {
            // Sprite coordinates use SAR; ray coordinates use signed IDIV,
            // hence truncate toward zero BEFORE adding the playfield origin.
            draw(DrawKind::line,ray.target.x/16+32,ray.target.y/16+16,0,9);
            draws_.back().end_left=motion::wrap(ray.origin.x/16+32);
            draws_.back().end_top=motion::wrap(ray.origin.y/16+16);
        }
    } else if(s.phase==254) {
        // The original pushes AX before loading the sprite byte; AX still
        // contains top here. Its register expression is not an undefined Y.
        draw(DrawKind::large_sprite,left,top,s.sprite);
    }
    orange::prepare_explosions(s,draws_);
}
Backdrop backdrop(const orange::Snapshot& s) {
    if(s.phase==0 || s.phase==254 || (s.phase>254 && s.phase_frame<=2)) return {};
    if(s.phase==1) return {BackdropKind::picture_and_tiles,
        motion::wrap(s.phase_frame>=0 ? s.phase_frame/2 : -((-int(s.phase_frame)+1)/2))};
    if(s.phase<254) return {BackdropKind::picture,0};
    return {BackdropKind::dirty_tiles,0};
}
std::vector<motion::Point> ray_pixels(motion::Point target,motion::Point origin) {
    const auto in_screen=[](motion::Point p) { return p.x>=0 && p.x<640 && p.y>=0 && p.y<400; };
    if(!in_screen(target) || !in_screen(origin)) throw std::out_of_range("Kurumi ray exceeds default screen clip");
    int x=target.x,y=target.y,end_x=origin.x,end_y=origin.y;
    // Original GRCG line always orders the endpoints by X before choosing
    // the major axis. It divides(minor<<16) by major and accumulates from
    // 8000h, rather than keeping the exact rational Bresenham error.
    if(x>end_x) { std::swap(x,end_x);std::swap(y,end_y); }
    const int dx=end_x-x,dy=std::abs(end_y-y),step_y=end_y>=y ? 1 : -1;
    const bool steep=dy>dx;const int major=steep ? dy : dx,minor=steep ? dx : dy;
    const unsigned delta=major ? (static_cast<unsigned>(minor)<<16)/static_cast<unsigned>(major) : 0;
    unsigned error=0x8000;std::vector<motion::Point> pixels;
    for(int i=0;i<=major;++i) {
        pixels.push_back({static_cast<std::int16_t>(x),static_cast<std::int16_t>(y)});
        error+=delta;const bool carry=error>=0x10000;error&=0xffff;
        if(steep) { y+=step_y;if(carry) ++x; }
        else { ++x;if(carry) y+=step_y; }
    }
    return pixels;
}
} // namespace th04::portable::kurumi
