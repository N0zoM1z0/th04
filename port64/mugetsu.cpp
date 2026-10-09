#include "mugetsu.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::mugetsu {
namespace {
using motion::wrap;
std::uint8_t byte(int value) { return std::uint8_t(value); }
void emit(const orange::Sink& sink,orange::EventType kind,motion::Point p={},unsigned value=0,unsigned count=0) {
    if(sink)sink({kind,p,std::uint16_t(value),std::uint16_t(count)});
}
void explosion(orange::Explosion& e,motion::Point center,unsigned type) {
    e.alive=1;e.age=0;e.center=center;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if(type==1)e.angle_offset=32;else if(type==2)e.angle_offset=224;
    else if(type==3)e.delta={208,112};else if(type==4)e.delta={112,208};
}
}
unsigned System::transition(const Context& c,bullet::System& bullets,gather::System& gathers,const orange::Sink& sink) {
    auto& q=state_;auto& s=q.boss;auto& g=gathers.scratch();
    q.gather_offset=q.transition==Transition::first ? 16 : q.transition==Transition::teleport ? 0 : -80;
    switch(wrap(int(s.phase_frame)+q.gather_offset)) {
    case 32:g.radius=5120;g.center={q.anchor.x,wrap(int(q.anchor.y)-160)};g.ring_points=16;g.color=14;[[fallthrough]];
    case 34:case 36:
        if(wrap(int(s.phase_frame)+q.gather_offset)==34)g.color=7;
        g.angle_delta=254;gathers.add(g,bullets.scratch(),true);
        g.angle_delta=2;gathers.add(g,bullets.scratch(),true);break;
    case 48:emit(sink,orange::EventType::circle,g.center);s.circle_color=15;break;
    }
    const auto f=s.phase_frame;
    if(q.transition==Transition::first) {
        if(f<16)return 0;
        if(f==16){s.sprite=129;return 0;}
        if(s.sprite<24)return 0;
        if(f<48){if(f==24)emit(sink,orange::EventType::sound,{},8);s.sprite=c.frame%2 ? 130 : 129;return 0;}
        if(f==48){s.sprite=128;return 1;}
        return f<128 ? 2 : 3;
    }
    switch(f) {
    case 34:s.sprite=0;s.position.current=q.anchor;break;
    case 32:case 38:s.sprite=135;break;
    case 30:case 40:s.sprite=134;break;
    case 28:case 42:s.sprite=133;break;
    case 26:case 44:s.sprite=132;break;
    case 24:case 46:s.sprite=131;break;
    case 16:case 48:s.sprite=129;break;
    }
    const int limit=q.transition==Transition::teleport ? 64 : 128;
    const int end=q.transition==Transition::teleport ? 144 : 192;
    if(f<48)return 0;
    if(f<limit) {
        // The short callback's original frame32 sound test sits inside
        // the >=48 branch and is unreachable; preserve that control flow.
        if(q.transition==Transition::long_teleport && f==48)emit(sink,orange::EventType::sound,{},8);
        s.sprite=c.frame%2 ? 130 : 129;return 0;
    }
    if(f==limit){s.sprite=128;return 1;}
    return f<end ? 2 : 3;
}
void System::pattern(Attack attack,const Context& c,bullet::System& bullets,gather::System& gathers,randring::SharedRandomRing& random,const orange::Sink& sink) {
    auto& s=state_.boss;auto& t=bullets.scratch();
    const auto sound=[&](unsigned id){emit(sink,orange::EventType::sound,{},id);};
    const auto fire=[&](bool special=false,bool fixed=false){bullets.add(t,c.bullets,random,special,fixed);};
    const auto finish=[&]{s.phase_frame=0;s.mode=255;};
    if(attack==Attack::final_rings) {
        if(c.frame%8)return;
        t.angle=s.angle;t.group=BG_RING;t.count=16;t.speed=byte(s.phase_frame/256+32);fire();
        t.pattern=76;t.spawn_type=2;t.angle=byte(-int(t.angle)*2);t.count=4;t.speed=byte(t.speed+16);fire();
        s.angle=byte(s.angle+(s.phase_frame%1024<512 ? 3 : -3));return;
    }
    if(attack==Attack::saturation) {
        if(c.frame%8)return;
        t.group=BG_RING;t.count=32;t.pattern=76;t.spawn_type=2;t.angle=byte(random.next16());t.speed=112;fire();return;
    }
    const auto step=transition(c,bullets,gathers,sink);
    switch(attack) {
    case Attack::accelerating_ring:
        if(step==1){t.group=BG_RING;t.count=8;t.speed=32;t.angle=byte(random.next16());s.additional[15]=byte(random.next16_and(1));}
        else if(step==2 && c.frame%4==0){fire();t.speed=byte(t.speed+3);t.angle=byte(t.angle+(s.additional[15] ? 4 : -4));sound(3);}
        else if(step==3)finish();break;
    case Attack::cross_turns:
        if(step==1) {
            sound(15);t.spawn_type=2;t.pattern=59;t.angle=0;t.group=BG_RING;t.count=32;t.special_motion=129;t.speed=40;
            bullets.set_special_parameter(2);bullets.set_special_angle(224);bullet::tune(t,c.bullets.rank,c.bullets.performance);fire(true,true);
            bullets.set_special_angle(32);fire(true,true);t.angle=motion::angle_to(s.position.current,c.bullets.player);t.delta=66;
        } else if(step==2) {
            const auto mod=s.phase_frame&7;if(!mod)t.delta=byte(t.delta-8);
            t.spawn_type=2;t.pattern=76;t.speed=byte(mod*12+32);t.group=BG_SPREAD;t.count=2;fire();if(c.frame%4==0)sound(3);
        } else if(step==3)finish();break;
    case Attack::cloud_ring:
        if(step==1){t.spawn_type=5;t.pattern=57;t.group=BG_RING;t.count=40;t.speed=16;t.angle=byte(random.next16());fire();sound(15);}
        else if(step==2)finish();break;
    case Attack::random_turns:
        if(step==1){t.special_motion=129;t.group=BG_SINGLE;bullets.set_special_parameter(1);}
        else if(step==2 && c.frame%2) {
            t.spawn_type=2;t.pattern=58;t.speed=byte(random.next16_and(63)+16);
            t.origin={wrap(int(s.position.current.x)-512+random.next16_mod(1024)),wrap(int(s.position.current.y)-416+random.next16_mod(512))};
            t.angle=0;bullets.set_special_angle(64);fire(true);
            t.speed=byte(random.next16_and(63)+16);t.angle=128;bullets.set_special_angle(192);fire(true);sound(9);
        } else if(step==3)finish();break;
    case Attack::random_rings:
        if(step==1){t.group=BG_RING;t.count=32;bullet::tune(t,c.bullets.rank,c.bullets.performance);}
        else if(step==2 && c.frame%8==0) {
            t.spawn_type=byte(random.next16_and(1));t.pattern=57;t.speed=byte(random.next16_and(63)+16);
            t.origin={wrap(int(s.position.current.x)-512+random.next16_mod(1024)),wrap(int(s.position.current.y)-416+random.next16_mod(512))};
            t.angle=byte(random.next16());fire();sound(3);
        } else if(step==3)finish();break;
    default:break;
    }
}
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,randring::SharedRandomRing& random,const orange::Sink& sink) {
    auto& q=state_;auto& s=q.boss;auto& t=bullets.scratch();
    const auto sound=[&](unsigned id){emit(sink,orange::EventType::sound,{},id);};
    const auto tick=[&]{s.phase_frame=wrap(int(s.phase_frame)+1);};
    const auto hit=[&] {
        if(q.bomb_invincibility) {
            emit(sink,orange::EventType::hit,s.position.current,768,768);
            const auto d=c.hit ? c.hit(s.position.current,{768,768}) : 0;if(d)sound(10);
        } else if(s.sprite<=130 && s.sprite) {
            tick();emit(sink,orange::EventType::hit,s.position.current,std::uint16_t(s.hitbox_radius.x),std::uint16_t(s.hitbox_radius.y));
            const auto d=c.hit ? c.hit(s.position.current,s.hitbox_radius) : 0;if(d)sound(4);
            s.damage=byte(d);s.hp=wrap(int(s.hp)-s.damage);return s.hp<=s.end_hp;
        }
        tick();return false;
    };
    const auto small=[&](unsigned type){explosion(s.small[s.small[0].alive ? 1 : 0],s.position.current,type);sound(15);};
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;s.score_delta+=std::uint16_t(units*1280u);
        const auto x=wrap(int(s.position.current.x)-1024),y=wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<units;++i) {
            const auto px=wrap(int(x)+random.next16_mod(2048)),py=wrap(int(y)+random.next16_mod(2048));
            emit(sink,orange::EventType::point,{std::int16_t(std::clamp(int(px),0,6144)),py},1280);
        }s.timed_out=0;
    };
    const auto drops=[&] {
        const auto x=wrap(int(s.position.current.x)-1024),y=wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<5;++i) {
            const auto px=wrap(int(x)+random.next16_mod(2048)),py=wrap(int(y)+random.next16_mod(2048));
            emit(sink,orange::EventType::item,{px,py},c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0));
        }
    };
    if(c.bombing)q.bomb_invincibility=32;
    if(q.bomb_invincibility)--q.bomb_invincibility;
    t.origin={s.position.current.x,wrap(int(s.position.current.y)-160)};t.spawn_type=1;
    const auto attack=[&](Attack a){pattern(a,c,bullets,gathers,random,sink);};
    switch(s.phase) {
    case 0:
        if(!s.phase_frame){q.stage_vm_disabled=true;q.midboss_frames_until=0;q.transition=Transition::first;q.bomb_invincibility=0;s.hp=9400;s.end_hp=3700;q.anchor=s.position.current;}
        hit();if(s.phase_frame<=128)break;
        ++s.phase;s.phase_frame=0;sound(13);s.tile_column=15;s.background=orange::Background::npc;break;
    case 1:
        hit();if(s.phase_frame<64)break;
        ++s.phase;s.mode=0;s.patterns_or_bonus=2;s.phase_frame=0;s.position.velocity.x=0;q.cycle=0;break;
    case 2:
        switch(s.mode) {
        case 0:case 6:attack(Attack::accelerating_ring);break;
        case 3:attack(Attack::random_turns);break;
        case 1:case 4:case 5:attack(Attack::cloud_ring);break;
        case 2:case 7:attack(Attack::cross_turns);break;
        case 255:
            if(s.phase_frame>16) {
                if(random.next16_and(3)==0)q.transition=Transition::first;
                else {
                    q.transition=Transition::teleport;unsigned mode;
                    do{mode=random.next16_mod(5);}while(mode==s.patterns_or_bonus);
                    s.patterns_or_bonus=byte(mode);q.anchor={wrap(int(mode)*1024+1024),s.position.current.y};
                }
                s.phase_frame=0;++q.cycle;s.mode=q.cycle&7;
            }break;
        }
        if(q.cycle>=32 && s.mode!=255 && s.phase_frame>24)attack(Attack::saturation);
        if(q.cycle<36){if(!hit())break;bonus(100);}
        bullets.clear();drops();small(0);++s.phase;s.phase_frame=0;s.mode=0;s.patterns_or_bonus=0;s.hp=s.end_hp;s.end_hp=0;q.cycle=0;q.anchor.x=3072;break;
    case 3:
        hit();if(s.phase_frame<64)break;
        ++s.phase;q.transition=Transition::long_teleport;s.phase_frame=0;break;
    case 4:
        hit();attack(Attack::random_rings);if(s.phase_frame)break;
        small(3);++s.phase;s.phase_frame=0;s.sprite=129;break;
    case 5:
        hit();if(s.phase_frame<128)break;++s.phase;s.phase_frame=0;break;
    case 6:
        attack(Attack::final_rings);if(s.phase_frame>=3000)attack(Attack::saturation);
        if(!hit() && s.phase_frame<4000)break;
        small(1);++s.phase;s.patterns_or_bonus=byte(s.phase_frame<4000);s.phase_frame=0;s.mode=0;s.palette_tone=100;s.palette_changed=1;break;
    case 7:
        tick();if(s.phase_frame==16)small(4);
        if(s.phase_frame==32) {
            explosion(s.big,s.position.current,2);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);
            if(s.patterns_or_bonus)bonus(200);
            s.sprite=4;s.phase_frame=0;sound(12);s.palette_changed=1;s.invincibility=255;
        }break;
    case 254:orange::update_defeat(s,c,sink);return;
    default:throw std::logic_error("Mugetsu phase requires the Extra dialog owner");
    }
    s.homing=s.position.current;emit(sink,orange::EventType::hp,{},std::uint16_t(s.hp),9400);
}
void System::prepare_render() {
    draws_.clear();auto& q=state_;auto& s=q.boss;
    const auto pixels=[](int n){return n>=0 ? n/16 : -((-n+15)/16);};
    const int x=pixels(s.position.current.x),y=pixels(s.position.current.y)-32;
    const auto draw=[&](orange::DrawKind kind,int left,unsigned pat){draws_.push_back({kind,wrap(left),wrap(y),std::uint16_t(pat),0});};
    if(s.sprite) {
        if(s.phase<254) {
            if(!s.damage) {
                draw(orange::DrawKind::sprite,x,s.sprite);
                if(q.bomb_invincibility && (q.bomb_invincibility>=32 || q.bomb_invincibility%2)) {
                    draw(orange::DrawKind::sprite,x-15,136);draw(orange::DrawKind::sprite,x+33,137);
                }
            } else {++q.flash;draw(q.flash%2 ? orange::DrawKind::sprite : orange::DrawKind::white_sprite,x,s.sprite);s.damage=0;}
        } else if(s.phase==254)draw(orange::DrawKind::large_sprite,x,s.sprite);
    }
    orange::prepare_explosions(s,draws_);
}
std::vector<BackgroundDraw> background(std::uint8_t phase,std::int16_t clock) {
    if(!phase)return clock<=2 ? std::vector<BackgroundDraw>{{5},{0}} : std::vector<BackgroundDraw>{{1}};
    if(phase==1) {
        const auto cel=byte(clock/4);
        if(cel<8)return {{0},{3,cel}};
        return {{4},{2,32,16,16},{3,cel}};
    }
    if(phase<254)return {{2,32,16,16},{4}};
    return {{phase==254 || clock<=2 ? 0u : 1u}};
}
}
