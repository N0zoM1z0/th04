#include "gengetsu.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::gengetsu {
Snapshot prepare_after_dialog(Snapshot state) {
    auto& boss=state.boss;
    boss.additional[0]=1;
    boss.phase=0;boss.mode=0;boss.patterns_or_bonus=0;
    boss.phase_frame=0;boss.position.velocity={};boss.damage=0;
    for(auto& explosion:boss.small)explosion.alive=0;
    boss.timed_out=1;
    boss.position.current=boss.position.previous={3072,1536};
    boss.sprite=128;boss.hitbox_radius={384,768};boss.bombing_disabled=0;
    return state;
}
namespace {
using motion::wrap;
std::uint8_t byte(int value) { return std::uint8_t(value); }
void emit(const orange::Sink& sink,orange::EventType kind,motion::Point p={},unsigned value=0,unsigned count=0) {
    if(sink)sink({kind,p,std::uint16_t(value),std::uint16_t(count)});
}
void explosion(orange::Explosion& e,motion::Point p,unsigned type) {
    e.alive=1;e.age=0;e.center=p;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if(type==1)e.angle_offset=32;else if(type==2)e.angle_offset=224;
    else if(type==3)e.delta={208,112};else if(type==4)e.delta={112,208};
}
}
void System::gather_intro(bullet::System& bullets,gather::System& gathers,const orange::Sink& sink) {
    auto& s=state_.boss;auto& g=gathers.scratch();
    switch(s.phase_frame) {
    case 48:g.radius=5120;g.center={wrap(int(s.position.current.x)-208),wrap(int(s.position.current.y)-768)};g.ring_points=16;g.color=15;break;
    case 50:g.color=9;break;
    case 52:break;
    case 64:emit(sink,orange::EventType::circle,g.center);s.circle_color=15;return;
    default:return;
    }
    g.angle_delta=254;gathers.add(g,bullets.scratch(),true);
    g.angle_delta=2;gathers.add(g,bullets.scratch(),true);
}
bool System::wave_step() {
    auto& q=state_;auto& s=q.boss;
    if(s.phase_frame==1)s.position.velocity.x=wrap(int(q.wave_target)-s.position.current.x)/64;
    s.position.current.x=wrap(int(s.position.current.x)+s.position.velocity.x);
    q.wave_amplitude=byte(q.wave_amplitude+(s.phase_frame<=32 ? 2 : -2));
    if(s.phase_frame!=64)return false;
    q.wave_amplitude=0;return true;
}
bool System::wave_bounce() {
    auto& q=state_;auto& s=q.boss;
    if(s.phase_frame==1)s.position.velocity.x=s.position.current.x<3072 ? 32 : -32;
    if((s.position.velocity.x<0 && s.position.current.x>=3088) || (s.position.velocity.x>0 && s.position.current.x<=3072))
        s.position.current.x=wrap(int(s.position.current.x)+s.position.velocity.x);
    q.wave_amplitude=byte(q.wave_amplitude+(s.phase_frame<=64 ? 1 : -1));
    if(s.phase_frame!=128)return false;
    s.position.current.x=3072;q.wave_amplitude=0;return true;
}
unsigned System::phase_state(const Context& c,bullet::System& bullets,gather::System& gathers,const orange::Sink& sink) {
    auto& s=state_.boss;gather_intro(bullets,gathers,sink);
    if(s.phase_frame<8)return 0;
    if(s.phase_frame==8){s.sprite=130;return 0;}
    if(s.sprite<32)return 0;
    if(s.phase_frame<80) {
        if(s.phase_frame==32)emit(sink,orange::EventType::sound,{},8);
        s.sprite=c.frame%2 ? 134 : 130;return 1;
    }
    if(s.phase_frame==80){s.sprite=132;return 2;}
    if(s.phase_frame<144)return 3;
    s.sprite=132;return 4;
}
bool System::hit(const Context& c,const orange::Sink& sink) {
    auto& q=state_;auto& s=q.boss;
    if(!q.wave_amplitude && (q.bomb_invincibility || s.sprite)) {
        const bool bomb=q.bomb_invincibility!=0;const auto radius=bomb ? motion::Point{768,768} : s.hitbox_radius;
        if(!bomb)s.phase_frame=wrap(int(s.phase_frame)+1);
        emit(sink,orange::EventType::hit,s.position.current,std::uint16_t(radius.x),std::uint16_t(radius.y));
        const auto damage=c.hit ? c.hit(s.position.current,radius) : 0;
        if(damage)emit(sink,orange::EventType::sound,{},bomb ? 10 : 4);
        if(!bomb){s.damage=byte(damage);s.hp=wrap(int(s.hp)-s.damage);return s.hp<=s.end_hp;}
    }
    s.phase_frame=wrap(int(s.phase_frame)+1);return false;
}
void System::pattern(Attack attack,const Context& c,bullet::System& bullets,gather::System& gathers,randring::SharedRandomRing& random,const orange::Sink& sink) {
    auto& q=state_;auto& s=q.boss;auto& t=bullets.scratch();auto& g=gathers.scratch();
    const auto sound=[&](unsigned id){emit(sink,orange::EventType::sound,{},id);};
    const auto fire=[&](bool special=false,bool fixed=false){bullets.add(t,c.bullets,random,special,fixed);};
    const auto aimed=[&]{return motion::angle_to(t.origin,c.bullets.player);};
    const auto finish=[&]{s.phase_frame=0;s.mode=255;};
    if(attack==Attack::blue_ring) {
        if(c.frame%8)return;
        t.group=BG_RING;t.count=32;t.pattern=76;t.spawn_type=2;t.angle=byte(random.next16());t.speed=112;fire();return;
    }
    if(attack==Attack::random_ring) {
        s.sprite=128;if(c.frame%8)return;
        t.angle=byte(random.next16());t.origin={wrap(random.next16_mod(1024)+wrap(int(s.position.current.x)-512)),
            wrap(random.next16_mod(512)+wrap(int(s.position.current.y)-416))};
        t.group=BG_RING;t.count=16;t.spawn_type=2;t.pattern=76;t.speed=byte(random.next16_and(63)+16);fire();sound(3);return;
    }
    if(attack==Attack::dual_clusters) {
        if(c.frame%4){s.sprite=130;return;}
        s.sprite=134;t.group=BG_SPREAD;t.delta=9;t.count=8;t.speed=56;t.angle=byte(c.frame*2);
        if(c.frame%512>=256)t.angle=byte(-int(t.angle));
        fire();t.angle=byte(t.angle+128);fire();
        t.speed=32;t.spawn_type=5;t.delta=1;t.count=3;t.pattern=57;
        t.origin.y=wrap(random.next16_mod(512)+wrap(int(s.position.current.y)-416));
        t.origin.x=wrap(int(s.position.current.x)+s.additional[15]*16);t.angle=s.additional[14];fire();
        t.origin.x=wrap(int(s.position.current.x)-s.additional[15]*16);t.angle=byte(-int(s.additional[14]));fire();
        s.additional[15]=byte(s.additional[15]+16);if(s.additional[15]>176)s.additional[15]=16;
        s.additional[14]=byte(s.additional[14]+11);sound(3);return;
    }
    if(attack==Attack::cloud_ring) {
        s.sprite=c.frame%2 ? 134 : 130;if(c.frame%4)return;
        t.spawn_type=byte(random.next16_and(1));t.origin={wrap(random.next16_mod(1024)+wrap(int(s.position.current.x)-512)),
            wrap(random.next16_mod(512)+wrap(int(s.position.current.y)-416))};
        t.group=BG_RING;t.count=32;t.angle=byte(random.next16());t.speed=100;fire();sound(3);return;
    }
    if(attack==Attack::columns && s.phase_frame==1) {
        const auto randomized=random.next16_and(1);
        for(unsigned i=0;i<q.columns.size();++i)q.columns[i].position={wrap(i*384+(randomized ? random.next16_mod(192)+96 : 192)),0};
    }
    const auto step=phase_state(c,bullets,gathers,sink);
    switch(attack) {
    case Attack::ring:
        if(step==2){t.spawn_type=5;t.pattern=62;t.speed=70;t.group=BG_RING;t.count=90;t.angle=byte(random.next16());fire();sound(9);}
        else if(step==4)finish();break;
    case Attack::spread_pair:
        if(step==2){t.group=BG_SPREAD;t.delta=8;s.additional[15]=byte(aimed()-64);}
        else if(step==3 && c.frame%2==0) {
            t.speed=byte(random.next16_and(63)+8);t.count=byte(random.next16_and(3)+5);t.angle=s.additional[15];fire();
            t.angle=byte(128-s.additional[15]);fire();s.additional[15]=byte(s.additional[15]+7);sound(9);
        } else if(step==4)finish();break;
    case Attack::bounce:
        if(step==2){t.special_motion=134;bullets.set_special_parameter(4);}
        else if(step==3 && c.frame%2) {
            t.group=BG_SINGLE;t.spawn_type=2;t.pattern=59;t.speed=byte(random.next16_and(63)+42);
            t.origin={wrap(int(s.position.current.x)-512+random.next16_mod(1024)),wrap(int(s.position.current.y)-512+random.next16_mod(512))};
            t.angle=224;fire(true);t.speed=byte(random.next16_and(63)+42);t.angle=160;fire(true);sound(9);
            if(c.frame%16==1){t.pattern=76;t.group=BG_RING_AIMED;t.count=32;t.speed=80;fire();}
        } else if(step==4)finish();break;
    case Attack::turn_gather:
        if(step==2){bullets.set_special_parameter(1);break;}
        if(step==4){finish();break;}
        if(step!=3)break;
        if(c.frame%2) {
            t.special_motion=129;t.group=BG_SINGLE;t.spawn_type=2;t.pattern=58;t.speed=byte(random.next16_and(63)+16);
            t.origin={wrap(int(s.position.current.x)-512+random.next16_mod(1024)),wrap(int(s.position.current.y)-416+random.next16_mod(512))};
            t.speed=byte(random.next16_and(63)+16);t.angle=128;bullets.set_special_angle(192);fire(true);
            t.angle=0;bullets.set_special_angle(64);fire(true);sound(9);
        }
        if(c.frame%4==0) {
            g.ring_points=8;g.radius=1024;g.color=14;t.spawn_type=1;g.center.y=t.origin.y;
            g.center.x=wrap(random.next16_mod(5120)+512);t.group=BG_RING_AIMED;t.count=16;t.speed=64;
            gathers.add(g,t,false);
        }break;
    case Attack::cycle:
        if(step==0){t.pattern=62;t.group=BG_SPREAD_AIMED;t.special_motion=255;t.delta=16;t.angle=0;t.count=2;}
        else if(step==1 && (s.phase_frame&15)==8) {
            t.spawn_type=4;t.speed=16;for(unsigned i=0;i<4;++i){fire(true,true);t.speed=byte(t.speed+20);}
            sound(15);t.count=byte(t.count+2);t.delta=byte(t.delta-2);
        } else if(step==2){t.group=BG_STACK_AIMED;t.count=8;t.delta=10;t.speed=32;t.pattern=57;t.angle=0;}
        else if(step==3 && (s.phase_frame&3)==0){t.spawn_type=4;fire();sound(15);}
        else if(step==4)finish();break;
    case Attack::aimed_spread:
        if(step==2){t.speed=80;t.group=BG_SPREAD;t.count=1;t.delta=6;t.angle=aimed();}
        else if(step==3 && c.frame%4==0){fire();t.count=byte(t.count+1);sound(9);}
        else if(step==4)finish();break;
    case Attack::mirror_spread:
        if(step==2){t.pattern=76;t.group=BG_SPREAD;t.count=5;t.delta=11;t.angle=0;t.speed=90;}
        else if(step==3 && c.frame%2==0){t.spawn_type=2;fire();t.angle=byte(128-t.angle);fire();t.angle=byte(120-t.angle);sound(3);}
        else if(step==4)finish();break;
    case Attack::columns:
        if(step==1){t.spawn_type=2;t.group=BG_SPREAD;t.count=5;t.delta=24;t.angle=192;t.pattern=52;t.speed=127;bullet::tune(t,c.bullets.rank,c.bullets.performance);fire();sound(3);s.additional[15]=byte(aimed()-48);}
        else if(step==2) {
            laser::System lasers(q.lasers);auto& beam=lasers.scratch();beam.origin={t.origin.x,s.position.current.y};
            beam.maximum_radius=64;beam.radius_speed=6;beam.line_frames=32;beam.static_frames=48;beam.outline=8;
            lasers.add(sound);q.lasers=lasers.snapshot();
        } else if(step==3 && c.frame%4==0) {
            if(c.frame%8==0){t.spawn_type=1;t.angle=s.additional[15];t.group=BG_STACK;t.count=12;t.speed=32;t.delta=8;s.additional[15]=byte(s.additional[15]+12);fire();}
            t.speed=128;t.angle=64;t.pattern=52;t.spawn_type=2;t.origin.y=0;t.group=BG_SINGLE;
            for(const auto& column:q.columns){t.origin.x=column.position.x;fire(false,true);}sound(3);
        } else if(step==4)finish();break;
    default:break;
    }
}
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,randring::SharedRandomRing& random,const orange::Sink& sink) {
    auto& q=state_;auto& s=q.boss;auto& t=bullets.scratch();
    const auto sound=[&](unsigned id){emit(sink,orange::EventType::sound,{},id);};
    const auto small=[&](unsigned type){explosion(s.small[s.small[0].alive ? 1 : 0],s.position.current,type);sound(15);};
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;s.score_delta+=std::uint16_t(units*1280u);
        const auto x=wrap(int(s.position.current.x)-1024),y=wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<units;++i){const auto px=wrap(int(x)+random.next16_mod(2048)),py=wrap(int(y)+random.next16_mod(2048));emit(sink,orange::EventType::point,{std::int16_t(std::clamp(int(px),0,6144)),py},1280);}s.timed_out=0;
    };
    const auto next=[&](unsigned type,int threshold) {
        small(type);
        if(!s.timed_out) {
            bullets.clear();const auto x=wrap(int(s.position.current.x)-1024),y=wrap(int(s.position.current.y)-1024);
            for(unsigned i=0;i<5;++i){const auto px=wrap(int(x)+random.next16_mod(2048)),py=wrap(int(y)+random.next16_mod(2048));emit(sink,orange::EventType::item,{px,py},c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0));}
        }
        s.timed_out=1;++s.phase;s.phase_frame=0;s.mode=0;s.patterns_or_bonus=0;s.hp=s.end_hp;s.end_hp=wrap(threshold);
    };
    const auto attack=[&](Attack a){pattern(a,c,bullets,gathers,random,sink);};
    if(c.bombing)q.bomb_invincibility=32;
    if(q.bomb_invincibility)--q.bomb_invincibility;
    t.origin={wrap(int(s.position.current.x)-208),wrap(int(s.position.current.y)-768)};t.spawn_type=1;
    switch(s.phase) {
    case 0:
        hit(c,sink);s.hp=18700;if(s.phase_frame<=128)break;
        s.end_hp=14700;++s.phase;s.phase_frame=0;sound(13);s.tile_column=15;s.background=orange::Background::npc;break;
    case 1:
        hit(c,sink);if(s.phase_frame<64)break;
        ++s.phase;s.mode=0;s.patterns_or_bonus=0;s.phase_frame=0;s.position.velocity.x=0;break;
    case 2:case 3:case 4:case 5: {
        const auto phase=s.phase;
        if(s.mode==0)attack(phase==2 ? Attack::ring : phase==3 ? Attack::bounce : phase==4 ? Attack::cycle : Attack::mirror_spread);
        else if(s.mode==1)attack(phase==2 ? Attack::spread_pair : phase==3 ? Attack::turn_gather : phase==4 ? Attack::aimed_spread : Attack::columns);
        else if(s.mode==255) {
            if(s.phase_frame==1)q.wave_target=s.patterns_or_bonus&1 ? std::int16_t(std::clamp(int(c.bullets.player.x),512,5632)) : wrap(random.next16_mod(4096)+1024);
            if(wave_step()) {
                // Phase2 increments before choosing its next attack; phases3..5
                // select with the old count. This difference is target-visible.
                if(phase==2)++s.patterns_or_bonus;
                s.mode=s.patterns_or_bonus&1;
                if(phase!=2)++s.patterns_or_bonus;
                s.phase_frame=0;
            }
        }
        if(s.patterns_or_bonus>=18 && s.mode!=255)attack(Attack::blue_ring);
        if(s.patterns_or_bonus<22){if(!hit(c,sink))break;bonus(100);}
        next(phase==2 ? 0 : 3,phase==2 ? 12700 : phase==3 ? 8900 : phase==4 ? 5500 : 3000);
        s.mode=255;q.wave_target=3072;break;
    }
    case 6:hit(c,sink);if(wave_bounce()){++s.phase;s.phase_frame=32;}break;
    case 7:
        attack(Attack::random_ring);if(s.phase_frame<1500){if(!hit(c,sink))break;bonus(100);}
        next(4,0);s.mode=255;q.wave_target=3072;s.additional[15]=16;break;
    case 8:
        attack(s.phase_frame<=3000 ? Attack::dual_clusters : Attack::cloud_ring);
        if(!hit(c,sink) && s.phase_frame<5000)break;
        small(1);++s.phase;s.patterns_or_bonus=s.phase_frame<5000 ? 1 : 0;s.phase_frame=0;s.mode=0;s.palette_tone=100;s.palette_changed=1;break;
    case 9:
        s.phase_frame=wrap(int(s.phase_frame)+1);if(s.phase_frame==16)small(4);
        if(s.phase_frame==32){explosion(s.big,s.position.current,3);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);if(s.patterns_or_bonus)bonus(200);s.sprite=4;s.phase_frame=0;sound(12);s.palette_changed=1;s.invincibility=255;}
        break;
    case 254:orange::update_defeat(s,c,sink);return;
    default:throw std::logic_error("Gengetsu requires Extra post-dialog owner");
    }
    if(!q.wave_amplitude)s.homing=s.position.current;
    laser::System lasers(q.lasers);lasers.update(c.bullets.player,sound);q.lasers=lasers.snapshot();
    emit(sink,orange::EventType::hp,{},std::uint16_t(s.hp),18700);
}
}
