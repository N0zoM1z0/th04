#include "midboss.hpp"
#include <algorithm>

namespace th04::portable::midboss {
namespace {
int pixels(motion::Subpixel value) {
    return value>=0 ? value/16 : -((-int(value)+15)/16);
}
int vram(motion::Subpixel y,const Context& context) {
    int top=pixels(y)+(context.scroll_active ? context.scroll_line : 0);
    // Original helper adjusts at most once; do not replace this with modulo
    // for deliberately out-of-range isolated state controls.
    if (top<0) top+=400;
    else if (top>=400) top-=400;
    return top;
}
void emit(const Sink& sink,EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
    if (sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
}
} // namespace
System::System() {
    state_.position.current=state_.position.previous={3072,5888};
    state_.position.velocity={0,16};
}
void System::activate(std::uint16_t frame) {
    if (frame!=state_.start_frame) return;
    state_.active=true;state_.phase=0;state_.phase_frame=0;
}
void System::reset() { state_.active=false;state_.hp=0; }
void System::update(const Context& context,bullet::System& bullets,
                    randring::SharedRandomRing& random,const Sink& sink) {
    const auto move=[this] { state_.position.update(); };
    const auto circle=[&](unsigned radius,unsigned count) {
        emit(sink,EventType::circle,state_.position.current,radius,count);
    };
    const auto sound=[&](unsigned id) { emit(sink,EventType::sound,{},id); };
    const auto hit=[&](motion::Point radius) {
        emit(sink,EventType::hit,state_.position.current,static_cast<std::uint16_t>(radius.x),static_cast<std::uint16_t>(radius.y));
        return context.hit ? context.hit(state_.position.current,radius) : std::uint16_t{0};
    };
    const auto homing=[&] { emit(sink,EventType::homing,state_.position.current); };
    const auto defeat=[&] {
        state_.phase=254;state_.sprite=4;state_.phase_frame=0;
        state_.position.velocity.y=0;circle(128,48);sound(12);
        emit(sink,EventType::scroll,{},4);
    };
    if (state_.phase==0) {
        state_.position.velocity.y=-16;move();
        const auto tiles=[&](unsigned first) {
            for (unsigned i=0;i<4;++i) {
                auto p=state_.position.current;
                if (!(i&1)) p.x=motion::wrap(int(p.x)-256);
                if (!(i&2)) p.y=motion::wrap(int(p.y)-256);
                emit(sink,EventType::tile,p,first+(i&1)+(i>=2 ? 16 : 0));
            }
        };
        tiles(40);state_.phase_frame=motion::wrap(int(state_.phase_frame)+1);
        if (state_.phase_frame>=288) {
            state_.phase=1;state_.phase_frame=0;state_.position.velocity.y=2;
            tiles(42);state_.sprite=136;
            state_.position.current.y=motion::wrap(int(state_.position.current.y)-64+context.scroll_delta);
            state_.vram_y=static_cast<std::int16_t>(vram(state_.position.current.y,context));
            circle(48,32);sound(9);
        }
    } else if (state_.phase==1 || state_.phase==2) {
        const auto phase=state_.phase;
        move();homing();state_.phase_frame=motion::wrap(int(state_.phase_frame)+1);
        if (phase==1) {
            if (state_.sprite<139) {
                if (state_.phase_frame%8==0) ++state_.sprite;
            } else if (state_.phase_frame>=96) {
                state_.phase=2;state_.phase_frame=0;state_.sprite=140;
                state_.position.current.y=motion::wrap(int(state_.position.current.y)-256);
                state_.vram_y=static_cast<std::int16_t>(vram(motion::wrap(int(state_.position.current.y)-256),context));
                circle(48,32);sound(9);
            }
        } else if (state_.sprite<146) {
            if (state_.phase_frame%8==0) state_.sprite=static_cast<std::uint8_t>(state_.sprite+2);
        } else { state_.phase=3;state_.phase_frame=0; }
        if (hit(phase==1 ? motion::Point{256,192} : motion::Point{384,256})) sound(10);
    } else if (state_.phase==3) {
        move();
        if (context.scroll_speed>2) defeat();
        else {
            homing();state_.phase_frame=motion::wrap(int(state_.phase_frame)+1);
            const auto damage=motion::wrap(hit({384,256}));
            auto& scratch=bullets.scratch();
            scratch.spawn_type=1;scratch.origin=state_.position.current;
            scratch.origin.y=motion::wrap(int(scratch.origin.y)-16);
            if (state_.position.current.y<4096) {
                if (state_.phase_frame==1) state_.pattern_angle=1;
                if (state_.phase_frame%8==0) {
                    scratch.spawn_type=2;scratch.pattern=76;scratch.angle=state_.pattern_angle;
                    scratch.speed=32;scratch.group=0;scratch.special_motion=255;
                    bullet::tune(scratch,context.bullets.rank,context.bullets.performance);
                    const auto fire=[&] {
                        emit(sink,EventType::fire,scratch.origin,scratch.angle,scratch.speed);
                        bullets.add(scratch,context.bullets,random,true);
                    };
                    fire();scratch.angle=static_cast<std::uint8_t>(128-state_.pattern_angle);fire();
                    state_.pattern_angle=static_cast<std::uint8_t>(state_.pattern_angle+12);
                }
            }
            if (damage) {
                state_.hp=motion::wrap(int(state_.hp)-damage);
                if (state_.hp>0) { state_.damaged=1;sound(4); }
                else {
                    bullets.zap();emit(sink,EventType::zap,{},1);
                    score_delta_+=6400;
                    const auto left=motion::wrap(int(state_.position.current.x)-1024);
                    const auto top=motion::wrap(int(state_.position.current.y)-1024);
                    for (unsigned i=0;i<5;++i) {
                        const int x=motion::wrap(int(left)+random.next16_mod(2048));
                        const auto y=motion::wrap(int(top)+random.next16_mod(2048));
                        emit(sink,EventType::point,{static_cast<std::int16_t>(std::clamp(x,0,6144)),y},1280);
                    }
                    defeat();
                }
            }
        }
    } else if (state_.phase==254) {
        if (state_.phase_frame==0) emit(sink,EventType::shake,{},12);
        state_.phase_frame=motion::wrap(int(state_.phase_frame)+1);
        if (state_.phase_frame%16==0) {
            ++state_.sprite;
            if (state_.sprite>=12) state_.phase=255;
        }
    } else reset();
    const int current=state_.hp<=0 ? 0 : (state_.hp>=620 ? 128 : int(state_.hp)*128/620+1);
    if (state_.hp_bar<current) state_.hp_bar=motion::wrap(int(state_.hp_bar)+1);
    if (state_.hp_bar>current) state_.hp_bar=static_cast<std::int16_t>(current);
    emit(sink,EventType::hp,{},static_cast<std::uint16_t>(state_.hp_bar));
}
void System::prepare_render(const Context& context) {
    draws_.clear();
    const auto draw=[&](motion::Point center,int left_offset,unsigned pattern,bool white=false) {
        draws_.push_back({pixels(center.x)+left_offset,pixels(center.y),vram(center.y,context),pattern,white});
    };
    const auto center=state_.position.current;
    if (state_.phase==1) draw(center,16,state_.sprite);
    else if (state_.phase==2 || state_.phase==3) {
        auto top=center,bottom=center;
        top.y=motion::wrap(int(top.y)-256);bottom.y=motion::wrap(int(bottom.y)+256);
        if (state_.phase==2) { draw(top,0,state_.sprite);draw(bottom,0,unsigned(state_.sprite)+1); }
        else {
            draw(top,0,(context.frame>>3)%5+147,state_.damaged!=0);
            draw(bottom,0,146,state_.damaged!=0);state_.damaged=0;
        }
    } else if (state_.phase==254) {
        auto radius=motion::wrap(int(state_.phase_frame)*16);
        if (radius>=768) { radius=768;++state_.defeat_angle; }
        for (unsigned i=0;i<16;++i) {
            const auto delta=motion::polar(state_.defeat_angle,radius);
            motion::Point p{motion::wrap(int(center.x)+delta.x),motion::wrap(int(center.y)+delta.y)};
            if (p.y>-256 && p.y<6144 && p.x>-256 && p.x<6400) draw(p,16,state_.sprite);
            state_.defeat_angle=static_cast<std::uint8_t>(state_.defeat_angle+16);
        }
    }
}
} // namespace th04::portable::midboss
