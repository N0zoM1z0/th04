#include "yuuka5.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::yuuka5 {
namespace {
using motion::wrap;
std::uint8_t byte(int value) { return static_cast<std::uint8_t>(value); }
constexpr std::uint8_t yellow_cross=59,blue_directional=76,blue_ball=57,blue_outlined_ball=55;
void emit(const Sink& sink,orange::EventType kind,motion::Point p={},unsigned value=0,unsigned count=0) {
    if(sink) sink({kind,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
}
void explosion(orange::Explosion& e,motion::Point center,unsigned type) {
    e.alive=1;e.age=0;e.center=center;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if(type==1) e.angle_offset=32;
    else if(type==2) e.angle_offset=224;
    else if(type==3) e.delta={208,112};
    else if(type==4) e.delta={112,208};
}
}
bool System::move(std::uint16_t centered,randring::SharedRandomRing& random) {
    auto& s=state_.boss;
    if(state_.move_state==0) {
        state_.move_state=1;s.damage=0;s.position.current.y=wrap(int(s.position.current.y)+256);
    }
    if(state_.move_state==1) {
        if(s.phase_frame<32) return false;
        s.phase_frame=0;state_.move_state=2;
        const int x=centered ? 3072 : random.next16_mod(4096)+1024;
        const int y=centered ? 1280 : random.next16_mod(1024)+1024;
        // SUB wraps as a WORD before signed IDIV64 truncates toward zero.
        s.position.velocity={static_cast<std::int16_t>(wrap(x-s.position.current.x)/64),
                             static_cast<std::int16_t>(wrap(y-s.position.current.y)/64)};
        return false;
    }
    if(state_.move_state==2) {
        // Motion updates even on the frame that closes this 64-frame leg.
        s.position.update();if(s.phase_frame<64) return false;
        s.phase_frame=0;state_.move_state=3;return false;
    }
    if(state_.move_state==3) {
        if(s.phase_frame<8) return false;
        s.phase_frame=0;state_.move_state=0;s.mode=254;
        s.position.current.y=wrap(int(s.position.current.y)-256);return true;
    }
    return false; // Retain unknown states without inventing a recovery reset.
}
void System::pattern(Attack attack,const Context& c,bullet::System& bullets,gather::System& gathers,
                     laser::System& lasers,randring::SharedRandomRing& random,const Sink& sink) {
    auto& s=state_.boss;auto& t=bullets.scratch();auto& g=gathers.scratch();
    const auto sound=[&](unsigned id) { emit(sink,orange::EventType::sound,{},id); };
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto fire=[&](bool special=false,bool fixed=false) {
        // Spawn contact and laser contact write the same original BYTE latch.
        // Detect this call's write separately from the bullet owner's retained
        // bool: a contact overwrites a noncanonical incoming BYTE (127) with1.
        const bool previous_hit=bullets.snapshot().player_hit;
        bullets.set_player_hit(false);bullets.add(t,c.bullets,random,special,fixed);
        const bool spawned_hit=bullets.snapshot().player_hit;
        if(spawned_hit) lasers.set_player_hit(1);
        bullets.set_player_hit(previous_hit || spawned_hit);
    };
    const auto gather_only=[&] { gathers.add(g,t,true); };
    // The pinned target calls 0AAF:1BA6, the ordinary circle entry.
    // Do not substitute the neighboring 1B5A entry from source names alone.
    const auto circle=[&] { emit(sink,orange::EventType::circle,t.origin); };
    const auto finish=[&] { s.mode=255;s.phase_frame=0; };
    switch(attack) {
    case Attack::sweep:
        if(s.phase_frame==1) {
            state_.sweep_x=wrap(int(s.position.current.x)-512);t.spawn_type=2;t.pattern=yellow_cross;
            t.group=BG_SPREAD;t.count=11;t.delta=5;t.speed=40;tune();
        } else if(s.phase_frame==15) t.angle=0;
        else if(s.phase_frame==31) { state_.sweep_x=wrap(int(state_.sweep_x)+1024);t.angle=128; }
        else if(s.phase_frame==47) { state_.sweep_x=wrap(int(state_.sweep_x)-1024);t.angle=16; }
        else if(s.phase_frame==63) { state_.sweep_x=wrap(int(state_.sweep_x)+1024);t.angle=112; }
        else if(s.phase_frame==79) { state_.sweep_x=wrap(int(state_.sweep_x)-1024);t.angle=32; }
        else if(s.phase_frame==95) { state_.sweep_x=wrap(int(state_.sweep_x)+1024);t.angle=96; }
        else if(s.phase_frame==111) { state_.sweep_x=wrap(int(state_.sweep_x)-1024);t.angle=48; }
        else if(s.phase_frame==127) { state_.sweep_x=wrap(int(state_.sweep_x)+1024);t.angle=80; }
        else if(s.phase_frame==140) finish();
        if(s.phase_frame%16==15) { t.origin={state_.sweep_x,s.position.current.y};fire();sound(3); }
        return;
    case Attack::clouds:
        if(s.phase_frame==1) {
            t.angle=0;t.spawn_type=4;t.pattern=blue_directional;t.group=BG_RING;t.count=byte(c.bullets.rank+1);t.speed=64;
            state_.cloud_step=1;state_.cloud_accumulator=0;return;
        }
        if(s.phase_frame<128 || (s.phase_frame>128 && s.phase_frame<256)) {
            // One threshold test per frame, not a while-loop. Step and
            // accumulator are BYTEs and deliberately overflow independently.
            if(state_.cloud_accumulator>=16) {
                t.angle=byte(t.angle+(s.phase_frame<128 ? 7 : -7));fire();sound(3);
                ++state_.cloud_step;state_.cloud_accumulator=byte(state_.cloud_accumulator-16);
            }
            state_.cloud_accumulator=byte(state_.cloud_accumulator+state_.cloud_step);return;
        }
        if(s.phase_frame==128 || s.phase_frame==256) {
            t.spawn_type=2;t.pattern=yellow_cross;t.angle=s.phase_frame==128 ? 128 : 0;t.speed=16;
            t.special_motion=130;bullets.set_special_parameter(1);t.count=32;tune();fire(true,true);
            if(s.phase_frame==128) {
                t.spawn_type=4;t.speed=64;t.count=byte(c.bullets.rank+1);
                state_.cloud_step=1;state_.cloud_accumulator=0;sound(9);t.pattern=blue_directional;
            } else sound(9);
            return;
        }
        if(s.phase_frame==288) finish();
        return;
    case Attack::gather:
        if(s.phase_frame==1) { g.center=t.origin;g.ring_points=32;g.color=11;g.radius=4096;g.angle_delta=3;gather_only(); }
        else if(s.phase_frame==3) { g.color=10;gather_only(); }
        else if(s.phase_frame==5) gather_only();
        else if(s.phase_frame==17) {
            circle();s.circle_color=15;t.spawn_type=2;t.speed=32;t.special_motion=135;t.group=BG_SPREAD;t.count=7;t.delta=8;t.pattern=yellow_cross;tune();bullets.set_special_parameter(1);
        }
        if(s.phase_frame>=32 && s.phase_frame%16==0) { t.angle=byte(random.next16());fire(true);sound(9); }return;
    case Attack::speedup_ring:
        if(s.phase_frame==1) {
            t.spawn_type=2;t.pattern=yellow_cross;t.group=BG_RING_AIMED;t.delta=6;t.speed=16;t.special_motion=130;t.count=8;bullets.set_special_parameter(1);
        } else if(s.phase_frame==170) finish();
        if(s.phase_frame%16==15) { fire(true);t.count=byte(t.count+3);sound(3); }return;
    case Attack::aimed_spread:
        if(s.phase_frame==1) {
            t.angle=motion::angle_to(t.origin,c.bullets.player);t.spawn_type=4;t.pattern=blue_ball;t.group=BG_SPREAD;t.count=5;t.delta=66;t.speed=80;tune();
        } else if(s.phase_frame==128) finish();
        if(s.phase_frame%8==7) { t.delta=byte(t.delta-4);fire();sound(3); }return;
    case Attack::laser_burst:
        switch(s.phase_frame) {
        case 16:g.angle_delta=3;break;
        case 48:
            t.angle=0;sound(8);state_.palette_tone=100;[[fallthrough]];
        case 56:case 64:case 72:case 80:
            s.circle_color=15;circle();[[fallthrough]];
        case 40:
            g.angle_delta=byte(-int(g.angle_delta));g.center=t.origin;g.ring_points=8;g.color=9;g.radius=4096;[[fallthrough]];
        case 44:case 52:case 60:case 68:case 76:case 84:
            gather_only();break;
        case 42:case 50:case 58:case 66:case 74:case 82:
            g.color=8;gather_only();break;
        case 96: {
            auto& beam=lasers.scratch();beam.origin=t.origin;beam.maximum_radius=s.additional[0];beam.radius_speed=6;
            beam.line_frames=32;beam.static_frames=144;beam.outline=8;lasers.add(sound);break;
        }
        }
        if(s.phase_frame<128) return;
        if(s.phase_frame<=160) { state_.palette_tone=byte(state_.palette_tone+2);s.palette_tone=state_.palette_tone;s.palette_changed=1; }
        else if(state_.palette_tone>100) { state_.palette_tone=byte(state_.palette_tone-(s.phase_frame&1));s.palette_tone=state_.palette_tone;s.palette_changed=1; }
        if(s.phase_frame%32==0) {
            t.spawn_type=2;t.group=BG_RING;t.count=32;t.pattern=blue_directional;t.speed=72;tune();fire();t.angle=byte(t.angle+2);sound(9);
        }
        if(s.phase_frame>=192 && c.bullets.frame_mod2) {
            t.spawn_type=2;t.group=BG_RANDOM_ANGLE;t.pattern=blue_outlined_ball;t.speed=32;t.count=2;tune();fire();
        }return;
    case Attack::mirrored_streams:
        if(s.phase_frame==48) {
            circle();s.circle_color=15;s.angle=16;s.additional[15]=16;
            t.special_motion=255; // Original BSM_NONE token.
            return;
        }
        if(s.phase_frame<64 || s.phase_frame%8!=0) return;
        t.spawn_type=4;t.count=5;t.delta=1;t.group=BG_SPREAD;t.pattern=blue_ball;t.speed=40;tune();
        t.origin.x=wrap(int(t.origin.x)+512);t.angle=s.angle;fire(true);
        t.origin.x=wrap(int(t.origin.x)-1024);t.angle=byte(128-s.angle);fire(true);s.angle=byte(s.angle-16);
        t.spawn_type=1;t.count=3;t.speed=24;tune();t.angle=s.additional[15];fire(true);
        t.origin.x=wrap(int(t.origin.x)+1024);t.angle=byte(128-s.additional[15]);fire(true);s.additional[15]=byte(s.additional[15]+9);sound(3);return;
    }
    throw std::invalid_argument("unknown Yuuka5 attack");
}
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,
                    laser::System& lasers,randring::SharedRandomRing& random,const Sink& sink) {
    auto& s=state_.boss;auto& t=bullets.scratch();
    const auto sound=[&](unsigned id) { emit(sink,orange::EventType::sound,{},id); };
    const auto increment=[&] { s.phase_frame=wrap(int(s.phase_frame)+1); };
    const auto hit=[&](unsigned se) {
        emit(sink,orange::EventType::hit,s.position.current,static_cast<std::uint16_t>(s.hitbox_radius.x),static_cast<std::uint16_t>(s.hitbox_radius.y));
        const auto damage=c.hit ? c.hit(s.position.current,s.hitbox_radius) : std::uint16_t{0};if(damage) sound(se);return damage;
    };
    const auto invulnerable=[&] { increment();hit(10); };
    const auto hit_phase=[&] { increment();s.damage=byte(hit(4));s.hp=wrap(int(s.hp)-s.damage);return s.hp<=s.end_hp; };
    const auto small=[&](unsigned type) { explosion(s.small[s.small[0].alive ? 1 : 0],s.position.current,type);sound(15); };
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;s.score_delta+=static_cast<std::uint16_t>(units*1280u);
        const auto left=wrap(int(s.position.current.x)-1024),top=wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<units;++i) {
            const auto x=wrap(int(left)+random.next16_mod(2048)),y=wrap(int(top)+random.next16_mod(2048));
            emit(sink,orange::EventType::point,{static_cast<std::int16_t>(std::clamp(int(x),0,6144)),y},1280);
        }s.timed_out=0;
    };
    const auto items=[&] {
        const auto left=wrap(int(s.position.current.x)-1024),top=wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<5;++i) {
            const auto x=wrap(int(left)+random.next16_mod(2048)),y=wrap(int(top)+random.next16_mod(2048));
            emit(sink,orange::EventType::item,{x,y},c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0));
        }
    };
    const auto reset_attack=[&] { s.phase_frame=0;s.patterns_or_bonus=0;s.mode=0; };
    const auto attack=[&](Attack a) { pattern(a,c,bullets,gathers,lasers,random,sink); };
    // All attacks inherit one scratch template. Entry refreshes only origin,
    // before any movement. Helpers may leave a displaced origin in that frame.
    t.origin={s.position.current.x,wrap(int(s.position.current.y)+256)};
    // 0/1: entrance; 2..16 alternate pairs, recentering and fixed attacks.
    // 17 is the final hit/timeout window; 18 schedules the big explosion.
    // Early pair exits reduce end HP by800; late pairs retain it until lasers.
    switch(s.phase) {
    case 0:
        if(s.phase_frame==0) { state_.stage_vm_disabled=true;state_.midboss_frames_until=0; }
        invulnerable();if(s.phase_frame<=128) break;
        ++s.phase;s.phase_frame=0;sound(13);state_.move_state=0;s.tile_column=15;s.background=orange::Background::yuuka;break;
    case 1:
        invulnerable();if(s.phase_frame==32) { s.palette_zero={64,64,64};s.palette_changed=1; }
        if(s.phase_frame<64) break;
        ++s.phase;s.position.velocity.x=0;reset_attack();s.hp=9000;s.end_hp=7900;s.position.current.y=wrap(int(s.position.current.y)-256);break;
    case 2:case 5:case 8:case 11:case 14: {
        const bool early=s.phase<11;
        if(s.mode==0) attack(early ? Attack::sweep : Attack::speedup_ring);
        else if(s.mode==1) attack(early ? Attack::clouds : Attack::aimed_spread);
        else if(s.mode==254) { s.phase_frame=0;++s.patterns_or_bonus;s.mode=s.patterns_or_bonus%2; }
        else if(s.mode==255) move(0,random);
        if(state_.move_state==0) {
            if(s.patterns_or_bonus<4) { if(!hit_phase()) break;bonus(15);items(); }
            bullets.clear();small(0);++s.phase;s.hp=s.end_hp;
            if(early) s.end_hp=wrap(int(s.end_hp)-800);
        } else increment();
        // While moving there is no hit wrapper and therefore no hit/damage
        // callback. The clock still advances exactly once through this branch.
        break;
    }
    case 3:case 6:case 9:case 12:case 15:
        increment();if(!move(1,random)) break;
        ++s.phase;reset_attack();break;
    case 4:case 7:case 10:
        attack(Attack::gather);
        if(s.phase_frame<500) { if(!hit_phase()) break;bonus(15);items(); }
        bullets.clear();small(1);++s.phase;reset_attack();s.hp=s.end_hp;
        s.end_hp=wrap(int(s.end_hp)-(s.phase<10 ? 1100 : 1200));break;
    case 13:case 16:
        attack(Attack::laser_burst);invulnerable();if(s.phase_frame<288) break;
        small(4);bullets.clear();++s.phase;s.hp=s.end_hp;
        if(s.phase==17) { s.end_hp=0;s.palette_zero={128,64,64};s.palette_changed=1; }
        else s.end_hp=wrap(int(s.end_hp)-1200);
        reset_attack();s.palette_tone=100;s.palette_changed=1;break;
    case 17:
        attack(Attack::mirrored_streams);
        if(!hit_phase() && s.phase_frame<1000) break;
        small(1);++s.phase;s.patterns_or_bonus=s.phase_frame<1000 ? 1 : 0;s.phase_frame=0;s.mode=0;s.palette_tone=100;s.palette_changed=1;break;
    case 18:
        increment();if(s.phase_frame==16) small(4);
        if(s.phase_frame==32) {
            explosion(s.big,s.position.current,2);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);
            if(s.patterns_or_bonus) bonus(60);
            s.sprite=4;s.phase_frame=0;sound(12);s.palette_zero={0,0,0};s.palette_changed=1;s.invincibility=255;
        }break;
    default:
        orange::update_defeat(s,c,sink);return; // No laser/HUD tail after defeat.
    }
    s.homing=s.position.current;lasers.update(c.bullets.player,sound);
    emit(sink,orange::EventType::hp,{},static_cast<std::uint16_t>(s.hp),9000);
}
void System::apply_departure(const transition::Departure& d) {
    state_.boss.phase_frame=d.frame;state_.boss.homing=d.homing;
    state_.boss.palette_tone=d.palette_tone;state_.boss.palette_changed=d.palette_changed;
}
} // namespace th04::portable::yuuka5
