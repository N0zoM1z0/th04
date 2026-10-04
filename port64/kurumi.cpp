#include "kurumi.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::kurumi {
namespace {
std::uint8_t byte(int n) { return static_cast<std::uint8_t>(n); }
bool inside(motion::Point p) { return p.x>0 && p.x<6144 && p.y>0 && p.y<5888; }
void explode(orange::Explosion& e,motion::Point center,unsigned type) {
    e.alive=1;e.age=0;e.center=center;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if(type==1) e.angle_offset=32;
    else if(type==2) e.angle_offset=224;
    else if(type==3) e.delta={208,112};
    else if(type==4) e.delta={112,208};
    // Unused byte and the unselected small-explosion slot survive allocation.
}
}
Snapshot prepare_stage2(orange::Snapshot previous,unsigned rank) {
    if(rank>3) throw std::invalid_argument("Kurumi belongs to the ordinary four-rank route");
    Snapshot next;next.boss=previous;auto& s=next.boss;
    s.phase=0;s.mode=0;s.patterns_or_bonus=0;s.phase_frame=0;s.damage=0;
    s.position.velocity={};s.small[0].alive=s.small[1].alive=0;s.timed_out=1;
    s.position.current=s.position.previous={3072,1296};
    s.sprite=0;s.hitbox_radius={384,384};
    // Actual rank_select stack order: Easy255, Normal128, Hard32, Lunatic8.
    // Extra never loads this ordinary Stage2 boss and is not a fifth entry.
    constexpr std::uint8_t periods[]{255,128,32,8};s.additional[0]=periods[rank];
    // HP, angle, end HP, other additional bytes and explosion metadata
    // survive boss_reset. The separate stage actor clear owns ray records.
    return next;
}
System::System(unsigned rank):state_(prepare_stage2({},rank)) {}
void System::apply_departure(const transition::Departure& d) {
    auto& s=state_.boss;s.phase_frame=d.frame;s.homing=d.homing;
    s.palette_tone=d.palette_tone;s.palette_changed=d.palette_changed;
}
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,
                    spark::System& sparks,randring::SharedRandomRing& random,const Sink& sink) {
    auto& s=state_.boss;auto& t=bullets.scratch();auto& g=gathers.scratch();
    const auto center=[&] { return s.position.current; };
    const auto emit=[&](EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
        if(sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
    };
    const auto sound=[&](unsigned id) { emit(EventType::sound,{},id); };
    const auto increment=[&] { s.phase_frame=motion::wrap(int(s.phase_frame)+1); };
    const auto hit=[&](unsigned se) {
        emit(EventType::hit,center(),static_cast<std::uint16_t>(s.hitbox_radius.x),static_cast<std::uint16_t>(s.hitbox_radius.y));
        const auto damage=c.hit ? c.hit(center(),s.hitbox_radius) : std::uint16_t{0};
        if(damage) sound(se);
        return damage;
    };
    const auto invulnerable=[&] { increment();hit(10); };
    const auto hit_phase=[&] {
        increment();s.damage=byte(hit(4));s.hp=motion::wrap(int(s.hp)-s.damage);return s.hp<=s.end_hp;
    };
    const auto tune=[&] { bullet::tune(t,c.bullets.rank,c.bullets.performance); };
    const auto fire=[&](bool special=false,bool fixed=false) {
        bullets.add(t,c.bullets,random,special,fixed,[&](const bullet::Event& e) {
            if(e.type==bullet::EventType::gather) gathers.request(e);
        });
    };
    const auto circle=[&](motion::Point p,bool growing=false) {
        // Count1 denotes the actual growing request; zero denotes shrinking.
        emit(EventType::circle,p,0,growing ? 1 : 0);
    };
    const auto small=[&](unsigned type) { explode(s.small[s.small[0].alive ? 1 : 0],center(),type);sound(15); };
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;s.score_delta+=static_cast<std::uint16_t>(units*1280);
        const auto left=motion::wrap(int(center().x)-1024),top=motion::wrap(int(center().y)-1024);
        for(unsigned i=0;i<units;++i) {
            const int x=motion::wrap(int(left)+random.next16_mod(2048));
            const auto y=motion::wrap(int(top)+random.next16_mod(2048));
            emit(EventType::point,{static_cast<std::int16_t>(std::clamp(x,0,6144)),y},1280);
        }
        s.timed_out=0;
    };
    const auto next=[&](int explosion_type,std::int16_t end_hp) {
        if(explosion_type>=0) {
            small(static_cast<unsigned>(explosion_type));
            if(!s.timed_out) {
                bullets.clear();
                const auto left=motion::wrap(int(center().x)-1024),top=motion::wrap(int(center().y)-1024);
                for(unsigned i=0;i<5;++i) {
                    const auto x=motion::wrap(int(left)+random.next16_mod(2048));
                    const auto y=motion::wrap(int(top)+random.next16_mod(2048));
                    const unsigned type=c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0);
                    emit(EventType::item,{x,y},type);
                }
            }
        }
        s.timed_out=1;++s.phase;s.phase_frame=0;s.mode=0;s.patterns_or_bonus=0;s.hp=s.end_hp;s.end_hp=end_hp;
    };
    const auto orbit=[&](bool reverse=false) {
        s.position.current={motion::wrap(3072+motion::polar(s.angle,1024).x),
                            motion::wrap(1456+motion::polar(s.angle,320).y)};
        s.angle=byte(s.angle+(reverse ? -1 : 1));
        // Direct orbit writes do not update previous position or velocity.
    };
    const auto seek_center=[&] {
        if(center().x<3056) s.position.velocity.x=24;
        else if(center().x>3088) s.position.velocity.x=-24;
        if(center().y<1264) s.position.velocity.y=12;
        else if(center().y>1296) s.position.velocity.y=-12;
        s.position.update(); // Retain velocity inside the dead band.
    };
    const auto add_ray=[&](int offset,unsigned angle) {
        for(auto& ray:state_.rays) if(ray.flag==0) {
            ray.flag=1;ray.target=ray.origin={motion::wrap(int(center().x)+offset),motion::wrap(int(center().y)-160)};
            ray.velocity=motion::polar(byte(angle),256);sound(5);break;
        }
    };
    const auto update_rays=[&] {
        unsigned free=0;
        for(auto& ray:state_.rays) {
            if(ray.flag==0) ++free;
            if(ray.flag==1) {
                if(inside(ray.target)) {
                    ray.target={motion::wrap(int(ray.target.x)+ray.velocity.x),motion::wrap(int(ray.target.y)+ray.velocity.y)};
                } else {
                    t.origin={motion::wrap(int(ray.target.x)-ray.velocity.x),motion::wrap(int(ray.target.y)-ray.velocity.y)};
                    t.special_motion=130;bullets.set_special_parameter(1);t.speed=32;
                    // The target writes SPEEDUP, but calls regular fixed-speed
                    // add. Preserve that producer, including its retained group.
                    for(unsigned i=0;i<3;++i) { fire(false,true);t.speed=byte(t.speed+6); }
                    ++ray.flag;sound(6);s.circle_color=9;circle(t.origin,true);
                }
            } else if(ray.flag==2) {
                if(inside(ray.origin)) {
                    ray.origin={motion::wrap(int(ray.origin.x)+ray.velocity.x),motion::wrap(int(ray.origin.y)+ray.velocity.y)};
                } else ray.flag=0;
            }
        }
        // Count at entry, so a ray freed above delays all-free by one call.
        return free==state_.rays.size();
    };
    const auto rays_pattern=[&](unsigned side,bool late) {
        const bool left=side==1,dual=side==3;
        if(s.phase_frame==16) { s.sprite=byte(dual ? 10 : left ? 8 : 9);return; }
        if(s.phase_frame==48) {
            // Early dual sends right then left; late dual reverses the order.
            const auto at=[&](int dx) { return motion::Point{motion::wrap(int(center().x)+dx),motion::wrap(int(center().y)-160)}; };
            if(dual) { circle(at(late ? -192 : 192));circle(at(late ? 192 : -192)); }
            else circle(at(left ? -192 : 192));
            s.circle_color=15;sound(8);return;
        }
        if(s.phase_frame==64) {
            s.sprite=0;
            if(late) { if(left || dual) add_ray(-192,24);if(!left || dual) add_ray(192,104); }
            else if(dual) {
                const unsigned angle=random.next16_and(15)+104;add_ray(192,angle);add_ray(-192,128-angle);
            } else if(left) add_ray(-192,24-random.next16_and(15));
            else add_ray(192,random.next16_and(15)+104);
            return;
        }
        if(s.phase_frame<=64) return;
        if(late && (s.phase_frame==80 || s.phase_frame==96)) {
            const unsigned angle=s.phase_frame==80 ? 16 : 8;
            if(left || dual) add_ray(-192,angle);
            if(!left || dual) add_ray(192,128-angle);
        }
        t.spawn_type=2;t.pattern=55;t.angle=0;t.group=44;
        t.count=byte(late ? (dual ? 6 : 12) : (dual ? 8 : 16));tune();
        if(update_rays()) { s.phase_frame=0;s.mode=0; }
    };
    const auto turning=[&] {
        orbit(true);s.sprite=s.angle>128 ? 4 : 6;
        if(c.frame%57) return;
        t.spawn_type=2;t.pattern=55;t.origin=center();t.group=44;t.count=16;t.special_motion=129;t.speed=48;
        t.angle=byte(random.next16());bullets.set_special_parameter(1);
        bullets.set_special_angle(state_.turn_toggle&1 ? 64 : 192);
        tune();fire(true);bullets.set_special_angle(byte(bullets.snapshot().special_angle+128));
        t.speed=32;t.angle=byte(random.next16());fire(true);++state_.turn_toggle;
    };
    const auto stacks=[&] {
        if(s.phase_frame<16) return;
        const auto reset_angles=[&] {
            s.additional[15]=byte(-32-random.next16_and(15));s.additional[14]=byte(random.next16_and(15)+160);s.additional[13]=0;
        };
        if(s.phase_frame==16) { reset_angles();t.pattern=76; }
        if(s.phase_frame%8==0) {
            t.speed=16;s.additional[15]=byte(s.additional[15]+16);s.additional[14]=byte(s.additional[14]-16);
            if(++s.additional[13]>10) reset_angles();
            sound(15);
        }
        t.spawn_type=4;t.group=0;t.origin={motion::wrap(int(center().x)+192),motion::wrap(int(center().y)-160)};
        t.angle=s.additional[15];fire(false,true);
        t.origin.x=motion::wrap(int(t.origin.x)-384);t.angle=s.additional[14];fire(false,true);t.speed=byte(t.speed+10);
        if(!s.additional[0]) throw std::domain_error("Kurumi stack period would divide by zero in the original");
        if(s.phase_frame%s.additional[0]) return;
        t.group=46;t.count=5;t.delta=9;t.angle=0;t.spawn_type=1;t.speed=byte(random.next16_and(15)+32);t.special_motion=255;
        tune();fire(true);
    };
    switch(s.phase) {
    case 0:
        // Kurumi tests the old clock before invulnerable hit increments it.
        if(s.phase_frame==0) {
            s.hp=s.end_hp=4800;s.palette_zero={96,0,0};s.palette_changed=1;
            for(auto& ray:state_.rays) ray.flag=0;
            g.center=center();g.ring_points=32;g.radius=5120;g.angle_delta=253;g.color=15;
        } else if(s.phase_frame>=288) {
            if(s.phase_frame==296) g.color=9;
            if((s.phase_frame&7)==0) gathers.add(g,t,true);
            if(s.phase_frame>=320) {
                ++s.phase;s.phase_frame=0;sound(13);state_.unknown_state=0;
                s.background=orange::Background::orange;s.tile_column=0;
            }
        } else if(s.phase_frame==128) sound(8);
        invulnerable();break;
    case 1:
        invulnerable();
        if(s.phase_frame>=32) { next(-1,3300);s.mode=3;s.angle=192;sound(6); }
        break;
    case 2:
    case 4: {
        bool timeout=false;const bool late=s.phase==4;
        if(s.mode==0) {
            orbit();
            if(s.phase_frame>=96) {
                s.phase_frame=0;s.mode=byte((late ? random.next16_mod(3) : random.next16_and(3))+1);
                ++s.patterns_or_bonus;timeout=s.patterns_or_bonus>10;
                if(!timeout) {
                    t.spawn_type=1;t.origin=center();t.pattern=55;t.group=38;t.count=22;t.angle=byte(random.next16());tune();t.speed=16;
                    const unsigned count=std::min(unsigned(s.patterns_or_bonus),5u);
                    for(unsigned i=0;i<count;++i) { fire(false,true);t.speed=byte(t.speed+8);t.angle=byte(t.angle+(late ? 3 : -3)); }
                }
            }
        } else if(s.mode<=3 || (!late && s.mode==4)) rays_pattern(s.mode>=3 ? 3 : s.mode,late);
        if(!timeout) { if(!hit_phase()) break;bonus(10); }
        next(late ? 3 : 1,late ? 0 : 2050);
        if(!late) bullets.set_special_angle(64);
        break;
    }
    case 3:
        update_rays();
        if(s.mode==0) { if(s.phase_frame>=128) { s.phase_frame=0;s.mode=1; } }
        else if(s.mode==1) turning();
        if(s.phase_frame<=2000) { if(!hit_phase()) break;bonus(10); }
        next(2,550);break;
    case 5:
        update_rays();
        if(s.mode==0) {
            if(s.phase_frame==144) { circle(center());s.circle_color=15; }
            if(s.phase_frame>64) { s.phase_frame=0;s.mode=1;s.sprite=12;s.angle=128; }
            seek_center();
        } else if(s.mode==1) stacks();
        if(!hit_phase() && s.phase_frame<700) break;
        ++s.phase;sparks.add_circle(center(),128,48);small(4);
        s.patterns_or_bonus=s.phase_frame<600 ? 1 : 0;s.phase_frame=0;break;
    case 6:
        update_rays();seek_center();increment();
        if(s.phase_frame==16) small(4);
        if(s.phase_frame==32) {
            explode(s.big,center(),0);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);
            if(s.patterns_or_bonus) bonus(20);
            s.sprite=4;s.phase_frame=0;sound(12);s.palette_zero[0]=0;s.palette_changed=1;s.invincibility=255;
        }
        break;
    default:
        orange::update_defeat(s,c,sink);return;
    }
    s.homing=center();emit(EventType::hp,{},static_cast<std::uint16_t>(s.hp),4800);
}
} // namespace th04::portable::kurumi
