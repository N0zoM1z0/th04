#include "reimu.hpp"
namespace th04::portable::reimu {
namespace {
int pixels(motion::Subpixel value) { return value>=0 ? value/16 : -((-int(value)+15)/16); }
}
void raster_sprite(const sprite::Sheet& sheet,unsigned image,int left,int top,orange::DrawKind kind,
                   const std::function<std::uint8_t(int,int)>& read,
                   const std::function<void(int,int,std::uint8_t)>& write) {
    for(unsigned y=0;y<sheet.height();++y) for(unsigned x=0;x<sheet.width();++x) {
        auto color=sheet.pixel(image,x,y);if(!color) continue;
        const int sx=left+int(x);int sy=top+int(y);
        // The original starts at the signed top address. Negative rows do
        // not belong to visible VRAM; only the bottom overflow rolls to row0.
        if(kind==orange::DrawKind::rolling_sprite && sy>=400) sy%=400;
        if(sx<0 || sx>=640 || sy<0 || sy>=400) continue;
        if(kind==orange::DrawKind::plane_sprite) color=static_cast<std::uint8_t>(read(sx,sy)|9);
        write(sx,sy,color);
    }
}
void System::prepare_render(std::uint16_t frame) {
    draws_.clear();auto& s=state_.boss;
    const auto draw=[&](orange::DrawKind kind,int left,int top,unsigned pattern,unsigned color=0) {
        draws_.push_back({kind,motion::wrap(left),motion::wrap(top),static_cast<std::uint16_t>(pattern),static_cast<std::uint8_t>(color)});
    };
    const int left=pixels(s.position.current.x),top=pixels(s.position.current.y)-16;
    if(s.phase<254) {
        if(state_.trail_visible) draw(orange::DrawKind::plane_sprite,pixels(s.position.previous.x),pixels(s.position.previous.y)-16,s.sprite,9);
        const unsigned pattern=s.sprite==136 ? 136+(frame%16)/4 : s.sprite;
        draw(s.damage ? orange::DrawKind::white_sprite : orange::DrawKind::sprite,left,top,pattern);
        if(s.damage) s.damage=0;
        for(unsigned i=0;i<state_.orbs.size();++i) {
            const auto& q=state_.orbs[i];if(!q.flag || q.center.y<=-256) continue;
            draw(orange::DrawKind::rolling_sprite,pixels(q.center.x)+16,pixels(q.center.y),state_.orb_pattern+(((frame+i)&7)>>1));
        }
    } else if(s.phase==254) draw(orange::DrawKind::large_sprite,left,top,s.sprite);
    orange::prepare_explosions(s,draws_);
}
void System::apply_departure(const transition::Departure& d) {
    auto& s=state_.boss;s.phase_frame=d.frame;s.homing=d.homing;s.palette_tone=d.palette_tone;s.palette_changed=d.palette_changed;
}
Backdrop backdrop(std::uint8_t phase,std::int16_t clock) {
    Backdrop plan;
    if(phase==0) { if(clock>2) plan.kind=BackdropKind::dirty_tiles; }
    else if(phase==1) {
        // Signed division truncates toward zero, then the target stores AL.
        plan.cel=static_cast<std::uint8_t>(clock/8);
        plan.kind=plan.cel<8 ? BackdropKind::tiles_and_mask : BackdropKind::picture_and_mask;
    } else if(phase<254) plan.kind=BackdropKind::picture;
    else if(phase==255 && clock>2) plan.kind=BackdropKind::dirty_tiles;
    return plan;
}
} // namespace th04::portable::reimu
