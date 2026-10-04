#include "yuuka6.hpp"
#include "yuuka6_entities.hpp"
#include "thick_lasers.hpp"
#include <algorithm>

namespace th04::portable::yuuka6 {
namespace {
using motion::wrap;
void emit(const orange::Sink& sink,orange::EventType kind,motion::Point p={},unsigned value=0,unsigned count=0) {
    if(sink) sink({kind,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count)});
}
void explosion(orange::Explosion& e,motion::Point center,unsigned type) {
    e.alive=1;e.age=0;e.center=center;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if(type==1) e.angle_offset=32;
    else if(type==2) e.angle_offset=224;
    else if(type==3) e.delta={208,112};
    else if(type==4) e.delta={112,208};
}
void small(orange::Snapshot& s,unsigned type,const orange::Sink& sink) {
    explosion(s.small[s.small[0].alive ? 1 : 0],s.position.current,type);
    emit(sink,orange::EventType::sound,{},15);
}
}
bool System::mirror_hittest(const Context& c,const orange::Sink& sink) {
    if(state_.mirror_state!=2) return false;
    state_.shot_center=state_.mirror;state_.shot_radius={384,768};
    emit(sink,orange::EventType::hit,state_.shot_center,384,768);
    state_.mirror_damage=static_cast<std::uint8_t>(c.ordinary_hit ? c.ordinary_hit(state_.shot_center,state_.shot_radius) : 0);
    if(state_.mirror_damage) emit(sink,orange::EventType::sound,{},4);
    state_.boss.hp=wrap(int(state_.boss.hp)-state_.mirror_damage);
    return state_.boss.hp<0; // This helper's return differs from phase-end HP.
}
void System::phase_next(unsigned type,std::int16_t end_hp,bullet::System& bullets,const orange::Sink& sink) {
    auto& s=state_.boss;
    if(bullets.snapshot().clear_time<20) bullets.clear();
    small(s,type,sink);++s.phase;s.phase_frame=0;s.patterns_or_bonus=0;s.mode=0;
    s.hp=s.end_hp;s.end_hp=end_hp;state_.animation_frame=0;s.sprite=128;state_.sprite_flag=1;
}
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,spark::System& sparks,
                    laser::System& lasers,Entities& entities,randring::SharedRandomRing& random,const orange::Sink& sink) {
    auto& s=state_.boss;
    const auto increment=[&] { s.phase_frame=wrap(int(s.phase_frame)+1); };
    const auto sound=[&](unsigned id) { emit(sink,orange::EventType::sound,{},id); };
    const auto hit=[&](unsigned se) {
        state_.shot_center=s.position.current;state_.shot_radius=s.hitbox_radius;
        emit(sink,orange::EventType::hit,state_.shot_center,static_cast<std::uint16_t>(state_.shot_radius.x),static_cast<std::uint16_t>(state_.shot_radius.y));
        const auto damage=c.hit ? c.hit(state_.shot_center,state_.shot_radius) : std::uint16_t{0};
        // AB48 sounds for the whole shot WORD; AB BE truncates afterward.
        // A shot result256 sounds but subtracts zero HP from the main body.
        if(damage) sound(se);
        return static_cast<std::uint8_t>(damage);
    };
    const auto invulnerable=[&] { increment();hit(10); };
    const auto hit_phase=[&] { increment();s.damage=hit(4);s.hp=wrap(int(s.hp)-s.damage);return s.hp<=s.end_hp; };
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;s.score_delta+=static_cast<std::uint16_t>(units*1280u);
        const auto left=wrap(int(s.position.current.x)-1024),top=wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<units;++i) {
            const auto x=wrap(int(left)+random.next16_mod(2048)),y=wrap(int(top)+random.next16_mod(2048));
            emit(sink,orange::EventType::point,{static_cast<std::int16_t>(std::clamp(int(x),0,6144)),y},1280);
        }
        s.timed_out=0;
    };
    const auto items=[&] {
        const auto left=wrap(int(s.position.current.x)-1024),top=wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<5;++i) {
            const auto x=wrap(int(left)+random.next16_mod(2048)),y=wrap(int(top)+random.next16_mod(2048));
            emit(sink,orange::EventType::item,{x,y},c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0));
        }
    };
    const auto attack=[&](Attack a) { this->attack(a,c,bullets,gathers,lasers,entities,random,sink); };
    const auto next=[&](unsigned type,int end) { phase_next(type,wrap(end),bullets,sink); };
    // There is no common clock increment. Hit wrappers, hidden/moving arms,
    // and explicit transition arms each own exactly their target increment.
    // In particular, an attack completion can reset the clock before hit.
    switch(s.phase) {
    case 0:
        if(s.phase_frame==0) {
            state_.stage_vm_disabled=true;state_.midboss_frames_until=0;
            state_.aux_flag=0;state_.mirror_state=0;
        }
        invulnerable();if(s.phase_frame<=128) break;
        ++s.phase;s.phase_frame=0;sound(13);state_.pattern_previous=0;
        s.background=orange::Background::yuuka;s.tile_column=15;break;
    case 1:
        invulnerable();if(s.phase_frame<64) break;
        ++s.phase;s.position.velocity.x=0;s.patterns_or_bonus=0;s.mode=0;
        s.hp=13300;s.end_hp=10600;s.phase_frame=0;state_.animation_frame=0;
        state_.sprite_flag=1;state_.fly_path=static_cast<std::uint8_t>(random.next16_and(1));break;
    case 2: {
        bool timeout=false;
        if(s.mode<=2) attack(static_cast<Attack>(s.mode));
        else if(s.mode==255 && phase2_fly()) { s.mode=s.patterns_or_bonus%3;timeout=s.patterns_or_bonus>=10; }
        if(!timeout) {
            if(s.sprite==0) { increment();break; }
            if(!hit_phase()) break;
            bonus(20);items();
        }
        next(0,7600);break;
    }
    case 3:
        increment();if(move_towards({3072,1280})) { ++s.phase;s.phase_frame=0;s.patterns_or_bonus=0; }break;
    case 4: {
        bool timeout=false;
        if(s.mode==0) attack(Attack::safety_circle);
        else if(s.mode==255 && move_towards({wrap(random.next16_mod(4608)+768),1280})) {
            s.mode=0;timeout=s.patterns_or_bonus>=10;
        }
        if(!timeout) {
            if(s.sprite==0 || s.mode==255) { increment();break; }
            if(!hit_phase()) break;
            bonus(20);items();
        }
        next(0,5400);state_.aux_flag=1;break;
    }
    case 5:case 9:
        increment();if(state_.sprite_flag!=0) animate(Animation::vanish);
        else { ++s.phase;s.phase_frame=0; }break;
    case 6:case 10:
        attack(Attack::bullets);increment();horizontal_wave();
        if(s.phase_frame<320 || s.position.current.y!=1280) break;
        small(s,2,sink);if(bullets.snapshot().clear_time<20) bullets.clear();
        ++s.phase;s.phase_frame=0;state_.animation_frame=0;break;
    case 7:case 11:
        hit_phase();if(!move_to_center()) break;
        ++s.phase;s.patterns_or_bonus=0;s.mode=255;s.phase_frame=0;
        state_.animation_frame=0;state_.sprite_flag=2;state_.mirror_state=1;state_.pattern_previous=255;break;
    case 8:case 12: {
        bool timeout=false;
        if(s.mode==0) attack(Attack::dual_lasers);
        else if(s.mode==1) attack(Attack::dual_spreads);
        else if(s.mode==2) attack(Attack::dual_aimed_spreads);
        else if(s.mode==255 && move_towards({wrap(random.next16_mod(2304)+768),1280})) {
            // Rejected repeats consume the same shared RNG as the movement
            // destination, which is sampled even when teleport is not due.
            do { s.mode=static_cast<std::uint8_t>(random.next16_mod(3)); } while(s.mode==state_.pattern_previous);
            state_.pattern_previous=s.mode;timeout=s.patterns_or_bonus>=10;
        }
        if(!timeout) {
            if(s.sprite==0) { increment();break; }
            if(s.mode<=2) { hit_phase();mirror_hittest(c,sink); }
            else increment();
            if(s.hp>s.end_hp) break;
            bonus(20);items();
        }
        next(0,s.phase==8 ? 3400 : 1200);
        if(s.phase==9) state_.aux_flag=1;
        state_.mirror_state=0;break;
    }
    case 13:
        invulnerable();if(!move_to_center()) break;
        ++s.phase;s.patterns_or_bonus=0;s.mode=0;s.phase_frame=0;
        state_.animation_frame=0;state_.sprite_flag=2;state_.mirror_state=1;break;
    case 14: {
        bool timeout=false;
        if(s.mode==0) attack(Attack::rotating_ring);
        else if(s.mode==1) attack(Attack::growing_ring);
        else if(s.mode==2) attack(Attack::chase_crosses);
        else if(s.mode==255) { ++s.patterns_or_bonus;s.mode=s.patterns_or_bonus%3;timeout=s.patterns_or_bonus>=18; }
        if(!timeout) { if(!hit_phase()) break;bonus(20);items(); }
        next(3,0);s.sprite=146;break;
    }
    case 15:
        hit_phase();if(s.phase_frame<128) break;
        ++s.phase;bullets.scratch().spawn_type=1;bullets.scratch().angle=0;break;
    case 16:
        attack(Attack::alternating_rings);if(!hit_phase() && s.phase_frame<2500) break;
        small(s,1,sink);++s.phase;s.patterns_or_bonus=s.phase_frame<2500 ? 1 : 0;
        s.phase_frame=0;s.mode=0;s.palette_tone=100;s.palette_changed=1;break;
    case 17:
        increment();if(s.phase_frame==16) small(s,4,sink);
        if(s.phase_frame==32) {
            explosion(s.big,s.position.current,2);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);
            if(s.patterns_or_bonus) bonus(70);
            s.sprite=4;s.phase_frame=0;sound(12);s.palette_changed=1;s.invincibility=255;
        }
        break;
    default:
        orange::update_defeat(s,c,sink);return; // No laser/custom/HUD tail.
    }
    s.homing=s.position.current;lasers.update(c.bullets.player,sound);
    // Mirror, laser, bullet and cross contacts share one raw BYTE. Score and
    // shot scratch likewise belong to the process; bridge their retained
    // values around the entity tail rather than accumulating them twice.
    auto shared=entities.snapshot();shared.player_hit=lasers.snapshot().player_hit;
    shared.score_delta=s.score_delta;shared.hit_center=state_.shot_center;shared.hit_radius=state_.shot_radius;
    entities=Entities(shared);
    EntityContext ec;ec.frame=c.frame;ec.boss_origin=s.position.current;ec.bullets=c.bullets;ec.hit=c.ordinary_hit;
    entities.update(ec,bullets,sparks,random,sink);
    const auto& after=entities.snapshot();s.score_delta=after.score_delta;
    state_.shot_center=after.hit_center;state_.shot_radius=after.hit_radius;
    lasers.set_player_hit(after.player_hit);
    emit(sink,orange::EventType::hp,{},static_cast<std::uint16_t>(s.hp),13300);
}
} // namespace th04::portable::yuuka6
