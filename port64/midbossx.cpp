#include "midbossx.hpp"

namespace th04::portable::midbossx {
void System::activate(std::uint16_t frame) {
    if(frame==state_.start_frame) {state_.phase=0;state_.phase_frame=0;state_.active=true;}
}
void System::reset() {state_.active=false;state_.hp=0;}
void System::update(const midboss::Context& c,bullet::System& bullets,
                    randring::SharedRandomRing& random,const midboss::Sink& sink) {
    auto& a=state_;auto& t=bullets.scratch();
    const auto emit=[&](midboss::EventType kind,motion::Point p,unsigned value=0,unsigned count=0) {
        if(sink)sink({kind,p,std::uint16_t(value),std::uint16_t(count)});
    };
    const auto sound=[&](unsigned value) {emit(midboss::EventType::sound,{},value);};
    const auto fire=[&](bool special=false) {
        bullet::tune(t,c.bullets.rank,c.bullets.performance);
        emit(midboss::EventType::fire,t.origin,t.angle,t.speed);
        bullets.add(t,c.bullets,random,special);
    };
    const auto orbit=[&] {
        a.position.previous=a.position.current;
        const auto d=motion::polar(a.unused_angle,a.hp);
        a.position.current={motion::wrap(3072+int(d.x)),motion::wrap(1536+int(d.y))};
        a.unused_angle=std::uint8_t(a.unused_angle-2);
    };
    const auto wave=[&] {
        a.position.previous=a.position.current;
        if(a.phase_frame==1) {a.position.velocity.x=16;a.unused_angle=0;}
        a.position.current.x=motion::wrap(int(a.position.current.x)+a.position.velocity.x);
        if(a.phase<=5 && (a.position.current.x<=256 || a.position.current.x>=5888))
            a.position.velocity.x=motion::wrap(-int(a.position.velocity.x));
        a.position.current.y=motion::wrap(1536+int(motion::polar(a.unused_angle,a.hp).y));
        a.unused_angle=std::uint8_t(a.unused_angle+2);
    };
    const auto ring=[&](unsigned count,unsigned speed) {
        t.group=BG_RING;t.count=std::uint8_t(count);t.angle=std::uint8_t(random.next16());
        t.speed=std::uint8_t(speed);fire();
    };
    const auto tick=[&] {a.phase_frame=motion::wrap(int(a.phase_frame)+1);};
    const auto advance=[&](int clock) {a.phase_frame=std::int16_t(clock);++a.phase;};
    // Original saves the pre-motion origin once, including on exit/unknown
    // phase frames. Moving it after orbit/wave changes every spawned bullet.
    t.origin=a.position.current;t.spawn_type=1;
    switch(a.phase) {
    case 0:case 1:case 2:
        orbit();tick();
        if(a.phase==1) {if(a.hp<896)a.hp=motion::wrap(int(a.hp)+8);}
        else if(a.hp>128)a.hp=motion::wrap(int(a.hp)-32);
        if(a.phase_frame>=128) {
            if(c.frame%16==0) {
                if(a.phase==2) {t.spawn_type=5;t.pattern=57;ring(32,a.phase_frame/4+10);sound(3);}
                else ring(32,48);
            }
            if(a.phase_frame>=320)advance(0);
        }
        break;
    case 3:
        if(a.phase_frame<128)orbit();
        else {
            wave();
            if(c.frame%16==0) {
                t.spawn_type=2;t.special_motion=135;t.group=BG_SPREAD;t.count=5;t.delta=12;
                t.pattern=59;t.speed=32;t.angle=std::uint8_t(random.next16_and(15)+184);
                bullets.set_special_parameter(2);fire(true);sound(9);
            }
            if(a.hp<768)a.hp=motion::wrap(int(a.hp)+8);
        }
        tick();if(a.phase_frame>=640)advance(0);
        break;
    case 4:
        wave();
        if(a.phase_frame>=160 && c.frame%16==0) {ring(32,32);ring(16,48);}
        tick();if(a.phase_frame>=440)advance(2);
        break;
    case 5: {
        wave();const int f=a.phase_frame;
        if(f==250 || f==258 || f==266 || f==274 || f==350 || f==358 || f==366 || f==374 || f==450) {
            sound(9);emit(midboss::EventType::item,a.position.current,f==450 ? 5 : (f<350 ? 2 : 3));
        } else if(f==290 || f==298 || f==306 || f==314 || f==390 || f==398 || f==406 || f==414 ||
                  f==490 || f==498 || f==506 || f==514) {
            sound(3);t.group=BG_SPREAD_AIMED;t.count=5;t.delta=6;t.angle=0;t.speed=64;fire();
        }
        tick();if(a.phase_frame>=520)advance(2);
        break;
    }
    case 6:
        wave();tick();if(a.position.current.x<=-256 || a.position.current.x>=6400)reset();
        break;
    default:break;
    }
}
void System::prepare_render(const midboss::Context& c) {
    draws_.clear();const auto p=state_.position.current;
    if(p.y<=-256 || p.x<=-256 || p.x>=6272)return;
    const auto pixels=[](int v) {return v>=0 ? v/16 : -((-v+15)/16);};
    int top=pixels(p.y)+(c.scroll_active ? c.scroll_line : 0);
    if(top<0)top+=400;else if(top>=400)top-=400;
    draws_.push_back({pixels(p.x)+16,pixels(p.y),top,148u+unsigned(c.frame%16)/4u,false});
}
}
