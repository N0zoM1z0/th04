#include "yuuka6.hpp"
#include "yuuka6_entities.hpp"
#include "thick_lasers.hpp"
#include <stdexcept>

namespace th04::portable::yuuka6 {
namespace {
using motion::wrap;
constexpr std::uint8_t yellow_cross=59,red_small_ball=60,blue_ball=57,
                       blue_directional=76,yellow_directional=92,red_ball=61;
std::uint8_t byte(int value) { return static_cast<std::uint8_t>(value); }
void sound(const orange::Sink& sink,unsigned id) {
    if(sink) sink({orange::EventType::sound,{},static_cast<std::uint16_t>(id),0});
}
}
void System::gathering(Gathering kind,gather::System& gathers,const bullet::Template& bullet,
                       const orange::Sink& sink) {
    auto& s=state_.boss;auto& g=gathers.scratch();
    const auto add=[&] { gathers.add(g,bullet,true); };
    const auto pair=[&] { g.angle_delta=byte(-2);add();g.angle_delta=2;add(); };
    const auto circle=[&](motion::Point p) {
        if(sink) sink({orange::EventType::circle,p,0,0});
    };
    switch(kind) {
    case Gathering::pair:pair();return;
    case Gathering::side:
        switch(s.phase_frame) {
        case 16:
            sound(sink,8);g.radius=5120;
            g.center={wrap(int(s.position.current.x)+384),wrap(int(s.position.current.y)-64)};
            g.ring_points=16;g.color=9;g.angle_delta=byte(-2);[[fallthrough]];
        case 20:
            add();g.center.x=wrap(int(g.center.x)-704);g.angle_delta=2;add();break;
        case 18:
            g.color=8;add();g.center.x=wrap(int(g.center.x)+704);g.angle_delta=byte(-2);add();break;
        case 32:
            // The scratch center ends on the left side after frame20.
            circle(g.center);circle({wrap(int(g.center.x)+704),g.center.y});s.circle_color=15;break;
        }
        return;
    case Gathering::center:
        switch(s.phase_frame) {
        case 48:
            sound(sink,8);g.radius=5120;g.center={s.position.current.x,wrap(int(s.position.current.y)+512)};
            g.ring_points=8;g.color=9;pair();break;
        case 50:g.color=8;pair();break;
        case 52:pair();break;
        case 64:circle(g.center);s.circle_color=15;break;
        }
        return;
    case Gathering::dual:
        switch(s.phase_frame) {
        case 32:
            sound(sink,8);g.radius=5120;g.ring_points=8;g.color=9;[[fallthrough]];
        case 34:case 36:
            if(s.phase_frame==34) g.color=8;
            // Recompute both centers even on later calls: the retained
            // template is left at the mirror, never restored to the boss.
            g.center={s.position.current.x,wrap(int(s.position.current.y)+512)};pair();
            g.center={state_.mirror.x,wrap(int(state_.mirror.y)+512)};pair();break;
        case 48:
            circle({s.position.current.x,wrap(int(s.position.current.y)+512)});
            circle({state_.mirror.x,wrap(int(state_.mirror.y)+512)});s.circle_color=15;break;
        }
        return;
    case Gathering::self:
        switch(s.phase_frame) {
        case 16:
            sound(sink,8);g.radius=5120;g.center=s.position.current;g.ring_points=16;g.color=7;pair();break;
        case 18:g.color=6;pair();break;
        case 20:pair();break;
        case 32:circle(g.center);s.circle_color=15;break;
        }
        return;
    }
    throw std::invalid_argument("unknown Yuuka6 gathering");
}
void System::attack(Attack kind,const orange::Context& c,bullet::System& bullets,gather::System& gathers,
                    laser::System& lasers,Entities& entities,randring::SharedRandomRing& random,
                    const orange::Sink& sink) {
    auto& s=state_.boss;auto& t=bullets.scratch();
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto fire=[&](bool special=false,bool fixed=false) {
        // Every new spawn aliases MAIN's hit BYTE. Preserve a retained bool
        // while detecting this call's contact write, including BYTE127->1.
        const bool previous=bullets.snapshot().player_hit;
        bullets.set_player_hit(false);bullets.add(t,c.bullets,random,special,fixed);
        const bool contact=bullets.snapshot().player_hit;
        if(contact) lasers.set_player_hit(1);
        bullets.set_player_hit(previous || contact);
    };
    const auto gather=[&](Gathering k) { gathering(k,gathers,t,sink); };
    const auto finish=[&] { s.phase_frame=0;s.mode=255; };
    const auto circle=[&](motion::Point p) {
        if(sink) sink({orange::EventType::circle,p,0,0});
        s.circle_color=15;
    };
    const auto start_forward=[&] {
        if(state_.sprite_flag==1) animate(Animation::close);
        else if(state_.sprite_flag==2) animate(Animation::pull_forward);
    };
    const auto end_forward=[&] {
        if(state_.sprite_flag!=2) animate(Animation::spin_back);
        else if(animate(Animation::open)) finish();
    };
    const auto spinning_sprite=[&] { s.sprite=byte(((c.frame%4)/2)*2+146); };
    switch(kind) {
    case Attack::ring_turn:
        if(state_.sprite_flag==1) animate(Animation::close);
        gather(Gathering::side);
        if(s.phase_frame==48 || s.phase_frame==64) {
            if(s.phase_frame==48) t.speed=40;
            t.spawn_type=2;t.pattern=yellow_cross;t.origin={s.position.current.x,wrap(int(s.position.current.y)-64)};
            t.angle=0;t.group=BG_RING;t.special_motion=129;t.count=20;
            bullets.set_special_angle(192);tune();fire(true,true);
            bullets.set_special_angle(64);fire(true,true);sound(sink,9);t.speed=byte(t.speed+16);
        } else if(s.phase_frame==80) finish();
        return;
    case Attack::spin_rings:
        if(s.phase_frame<48) {
            if(state_.sprite_flag==2) animate(Animation::pull_left);
        } else if(state_.sprite_flag==4) {
            animate(Animation::spin_back);
            // The condition is evaluated after animation, even on its
            // terminal frame; angle for the second origin is not t.angle.
            if(s.phase_frame<=80) {
                t.spawn_type=1;t.group=BG_RING;t.count=s.additional[1];
                auto angle=byte(-int(wrap(int(s.phase_frame)*8)));
                t.speed=40;t.angle=angle;
                auto offset=motion::polar(angle,544);
                t.origin={wrap(int(s.position.current.x)+offset.x),wrap(int(s.position.current.y)+offset.y)};fire();
                angle=byte(128-angle);offset=motion::polar(angle,544);
                t.origin={wrap(int(s.position.current.x)+offset.x),wrap(int(s.position.current.y)+offset.y)};
                t.speed=byte(60-s.phase_frame/2);fire();if(c.frame%4==0) sound(sink,9);
            }
        }
        if(s.phase_frame==32) circle({wrap(int(s.position.current.x)-640),wrap(int(s.position.current.y)+640)});
        else if(s.phase_frame==96) finish();
        return;
    case Attack::gravity:
        if(state_.sprite_flag==2) animate(Animation::open);
        if(s.phase_frame>=48 && s.phase_frame<=80) {
            if(c.frame%4==0) {
                t.spawn_type=byte((c.frame%8)/4+1);t.pattern=red_small_ball;t.origin.y=wrap(int(s.position.current.y)-64);
                t.group=BG_RANDOM_ANGLE_AND_SPEED;t.count=4;t.special_motion=136;t.speed=byte(random.next16_mod(24)+8);
                t.origin.x=wrap(int(s.position.current.x)-320);t.angle=byte(random.next16());
                bullets.set_special_parameter(1);tune();fire(true,true);
                t.angle=byte(random.next16());t.origin.x=wrap(int(t.origin.x)+704);fire(true,true);sound(sink,9);
            }
        } else if(s.phase_frame>80) finish();
        // This gather sees the reset clock after the terminal branch.
        gather(Gathering::side);return;
    case Attack::safety_circle:
        if(s.phase_frame<64) start_forward();
        else if(s.phase_frame<=112) s.sprite=140;
        else if(s.phase_frame>=288) end_forward();
        gather(Gathering::center);
        if(s.phase_frame==64) entities.add_safety_circle(c.bullets.player,sink);
        return;
    case Attack::bullets:
        if(c.frame%16!=0) return;
        t.origin=s.position.current;
        if(s.phase==6) {
            t.spawn_type=2;t.pattern=red_small_ball;t.angle=byte(random.next16());t.group=BG_RING;t.count=16;t.speed=30;tune();fire();
            t.spawn_type=4;t.pattern=blue_ball;t.count=byte(s.phase_frame/16+2);t.speed=34;
        } else {
            t.spawn_type=4;t.pattern=blue_directional;t.angle=0;t.group=BG_STACK_AIMED;t.count=7;t.speed=32;t.delta=10;tune();fire(false,true);sound(sink,15);
            t.spawn_type=1;t.group=BG_RANDOM_ANGLE_AND_SPEED;t.count=4;t.speed=24;
        }
        tune();fire();return;
    case Attack::dual_lasers:
        if(s.phase_frame<64) { start_forward();t.speed=16; }
        else if(s.phase_frame<=128) {
            s.sprite=140;
            if(c.frame%8==0) {
                t.origin=s.position.current;t.spawn_type=4;t.pattern=blue_directional;t.group=BG_SPREAD;t.delta=8;t.count=3;tune();
                t.angle=96;fire();t.angle=32;fire();t.origin.x=state_.mirror.x;fire();t.angle=96;fire();t.speed=byte(t.speed+12);sound(sink,3);
            }
        } else end_forward();
        gather(Gathering::dual);
        if(s.phase_frame==64) {
            auto& l=lasers.scratch();l.maximum_radius=s.additional[0];l.radius_speed=4;l.line_frames=36;l.static_frames=40;l.outline=8;
            l.origin={s.position.current.x,wrap(int(s.position.current.y)+512)};lasers.add([&](unsigned id){sound(sink,id);});
            l.origin={state_.mirror.x,wrap(int(state_.mirror.y)+640)};lasers.add([&](unsigned id){sound(sink,id);});
        }
        return;
    case Attack::dual_spreads:
        if(s.phase_frame<64) { start_forward();s.additional[15]=2; }
        else if(s.phase_frame<=128) {
            s.sprite=140;
            if(c.frame%4==0) {
                t.origin.y=wrap(int(s.position.current.y)+512);t.spawn_type=2;t.pattern=yellow_directional;t.group=BG_SPREAD;t.count=5;
                t.speed=byte(random.next16_and(31)+12);t.delta=16;
                // BYTE range doubles in a WORD. Zero raises the same RNG
                // divisor failure; do not fabricate a fallback direction.
                t.angle=byte(random.next16_mod(s.additional[15]*2)+(64-s.additional[15]));t.origin.x=s.position.current.x;fire();
                t.angle=byte(random.next16_mod(s.additional[15]*2)+(64-s.additional[15]));t.origin.x=state_.mirror.x;fire();
                sound(sink,9);s.additional[15]=byte(s.additional[15]+6);
            }
        } else end_forward();
        gather(Gathering::dual);return;
    case Attack::rotating_ring:
        if(s.phase_frame<=48) { if(state_.sprite_flag!=8) animate(Animation::shield); }
        else if(s.phase_frame<136) {
            spinning_sprite();if(c.bullets.frame_mod2) fire(false,true);if(c.frame%4==0) sound(sink,3);
            if(s.phase_frame>=112) t.angle=byte(t.angle+s.angle);
        } else if(c.bullets.rank>=2 && s.phase_frame<150) {
            // During the return leg rotation precedes the spawn, unlike
            // the outward leg above. Angle0xFF is a raw signed-step BYTE.
            t.angle=byte(t.angle-s.angle);if(c.bullets.frame_mod2) fire(false,true);if(c.frame%4==0) sound(sink,3);
        } else s.sprite=146;
        gather(Gathering::self);
        if(s.phase_frame==48) {
            // This entry passes boss-minus-player to iatan2, pointing
            // opposite ordinary aim, then rotates by16 angle units.
            t.angle=byte(motion::angle_to(c.bullets.player,s.position.current)+16);
            t.spawn_type=4;t.pattern=red_ball;t.origin=s.position.current;t.group=BG_RING;t.count=8;t.speed=144;
            s.angle=c.bullets.rank==0 ? 0 : (random.next16_and(1) ? 1 : 255);
        } else if(s.phase_frame==156 || (s.phase_frame==144 && c.bullets.rank<2)) finish();
        return;
    case Attack::growing_ring:
        if(s.phase_frame>48) {
            spinning_sprite();if(c.frame%8==0) {
                sound(sink,3);t.angle=byte(t.angle+2);t.group=BG_RING;t.spawn_type=2;t.pattern=blue_directional;t.speed=48;t.count=byte(s.phase_frame/4+4);tune();fire();
            }
        } else s.sprite=146;
        gather(Gathering::self);if(s.phase_frame==144) finish();return;
    case Attack::chase_crosses:
        if(s.phase_frame>48) {
            spinning_sprite();if(c.frame%8==0) {
                // Random samples are consumed even when all32 slots are full.
                entities.add_cross(s.position.current,byte(random.next16()),32);
                entities.add_cross(s.position.current,byte(random.next16()),32);sound(sink,3);
            }
        } else s.sprite=146;
        if(s.phase_frame==144) finish();
        return;
    case Attack::alternating_rings: {
        const auto sub=byte(s.phase_frame)&31;spinning_sprite();
        if((sub&3)==0) {
            t.origin=s.position.current;t.spawn_type=byte(3-t.spawn_type);t.pattern=red_small_ball;t.group=BG_RING;t.count=8;t.speed=byte(sub+32);tune();
            t.angle=byte(130-t.angle);fire(false,true);t.angle=byte(128-t.angle);fire(false,true);
        }
        if(sub==0) {
            t.angle=byte(t.angle+8);auto& g=gathers.scratch();g.ring_points=8;g.color=9;g.angle_delta=byte(-g.angle_delta);gathers.add(g,t,true);
        }
        return;
    }
    case Attack::dual_aimed_spreads:
        if(s.phase_frame<64) start_forward();
        else if(s.phase_frame<=192) {
            s.sprite=140;if(c.frame%16==0) {
                t.spawn_type=2;t.pattern=blue_directional;t.speed=40;t.delta=14;
                if((c.frame&31)==0) { t.count=10;t.group=BG_SPREAD;t.angle=64; }
                else { t.count=7;t.group=BG_SPREAD_AIMED;t.angle=0; }
                t.origin={s.position.current.x,wrap(int(s.position.current.y)+512)};fire();t.origin.x=state_.mirror.x;fire();sound(sink,3);
            }
        } else end_forward();
        gather(Gathering::dual);return;
    }
    throw std::invalid_argument("unknown Yuuka6 attack");
}
} // namespace th04::portable::yuuka6
