#include "midboss3.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::midboss3 {
namespace {
// Observed DS:1790 flight directions. The last dash exits the playfield;
// indices past eleven are outside the twelve-dash gameplay schedule.
constexpr std::uint8_t fly_angles[]{24,104,152,232,0,96,160,64,224,128,32,96};
int pixels(motion::Subpixel v) { return v>=0 ? v/16 : -((-int(v)+15)/16); }
void emit(const midboss::Sink& sink,midboss::EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
    if(sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
}
}
void System::activate(std::uint16_t frame) {
    auto& a=state_.actor;if(frame==a.start_frame) { a.active=true;a.phase=0;a.phase_frame=0; }
}
void System::reset() { state_.actor.active=false;state_.actor.hp=0; }
void System::update(const midboss::Context& c,bullet::System& bullets,gather::System& gathers,
                    randring::SharedRandomRing& random,const midboss::Sink& sink) {
    auto& a=state_.actor;auto& t=bullets.scratch();
    const auto sound=[&](unsigned id) { emit(sink,midboss::EventType::sound,{},id); };
    const auto hit=[&](unsigned sound_id) {
        emit(sink,midboss::EventType::hit,a.position.current,384,384);
        const auto value=c.hit ? c.hit(a.position.current,{384,384}) : std::uint16_t{0};
        if(value) sound(sound_id);
        return motion::wrap(value);
    };
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto fire=[&](bool fixed=false) {
        emit(sink,midboss::EventType::fire,t.origin,t.angle,t.speed);
        bullets.add(t,c.bullets,random,false,fixed);
    };
    emit(sink,midboss::EventType::homing,a.position.current); // Original publishes before movement.
    if(a.phase==0) {
        a.position.update();a.phase_frame=motion::wrap(int(a.phase_frame)+1);hit(10);
        if(a.phase_frame>=20) {
            ++a.phase;a.phase_frame=0;a.position.velocity={};
            state_.pattern=static_cast<std::uint8_t>(random.next16()&3);
            state_.mirror=static_cast<std::uint8_t>(random.next16()&1);state_.patterns_done=0;
        }
    } else if(a.phase==1) {
        a.position.update();a.phase_frame=motion::wrap(int(a.phase_frame)+1);
        t.spawn_type=1;t.origin=a.position.current;t.origin.y=motion::wrap(int(t.origin.y)-256);
        const int frame=a.phase_frame;
        if(state_.pattern==0) {
            if(frame==2) {
                a.unused_angle=motion::angle_to(a.position.current,c.bullets.player);
                t.spawn_type=2;t.pattern=57;t.group=BG_RING;t.count=32;t.speed=40;t.angle=0;tune();fire();
            }
            if(frame%4==0) { t.group=BG_SPREAD;t.count=2;t.delta=12;t.speed=52;t.angle=a.unused_angle;tune();fire();sound(3); }
            if(frame>=32) { state_.pattern=255;a.phase_frame=0; }
        } else if(state_.pattern==1) {
            if(frame>=32) {
                state_.pattern=255;a.phase_frame=0;t.spawn_type=5;t.pattern=57;
                t.group=BG_RING;t.count=32;t.speed=40;t.angle=static_cast<std::uint8_t>(random.next16());tune();fire(true);sound(9);
            }
        } else if(state_.pattern==2) {
            if(frame==1) a.unused_angle=128;
            if(frame%2==0) {
                t.group=BG_SPREAD;t.count=2;t.delta=18;t.speed=46;t.angle=a.unused_angle;
                a.unused_angle=static_cast<std::uint8_t>(a.unused_angle-8);tune();fire();sound(3);
            }
            if(frame>=32) { state_.pattern=255;a.phase_frame=0; }
        } else if(state_.pattern==3) {
            if(frame==1) a.unused_angle=static_cast<std::uint8_t>(random.next16());
            if(frame%6==0) {
                t.spawn_type=2;t.pattern=76;t.group=BG_RING;t.speed=32;t.angle=a.unused_angle;t.count=24;
                tune();fire(true);sound(9);a.unused_angle=static_cast<std::uint8_t>(a.unused_angle+6);
            }
            if(frame>=32) { state_.pattern=255;a.phase_frame=0; }
        } else if(state_.pattern==255) {
            // After the twelfth dash this block deliberately does not stop
            // velocity or select another attack. The ordinary boundary exits.
            if(state_.patterns_done<=11) {
                auto& g=gathers.scratch();g.center=a.position.current;
                const auto gather_frame=motion::wrap(frame-64);
                if(gather_frame==0 || gather_frame==2 || gather_frame==4) {
                    if(gather_frame==0) g.color=15;else if(gather_frame==2) g.color=9;
                    gathers.add(g,t,true);
                    emit(sink,midboss::EventType::gather,g.center,g.color,static_cast<std::uint16_t>(g.ring_points));
                }
                if(frame==64) a.position.velocity={};
                else if(frame==68) { a.phase_frame=0;state_.pattern=state_.patterns_done&3;a.sprite=0; }
            }
            if(a.phase_frame==1) {
                if(state_.patterns_done>=12) throw std::domain_error("Stage3 flight index outside twelve-dash gameplay schedule");
                const auto angle=state_.mirror ? static_cast<std::uint8_t>(128-fly_angles[state_.patterns_done]) : fly_angles[state_.patterns_done];
                a.position.velocity=motion::polar(angle,32);++state_.patterns_done;a.sprite=1;gathers.scratch().ring_points=8;
            }
        }
        if(a.position.current.y>=5888 || a.position.current.x<=0 || a.position.current.x>=6144) a.phase=3;
        // Boundary exit still executes shot collision. A lethal shot on that
        // frame wins and receives the original awards; do not return early.
        const auto damage=hit(4);
        if(damage) {
            a.hp=motion::wrap(int(a.hp)-damage);a.damaged=1;
            if(a.hp<=0) {
                bullets.set_zap(1);emit(sink,midboss::EventType::zap,{},1);
                const auto units=static_cast<std::uint16_t>(20-state_.patterns_done);
                score_delta_+=static_cast<std::uint16_t>(units*1280u);
                const auto left=motion::wrap(int(a.position.current.x)-1024),top=motion::wrap(int(a.position.current.y)-1024);
                for(unsigned i=0;i<units;++i) {
                    const auto x=motion::wrap(int(left)+random.next16_mod(2048));
                    const auto y=motion::wrap(int(top)+random.next16_mod(2048));
                    emit(sink,midboss::EventType::point,{static_cast<std::int16_t>(std::clamp(int(x),0,6144)),y},1280);
                }
                a.phase=254;a.sprite=4;a.phase_frame=0;a.position.velocity.x=0;
                emit(sink,midboss::EventType::circle,a.position.current,96,48);sound(12);
                emit(sink,midboss::EventType::item,a.position.current,5);
            }
        }
    } else if(a.phase==254) {
        if(a.phase_frame==0) emit(sink,midboss::EventType::shake,{},12);
        a.phase_frame=motion::wrap(int(a.phase_frame)+1);
        if(a.phase_frame%16==0) { ++a.sprite;if(a.sprite>=12) a.phase=255; }
    } else reset();
    const int value=a.hp<=0 ? 0 : (a.hp>=850 ? 128 : int(a.hp)*128/850+1);
    if(a.hp_bar<value) a.hp_bar=motion::wrap(int(a.hp_bar)+1);
    if(a.hp_bar>value) a.hp_bar=static_cast<std::int16_t>(value);
    emit(sink,midboss::EventType::hp,{},static_cast<std::uint16_t>(a.hp_bar));
}
void System::prepare_render(const midboss::Context& c) {
    draws_.clear();auto& a=state_.actor;const auto center=a.position.current;
    if(center.y<=0 || center.y>=5888 || center.x<=0 || center.x>=6144) return;
    const auto draw=[&](motion::Point p,int offset,unsigned pattern,bool white=false) {
        int top=pixels(p.y)+(c.scroll_active ? c.scroll_line : 0);
        if(top<0) top+=400;else if(top>=400) top-=400;
        draws_.push_back({pixels(p.x)+offset,pixels(p.y),top,pattern,white});
    };
    if(a.phase==254) {
        auto radius=motion::wrap(int(a.phase_frame)*16);
        if(radius>=768) { radius=768;++a.defeat_angle; }
        for(unsigned i=0;i<16;++i) {
            const auto delta=motion::polar(a.defeat_angle,radius);
            const motion::Point p{motion::wrap(int(center.x)+delta.x),motion::wrap(int(center.y)+delta.y)};
            if(p.y>-256 && p.y<6144 && p.x>-256 && p.x<6400) draw(p,16,a.sprite);
            a.defeat_angle=static_cast<std::uint8_t>(a.defeat_angle+16);
        }
    } else if(a.phase<=2) {
        int pattern=144;
        if(a.sprite==1) pattern+=(a.phase_frame%32<16 ? (a.phase_frame%16)/4 : 3-(a.phase_frame%16)/4);
        draw({center.x,motion::wrap(int(center.y)-256)},0,static_cast<unsigned>(pattern),a.damaged!=0);a.damaged=0;
    }
}
} // namespace th04::portable::midboss3
