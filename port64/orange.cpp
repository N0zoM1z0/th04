#include "orange.hpp"
#include <algorithm>

namespace th04::portable::orange {
namespace {
std::uint8_t byte(int value) { return static_cast<std::uint8_t>(value); }
void emit(const Sink& sink,EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
    if (sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
}
void explosion(Explosion& e,motion::Point center,unsigned type) {
    e.alive=1;e.age=0;e.center=center;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if (type==1) e.angle_offset=32;
    else if (type==2) e.angle_offset=224;
    else if (type==3) e.delta={208,112};
    else if (type==4) e.delta={112,208};
    // The unused byte and the other slot survive the original typed add.
}
} // namespace
System::System() { state_.position.current=state_.position.previous={3072,640}; }
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,
                    spark::System& sparks,randring::SharedRandomRing& random,const Sink& sink) {
    auto& s=state_;auto& t=bullets.scratch();auto& g=gathers.scratch();
    const auto center=[&] { return s.position.current; };
    const auto sound=[&](unsigned id) { emit(sink,EventType::sound,{},id); };
    const auto gather_only=[&] { gathers.add(g,t,true); };
    const auto circle=[&](motion::Point p) { emit(sink,EventType::circle,p);s.circle_color=15; };
    const auto fire=[&](bool special=false,bool fixed=false) {
        bullets.add(t,c.bullets,random,special,fixed,[&](const bullet::Event& e) {
            if (e.type==bullet::EventType::gather) gathers.request(e);
        });
    };
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto small=[&](unsigned type) { explosion(s.small[s.small[0].alive ? 1 : 0],center(),type);sound(15); };
    const auto hit=[&](motion::Point radius,unsigned se) {
        emit(sink,EventType::hit,center(),static_cast<std::uint16_t>(radius.x),static_cast<std::uint16_t>(radius.y));
        const auto damage=c.hit ? c.hit(center(),radius) : std::uint16_t{0};
        if (damage) sound(se);
        return damage;
    };
    const auto increment=[&] { s.phase_frame=motion::wrap(int(s.phase_frame)+1); };
    const auto hit_phase=[&] {
        increment();s.damage=byte(hit(s.hitbox_radius,4));
        s.hp=motion::wrap(int(s.hp)-s.damage);return s.hp<=s.end_hp;
    };
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;
        s.score_delta+=static_cast<std::uint16_t>(units*1280);
        const auto left=motion::wrap(int(center().x)-1024),top=motion::wrap(int(center().y)-1024);
        for (unsigned i=0;i<units;++i) {
            const int x=motion::wrap(int(left)+random.next16_mod(2048));
            const auto y=motion::wrap(int(top)+random.next16_mod(2048));
            emit(sink,EventType::point,{static_cast<std::int16_t>(std::clamp(x,0,6144)),y},1280);
        }
        s.timed_out=0;
    };
    const auto next_phase=[&](std::int16_t end_hp) {
        small(1);
        if (!s.timed_out) {
            bullets.clear();
            const auto left=motion::wrap(int(center().x)-1024),top=motion::wrap(int(center().y)-1024);
            for (unsigned i=0;i<5;++i) {
                const auto x=motion::wrap(int(left)+random.next16_mod(2048));
                const auto y=motion::wrap(int(top)+random.next16_mod(2048));
                const unsigned type=c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0);
                emit(sink,EventType::item,{x,y},type);
            }
        }
        s.timed_out=1;++s.phase;s.phase_frame=0;s.mode=0;s.patterns_or_bonus=0;
        s.hp=s.end_hp;s.end_hp=end_hp;
    };
    const auto seek_center=[&] {
        if (center().x<3056) s.position.velocity.x=24;
        else if (center().x>3088) s.position.velocity.x=-24;
        if (center().y<1264) s.position.velocity.y=12;
        else if (center().y>1296) s.position.velocity.y=-12;
        // Within the dead band, retain the velocity rather than stopping.
        s.position.update();
    };
    const auto phase_entry=[&] {
        const auto relative=motion::wrap(int(s.phase_frame)-70);
        if (relative==0) { g.color=7;gather_only(); }
        else if (relative==2) { g.color=6;gather_only(); }
        else if (relative==4) gather_only();
        if (s.phase_frame<16) return 1;
        if (s.phase_frame==16) {
            const int x=random.next16_mod(5120)+512,y=random.next16_mod(1536)+1024;
            s.position.velocity={static_cast<std::int16_t>(motion::wrap(x-center().x)/64),
                                 static_cast<std::int16_t>(motion::wrap(y-center().y)/64)};
            g.radius=1536;g.ring_points=8;
        }
        if (s.phase_frame<70) { s.position.update();return 0; }
        if (s.phase_frame==70) { circle(center());return 0; }
        return s.phase_frame<86 ? 1 : 2;
    };
    g.center=center();
    switch (s.phase) {
    case 0:
        if (s.phase_frame==0) { s.hp=3050;s.end_hp=1950;s.palette_zero={0,0,96};s.palette_changed=1; }
        increment();
        if (s.phase_frame==192) {
            s.sprite=byte(s.sprite+2);sound(8);
            g.center={motion::wrap(int(center().x)+128),motion::wrap(int(center().y)-640)};
            g.radius=5120;g.ring_points=32;g.angle_delta=3;g.color=7;
        } else if (s.phase_frame>320) {
            if (s.phase_frame==336) g.color=6;
            if ((s.phase_frame&7)==0) gather_only();
            if (s.phase_frame>=352) {
                ++s.phase;s.phase_frame=0;sound(13);s.additional[15]=0;s.additional[14]=255;
                s.background=Background::orange;s.tile_column=0;
            }
        }
        hit({256,256},10);break;
    case 1:
        increment();
        if (s.phase_frame>=32) {
            g.radius=1024;g.angle_delta=2;g.ring_points=8;
            s.phase=2;s.phase_frame=0;s.mode=0;s.sprite=byte(s.sprite+2);
            t.spawn_type=1;t.origin=center();t.group=38;t.count=16;t.speed=64;t.angle=0;tune();
            for (unsigned i=0;i<3;++i) { fire();t.speed=byte(t.speed-16); }
            sound(6);
        }
        hit({256,256},10);break;
    case 2: {
        bool timed_out=false;
        if (s.mode==0) {
            s.phase_frame=0;
            do { s.mode=byte(random.next16_and(3)+1); } while (s.additional[14]==s.mode);
            s.additional[14]=s.mode;++s.additional[15];timed_out=s.additional[15]>=16;
        } else if (s.mode<=4 && phase_entry()==2) {
            if (s.mode==1) {
                if (s.phase_frame==86) {
                    const bool reverse=random.next16_and(1)!=0;
                    s.angle=reverse ? 128 : 0;s.patterns_or_bonus=reverse ? 245 : 11;
                }
                if ((c.frame&1)==0) {
                    t.spawn_type=1;t.origin=center();t.group=38;t.count=2;t.angle=s.angle;t.speed=30;fire();
                    t.angle=byte(t.angle+5);t.speed=20;fire();s.angle=byte(s.angle+s.patterns_or_bonus);sound(9);
                }
            } else if (s.mode==2) {
                if (s.phase_frame==86) { s.angle=motion::angle_to(center(),c.bullets.player);t.speed=16; }
                if ((c.frame&3)==0) {
                    t.spawn_type=4;t.pattern=52;t.origin=center();t.group=45;t.count=3;t.delta=12;t.special_motion=255;
                    t.angle=byte(s.angle-32);tune();fire(true);t.angle=byte(t.angle+64);fire(true);sound(3);t.speed=byte(t.speed+6);
                }
            } else if (s.mode==3) {
                if ((c.frame&7)==0) {
                    t.spawn_type=2;t.pattern=52;t.origin=center();t.group=44;t.count=16;t.speed=32;t.angle=0;tune();fire();sound(9);
                }
            } else if ((c.frame&7)==0) {
                t.spawn_type=1;t.origin={motion::wrap(int(center().x)-512),center().y};t.group=38;t.count=8;t.speed=30;t.angle=byte(t.angle+8);
                tune();fire();t.origin.x=motion::wrap(int(t.origin.x)+1024);fire();sound(9);
            }
            if (s.phase_frame>=118) s.mode=0;
        }
        if (!timed_out) { if (!hit_phase()) break;bonus(5); }
        next_phase(450);s.palette_zero[0]=112;s.palette_zero[2]=112;s.palette_changed=1;break;
    }
    case 3:
        if (s.mode==0) {
            if (s.phase_frame>128) { s.phase_frame=0;s.mode=1; }
        } else if (s.mode==1) {
            if (s.phase_frame==1) { s.position.velocity.x=center().x<3072 ? 16 : -16;s.angle=0; }
            s.position.velocity.y=motion::polar(s.angle,16).y;
            if (center().y>=1536) s.position.velocity.y=-16;
            if (center().y<=768) s.position.velocity.y=16;
            s.angle=byte(s.angle+2);s.position.update();
            if (center().x<=512 || center().x>=5632) s.position.velocity.x=motion::wrap(-int(s.position.velocity.x));
            if ((c.frame&3)==0 && !(c.bullets.rank==0 && (c.frame&7)==0)) {
                t.pattern=52;t.origin={motion::wrap(int(center().x)-512),center().y};t.group=27;
                t.count=s.hp<=700 ? (c.bullets.rank<3 ? 2 : 4) : 1;t.speed=32;
                t.spawn_type=random.next16_and(1)==0 ? 1 : 4;t.angle=byte(random.next16());tune();fire();
                t.origin.x=motion::wrap(int(t.origin.x)+1024);
                t.spawn_type=random.next16_and(1)==0 ? 1 : 4;t.angle=byte(random.next16());fire();
            }
        }
        if (s.phase_frame<=1500) { if (!hit_phase()) break;bonus(5); }
        next_phase(0);s.sprite=byte(s.sprite+4);s.palette_zero[0]=144;s.palette_zero[2]=32;s.palette_changed=1;g.color=9;break;
    case 4:
        t.origin={motion::wrap(int(center().x)+128),motion::wrap(int(center().y)-256)};
        if (s.mode==0) {
            if (s.phase_frame==96) { g.center=t.origin;gather_only(); }
            if (s.phase_frame==112) circle(t.origin);
            if (s.phase_frame>128) { s.phase_frame=0;s.mode=1; }
            seek_center();
        } else if (s.mode==1) {
            const auto frame=s.phase_frame;
            if (frame==96 || frame==160 || frame==224 || frame==288) { g.center=t.origin;gather_only(); }
            if (frame==112 || frame==160 || frame==240 || frame==304) circle(t.origin);
            if ((c.frame&3)==0) {
                t.spawn_type=1;t.group=0;s.angle=byte(s.angle-7);t.speed=32;t.angle=s.angle;tune();fire(false,true);
                const unsigned extra=frame<128 ? 0 : frame<192 ? 1 : frame<256 ? 2 : 3;
                for (unsigned i=0;i<extra;++i) { t.angle=byte(t.angle+64);fire(false,true); }
                if (frame>=320) {
                    t.speed=byte(t.speed+16);t.spawn_type=2;t.pattern=52;t.angle=byte(-int(t.angle)-32);
                    fire(false,true);t.angle=byte(t.angle+128);fire(false,true);
                }
            }
        }
        if (s.phase_frame<=600 && !hit_phase()) break;
        s.patterns_or_bonus=s.phase_frame<=600 ? 1 : 0;
        small(3);++s.phase;s.phase_frame=0;s.mode=0;sparks.add_circle(center(),128,48);break;
    case 5:
        seek_center();increment();
        if (s.phase_frame==16) small(4);
        if (s.phase_frame==32) {
            explosion(s.big,center(),0);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);
            if (s.patterns_or_bonus) bonus(10);
            s.sprite=4;s.phase_frame=0;sound(12);s.palette_zero[0]=0;s.palette_zero[2]=0;s.palette_changed=1;s.invincibility=255;
        }
        break;
    default:
        if (s.phase==254) {
            if (s.phase_frame<12) { s.shake_x=(c.frame&1) ? 4 : -4;s.shake_y=(c.frame&3)<=1 ? -4 : 4; }
            s.background=Background::tiles;s.slowdown=2;increment();
            if (s.phase_frame%8==0) {
                ++s.sprite;
                if (s.sprite>=12) { ++s.phase;s.phase_frame=0;s.bombing_disabled=1; }
            }
        } else {
            transition::Departure departure;
            departure.frame=s.phase_frame;departure.homing=s.homing;
            transition::Overlay overlay;
            transition::update_departure(departure,overlay,false,[&](const transition::Event& e) {
                switch(e.kind) {
                case transition::Kind::tone:emit(sink,EventType::tone,{},e.value);break;
                case transition::Kind::dialog:emit(sink,EventType::dialog);break;
                case transition::Kind::bonus:emit(sink,EventType::stage_bonus);break;
                case transition::Kind::fade:emit(sink,EventType::fade,{},e.value);break;
                case transition::Kind::next_stage:emit(sink,EventType::next_stage);break;
                case transition::Kind::delay:emit(sink,EventType::delay,{},e.value);break;
                }
            });
            apply_departure(departure);
        }
        return;
    }
    s.homing=center();emit(sink,EventType::hp,{},static_cast<std::uint16_t>(s.hp),3050);
}
void System::apply_departure(const transition::Departure& departure) {
    state_.phase_frame=departure.frame;state_.homing=departure.homing;
    state_.palette_tone=departure.palette_tone;state_.palette_changed=departure.palette_changed;
}
} // namespace th04::portable::orange
