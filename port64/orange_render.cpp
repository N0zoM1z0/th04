#include "orange.hpp"

namespace th04::portable::orange {
namespace {
int pixels(motion::Subpixel n) { return n>=0 ? n/16 : -((-int(n)+15)/16); }
void advance(Explosion& e) {
    e.radius.x=motion::wrap(int(e.radius.x)+e.delta.x);
    e.radius.y=motion::wrap(int(e.radius.y)+e.delta.y);
    ++e.age;if (e.age>=32) e.alive=0;
}
} // namespace
void System::prepare_render(std::uint16_t frame) {
    draws_.clear();auto& s=state_;
    const auto draw=[&](DrawKind kind,int x,int y,unsigned pattern,unsigned color=0) {
        draws_.push_back({kind,motion::wrap(x),motion::wrap(y),static_cast<std::uint16_t>(pattern),static_cast<std::uint8_t>(color)});
    };
    const int x=pixels(s.position.current.x),y=pixels(s.position.current.y);
    if (s.phase<2) {
        draw(DrawKind::sprite,x+16,y-8,s.sprite+(frame%8)/4);
        if (s.phase==0 && s.phase_frame>=192) {
            const auto radius=motion::wrap((352-int(s.phase_frame))*2);
            draw(DrawKind::circle,x+40,y,radius,15);
            draw(DrawKind::circle,x+40,y,motion::wrap(int(radius)+6),9);
            draw(DrawKind::circle,x+40,y,motion::wrap(int(radius)+12),9);
        }
    } else if (s.phase<254) {
        draw(s.damage ? DrawKind::white_sprite : DrawKind::sprite,x,y-24,s.sprite+(frame%16)/4);
        // The original does not consume/reset the damage byte in this draw.
    } else if (s.phase==254) draw(DrawKind::large_sprite,x,y-16,s.sprite);
    for (auto& e:s.small) {
        if (!e.alive) continue;
        for (unsigned angle=0;angle<256;angle+=4) {
            const auto dx=motion::polar(static_cast<std::uint8_t>(angle),e.radius.x).x;
            const auto dy=motion::polar(static_cast<std::uint8_t>(angle+e.angle_offset),e.radius.y).y;
            const int left=pixels(motion::wrap(int(e.center.x)+dx))+24;
            const int top=pixels(motion::wrap(int(e.center.y)+dy))+8;
            if (left>16 && left<416 && top>0 && top<384) draw(DrawKind::tiny_sprite,left,top,68);
        }
        advance(e);
    }
    if (s.big.alive) {
        for (unsigned angle=0;angle<256;angle+=16) {
            const auto dx=motion::polar(static_cast<std::uint8_t>(angle),s.big.radius.x).x;
            const auto dy=motion::polar(static_cast<std::uint8_t>(angle+s.big.angle_offset),s.big.radius.y).y;
            const int left=pixels(motion::wrap(int(s.big.center.x)+dx));
            const int top=pixels(motion::wrap(int(s.big.center.y)+dy))-16;
            // MIKOD is48x48, but the target transforms/clips as64x64.
            if (left>=0 && left<=384 && top>=0 && top<=336) draw(DrawKind::sprite,left,top,3);
        }
        advance(s.big);s.big_frame=motion::wrap(int(s.big_frame)+1);
        if (s.big_frame<8 && (s.big_frame&1)) s.palette_tone=150;
        else if (s.big_frame>=8 && s.big_frame<16) s.palette_tone=motion::wrap(196-s.big_frame*6);
        else s.palette_tone=100;
        s.palette_changed=1;
    } else s.big_frame=0;
}
} // namespace th04::portable::orange
