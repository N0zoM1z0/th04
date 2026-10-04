#include "yuuka6_background.hpp"
#include <stdexcept>

namespace th04::portable::yuuka6 {
namespace {
int pixels(motion::Subpixel n) { return n>=0 ? n/16 : -((-int(n)+15)/16); }
}
void Checkerboard::prepare_render() {
    // Bound the paragraph walk to the observed visible-layout domain. Raw
    // malformed segments can wrap far outside VRAM; no host pointer is formed.
    if(state_.segment<0xA850 || state_.segment>0xAF6C)
        throw std::domain_error("checkerboard paragraph outside visible-layout range");
    stores_.clear();auto remaining=state_.passes;std::uint8_t color=0,x=state_.dark_x;
    do {
        auto segment=state_.segment;
        auto offset=static_cast<std::uint16_t>(x+state_.bottom);
        for(;;) {
            do {
                for(unsigned column=0;column<6;++column) {
                    stores_.push_back({(int(segment)-0xA800)*16+offset,color});
                    offset=static_cast<std::uint16_t>(offset+8);
                }
                offset=static_cast<std::uint16_t>(offset-128);
            } while(motion::wrap(offset)>=0);
            x^=12;segment=static_cast<std::uint16_t>(segment-160);
            if(motion::wrap(segment)>motion::wrap(0xA850)) {
                offset=static_cast<std::uint16_t>(x+2480);continue;
            }
            if(segment==0xA7B0) break;
            segment=0xA850;offset=static_cast<std::uint16_t>(x+state_.top);
        }
        // A stored zero pass BYTE means256 passes, not an empty rectangle.
        // Every pass after the first uses color1 and the original dark XOR12.
        --remaining;color=1;x=state_.dark_x^12;
    } while(remaining);
    state_.segment=static_cast<std::uint16_t>(state_.segment-20);
    state_.bottom=static_cast<std::uint16_t>(state_.bottom+320);
    if(motion::wrap(state_.segment)<motion::wrap(0xAEE0)) {
        state_.segment=0xAF6C;state_.bottom=320;state_.dark_x^=12;
    }
    state_.top=static_cast<std::uint16_t>(state_.top-320);
    if(motion::wrap(state_.top)<0) state_.top=2480;
}
void Background::clip_shape(BackgroundShape& shape,ShapeClip clip,std::uint16_t speed) {
    auto& p=shape.position;
    if(clip==ShapeClip::center) {
        ++shape.speed;
        if(p.x<=-128 || p.x>=6272 || p.y<=-128 || p.y>=6144) {
            p={3072,2944};shape.speed=static_cast<std::uint8_t>(speed);
        }
    } else if(clip==ShapeClip::wrap) {
        if(p.x<=-128) p.x=motion::wrap(int(p.x)+6400);
        else if(p.x>=6272) p.x=motion::wrap(int(p.x)-6400);
        if(p.y<=-128) p.y=motion::wrap(int(p.y)+6272);
        else if(p.y>=6144) p.y=motion::wrap(int(p.y)-6272);
    } else throw std::domain_error("background clip callback is not initialized");
}
void Background::prepare_render(std::uint8_t phase,std::int16_t clock,randring::SharedRandomRing& random) {
    draws_.clear();draw(BackgroundKind::mode,128);
    const auto fill=[&] { draw(BackgroundKind::color,1);draw(BackgroundKind::fill); };
    const auto checker=[&] { draw(BackgroundKind::checkerboard);board_.prepare_render(); };
    if(phase==0) {
        fill();draw(BackgroundKind::disable);
        if(clock!=2) return;
        for(unsigned i=0;i<56;++i) {
            auto& shape=state_.shapes[i];shape.position={static_cast<std::int16_t>(random.next16_mod(6144)),static_cast<std::int16_t>(random.next16_mod(5888))};shape.angle=96;shape.speed=16;
        }
        state_.flyout_speed=16;state_.pattern=120;state_.state=0;state_.fade=0;
        return; // Sentinel, clip callback and palette latch are retained.
    }
    if(phase==1) {
        const auto cel=static_cast<std::uint8_t>(clock/4);
        draw(BackgroundKind::color,1);
        if(cel<8) draw(BackgroundKind::fill);else checker();
        state_.current_bb=state_.boss_bb;draw(BackgroundKind::entrance,cel);return;
    }
    if(phase<254) checker();else { fill();draw(BackgroundKind::disable); }
    particles(phase,random);
}
void Background::update_particles(std::uint8_t phase,randring::SharedRandomRing& random) {
    draws_.clear();particles(phase,random);
}
void Background::particles(std::uint8_t phase,randring::SharedRandomRing& random) {
    auto& s=state_;
    if(s.fade==0) {
        if(s.state==0 || s.state==8 || s.state==12) s.clip=ShapeClip::wrap;
        else if(s.state==6 || s.state==10) s.clip=ShapeClip::center;
    }
    draw(BackgroundKind::mode,192);
    const auto fade=s.fade<128 ? s.fade : 255-s.fade;
    draw(BackgroundKind::color,s.state<16 ? 8 : 9);
    if(s.state<16) {
        if(s.state&1) { s.palette_zero[0]=fade;s.palette_zero[2]=fade; }
        else s.palette_zero[2]=(fade*3)/2;
    } else if(!s.palette_latch) {
        s.palette_zero={0,0,static_cast<std::uint8_t>((fade*3)/2)};
        if(fade>=127) s.palette_latch=1;
    }
    s.palette_changed=1;
    const auto set_motion=[&](std::uint8_t angle,std::uint8_t speed) {
        for(unsigned i=0;i<56;++i) { s.shapes[i].angle=angle;s.shapes[i].speed=speed; }
    };
    // The outward vector uses center+(8px,8px), distinct from the actual
    // respawn center3072/2944. Preserve signed WORD subtraction in angle_to.
    const auto outward=[&](std::uint8_t speed) {
        for(unsigned i=0;i<56;++i) {
            auto& q=s.shapes[i];q.angle=motion::angle_to({3200,3072},q.position);q.speed=speed;
        }
    };
    const auto scatter=[&](bool diagonal,std::uint8_t speed) {
        for(unsigned i=0;i<56;++i) {
            auto& q=s.shapes[i];q.position={static_cast<std::int16_t>(random.next16_mod(6144)),static_cast<std::int16_t>(random.next16_mod(5888))};
            q.angle=diagonal ? static_cast<std::uint8_t>(random.next16_and(15)-72) : 64;q.speed=speed;
        }
    };
    const auto toggle=[&] { s.state=static_cast<std::uint8_t>(s.state+(s.state&1 ? -1 : 1)); };
    // Transition arms increment fade before the comparison, then the common
    // tail increments it again.255 therefore wraps before that comparison;
    // transition reset255 deliberately becomes0 at the common tail.
    if(s.state<=3) {
        if(phase>2) {
            ++s.fade;
            if(s.fade>=254) { s.pattern=120;s.state=4;set_motion(64,64);s.fade=255;s.flyout_speed=64; }
        } else if(s.fade==255) {
            ++s.pattern;++s.state;
            if(s.state>=4) { s.state=0;s.pattern=120; }
            for(unsigned i=0;i<56;++i) s.shapes[i].angle=static_cast<std::uint8_t>(128-s.shapes[i].angle);
        }
    } else if(s.state<=5) {
        if(phase>4) {
            ++s.fade;
            if(s.fade>=254) { s.pattern=120;s.state=6;outward(16);s.flyout_speed=16;s.fade=255; }
        } else if(s.fade==255) toggle();
    } else if(s.state==6 || s.state==7 || s.state==10 || s.state==11) {
        if(phase==7 || phase==8 || phase==11 || phase==12) {
            ++s.fade;
            if(s.fade>=254) { s.pattern=120;s.state=s.state<10 ? 8 : 12;scatter(true,72);s.flyout_speed=64;s.fade=255; }
        } else if(s.fade==255) toggle();
    } else if(s.state==8 || s.state==9 || s.state==12 || s.state==13) {
        if(phase==9 || phase==10 || phase>=13) {
            ++s.fade;
            if(s.fade>=254) { s.pattern=120;s.state=s.state<12 ? 10 : 14;outward(s.state==14 ? 64 : 16);s.flyout_speed=64;s.fade=255; }
        } else if(s.fade==255) toggle();
    } else if(s.state<=15) {
        for(unsigned i=0;i<56;++i) s.shapes[i].angle=static_cast<std::uint8_t>(s.shapes[i].angle+(s.state==14 ? 2 : -2));
        if(phase>=15) {
            ++s.fade;
            if(s.fade>=254) { s.pattern=124;s.state=16;s.fade=255;scatter(false,192);s.flyout_speed=192; }
        } else if(s.fade==255) toggle();
    } else if(s.state==16 && phase>=254) {
        s.pattern=125;s.state=17;s.fade=255;set_motion(64,16);s.flyout_speed=16;
    }
    ++s.fade;
    // Retain the callback selected at entry, even if this frame transitions
    // into a state that selects a different one at fade0 on the next frame.
    for(unsigned i=0;i<56;++i) {
        auto& q=s.shapes[i];const auto v=motion::polar(q.angle,q.speed);
        q.position={motion::wrap(int(q.position.x)+v.x),motion::wrap(int(q.position.y)+v.y)};
        clip_shape(q,s.clip,s.flyout_speed);
    }
    for(unsigned i=0;i<56;++i) {
        const auto& q=s.shapes[i];const auto pattern=static_cast<std::uint16_t>(s.pattern+(s.state>=17 ? i%3 : 0));
        draw(BackgroundKind::mono,pattern,{motion::wrap(pixels(q.position.x)+24),motion::wrap(pixels(q.position.y)+8)});
    }
    draw(BackgroundKind::disable);
}
void raster_mono(const std::array<std::uint8_t,32>& mask,std::int16_t left,std::int16_t top,
                 std::uint8_t color,const std::function<void(int,int,std::uint8_t)>& write) {
    const auto x=static_cast<std::uint16_t>(left);const auto start=static_cast<std::uint16_t>(int(top)*80+(x>>3));
    for(unsigned y=0;y<16;++y) for(unsigned pixel=0;pixel<16;++pixel) {
        if(!(mask[y*2+pixel/8]&(128>>(pixel%8)))) continue;
        const auto byte=static_cast<std::uint16_t>(start+y*80+((x&7)+pixel)/8);
        if(byte>=32000) continue;
        const unsigned position=byte*8+((x&7)+pixel)%8;
        write(position%640,position/640,color&15);
    }
}
} // namespace th04::portable::yuuka6
