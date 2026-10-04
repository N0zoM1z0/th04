#include "midboss4.hpp"
#include <algorithm>
namespace th04::portable::midboss4 {
namespace {
std::uint8_t byte(int v) { return static_cast<std::uint8_t>(v); }
int pixels(motion::Subpixel v) { return v>=0 ? v/16 : -((-int(v)+15)/16); }
void emit(const midboss::Sink& sink,midboss::EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
    if(sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
}
}
void System::activate(std::uint16_t frame) {
    auto& a=state_.actor;if(frame==a.start_frame) { a.active=true;a.phase=0;a.phase_frame=0; }
}
void System::reset() { state_.actor.active=false;state_.actor.hp=0; }
void System::update(const midboss::Context& c,bullet::System& bullets,gather::System&,
                    randring::SharedRandomRing& random,const midboss::Sink& sink) {
    auto& a=state_.actor;auto& t=bullets.scratch();
    const auto sound=[&](unsigned id) { emit(sink,midboss::EventType::sound,{},id); };
    const auto hit=[&](unsigned sound_id) {
        emit(sink,midboss::EventType::hit,a.position.current,384,384);
        const auto value=c.hit ? c.hit(a.position.current,{384,384}) : std::uint16_t{0};
        if(value) sound(sound_id);return motion::wrap(value);
    };
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto fire=[&](bool fixed=false) {
        emit(sink,midboss::EventType::fire,t.origin,t.angle,t.speed);bullets.add(t,c.bullets,random,false,fixed);
    };
    emit(sink,midboss::EventType::homing,a.position.current);
    if(a.phase==0) {
        a.position.update();a.phase_frame=motion::wrap(int(a.phase_frame)+1);hit(10);
        if(a.phase_frame>=48) { ++a.phase;a.phase_frame=0;a.position.velocity={};state_.unused_state=state_.pattern=state_.patterns_done=0; }
    } else if(a.phase==1) {
        a.position.update();a.phase_frame=motion::wrap(int(a.phase_frame)+1);
        t.spawn_type=1;t.origin=a.position.current;t.origin.y=motion::wrap(int(t.origin.y)-256);
        const int f=a.phase_frame;
        if(state_.pattern<4 && f<=24) {
            // Signed IDIV truncates toward zero; an overflowed clock must not
            // silently become unsigned or use arithmetic-shift rounding.
            a.sprite=byte(f/8);
            if(f==24) {
                sound(6);
                if(state_.pattern==2) { t.angle=a.position.current.x<3072 ? 54 : 86;++state_.aim_toggle; }
                else if(state_.pattern==3) t.angle=224;
            }
        } else if(state_.pattern==0) {
            if(f<128) {
                if((f&3)==0) {
                    t.group=BG_SPREAD_AIMED;t.count=2;t.delta=6;
                    t.speed=byte(random.next16_mod(24)+32);t.angle=byte(random.next16_mod(96)-48);tune();fire();
                    t.spawn_type=2;t.pattern=58;t.speed=byte(random.next16_mod(24)+32);t.angle=byte(random.next16_mod(96)-48);
                    fire();sound(3); // Second shot deliberately does not retune.
                }
            } else if(f<152) a.sprite=byte(motion::wrap(159-f)/8);
            else { a.phase_frame=0;state_.pattern=255; }
        } else if(state_.pattern==1) {
            if(f<=120) {
                if((f&7)==0) {
                    t.group=BG_SPREAD_AIMED;t.count=byte((random.next16()&3)*2+1);t.delta=byte((random.next16()&7)+10);
                    t.speed=50;t.angle=0;tune();fire(true);
                }
                const unsigned mod32=static_cast<std::uint16_t>(f-25)&31;
                if(mod32==0) a.unused_angle=motion::angle_to(a.position.current,c.bullets.player);
                if((mod32&3)==0) {
                    t.spawn_type=2;t.group=BG_SINGLE;t.pattern=92;t.speed=byte(int(mod32)*3+40);t.angle=a.unused_angle;
                    tune();fire(true);sound(3);
                }
            } else if(f<144) a.sprite=byte(motion::wrap(151-f)/8);
            else { a.phase_frame=0;state_.pattern=255; }
        } else if(state_.pattern==2) {
            if(f<=136) {
                if(((f-25)&15)==0) {
                    t.group=BG_STACK;
                    t.angle=(state_.aim_toggle&1) ? motion::angle_to(a.position.current,c.bullets.player) : byte(t.angle-8);
                    const auto previous_angle=t.angle;sound(3);t.spawn_type=2;t.pattern=58;tune();t.speed=16;t.count=12;t.delta=7;fire(true);
                    t.angle=byte((a.position.current.x>3072 ? -96 : 96)-t.angle);fire(true);t.angle=previous_angle;
                }
            } else if(f<160) a.sprite=byte(motion::wrap(165-f)/8);
            else { a.phase_frame=0;state_.pattern=255; }
        } else if(state_.pattern==3) {
            if(f<128) {
                // Original tests bit1, rather than a modulo-four equality.
                if((f&2)==0) {
                    t.group=BG_SPREAD;t.count=3;t.delta=6;t.speed=60;
                    if(a.position.current.x<3072) t.angle=byte(128-t.angle);
                    tune();fire();if(a.position.current.x<3072) t.angle=byte(128-t.angle);sound(3);t.angle=byte(t.angle+6);
                }
            } else if(f<152) a.sprite=byte(motion::wrap(159-f)/8);
            else { a.phase_frame=0;state_.pattern=255; }
        } else if(state_.pattern==255) {
            if(f==1) a.position.velocity.x=a.position.current.x>=2880 ? -64 : 64;
            else if(state_.patterns_done<8) {
                if(a.position.current.x<=768 || a.position.current.x>=5376) {
                    a.position.velocity.x=0;a.phase_frame=0;++state_.patterns_done;state_.pattern=state_.patterns_done&3;
                }
            } else if(a.position.current.x<=-512 || a.position.current.x>=6656) a.phase=3;
        }
        if(a.position.current.y>=5888 || a.position.current.x<=0 || a.position.current.x>=6144) a.phase=255;
        // Shot collision still runs after a boundary exit; a lethal hit wins.
        const auto damage=hit(4);
        if(damage) {
            a.hp=motion::wrap(int(a.hp)-damage);a.damaged=1;
            if(a.hp<=0) {
                bullets.set_zap(1);emit(sink,midboss::EventType::zap,{},1);
                const auto units=static_cast<std::uint16_t>(30-state_.patterns_done);score_delta_+=static_cast<std::uint16_t>(units*1280u);
                const auto left=motion::wrap(int(a.position.current.x)-1024),top=motion::wrap(int(a.position.current.y)-1024);
                for(unsigned i=0;i<units;++i) {
                    const auto x=motion::wrap(int(left)+random.next16_mod(2048)),y=motion::wrap(int(top)+random.next16_mod(2048));
                    emit(sink,midboss::EventType::point,{static_cast<std::int16_t>(std::clamp(int(x),0,6144)),y},1280);
                }
                emit(sink,midboss::EventType::shake,{},12);a.phase=254;a.sprite=4;a.phase_frame=0;a.position.velocity.x=0;
                emit(sink,midboss::EventType::circle,a.position.current,96,48);sound(12);
                emit(sink,midboss::EventType::item,a.position.current,a.start_frame==2800 ? 4 : 5);
            }
        }
    } else if(a.phase==254) {
        a.position.velocity={};a.position.update();a.phase_frame=motion::wrap(int(a.phase_frame)+1);
        if(a.phase_frame%16==0) { ++a.sprite;if(a.sprite>=12) { ++a.phase;a.hp=0; } }
    } else {
        reset();
        // The first encounter re-arms the same actor for frame5600, even on
        // timeout. Reset only owned fields and do not render HP on this return.
        if(a.start_frame==2800) {
            a.start_frame=5600;a.position.current=a.position.previous={3840,-512};a.position.velocity={-64,32};a.hp=1200;a.sprite=0;a.phase_frame=0;return;
        }
    }
    const int value=a.hp<=0 ? 0 : (a.hp>=1200 ? 128 : int(a.hp)*128/1200+1);
    if(a.hp_bar<value) a.hp_bar=motion::wrap(int(a.hp_bar)+1);
    if(a.hp_bar>value) a.hp_bar=static_cast<std::int16_t>(value);
    emit(sink,midboss::EventType::hp,{},static_cast<std::uint16_t>(a.hp_bar));
}
void System::prepare_render(const midboss::Context& c) {
    draws_.clear();auto& a=state_.actor;const auto center=a.position.current;
    // Preserve the original small-point clip, even for these64x64 sprites.
    if(center.y<=0 || center.y>=5888 || center.x<=0 || center.x>=6144) return;
    const auto draw=[&](motion::Point p,int offset,unsigned pattern,bool white=false) {
        int top=pixels(p.y)+(c.scroll_active ? c.scroll_line : 0);
        if(top<0) top+=400;else if(top>=400) top-=400;
        draws_.push_back({pixels(p.x)+offset,pixels(p.y),top,pattern,white});
    };
    if(a.phase<=2) {
        draw({center.x,motion::wrap(int(center.y)-256)},0,156+a.sprite+(center.x>=3072 ? 4u : 0u),a.damaged!=0);a.damaged=0;
    } else if(a.phase==254) {
        auto radius=motion::wrap(int(a.phase_frame)*16);if(radius>=768) { radius=768;++a.defeat_angle; }
        for(unsigned i=0;i<16;++i) {
            const auto delta=motion::polar(a.defeat_angle,radius);const motion::Point p{motion::wrap(int(center.x)+delta.x),motion::wrap(int(center.y)+delta.y)};
            if(p.y>-256 && p.y<6144 && p.x>-256 && p.x<6400) draw(p,16,a.sprite);
            a.defeat_angle=byte(a.defeat_angle+16);
        }
    }
}
} // namespace th04::portable::midboss4
