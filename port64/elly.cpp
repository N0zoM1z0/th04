#include "elly.hpp"
#include <algorithm>
namespace th04::portable::elly {
namespace {
std::uint8_t byte(int n) { return static_cast<std::uint8_t>(n); }
void explosion(orange::Explosion& e,motion::Point center,unsigned type) {
    e.alive=1;e.age=0;e.center=center;e.radius={8,8};e.delta={176,176};e.angle_offset=0;
    if(type==1) e.angle_offset=32;
    else if(type==2) e.angle_offset=224;
    else if(type==3) e.delta={208,112};
    else if(type==4) e.delta={112,208};
}
int pixels(motion::Subpixel v) { return v>=0 ? v/16 : -((-int(v)+15)/16); }
}
Snapshot prepare_stage3(orange::Snapshot previous) {
    Snapshot next;next.boss=previous;auto& s=next.boss;
    s.phase=0;s.mode=0;s.patterns_or_bonus=0;s.phase_frame=0;s.damage=0;
    s.position.velocity={};s.small[0].alive=s.small[1].alive=0;s.timed_out=1;
    s.position.current=s.position.previous={3072,1024};s.sprite=134;s.hitbox_radius={384,384};
    // HP/endHP/angle/additional/explosion metadata retain boss_reset ownership.
    // Private fields start from fresh MAIN BSS for the first Stage3 load;
    // stage3_setup itself does not write the scythe or orbit globals.
    return next;
}
void System::initialize_scythe(motion::Point player) {
    auto& q=state_.scythe;q.speed=8;q.angle=motion::angle_to(state_.boss.position.current,player);
    q.mode=1;q.frame=0;q.flag=0;q.turn=0;
}
void System::update_orbit() {
    auto& s=state_.boss;auto& f=state_.orbit_frame;
    if(f<128) { s.position.previous.x=motion::wrap(int(s.position.previous.x)+8);s.angle=96; }
    else if(f<256) --s.angle;
    else if(f<384) s.position.previous.x=motion::wrap(int(s.position.previous.x)-8);
    else if(f<512) { s.position.previous.x=motion::wrap(int(s.position.previous.x)+8);s.angle=32; }
    else if(f<640) ++s.angle;
    else if(f<768) s.position.previous.x=motion::wrap(int(s.position.previous.x)-8);
    else { s.position.previous.x=motion::wrap(int(s.position.previous.x)+8);s.angle=96;f=0; }
    // prev.x is the orbit radius, not a previous position. Direct polar writes
    // leave the other previous/velocity fields alone, as the target does.
    const auto delta=motion::polar(s.angle,s.position.previous.x);
    s.position.current={motion::wrap(3072+int(delta.x)),motion::wrap(1536+int(delta.y))};
}
void System::update_scythe(const Context& c,const Sink& sink) {
    auto& q=state_.scythe;auto& s=state_.boss;
    const auto sound=[&](unsigned id) { if(sink) sink({orange::EventType::sound,{},static_cast<std::uint16_t>(id),0}); };
    if(q.flag==2) q.flag=0;
    switch(q.mode) {
    case 1:
        if(q.frame<64 && (q.frame&7)==0) s.sprite=byte((q.frame>>3)+134);
        if(q.frame==0) { sound(8);++q.frame;break; }
        if(q.frame==56) { sound(9);q.flag=1;q.position.current=s.position.current;++q.frame;break; }
        if(q.frame<64) { ++q.frame;break; }
        s.sprite=141;q.mode=2;
        [[fallthrough]];
    case 2:
        if(q.frame<80) {
            const auto delta=byte(motion::angle_to(q.position.current,c.bullets.player)-q.angle);
            if(delta>=16 && delta<128) { q.turn=1;q.speed=byte(q.speed+(c.frame&1)); }
            else if(delta>=128 && delta<=240) { q.turn=-1;q.speed=byte(q.speed+(c.frame&1)); }
            else { ++q.speed;q.turn=0; }
            q.angle=byte(q.angle+q.turn);
        } else q.speed=byte(q.speed+(c.frame&1));
        if(q.position.current.x<=1024) q.mode=3;
        else if(q.position.current.x>=5120) q.mode=4;
        else if(q.position.current.y>=4864) q.mode=5;
        else if(q.position.current.y<=512) q.mode=6;
        ++q.frame;break;
    case 3:case 4:case 5:case 6:
        q.speed=byte(q.speed-4);q.angle=byte(q.angle+q.turn);
        if(q.mode==4) q.angle=byte(q.angle+(q.turn ? q.turn : 1));
        if(q.speed<=4) q.mode=7;
        break; // These modes do not advance the animation clock.
    case 7:
        q.angle=motion::angle_to(q.position.current,s.position.current);q.speed=byte(q.speed+8);
        if(motion::wrap(int(s.position.current.x)-256)<q.position.current.x &&
           motion::wrap(int(s.position.current.x)+256)>q.position.current.x &&
           motion::wrap(int(s.position.current.y)-256)<q.position.current.y &&
           motion::wrap(int(s.position.current.y)+256)>q.position.current.y) {
            q.mode=8;q.flag=2;q.frame=0;
        }
        break;
    case 8:
        if(q.frame<32 && (q.frame&7)==0) s.sprite=byte(((31-q.frame)>>2)+134);
        if(q.frame>=32) { s.sprite=134;q.mode=0; }
        ++q.frame;break;
    }
    if(q.flag!=1) return;
    q.position.velocity=motion::polar(q.angle,q.speed);
    if(sink) sink({orange::EventType::hit,q.position.current,512,512});
    const auto& shot_hit=c.scythe_hit ? c.scythe_hit : c.hit;
    const auto damage=shot_hit ? shot_hit(q.position.current,{512,512}) : std::uint16_t{0};
    // Shots deflect only vertical velocity; this collision is not against-boss.
    q.position.velocity.y=motion::wrap(int(q.position.velocity.y)-(damage>>1));q.position.update();
    if(motion::wrap(int(q.position.current.x)-384)<c.bullets.player.x &&
       motion::wrap(int(q.position.current.x)+384)>c.bullets.player.x &&
       motion::wrap(int(q.position.current.y)-384)<c.bullets.player.y &&
       motion::wrap(int(q.position.current.y)+384)>c.bullets.player.y) state_.player_hit=1;
}
void System::apply_departure(const transition::Departure& d) {
    auto& s=state_.boss;s.phase_frame=d.frame;s.homing=d.homing;
    s.palette_tone=d.palette_tone;s.palette_changed=d.palette_changed;
}
void System::update(const Context& c,bullet::System& bullets,gather::System& gathers,
                    spark::System& sparks,randring::SharedRandomRing& random,const Sink& sink) {
    auto& s=state_.boss;auto& q=state_.scythe;auto& t=bullets.scratch();auto& g=gathers.scratch();
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
    const auto fire=[&](bool fixed=false) { bullets.add(t,c.bullets,random,false,fixed); };
    const auto circle=[&] { emit(orange::EventType::circle,s.position.current); };
    const auto small=[&](unsigned type) { explosion(s.small[s.small[0].alive ? 1 : 0],s.position.current,type);sound(15); };
    const auto bonus=[&](unsigned units) {
        s.point_times_two=0;s.score_delta+=static_cast<std::uint16_t>(units*1280u);
        const auto left=motion::wrap(int(s.position.current.x)-1024),top=motion::wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<units;++i) {
            const auto x=motion::wrap(int(left)+random.next16_mod(2048));
            const auto y=motion::wrap(int(top)+random.next16_mod(2048));
            emit(orange::EventType::point,{static_cast<std::int16_t>(std::clamp(int(x),0,6144)),y},1280);
        }
        s.timed_out=0;
    };
    const auto drop=[&] {
        const auto left=motion::wrap(int(s.position.current.x)-1024),top=motion::wrap(int(s.position.current.y)-1024);
        for(unsigned i=0;i<5;++i) {
            const auto x=motion::wrap(int(left)+random.next16_mod(2048)),y=motion::wrap(int(top)+random.next16_mod(2048));
            const unsigned type=c.power>=128 ? 1 : (c.power<=123 && i==2 ? 3 : 0);
            emit(orange::EventType::item,{x,y},type);
        }
    };
    const auto orbit=[&](unsigned times=1) {
        for(unsigned i=0;i<times;++i) { update_orbit();state_.orbit_frame=motion::wrap(int(state_.orbit_frame)+1); }
    };
    const auto gather=[&]() {
        if(s.phase_frame>32) return 0;
        if(s.phase_frame==1) { g.center=s.position.current;g.ring_points=8;g.radius=3072;g.color=15; }
        else if(s.phase_frame==8) g.color=7;
        else if(s.phase_frame==16) { circle();s.circle_color=15;g.color=7; }
        else if(s.phase_frame==32) return 2;
        else return 1;
        g.angle_delta=254;gathers.add(g,t,true);g.angle_delta=2;gathers.add(g,t,true);return 1;
    };
    const auto burst=[&] { s.mode=255;s.phase_frame=0;t.angle=0;t.spawn_type=5;t.pattern=57;t.speed=32;t.group=BG_RING_AIMED;t.count=48;tune();fire(true); };
    const auto end_scythe=[&] { if(q.mode==0) { s.mode=255;s.phase_frame=0; } };
    // The scythe runs before the phase dispatcher, including the first frame
    // and defeat/departure. Phase0 clears it only after this update.
    update_scythe(c,sink);
    switch(s.phase) {
    case 0:
        q.flag=q.mode=0;++s.phase;s.mode=0;s.palette_zero[2]=128;s.palette_changed=1;s.hp=s.end_hp=6000;break;
    case 1:
        s.position.update();
        if(s.mode==0) { if(s.phase_frame==32) initialize_scythe(c.bullets.player);if(s.phase_frame>32) end_scythe(); }
        else if(s.mode==255) {
            if(s.phase_frame<=64) {
                if(s.patterns_or_bonus==0 || s.patterns_or_bonus==3) s.position.velocity.x=-16;
                else if(s.patterns_or_bonus==1 || s.patterns_or_bonus==2) s.position.velocity.x=16;
            } else { s.patterns_or_bonus=s.patterns_or_bonus<3 ? byte(s.patterns_or_bonus+1) : 0;s.mode=0;s.phase_frame=0;s.position.velocity.x=0; }
        }
        increment();invulnerable(); // Observed double increment in entrance.
        if(c.frame>=9240) { ++s.phase;s.phase_frame=0;sound(13);s.position.velocity.y=8;s.background=orange::Background::elly;s.tile_column=0; }
        break;
    case 2:
        s.position.update();s.position.velocity.x=s.position.current.x<3072 ? 32 : (s.position.current.x>=3088 ? -32 : 0);
        invulnerable();
        if(s.phase_frame>=32) {
            s.position.velocity.x=0;s.palette_zero[2]=0;s.palette_changed=1;state_.orbit_frame=0;
            s.position.current={3072,1536};s.position.previous.x=0;
            s.timed_out=1;++s.phase;s.phase_frame=0;s.mode=0;s.patterns_or_bonus=0;s.hp=s.end_hp;s.end_hp=0;state_.pattern_group=0;
        }
        break;
    case 3: {
        bool timed_completion=false;
        t.origin=s.position.current;
        switch(s.mode) {
        case 0:case 2:case 4:case 6:case 8: {
            const auto mode=s.mode;orbit(mode>=4 ? 2 : 1);
            if(s.phase_frame==16) {
                initialize_scythe(c.bullets.player);
                if(mode==0) t.angle=192;
                else if(mode==4) { t.angle=64;t.spawn_type=4;t.speed=64;t.group=BG_SINGLE_AIMED;t.pattern=55;tune(); }
                else if(mode==6) { t.angle=0;t.spawn_type=1;t.speed=32;t.group=BG_RING_AIMED;t.count=16;tune(); }
            }
            if(s.phase_frame>16) {
                if(mode==0 && (c.frame&15)==0) { t.spawn_type=2;t.pattern=92;t.speed=48;t.group=BG_SPREAD;t.count=5;t.delta=16;tune();fire();t.angle=byte(t.angle-16); }
                else if(mode==2 && s.phase_frame%16==0) { t.angle=0;t.spawn_type=1;t.speed=32;t.group=BG_RING_AIMED;t.count=8;fire(); }
                else if(mode==4 && (c.frame&7)==0) { fire();t.angle=byte(-t.angle);fire();t.angle=byte(-t.angle-3);sound(3); }
                else if(mode==6 && s.phase_frame%16==0) { fire();sound(3); }
                else if(mode==8) {
                    if(s.phase_frame%16==0) { t.spawn_type=2;t.pattern=76;t.speed=56;t.group=BG_RING_AIMED;t.count=16;t.angle=0;tune();fire();sound(3); }
                    if(s.hp<=200) { t.spawn_type=1;t.speed=32;t.group=BG_RANDOM_ANGLE;t.count=2;tune();fire(); }
                }
                end_scythe();
            }
            break;
        }
        case 1:case 3:case 5:case 7: {
            const auto mode=s.mode;const auto gathered=gather();
            if(gathered==1) break;
            if(gathered==2) {
                if(mode!=7) { t.angle=byte(motion::angle_to(s.position.current,c.bullets.player)+(mode==5 ? 64 : -64));break; }
                t.spawn_type=1;t.speed=32;t.group=BG_RING;t.count=16;
                t.angle=byte(random.next16());t.origin.x=motion::wrap(int(t.origin.x)-512);tune();fire();
                t.angle=byte(random.next16());t.origin.x=motion::wrap(int(t.origin.x)+1024);fire();
                t.angle=byte(random.next16());t.origin.x=motion::wrap(int(t.origin.x)-512);t.origin.y=motion::wrap(int(t.origin.y)-512);fire();
                t.angle=byte(random.next16());t.origin.y=motion::wrap(int(t.origin.y)+1024);fire();sound(9);
            }
            if(mode==7) { if(s.phase_frame>=80) burst();break; }
            if(s.phase_frame%4==0) sound(9);
            if(mode==1) {
                if(s.phase_frame<72) { if(s.phase_frame%2==0) { t.spawn_type=1;t.speed=64;t.group=BG_SPREAD;t.count=2;t.delta=12;tune();fire();t.angle=byte(t.angle+4); } }
                else if(s.phase_frame==72) t.angle=byte(t.angle+64);
                else if(s.phase_frame<144) { if(s.phase_frame%2==0) { t.spawn_type=1;t.speed=64;t.group=BG_SPREAD;t.count=2;t.delta=12;tune();fire();t.angle=byte(t.angle-2); } }
                else burst();
            } else {
                if(s.phase_frame<80) {
                    if(s.phase_frame%4==0) { t.spawn_type=4;t.speed=byte(s.phase_frame/8+44);t.group=BG_SPREAD;t.count=4;t.delta=12;t.pattern=52;tune();fire();t.angle=byte(t.angle+(mode==3 ? 11 : -11)); }
                } else if(mode==5 && s.phase_frame==80) t.angle=byte(t.angle+64);
                else burst();
            }
            break;
        }
        case 255:
            if(s.phase_frame<32) { orbit();break; }
            ++s.patterns_or_bonus;
            if(state_.pattern_group<4) {
                constexpr unsigned ends[]{8,16,24,32};
                s.mode=byte(s.patterns_or_bonus%(state_.pattern_group==0 ? 2 : 4)+(state_.pattern_group>=2 ? (state_.pattern_group-1)*2 : 0));
                if(s.patterns_or_bonus>=ends[state_.pattern_group]) { small(state_.pattern_group);s.mode=255;++state_.pattern_group;s.hp=motion::wrap(6000-int(state_.pattern_group)*1500); }
            } else if(state_.pattern_group==4) {
                s.mode=byte(s.patterns_or_bonus%4+5);
                if(s.patterns_or_bonus>=40) { s.patterns_or_bonus=0;timed_completion=true;++s.phase;sparks.add_circle(s.position.current,128,48);small(4);s.phase_frame=0; }
            }
            s.phase_frame=0;break;
        }
        if(!timed_completion && hit_phase()) { s.patterns_or_bonus=1;++s.phase;sparks.add_circle(s.position.current,128,48);small(4);s.phase_frame=0; }
        if(state_.pattern_group<4) {
            constexpr int threshold[]{4700,3300,2100,700};
            if(s.hp<=threshold[state_.pattern_group]) { drop();bullets.clear();bonus(10);small(state_.pattern_group);s.mode=255;s.phase_frame=0;++state_.pattern_group; }
        }
        break;
    }
    case 4:
        increment();if(s.phase_frame==16) small(4);
        if(s.phase_frame==32) {
            explosion(s.big,s.position.current,3);sound(15);s.phase=254;bullets.set_zap(s.patterns_or_bonus);
            if(s.patterns_or_bonus) bonus(40);
            s.sprite=4;s.phase_frame=0;sound(12);s.invincibility=255;q.mode=q.flag=0;
        }
        break;
    default:orange::update_defeat(s,c,sink);return;
    }
    s.homing=s.position.current;emit(orange::EventType::hp,{},static_cast<std::uint16_t>(s.hp),6000);
}
void System::prepare_render(std::uint16_t frame) {
    draws_.clear();auto& s=state_.boss;const auto& q=state_.scythe;
    const int left=pixels(s.position.current.x),top=pixels(s.position.current.y)-16;
    if(s.phase<254) draws_.push_back({s.damage ? orange::DrawKind::white_sprite : orange::DrawKind::sprite,static_cast<std::int16_t>(left),static_cast<std::int16_t>(top),s.sprite,0});
    else if(s.phase==254) draws_.push_back({orange::DrawKind::large_sprite,static_cast<std::int16_t>(left),static_cast<std::int16_t>(top),s.sprite,0});
    if(q.flag==1 && q.position.current.x>=0 && q.position.current.x<6144 && q.position.current.y>=0 && q.position.current.y<5888)
        draws_.push_back({orange::DrawKind::sprite,static_cast<std::int16_t>(pixels(q.position.current.x)),static_cast<std::int16_t>(pixels(q.position.current.y)-16),static_cast<std::uint16_t>(142+(frame%8)/2),0});
    orange::prepare_explosions(s,draws_);
}
Backdrop backdrop(const Snapshot& state) {
    const auto& s=state.boss;Backdrop plan;
    if(s.phase<=1) {
        if(s.phase_frame<=2) return plan;
        plan.kind=BackdropKind::dirty_tiles;plan.invalidations.push_back(s.position.previous);
        if(state.scythe.flag) plan.invalidations.push_back(state.scythe.position.previous);
    } else if(s.phase==2) {
        plan.kind=BackdropKind::picture_and_tiles;
        plan.mask_cel=motion::wrap(s.phase_frame>=0 ? s.phase_frame/2 : -((-int(s.phase_frame)+1)/2));
    } else if(s.phase<254) plan.kind=BackdropKind::picture;
    else if(s.phase==255 && s.phase_frame>2) plan.kind=BackdropKind::dirty_tiles;
    return plan;
}
} // namespace th04::portable::elly
