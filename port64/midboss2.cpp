#include "midboss2.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::midboss2 {
namespace {
int pixels(motion::Subpixel v) { return v>=0 ? v/16 : -((-int(v)+15)/16); }
void emit(const midboss::Sink& sink,midboss::EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
    if(sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
}
} // namespace
void System::activate(std::uint16_t frame) {
    auto& a=state_.actor;
    if(frame==a.start_frame) { a.active=true;a.phase=0;a.phase_frame=0; }
}
void System::reset() { state_.actor.active=false;state_.actor.hp=0; }
void System::update(const midboss::Context& c,bullet::System& bullets,gather::System& gathers,
                    randring::SharedRandomRing& random,const midboss::Sink& sink) {
    auto& a=state_.actor;
    auto& t=bullets.scratch();
    const auto sound=[&](unsigned id) { emit(sink,midboss::EventType::sound,{},id); };
    const auto fire=[&](bool special=false) {
        emit(sink,midboss::EventType::fire,t.origin,t.angle,t.speed);
        bullets.add(t,c.bullets,random,special);
    };
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto hit=[&] {
        emit(sink,midboss::EventType::hit,a.position.current,384,384);
        const auto damage=c.hit ? c.hit(a.position.current,{384,384}) : std::uint16_t{0};
        // 10 is the hit sound ID, not a damage cap. Entry is invulnerable but
        // still consumes colliding shots and plays this sound.
        if(damage) sound(10);
        return motion::wrap(damage);
    };
    const auto defeat=[&] {
        a.phase=2;a.sprite=0;a.phase_frame=0;a.position.velocity={0,-16};
        emit(sink,midboss::EventType::circle,a.position.current,128,48);sound(12);
    };
    emit(sink,midboss::EventType::homing,a.position.current); // Before movement.
    if(a.phase==0) {
        a.position.update();a.phase_frame=motion::wrap(int(a.phase_frame)+1);hit();
        if(a.phase_frame>=96) {
            ++a.phase;a.phase_frame=0;a.position.velocity={};
            state_.pattern=0;state_.direction=1;state_.patterns_done=0;
        }
    } else if(a.phase==1) {
        a.position.update();a.phase_frame=motion::wrap(int(a.phase_frame)+1);
        t.spawn_type=1;t.origin=a.position.current;t.origin.y=motion::wrap(int(t.origin.y)-256);
        const int frame=a.phase_frame;
        if(state_.pattern==0) {
            if(frame%8==0) {
                sound(3);t.angle=static_cast<std::uint8_t>((state_.direction<<5)+32);
                if((frame/8)&1) {
                    t.spawn_type=4;t.pattern=57;t.group=BG_SINGLE;t.speed=42;tune();fire();t.delta=15;
                } else t.delta=10;
                t.group=BG_SPREAD;t.count=6;t.speed=36;tune();fire();
            }
            if(frame>=64) { a.phase_frame=0;state_.pattern=255; }
        } else if(state_.pattern==1) {
            if(frame%8==0) {
                sound(3);t.angle=static_cast<std::uint8_t>((state_.direction<<5)+32);
                t.speed=static_cast<std::uint8_t>(frame/2+32);t.group=BG_RING;t.count=32;tune();fire();
            }
            if(frame>=32) { a.phase_frame=0;state_.pattern=255; }
        } else if(state_.pattern==2) {
            if(frame%4==0) {
                sound(3);t.speed=64;t.group=BG_SINGLE;t.angle=static_cast<std::uint8_t>((state_.direction<<5)+8);
                tune();fire();
                // Only the first shot is tuned. Retain its tuned group/count
                // for the other three directions, especially Hard/Lunatic.
                for(unsigned delta:{16u,56u,48u}) { t.angle=static_cast<std::uint8_t>((state_.direction<<5)+delta);fire(); }
            }
            if(frame>=32) { a.phase_frame=0;state_.pattern=255; }
        } else if(state_.pattern==3) {
            const int aimed_frame=motion::wrap(frame-1);
            if(aimed_frame==0) a.unused_angle=motion::angle_to(a.position.current,c.bullets.player);
            if(aimed_frame%8==0) {
                sound(3);t.speed=40;t.group=BG_SPREAD;t.count=5;t.delta=16;t.angle=a.unused_angle;tune();fire();
                t.speed=10;t.angle=motion::angle_to(a.position.current,c.bullets.player);
                t.pattern=76;t.group=BG_SINGLE;t.special_motion=255;
            }
            if(aimed_frame%32>=24) { t.spawn_type=4;t.speed=static_cast<std::uint8_t>(t.speed+10);fire(true); }
            if(aimed_frame>=64) { a.phase_frame=0;state_.pattern=255; }
        } else if(state_.pattern==255) {
            auto& g=gathers.scratch();g.center=a.position.current;
            const auto gather_frame=motion::wrap(frame-48);
            if(gather_frame==0 || gather_frame==2 || gather_frame==4) {
                if(gather_frame==0) g.color=15;else if(gather_frame==2) g.color=7;
                gathers.add(g,t,true);
                emit(sink,midboss::EventType::gather,g.center,g.color,static_cast<std::uint16_t>(g.ring_points));
            }
            if(frame==48) a.position.velocity.x=0;
            else if(frame==52) {
                a.phase_frame=0;if(state_.direction==1) a.sprite=0;
                ++state_.patterns_done;state_.pattern=state_.patterns_done&3;
                // Timeout branches before shot collision and all rewards.
                if(state_.patterns_done>16) { defeat();goto hp; }
            } else if(frame==1) {
                g.ring_points=8;g.radius=1536;
                if(state_.direction==1) {
                    if(random.next16()&1) { a.sprite=1;state_.direction=0;a.position.velocity.x=-48; }
                    else { a.sprite=2;state_.direction=2;a.position.velocity.x=48; }
                } else if(state_.direction==0) { state_.direction=1;a.position.velocity.x=48;a.sprite=2; }
                else if(state_.direction==2) { state_.direction=1;a.position.velocity.x=-48;a.sprite=1; }
            }
        }
        {
            const auto damage=hit();
            if(damage) {
                a.hp=motion::wrap(int(a.hp)-damage);
                a.damaged=1;
                if(a.hp>0) sound(4);
                else {
                    bullets.zap();emit(sink,midboss::EventType::zap,{},1);
                    const auto units=static_cast<std::uint16_t>(18-state_.patterns_done);
                    // The original multiplies these unsigned 16-bit values
                    // before adding to the 32-bit pending score owner.
                    score_delta_+=static_cast<std::uint16_t>(units*1280u);
                    const auto left=motion::wrap(int(a.position.current.x)-1024);
                    const auto top=motion::wrap(int(a.position.current.y)-1024);
                    for(unsigned i=0;i<units;++i) {
                        const int x=motion::wrap(int(left)+random.next16_mod(2048));
                        const auto y=motion::wrap(int(top)+random.next16_mod(2048));
                        emit(sink,midboss::EventType::point,{static_cast<std::int16_t>(std::clamp(x,0,6144)),y},1280);
                    }
                    emit(sink,midboss::EventType::item,a.position.current,4);
                    emit(sink,midboss::EventType::shake,{},12);defeat();
                }
            }
        }
    } else if(a.phase==2) {
        a.position.update();a.phase_frame=motion::wrap(int(a.phase_frame)+1);
        if(a.position.current.y<=0) { ++a.phase;a.hp=0; }
        if(c.frame%16==0) emit(sink,midboss::EventType::circle,a.position.current,128,16);
    } else reset();
hp:
    const int target=a.hp<=0 ? 0 : (a.hp>=750 ? 128 : int(a.hp)*128/750+1);
    if(c.hp_previous)a.hp_bar=*c.hp_previous;
    if(a.hp_bar<target) a.hp_bar=motion::wrap(int(a.hp_bar)+1);
    if(a.hp_bar>target) a.hp_bar=static_cast<std::int16_t>(target);
    if(c.hp_previous)*c.hp_previous=a.hp_bar;
    emit(sink,midboss::EventType::hp,{},static_cast<std::uint16_t>(a.hp_bar));
}
void System::prepare_render(const midboss::Context& c) {
    draws_.clear();auto& a=state_.actor;
    if(a.position.current.y<=0 || a.phase>2) return;
    // The target leaves SI undefined for corrupt sprites above2. Reject that
    // state explicitly instead of inventing a cel or host register value.
    if(a.sprite>2) throw std::domain_error("Stage2 midboss sprite outside gameplay range");
    const unsigned pattern=a.sprite==0 ? 146+(c.frame%16)/4 : (a.sprite==1 ? 150 : 152)+(c.frame%8)/4;
    const auto top=motion::wrap(int(a.position.current.y)-256);
    int vram_top=pixels(top)+(c.scroll_active ? c.scroll_line : 0);
    if(vram_top<0) vram_top+=400;else if(vram_top>=400) vram_top-=400;
    draws_.push_back({pixels(a.position.current.x),pixels(top),vram_top,pattern,a.damaged!=0});
    a.damaged=0; // Consumed only when the generic sprite call actually runs.
}
} // namespace th04::portable::midboss2
