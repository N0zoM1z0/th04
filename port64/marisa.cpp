#include "marisa.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::marisa {
namespace {
std::uint8_t byte(int n) { return static_cast<std::uint8_t>(n); }
std::int8_t signed_byte(int n) { const auto v=byte(n);return static_cast<std::int8_t>(v<128 ? v : int(v)-256); }
int sar4(std::int16_t n) { return n>=0 ? n/16 : -((-int(n)+15)/16); }
void emit(const Sink& sink,orange::EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
    if(sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
}
void explode(orange::Explosion& e,motion::Point p,unsigned type) {
    e.alive=1;e.age=0;e.center=p;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if(type==1) e.angle_offset=32;
    else if(type==2) e.angle_offset=224;
    else if(type==3) e.delta={208,112};
    else if(type==4) e.delta={112,208};
}
std::int16_t divide(std::int16_t numerator,int divisor) {
    if(!divisor) throw std::domain_error("original Marisa flystep IDIV by zero");
    const int q=int(numerator)/divisor;
    if(q<-32768 || q>32767) throw std::domain_error("original Marisa flystep IDIV overflow");
    return static_cast<std::int16_t>(q);
}
}
Snapshot prepare_stage4(orange::Snapshot previous) {
    Snapshot next;next.boss=previous;auto& s=next.boss;
    s.phase=0;s.mode=0;s.patterns_or_bonus=0;s.phase_frame=0;s.damage=0;
    s.position.velocity={};s.small[0].alive=s.small[1].alive=0;s.timed_out=1;
    s.position.current=s.position.previous={3072,1024};s.hp=6000;s.sprite=128;s.hitbox_radius={384,384};
    // The Marisa branch writes no additional bytes or private bit state.
    // Retained endHP/angle/explosion metadata are boss_reset inputs.
    return next;
}
void System::initialize_bits(randring::SharedRandomRing& random) {
    auto angle=byte(random.next16());
    for(unsigned i=0;i<4;++i) {
        auto& q=state_.bits[i];q.flag=1;q.angle_speed=signed_byte(state_.angle_speed);
        q.angle=angle;angle=byte(angle+64);q.pattern=static_cast<std::int16_t>(136+i);
        q.distance=0;q.hp=state_.hp_table[i];q.moveout_speed=32;
    }
}
void System::update_bits(const Context& c,spark::System& sparks,randring::SharedRandomRing& random,const Sink& sink) {
    state_.alive=0;
    for(unsigned i=0;i<4;++i) {
        auto& q=state_.bits[i];if(!q.flag) continue;
        if(q.flag>=128) {
            ++q.flag;q.pattern=static_cast<std::int16_t>((int(q.flag)-128)/4+4);
            // Includes flag255 wrapping to0 and leaving pattern-28.
            if(q.pattern>=12) q.flag=0;
            continue;
        }
        q.angle=byte(q.angle+q.angle_speed);q.distance=motion::wrap(int(q.distance)+q.moveout_speed);
        const auto d=motion::polar(q.angle,q.distance);
        q.center={motion::wrap(int(state_.boss.position.current.x)+d.x),motion::wrap(int(state_.boss.position.current.y)+d.y)};
        if(q.flag==1 && q.distance>=1024) { ++q.flag;q.moveout_speed=0; }
        else if(q.flag==2 && q.distance>=64) ++q.flag;
        emit(sink,orange::EventType::hit,q.center,192,192);
        q.damage=motion::wrap(c.bit_hit ? c.bit_hit(q.center,{192,192}) : 0);
        q.hp=motion::wrap(int(q.hp)-q.damage);
        if(q.hp<=0) {
            q.pattern=4;q.flag=128;emit(sink,orange::EventType::sound,{},3);
            state_.boss.score_delta+=5120;sparks.add_random(q.center,64,8,random);continue;
        }
        const auto left=motion::wrap(int(q.center.x)-192),top=motion::wrap(int(q.center.y)-192);
        if(static_cast<std::uint16_t>(int(c.bullets.player.x)-left)<384 &&
           static_cast<std::uint16_t>(int(c.bullets.player.y)-top)<384) state_.player_hit=1;
        if(q.center.y<state_.boss.homing.y) state_.boss.homing=q.center;
        state_.center_x[state_.alive]=motion::wrap(sar4(q.center.x)+32);
        state_.center_y[state_.alive]=motion::wrap(sar4(q.center.y)+16);++state_.alive;
    }
}
void System::fire_bits(const Context& c,bullet::System& bullets,randring::SharedRandomRing& random) {
    auto& t=bullets.scratch();
    for(unsigned i=0;i<4;++i) {
        const auto& q=state_.bits[i];if(!q.flag || q.flag>=128) continue;
        if(state_.fire==Fire::spread) {
            if(state_.alive<=2) t.count=5;
            t.angle=byte(q.angle+(q.angle_speed>=0 ? -64 : 64));
        } else if(state_.fire!=Fire::single) throw std::domain_error("unknown original Marisa bit-fire callback");
        t.origin=q.center;bullets.add(t,c.bullets,random);
    }
}
unsigned System::phase_entry(gather::System& gathers,const bullet::Template& t,const Sink& sink) {
    auto& s=state_.boss;auto& g=gathers.scratch();
    if(s.mode>=1 && s.mode<=6) {
        if(s.phase_frame==32) {
            g.center={motion::wrap(int(s.position.current.x)-320),motion::wrap(int(s.position.current.y)-128)};
            g.ring_points=16;g.angle_delta=254;g.color=3;g.radius=4096;gathers.add(g,t,true);
        } else if(s.phase_frame==34 || s.phase_frame==36) {
            if(s.phase_frame==34) g.color=2;
            gathers.add(g,t,true);
        }
    }
    if(s.phase_frame==16) { s.sprite=130;emit(sink,orange::EventType::sound,{},8); }
    else if(s.phase_frame==30) emit(sink,orange::EventType::circle,{motion::wrap(int(s.position.current.x)-320),motion::wrap(int(s.position.current.y)-128)});
    else if(s.phase_frame>=44 && s.phase_frame<64) s.sprite=byte((s.phase_frame-32)/4+128);
    else if(s.phase_frame==64) { s.sprite=130;emit(sink,orange::EventType::sound,{},15);return 2; }
    return s.phase_frame<64 ? 0 : 1;
}
void System::move(randring::SharedRandomRing& random) {
    auto& p=state_.boss.position;
    if((static_cast<std::uint16_t>(state_.boss.phase_frame)&31)==1) {
        p.velocity.x=p.current.x<=1792 ? 32 : (p.current.x>=4352 ? -32 : (random.next16_and(1) ? 16 : -16));
        if(p.current.y<=1280) p.velocity.y=16;
        else if(p.current.y>=2304) p.velocity.y=-16;
        else { const auto d=random.next16_and(3);p.velocity.y=static_cast<std::int16_t>(d==0 ? 16 : (d==1 ? -16 : (d==2 ? 24 : -24))); }
    }
    p.update();
}
bool System::flystep(std::int16_t duration) {
    auto& s=state_.boss;auto& tick=s.additional[13];auto& p=s.position;
    if(!tick) {
        // Modes1/2 pass160-last_alive_clock. A final bit lost after clock148
        // can make the next four-frame firing tick pass12 here and fault.
        // This core preserves the observed error; a production runtime repair
        // must be an explicit portable policy, with its own controls.
        const auto divisor=motion::wrap(int(duration)/2-6);
        // Sequential writes matter: Y can fail after the X velocity commits.
        p.velocity.x=divide(motion::wrap(3072-int(p.current.x)),divisor);
        p.velocity.y=divide(motion::wrap(1792-int(p.current.y)),divisor);
    }
    ++tick;
    if(tick>=motion::wrap(int(duration)-12)) {
        p.velocity.x=static_cast<std::int16_t>(p.velocity.x/2);p.velocity.y=static_cast<std::int16_t>(p.velocity.y/2);
    }
    if(tick>=duration) return true;
    p.update();return false;
}
bool System::hittest_phase(const Context& c,const Sink& sink) {
    auto& s=state_.boss;s.phase_frame=motion::wrap(int(s.phase_frame)+1);s.hitbox_radius={384,384};
    emit(sink,orange::EventType::hit,s.position.current,384,384);
    const auto damage=c.hit ? c.hit(s.position.current,s.hitbox_radius) : std::uint16_t{0};
    if(damage) emit(sink,orange::EventType::sound,{},4);
    s.damage=byte(damage);s.hp=motion::wrap(int(s.hp)-s.damage/(int(state_.alive)+1));
    return s.hp<=s.end_hp;
}
void System::pattern(const Context& c,bullet::System& bullets,gather::System& gathers,randring::SharedRandomRing& random,const Sink& sink) {
    auto& s=state_.boss;auto& t=bullets.scratch();auto& g=gathers.scratch();
    const auto sound=[&](unsigned n) { emit(sink,orange::EventType::sound,{},n); };
    const auto entry=[&] { return phase_entry(gathers,t,sink); };
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto fire=[&](bool special=false,bool fixed=false) { bullets.add(t,c.bullets,random,special,fixed); };
    const auto bits=[&] { fire_bits(c,bullets,random); };
    const auto fly_without_bits=[&] {
        auto duration=static_cast<std::int16_t>(160-s.additional[15]);
        // Explicit portable gameplay policy. Preserve every other duration
        // and the strict flystep API's divide/overflow failure behavior.
        if(c.repair_flystep_zero_divisor && (duration==12 || duration==13)) duration=14;
        return flystep(duration);
    };
    const auto finish=[&] { s.phase_frame=0;s.mode=255;s.sprite=129; };
    const auto reverse=[&](unsigned step) { for(unsigned i=0;i<4;i+=step) state_.bits[i].angle_speed=signed_byte(-int(state_.bits[i].angle_speed)); };
    const auto stack=[&](bool aimed) { t.spawn_type=4;t.pattern=57;t.group=aimed ? BG_STACK_AIMED : BG_STACK;t.count=16;t.delta=5;t.speed=16;tune();fire(false,true); };
    const unsigned mode=s.mode;const auto stage=entry();
    // Mode7 calls the entry helper twice, including both sounds at clock64.
    if(mode==7) {
        if(stage==2) { s.additional[14]=32;s.additional[15]=byte(random.next16_and(1)); }
        if(entry()!=1) return;
    } else if(mode==0) {
        switch(s.phase_frame) {
        case 32:g.center=s.position.current;g.ring_points=32;g.angle_delta=254;g.color=9;g.radius=4096;gathers.add(g,t,true);break;
        case 34:g.color=8;[[fallthrough]];
        case 36:gathers.add(g,t,true);break;
        case 64:initialize_bits(random);state_.angle_speed=byte(-int(state_.angle_speed));break;
        case 96:finish();break;
        }
        return;
    } else if(stage==2) {
        switch(mode) {
        case 1:t.spawn_type=1;t.speed=56;t.group=BG_SPREAD;t.count=3;t.delta=8;tune();state_.fire=Fire::spread;s.additional[15]=byte(s.phase_frame);break;
        case 2:t.spawn_type=1;t.speed=16;t.group=BG_SINGLE;tune();state_.fire=Fire::single;
            for(unsigned i=0;i<4;++i) state_.bits[i].angle_speed=signed_byte(int(state_.bits[i].angle_speed)*2);
            s.additional[15]=byte(s.phase_frame);break;
        case 3:t.spawn_type=1;state_.fire=Fire::spread;s.additional[15]=0;break;
        case 4:t.spawn_type=5;t.pattern=57;t.speed=50;t.group=BG_RING_AIMED;t.angle=0;tune();state_.fire=Fire::single;break;
        case 5:t.spawn_type=2;t.pattern=56;t.speed=92;t.group=BG_SINGLE;t.special_motion=131;tune();state_.fire=Fire::single;s.additional[15]=0;break;
        case 6:t.spawn_type=2;t.pattern=56;t.group=BG_SINGLE;t.special_motion=255;t.angle=192;t.speed=96;state_.fire=Fire::single;s.additional[15]=0;break;
        case 10:t.spawn_type=4;t.pattern=57;t.group=BG_SPREAD;t.angle=128;t.delta=8;tune();break;
        case 11:t.spawn_type=1;t.count=32;t.group=BG_RING;t.speed=56;tune();s.additional[15]=random.next16_and(1) ? 255 : 1;break;
        }
        return;
    } else if(stage!=1) return;
    switch(mode) {
    case 1:
        if(s.phase_frame%4==0) {
            if(state_.alive) { bits();s.additional[15]=byte(s.phase_frame); }
            else {
                fly_without_bits();t.spawn_type=2;t.pattern=76;t.speed=52;t.group=BG_SPREAD;t.count=3;t.delta=6;t.angle=byte(t.angle+6);tune();
                for(unsigned i=0;i<4;++i) { fire();if(i<3) t.angle=byte(t.angle+64); }
            }
            sound(9);
        }
        if(s.phase_frame>=160) { reverse(1);finish(); }break;
    case 2:
        if(s.phase_frame%4==0) {
            t.angle=motion::angle_to(s.position.current,c.bullets.player);
            if(state_.alive) { bits();s.additional[15]=byte(s.phase_frame); }
            else { fly_without_bits();t.spawn_type=2;t.pattern=56;t.group=BG_SPREAD_AIMED;t.count=3;t.delta=12;t.angle=0;tune();fire(); }
            t.speed=byte(t.speed+4);sound(9);
        }
        if(s.phase_frame>=160) {
            for(unsigned i=0;i<4;++i) state_.bits[i].angle_speed=static_cast<std::int8_t>(state_.bits[i].angle_speed/2);
            finish();
        }break;
    case 3:
        // Expansion/contraction updates all four distances, even dead slots.
        if(state_.alive) {
            if(s.phase_frame<=192) { for(unsigned i=0;i<4;++i) state_.bits[i].distance=motion::wrap(int(state_.bits[i].distance)+24); }
            else if(s.phase_frame<=256) {
                if(s.phase_frame%4) break;
                if(s.phase_frame%32==0) { t.speed=32;t.group=BG_RING_AIMED;t.count=16;tune();fire(); }
                t.group=BG_SPREAD;t.count=3;t.delta=6;tune();t.speed=64;sound(9);bits();
            } else if(s.phase_frame<=384) { for(unsigned i=0;i<4;++i) state_.bits[i].distance=motion::wrap(int(state_.bits[i].distance)-24); }
            else { reverse(2);finish(); }
            break;
        }
        flystep(96);
        if(!s.additional[15]) { s.additional[15]=1;t.spawn_type=4;t.pattern=57;t.group=BG_SPREAD;t.angle=128;t.delta=8;sound(15); }
        if(s.phase_frame%2) break;
        t.count=byte(random.next16_and(3)+1);t.speed=byte(random.next16_and(31)+16);
        t.angle=byte(t.angle+(s.additional[15]&1 ? -8 : 8));t.origin.x=motion::wrap(int(t.origin.x)-96);fire();
        t.count=byte(random.next16_and(3)+1);t.speed=byte(random.next16_and(31)+16);t.origin.x=motion::wrap(int(t.origin.x)+192);fire();
        if(t.angle && t.angle<128) break;
        ++s.additional[15];if(s.additional[15]<4) sound(15);else finish();break;
    case 4:
        // Count changes after the clock64 tune; do not retune each burst.
        if(state_.alive) {
            if(s.phase_frame%32==0) { t.count=byte(24-2*state_.alive);if(state_.variant==2) t.count=28;bits();sound(9); }
            if(s.phase_frame>=160) { reverse(2);finish(); }break;
        }
        if(flystep(64)) { finish();break; }
        if(s.phase_frame%16) break;
        t.spawn_type=4;t.pattern=61;t.group=BG_SINGLE_AIMED;t.special_motion=255;tune();
        for(unsigned i=0;i<32;++i) {
            t.origin={motion::wrap(int(s.position.current.x)-832+random.next16_mod(1024)),motion::wrap(int(s.position.current.y)-640+random.next16_mod(1024))};
            int speed=random.next16_mod(96)+16;t.speed=byte(speed);
            if(speed>=64) t.angle=0;
            else { speed=64-speed;t.angle=byte(int(random.next16_mod(static_cast<std::uint16_t>(speed)))-speed/2); }
            fire(true);
        }
        sound(15);break;
    case 5:
        // The surviving-bit branch fires from the retained body origin.
        // It updates the process-wide target angle instead of firing bits.
        if(state_.alive) {
            if(s.phase_frame<=224 && s.phase_frame%4==0) {
                if(s.phase_frame<=128 && s.phase_frame>96) {
                    for(unsigned i=0;i<4;++i) { bullets.set_special_angle(i&1 ? 80 : 48);t.angle=byte(144+32*i);fire(true,true); }
                } else {
                    bullets.set_special_angle(s.phase_frame<=96 ? 64 : (s.phase_frame<=160 ? 112 : (s.phase_frame<=192 ? 16 : 64)));
                    t.angle=16;for(unsigned i=0;i<4;++i) { fire(true,true);t.angle=byte(t.angle+32); }
                }
                sound(3);
            }
        } else {
            flystep(128);if(!s.additional[15]) { t.angle=byte(128-random.next16_and(31));s.additional[15]=1; }
            if(s.phase_frame%8==0) { stack(false);t.angle=byte(t.angle-8);sound(15); }
            if(t.angle>128 && t.angle<=224) { finish();break; }
        }
        if(s.phase_frame>=256) finish();
        break;
    case 6:
        if(state_.alive) {
            if(s.phase_frame<=128) { if(c.frame%4==0) { bits();sound(9); } }
            else if(s.phase_frame<=192) {
                if(c.frame%4) break;
                t.origin={0,static_cast<std::int16_t>(random.next16_mod(3072))};t.speed=byte(random.next16_and(31)+16);t.angle=byte(48-random.next16_and(31));fire(true);
                t.origin={6144,static_cast<std::int16_t>(random.next16_mod(3072))};t.speed=byte(random.next16_and(31)+16);t.angle=byte(random.next16_and(31)+80);fire(true);
                t.origin={static_cast<std::int16_t>(random.next16_mod(6144)),0};t.speed=byte(random.next16_and(31)+16);t.angle=byte(random.next16_and(31)+48);fire(true);
            } else if(s.phase_frame>=256) finish();
        } else {
            flystep(160);if(!s.additional[15]) { t.angle=byte(random.next16_and(31));s.additional[15]=1; }
            if(s.phase_frame%8==0) { stack(false);t.angle=byte(t.angle+8);sound(15); }
            if(s.phase_frame>=192) finish();
        }break;
    case 7:
        if(state_.alive) {
            if(s.phase_frame%4==0) {
                state_.fire=Fire::single;t.spawn_type=1;t.speed=32;t.group=BG_SINGLE;t.angle=byte(c.frame*8);if(s.additional[15]) t.angle=byte(-int(t.angle));tune();bits();
                if(s.phase_frame%8==0) { state_.fire=Fire::spread;t.spawn_type=4;t.pattern=57;t.speed=s.additional[14];s.additional[14]=byte(s.additional[14]+2);t.group=BG_SINGLE;t.angle=0;tune();bits(); }
                sound(9);
            }
            if(s.phase_frame>=160) { reverse(1);finish(); }
        } else {
            if(flystep(72)) { finish();break; }
            if(s.phase_frame%8==0) { t.angle=0;stack(true);sound(15); }
        }break;
    case 10:
        if(s.phase_frame%2==0) {
            t.count=byte(random.next16_and(3)+1);t.speed=byte(random.next16_and(31)+32);t.angle=byte(t.angle-8);t.origin.x=motion::wrap(int(t.origin.x)-96);fire();
            t.count=byte(random.next16_and(3)+1);t.speed=byte(random.next16_and(31)+32);t.origin.x=motion::wrap(int(t.origin.x)+192);fire();
        }
        if(!t.angle) finish();
        break;
    case 11:
        if(s.phase_frame%8==0) { fire();t.angle=byte(t.angle+s.additional[15]);sound(9); }
        if(s.phase_frame>=128) finish();
        break;
    }
}
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,spark::System& sparks,randring::SharedRandomRing& random,const Sink& sink) {
    auto& s=state_.boss;auto& t=bullets.scratch();
    const auto sound=[&](unsigned n) { emit(sink,orange::EventType::sound,{},n); };
    const auto small=[&](unsigned type) { explode(s.small[s.small[0].alive ? 1 : 0],s.position.current,type);sound(15); };
    const auto increment=[&] { s.phase_frame=motion::wrap(int(s.phase_frame)+1); };
    const auto invulnerable=[&] {
        increment();emit(sink,orange::EventType::hit,s.position.current,static_cast<std::uint16_t>(s.hitbox_radius.x),static_cast<std::uint16_t>(s.hitbox_radius.y));
        if(c.hit && c.hit(s.position.current,s.hitbox_radius)) sound(10);
    };
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;s.score_delta+=static_cast<std::uint16_t>(units*1280u);
        const auto left=motion::wrap(int(s.position.current.x)-1024),top=motion::wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<units;++i) {
            const auto x=motion::wrap(int(left)+random.next16_mod(2048)),y=motion::wrap(int(top)+random.next16_mod(2048));
            emit(sink,orange::EventType::point,{static_cast<std::int16_t>(std::clamp(int(x),0,6144)),y},1280);
        }
        s.timed_out=0;
    };
    const auto items=[&] {
        const auto left=motion::wrap(int(s.position.current.x)-1024),top=motion::wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<5;++i) {
            const auto x=motion::wrap(int(left)+random.next16_mod(2048)),y=motion::wrap(int(top)+random.next16_mod(2048));
            emit(sink,orange::EventType::item,{x,y},c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0));
        }
    };
    t.origin={motion::wrap(int(s.position.current.x)-320),motion::wrap(int(s.position.current.y)-128)};
    switch(s.phase) {
    case 0:
        if(!s.phase_frame) { s.hp=6000;state_.angle_speed=2; }
        invulnerable();
        if(s.phase_frame>96) {
            ++s.phase;s.palette_zero={0,0,7};s.palette_changed=1;s.phase_frame=0;sound(13);s.background=orange::Background::npc;s.tile_column=15;state_.palette_direction=0;
        }break;
    case 1:
        increment();invulnerable(); // Entrance advances twice per update.
        if(s.phase_frame>=128) {
            ++s.phase;s.position.velocity.x=0;s.patterns_or_bonus=0;s.mode=10;s.phase_frame=0;s.sprite=129;
            state_.bitless_cycle=1;state_.variant=0;state_.previous_mode=10;state_.previous_alive=0;s.additional[13]=0;
        }break;
    case 2: {
        bool complete=false;
        if(s.mode==255) {
            move(random);
            if(s.phase_frame>=64) {
                ++s.patterns_or_bonus;s.additional[13]=0;
                if(!state_.previous_alive && !state_.alive) {
                    ++state_.bitless_cycle;
                    if(state_.bitless_cycle>=2) { s.mode=0;state_.bitless_cycle=0; }
                    else s.mode=byte(random.next16_and(1)+10);
                } else {
                    unsigned candidate;
                    do { candidate=random.next16_mod(7)+1; } while(candidate==state_.previous_mode);
                    s.mode=byte(candidate);state_.previous_mode=s.mode;state_.previous_alive=state_.alive;
                }
                s.phase_frame=0;
                if(s.patterns_or_bonus>=52) { s.patterns_or_bonus=0;complete=true; }
            }
        } else if(s.mode<=7 || s.mode==10 || s.mode==11) pattern(c,bullets,gathers,random,sink);
        if(!complete && hittest_phase(c,sink)) { s.patterns_or_bonus=1;complete=true; }
        if(complete) { small(3);++s.phase;s.phase_frame=0; }
        if(c.frame%4==0) {
            if(!state_.palette_direction) { s.palette_zero[2]=byte(s.palette_zero[2]+2);if(s.palette_zero[2]>=192) state_.palette_direction=1; }
            else { s.palette_zero[2]=byte(s.palette_zero[2]-2);if(s.palette_zero[2]<=38) state_.palette_direction=0; }
            s.palette_changed=1;
        }
        if((s.hp<=4500 && state_.variant==0) || (s.hp<=2500 && state_.variant==1) || (s.hp<=1000 && state_.variant==2)) {
            items();if(bullets.snapshot().clear_time<20) bullets.clear();bonus(10);small(state_.variant);++state_.variant;
        }
        break;
    }
    case 3:
        increment();if(s.phase_frame==16) small(4);
        if(s.phase_frame==32) {
            explode(s.big,s.position.current,2);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);
            if(s.patterns_or_bonus) bonus(40);
            s.sprite=4;s.phase_frame=0;sound(12);s.palette_zero[0]=s.palette_zero[2]=0;s.palette_changed=1;s.invincibility=255;
        }break;
    default:orange::update_defeat(s,c,sink);return;
    }
    // alive used above is the PREVIOUS update's count. Body hits, mode choice
    // and bullet callbacks precede bit motion/destruction and packed centers.
    s.homing=s.position.current;update_bits(c,sparks,random,sink);emit(sink,orange::EventType::hp,{},static_cast<std::uint16_t>(s.hp),6000);
}
} // namespace th04::portable::marisa
