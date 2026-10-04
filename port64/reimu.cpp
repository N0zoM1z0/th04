#include "reimu.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::reimu {
namespace {
std::uint8_t byte(int value) { return static_cast<std::uint8_t>(value); }
std::int8_t signed_byte(int value) { const auto n=byte(value);return static_cast<std::int8_t>(n<128 ? n : int(n)-256); }
void explosion(orange::Explosion& e,motion::Point center,unsigned type) {
    e.alive=1;e.age=0;e.center=center;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if(type==1) e.angle_offset=32;
    else if(type==2) e.angle_offset=224;
    else if(type==3) e.delta={208,112};
    else if(type==4) e.delta={112,208};
}
}
Snapshot prepare_stage4(orange::Snapshot previous,unsigned rank) {
    Snapshot next;next.boss=previous;auto& s=next.boss;
    s.phase=0;s.mode=0;s.patterns_or_bonus=0;s.phase_frame=0;s.damage=0;
    s.position.velocity={};s.small[0].alive=s.small[1].alive=0;s.timed_out=1;
    s.position.current=s.position.previous={3072,1024};s.sprite=128;s.hitbox_radius={384,384};
    constexpr std::uint8_t parameters[4][7]={{4,16,1,23,8,18,6},{6,12,2,23,9,16,8},{8,8,3,24,9,14,9},{12,6,4,24,10,10,10}};
    std::copy(std::begin(parameters[rank<4 ? rank : 1]),std::end(parameters[rank<4 ? rank : 1]),s.additional.begin());
    // HP/endHP/angle/additional7..15 and explosion metadata retain boss_reset
    // ownership. Private state is fresh MAIN state, not stage4_setup writes.
    return next;
}
void System::add_moving() {
    const auto& t=state_.scratch;
    for(auto& q:state_.orbs) {
        if(q.flag) continue;
        q.flag=2;q.center=t.center;q.origin=t.origin;q.unknown=t.unknown;
        q.move_speed=t.move_speed;q.angle=t.angle;q.distance=0;
        q.velocity=motion::polar(t.angle,t.move_speed);return;
    }
}
void System::add_spinning(std::uint8_t offset,std::int16_t count) {
    const auto& t=state_.scratch;int spawned=0;
    for(auto& q:state_.orbs) {
        if(q.flag) continue;
        q.flag=1;q.spin_time=t.spin_time;q.center=t.center;q.origin=t.origin;
        q.unknown=t.unknown;q.move_speed=t.move_speed;
        // The target commits these fields before the potentially failing IDIV.
        if(!count) throw std::domain_error("original Reimu spinning-orb IDIV by zero");
        q.angle=byte((spawned*256)/count+offset);
        q.distance=0;q.angle_speed=t.angle_speed;
        if(++spawned>=count) return;
    }
}
void System::update_orbs(const Context& c,const Sink& sink) {
    for(auto& q:state_.orbs) {
        if(!q.flag) continue;
        if(q.flag==1) {
            const auto delta=motion::polar(q.angle,q.distance);
            q.center={motion::wrap(int(q.origin.x)+delta.x),motion::wrap(int(q.origin.y)+delta.y)};
            if(q.distance<1024) q.distance=motion::wrap(int(q.distance)+64);
            --q.spin_time;q.angle=byte(q.angle+q.angle_speed);
            if(q.spin_time==0) {
                q.angle=byte(q.angle+(q.angle_speed>=0 ? 64 : -64));
                q.velocity=motion::polar(q.angle,q.move_speed);++q.flag;
            }
        } else if(q.flag==2) {
            ++q.spin_time;q.center.x=motion::wrap(int(q.center.x)+q.velocity.x);
            if(q.center.x<0 || q.center.x>6144) q.velocity.x=motion::wrap(-int(q.velocity.x));
            q.center.y=motion::wrap(int(q.center.y)+q.velocity.y);
            if(q.center.y>=5888) q.flag=0;
            q.velocity.y=motion::wrap(int(q.velocity.y)+1);
        }
        // Includes the final freeing update and unknown nonzero flags. Raw
        // shot damage is discarded; player collision uses wrapped unsigned
        // rectangles, unlike the body wrapper's invulnerable/damage handling.
        if(sink) sink({orange::EventType::hit,q.center,192,192});
        if(c.orb_hit) c.orb_hit(q.center,{192,192});
        const auto left=motion::wrap(int(q.center.x)-192),top=motion::wrap(int(q.center.y)-192);
        if(static_cast<std::uint16_t>(int(c.bullets.player.x)-left)<384 &&
           static_cast<std::uint16_t>(int(c.bullets.player.y)-top)<384) state_.player_hit=1;
    }
}
void System::pulse() {
    auto& s=state_.boss;
    if(!state_.pulse_direction) { ++s.palette_zero[0];if(s.palette_zero[0]>=240) state_.pulse_direction=1; }
    else { --s.palette_zero[0];if(s.palette_zero[0]<=64) state_.pulse_direction=0; }
    s.palette_changed=1;
}
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,
                    spark::System& sparks,randring::SharedRandomRing& random,const Sink& sink) {
    (void)sparks;auto& s=state_.boss;auto& t=bullets.scratch();auto& g=gathers.scratch();auto& orb=state_.scratch;
    const auto emit=[&](orange::EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
        if(sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
    };
    const auto sound=[&](unsigned id) { emit(orange::EventType::sound,{},id); };
    const auto increment=[&] { s.phase_frame=motion::wrap(int(s.phase_frame)+1); };
    const auto hit=[&](unsigned se) {
        emit(orange::EventType::hit,s.position.current,static_cast<std::uint16_t>(s.hitbox_radius.x),static_cast<std::uint16_t>(s.hitbox_radius.y));
        const auto damage=c.hit ? c.hit(s.position.current,s.hitbox_radius) : std::uint16_t{0};
        if(damage) sound(se);
        return damage;
    };
    const auto invulnerable=[&] { increment();hit(10); };
    const auto hit_phase=[&] { increment();s.damage=byte(hit(4));s.hp=motion::wrap(int(s.hp)-s.damage);return s.hp<=s.end_hp; };
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto fire=[&](bool special=false,bool fixed=false) { bullets.add(t,c.bullets,random,special,fixed); };
    const auto small=[&](unsigned type) { explosion(s.small[s.small[0].alive ? 1 : 0],s.position.current,type);sound(15); };
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;s.score_delta+=static_cast<std::uint16_t>(units*1280u);
        const auto left=motion::wrap(int(s.position.current.x)-1024),top=motion::wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<units;++i) {
            const auto x=motion::wrap(int(left)+random.next16_mod(2048)),y=motion::wrap(int(top)+random.next16_mod(2048));
            emit(orange::EventType::point,{static_cast<std::int16_t>(std::clamp(int(x),0,6144)),y},1280);
        }
        s.timed_out=0;
    };
    const auto phase_next=[&](int type,int next_hp) {
        if(type!=-1) {
            small(static_cast<unsigned>(type));
            if(!s.timed_out) {
                bullets.clear();
                const auto left=motion::wrap(int(s.position.current.x)-1024),top=motion::wrap(int(s.position.current.y)-1024);
                for(unsigned i=0;i<5;++i) {
                    const auto x=motion::wrap(int(left)+random.next16_mod(2048)),y=motion::wrap(int(top)+random.next16_mod(2048));
                    emit(orange::EventType::item,{x,y},c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0));
                }
            }
        }
        s.timed_out=1;++s.phase;s.phase_frame=0;s.mode=0;s.patterns_or_bonus=0;s.hp=s.end_hp;s.end_hp=motion::wrap(next_hp);
    };
    // Intro runs before the hit wrapper advances the phase clock. Its gather
    // allocation retains the saved bullet fields and consumes no ring samples.
    const auto gather=[&] {
        switch(s.phase_frame) {
        case 14:g.center={motion::wrap(int(s.position.current.x)+64),motion::wrap(int(s.position.current.y)-448)};
            g.ring_points=16;g.radius=4096;g.color=9;gathers.add(g,t,true);s.sprite=129;sound(8);s.circle_color=15;break;
        case 16:g.color=8;[[fallthrough]];
        case 18:gathers.add(g,t,true);break;
        case 22:s.sprite=130;break;
        case 26:s.sprite=131;break;
        case 30:s.sprite=132;emit(orange::EventType::circle,g.center);break;
        case 34:s.sprite=133;break;
        case 38:s.sprite=134;break;
        case 42:s.sprite=135;break;
        case 46:s.sprite=129;sound(3);return 2;
        }
        return s.phase_frame<46 ? 0 : 1;
    };
    const auto end_pattern=[&] { s.sprite=128;s.phase_frame=0;s.mode=255; };
    const auto random_origin=[&] {
        t.origin={motion::wrap(int(s.position.current.x)-512+random.next16_mod(1024)),
                  motion::wrap(int(s.position.current.y)-512+random.next16_mod(1024))};
    };
    const auto move=[&](bool reverse) {
        const auto pattern=s.patterns_or_bonus%3;
        if(s.phase_frame==1) {
            state_.trail_visible=1;s.position.velocity={static_cast<std::int16_t>(pattern==1 ? 64 : -64),static_cast<std::int16_t>(pattern==0 ? 16 : (pattern==1 ? 0 : -16))};
            if(reverse) { s.position.velocity.x=motion::wrap(-int(s.position.velocity.x));s.position.velocity.y=motion::wrap(-int(s.position.velocity.y)); }
        }
        s.position.update();
        if(s.phase_frame==(pattern==1 ? 64 : 32)) { ++s.patterns_or_bonus;s.mode=s.patterns_or_bonus%2;s.phase_frame=0;state_.trail_visible=0; }
    };
    const auto pellet_cloud=[&] {
        if(gather()!=1) return;
        if(s.phase_frame%4==0) {
            t.spawn_type=1;t.speed=128;t.angle=byte(random.next16_and(7)-68);t.group=BG_SPREAD;t.count=s.additional[3];t.delta=s.additional[4];fire(false,true);
            if(s.phase_frame%16==0) { random_origin();t.group=BG_STACK_AIMED;t.count=byte(c.bullets.rank+3);t.delta=16;t.spawn_type=4;t.speed=32;t.angle=0;t.pattern=61;fire();sound(3); }
        }
        if(s.phase_frame>=192) end_pattern();
    };
    const auto toward_center=[&] {
        s.position.velocity.x=s.position.current.x<3072 ? 32 : (s.position.current.x>3072 ? -32 : 0);
        s.position.velocity.y=s.position.current.y<1536 ? 16 : (s.position.current.y>1536 ? -16 : 0);s.position.update();
    };
    t.origin={motion::wrap(int(s.position.current.x)+64),motion::wrap(int(s.position.current.y)-448)};
    switch(s.phase) {
    case 0:
        if(!s.phase_frame) state_.trail_visible=0;
        invulnerable();
        if(s.phase_frame>96) { ++s.phase;s.palette_zero={128,0,224};s.palette_changed=1;s.phase_frame=0;sound(13);s.background=orange::Background::npc;s.tile_column=15; }
        break;
    case 1:
        pulse();increment();invulnerable(); // Original entrance advances twice.
        if(s.phase_frame>=128) { s.position.velocity.x=0;s.end_hp=9100;phase_next(-1,7900); }
        break;
    case 2:
        if(s.mode==0) {
            const auto state=gather();
            if(state==2) { t.spawn_type=2;t.pattern=92;t.speed=96;s.angle=motion::angle_to(s.position.current,c.bullets.player);t.group=BG_SPREAD;t.count=6;t.delta=s.additional[5];tune();state_.angle_delta=c.bullets.player.x<3072 ? -2 : 2; }
            if(state==1) { if(s.phase_frame%4==0) { t.angle=s.angle;fire();sound(3);if(s.phase_frame>=64) s.angle=byte(s.angle+state_.angle_delta); }if(s.phase_frame>=112) end_pattern(); }
        } else if(s.mode==1) {
            const auto state=gather();
            if(state==2) { t.spawn_type=4;t.pattern=57;t.speed=85;t.angle=0;t.special_motion=128;bullets.set_special_parameter(s.additional[2]);t.group=BG_SPREAD_AIMED;t.count=9;t.delta=6;tune();fire(true,true); }
            if(state==1 && s.phase_frame>=128) end_pattern();
        } else if(s.mode==255) move(false);
        pulse();
        if(s.patterns_or_bonus<9) { if(!hit_phase()) break;bonus(10); }
        phase_next(0,6300);s.sprite=129;state_.trail_visible=0;break;
    case 3:case 7:case 10: {
        const auto phase=s.phase;toward_center();
        if(phase==10) { s.palette_zero[0]=byte(s.palette_zero[0]+3);s.palette_zero[2]=byte(s.palette_zero[2]-2);s.palette_changed=1; }
        else pulse();
        hit_phase();
        if(s.phase_frame>=64) {
            ++s.phase;s.phase_frame=0;s.patterns_or_bonus=0;s.mode=0;s.sprite=129;orb.angle_speed=phase==7 ? 18 : 4;
            if(phase==3) { state_.orb_pattern=140;s.additional[10]=0; }
            else if(phase==7) state_.orb_pattern=144;
        }
        break;
    }
    case 4:
        if(s.mode<=2) {
            if(s.phase_frame==32) { s.sprite=136;orb.spin_time=64;orb.move_speed=56;orb.origin=s.position.current;add_spinning(byte(random.next16()),s.additional[0]);sound(8); }
            if(s.phase_frame>=96) { s.phase_frame=0;s.mode=255;orb.angle_speed=signed_byte(-int(orb.angle_speed)); }
        } else if(s.mode==3) {
            if(gather()==1) {
                if(s.phase_frame%32==0) { random_origin();t.angle=byte(random.next16()); // Discarded original draw still advances the ring.
                    t.spawn_type=5;t.pattern=57;t.speed=16;t.angle=0;t.special_motion=130;bullets.set_special_parameter(1);t.group=BG_RING;t.count=16;tune();fire(true,true);sound(3); }
                if(s.phase_frame%32==16) { random_origin();t.angle=byte(random.next16());t.spawn_type=1;t.speed=24;t.group=BG_STACK;t.count=4;t.delta=8;tune();t.angle=byte(random.next16());for(unsigned i=0;i<12;++i) { fire();t.angle=byte(t.angle+21); }sound(3); }
                if(s.phase_frame>=288) end_pattern();
            }
        } else if(s.mode==255) { ++s.patterns_or_bonus;s.additional[10]=s.additional[10]<=2 ? (random.next16_and(1) ? byte(s.additional[10]+1) : 3) : 0;s.mode=s.additional[10];s.phase_frame=0; }
        pulse();
        if(s.patterns_or_bonus<18) { if(!hit_phase()) break;bonus(10); }
        phase_next(1,4500);s.position.velocity.x=0;break;
    case 5:
        s.position.velocity.y=s.position.current.y<2048 ? 16 : (s.position.current.y>2048 ? -16 : 0);s.position.update();pulse();hit_phase();
        if(s.phase_frame>=64) { ++s.phase;s.phase_frame=0;s.patterns_or_bonus=0;s.mode=0;s.sprite=129;orb.angle_speed=4; }break;
    case 6:
        if(s.mode==0) pellet_cloud();
        else if(s.mode==1) {
            const auto state=gather();
            if(state==2) { t.spawn_type=1;t.speed=54;t.angle=motion::angle_to(s.position.current,c.bullets.player);t.group=BG_RANDOM_ANGLE_AND_SPEED;t.count=3;tune(); }
            if(state==1) {
                if(s.phase_frame<96) { if(s.phase_frame%2==0) { fire();sound(3); } }
                else if(s.phase_frame<=128) { if(s.phase_frame%16==0) { t.spawn_type=5;t.pattern=57;t.group=BG_RING;t.count=32;t.angle=byte(random.next16());t.speed=48;t.special_motion=130;bullets.set_special_parameter(1);tune();fire(true);sound(15); } }
                else end_pattern();
            }
        } else if(s.mode==255) move(true);
        pulse();
        if(s.patterns_or_bonus<11) { if(!hit_phase()) break;bonus(10); }
        phase_next(2,2700);s.sprite=129;state_.trail_visible=0;break;
    case 8:
        if(s.mode==0) {
            if(s.phase_frame==32) { s.sprite=136;orb.angle=0;orb.move_speed=56;orb.center=s.position.current;sound(8); }
            if(s.phase_frame>=32) {
                if(!s.additional[1]) throw std::domain_error("original Reimu orb-stream IDIV by zero");
                if(s.phase_frame%s.additional[1]==0) { orb.angle=byte(orb.angle-orb.angle_speed);add_moving(); }
            }
            if(s.phase_frame>=180) { s.phase_frame=0;s.mode=255;orb.angle_speed=signed_byte(-int(orb.angle_speed)); }
        } else if(s.mode==1) {
            const auto state=gather();
            if(state==2) { t.spawn_type=4;t.pattern=57;t.angle=192;t.special_motion=255;t.delta=8;state_.pattern8_angle=state_.pattern8_angle!=120 ? 120 : 136; }
            if(state==1) {
                if(s.phase_frame%4==0) { t.speed=byte(random.next16_and(31)+16);t.group=BG_SPREAD;t.count=byte(random.next16_and(3)+2);tune();random_origin();t.angle=byte(t.angle+state_.pattern8_angle);fire(true);t.angle=byte(t.angle+128);fire(true);sound(3); }
                if(s.phase_frame>=224) end_pattern();
            }
        } else if(s.mode==255) { ++s.patterns_or_bonus;s.mode=s.patterns_or_bonus&1;s.phase_frame=0; }
        pulse();
        if(s.patterns_or_bonus<10) { if(!hit_phase()) break;bonus(10); }
        phase_next(3,900);s.position.velocity.x=0;orb.angle_speed=3;break;
    case 9:
        if(s.mode==0) pellet_cloud();
        else if(s.mode==1) {
            const auto state=gather();
            if(state==2) { t.spawn_type=4;t.group=BG_STACK_AIMED;t.count=s.additional[6];t.delta=12;t.special_motion=255;t.angle=0;t.pattern=57; }
            if(state==1) {
                if(s.phase_frame%32==16) { t.angle=32;for(unsigned i=0;i<5;++i) { fire(true,true);t.angle=byte(t.angle-16); }sound(15); }
                if(s.phase_frame>=128) end_pattern();
            }
        } else if(s.mode==255) move(false);
        pulse();
        if(s.patterns_or_bonus<12) { if(!hit_phase()) break;bonus(10); }
        phase_next(4,0);s.position.velocity.x=0;orb.angle_speed=3;s.palette_zero[0]=60;break;
    case 11:
        t.origin=s.position.current;
        if(s.phase_frame==32) { s.sprite=136;s.angle=0;t.spawn_type=4;t.pattern=57;t.angle=192;t.special_motion=255;t.delta=8; }
        if(s.phase_frame>=32 && s.phase_frame%16==0) {
            random_origin();t.angle=byte(random.next16());t.spawn_type=1;t.speed=24;t.group=BG_STACK;t.count=4;t.delta=10;tune();
            t.angle=byte(random.next16());for(unsigned i=0;i<8;++i) { fire();t.angle=byte(t.angle+32); }sound(3);
        }
        if(hit_phase() || s.phase_frame>=1000) { small(3);++s.phase;s.patterns_or_bonus=s.phase_frame<1000 ? 1 : 0;s.phase_frame=0; }break;
    case 12:
        increment();if(s.phase_frame==16) small(4);
        if(s.phase_frame==32) { explosion(s.big,s.position.current,2);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);if(s.patterns_or_bonus) bonus(40);s.sprite=4;s.phase_frame=0;sound(12);s.palette_zero[0]=s.palette_zero[2]=0;s.palette_changed=1;s.invincibility=255; }
        break;
    default:orange::update_defeat(s,c,sink);return;
    }
    s.homing=s.position.current;update_orbs(c,sink);emit(orange::EventType::hp,{},static_cast<std::uint16_t>(s.hp),9100);
}
} // namespace th04::portable::reimu
