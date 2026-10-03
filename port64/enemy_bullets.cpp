#include "enemy_bullets.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::bullet {
namespace {
std::uint8_t byte(int value) { return static_cast<std::uint8_t>(value); }
std::uint16_t distance(motion::Subpixel a,motion::Subpixel b,int bias) {
    return static_cast<std::uint16_t>(std::int32_t(a)-b+bias);
}
bool inside(motion::Point p) { return p.x>-128 && p.x<6272 && p.y>-128 && p.y<6016; }
bool hit(motion::Point p,motion::Point player) {
    return distance(p.x,player.x,64)<=128 && distance(p.y,player.y,64)<=128;
}
void velocity(Entity& b) { b.position.velocity=motion::polar(b.angle,b.speed); }
void emit(const Sink& sink,EventType type,motion::Point p={},unsigned value=0,unsigned count=0) {
    if (sink) sink({type,p,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count),{}});
}
// Group completion is a signed TC4J comparison. Non-ring count zero emits
// one member; an undefined group keeps filling the available pool.
bool resolve(Template& b,unsigned member,motion::Point player,randring::SharedRandomRing& random,std::uint8_t& angle) {
    unsigned offset=0;auto speed=b.speed;
    bool complete=false,aimed=true;
    const bool last=int(member)>=int(b.count)-1;
    switch (b.group) {
    case BG_SPREAD: case BG_SPREAD_AIMED:
        if (b.count&1) {
            const unsigned magnitude=((member+1)/2)*b.delta;
            offset=(member&1) ? unsigned(-byte(magnitude)) : byte(magnitude);
        } else {
            const unsigned magnitude=b.delta/2+(member/2)*b.delta;
            offset=(member&1) ? unsigned(-byte(magnitude)) : byte(magnitude);
        }
        complete=last;aimed=b.group==BG_SPREAD_AIMED;break;
    case BG_RING: case BG_RING_AIMED:
        offset=member*256/b.count;complete=last;aimed=b.group==BG_RING_AIMED;break;
    case BG_FORCESINGLE_RANDOM_ANGLE:
        offset=random.next16();complete=true;aimed=false;break;
    case BG_FORCESINGLE: case BG_SINGLE: complete=true;aimed=false;break;
    case BG_RANDOM_ANGLE: offset=random.next16();complete=last;aimed=false;break;
    case BG_RANDOM_ANGLE_AND_SPEED:
        offset=random.next16();speed=byte(speed+random.next16_and(31));complete=last;aimed=false;break;
    case BG_RANDOM_CONSTRAINED_ANGLE_AIMED:
        offset=unsigned(int(random.next16_and(31))-16);complete=last;break;
    case BG_FORCESINGLE_AIMED: case BG_SINGLE_AIMED: complete=true;break;
    case BG_STACK: case BG_STACK_AIMED:
        speed=byte(speed+b.delta*member);complete=last || b.speed>=160;aimed=b.group==BG_STACK_AIMED;break;
    default: break;
    }
    if (aimed) offset+=motion::angle_to(b.origin,player);
    angle=byte(offset+b.angle);b.velocity=motion::polar(angle,speed);return complete;
}
} // namespace

std::uint8_t pellet_pixel(unsigned x,unsigned y) {
    if (x>=8 || y>=8) throw std::out_of_range("pellet pixel");
    unsigned color=0;
    const int dx=2*int(x)-7,dy=2*int(y)-7;
    if (y<6 && dx*dx+dy*dy<=64) color=15;
    if (y>=3) {
        const auto row=y-3;
        const bool ink=row<2 ? x==7 : (row==2 ? x==0 || x>=6 : (row==3 ? x>=1 && x<=6 : x>=2 && x<=5));
        if (ink) color=9;
    }
    return static_cast<std::uint8_t>(color);
}

void tune(Template& b,std::uint8_t rank,std::uint8_t performance) {
    // Performance tuning runs before rank tuning; every compound assignment
    // stores back to a byte before the following arithmetic operation.
    switch (b.group) {
    case BG_STACK: case BG_STACK_AIMED:
        if (performance>=24) ++b.count;else if (performance<=6 && b.count>=2) --b.count;break;
    case BG_SPREAD: case BG_SPREAD_AIMED:
        if (performance>=24) b.count=byte(b.count+2);else if (performance<=6 && b.count>=3) b.count=byte(b.count-2);break;
    case BG_RING: case BG_RING_AIMED:
        if (performance>=24) b.count=byte(b.count+4);
        else if (performance>=20) b.count=byte(b.count+2);
        else if (b.count>=5) {
            if (performance<=10) b.count=byte(b.count-2);
            if (performance<=4) b.count=byte(b.count-4);
        }
        break;
    default: break;
    }
    if (rank==0) {
        switch (b.group) {
        case BG_STACK: case BG_STACK_AIMED: b.delta=byte(b.delta-b.delta/4);if (b.count>=2) --b.count;break;
        case BG_SPREAD: case BG_SPREAD_AIMED: if (b.count>=3) b.count=byte(b.count-2);break;
        case BG_RANDOM_ANGLE: case BG_RING: case BG_RING_AIMED: b.count/=2;break;
        default: break;
        }
    } else if (rank==2 || rank==3) {
        const bool lunatic=rank==3;
        switch (b.group) {
        case BG_SINGLE: case BG_SINGLE_AIMED:
            b.group=b.group==BG_SINGLE ? (lunatic ? BG_SPREAD : BG_STACK) : (lunatic ? BG_SPREAD_AIMED : BG_STACK_AIMED);
            b.count=lunatic ? 3 : 2;b.delta=6;break;
        case BG_STACK: case BG_STACK_AIMED: b.delta=byte(b.delta+b.delta/2);if (lunatic) ++b.count;break;
        case BG_SPREAD: case BG_SPREAD_AIMED: b.count=byte(b.count+(lunatic ? 4 : 2));break;
        case BG_RING: case BG_RING_AIMED:
            b.count=byte(b.count*(lunatic ? 2 : 3));if (!lunatic) b.count/=2;
            b.count=std::min<std::uint8_t>(b.count,48);break;
        case BG_RANDOM_ANGLE: case BG_RANDOM_ANGLE_AND_SPEED: b.count=byte(lunatic ? b.count*2 : b.count+b.count/2);break;
        default: break;
        }
    }
}
void System::fire(const enemy::Event& event,Context c,randring::SharedRandomRing& random,const Sink& sink) {
    if (event.value) state_.scratch=event.bullet;
    else {
        auto& b=state_.scratch;const auto& in=event.bullet;
        b.spawn_type=in.spawn_type;b.pattern=in.pattern;b.origin=in.origin;b.group=in.group;
        b.angle=in.angle;b.speed=in.speed;b.count=in.count;b.delta=in.delta;
    }
    tune(state_.scratch,c.rank,c.performance);add(state_.scratch,c,random,false,false,sink);
}
void System::add(Template& b,Context c,randring::SharedRandomRing& random,bool special,bool fixed_speed,const Sink& sink) {
    if (state_.zap_frame) return;
    const auto saved_speed=b.speed,saved_count=b.count;
    if (!special && b.spawn_type==3) {
        b.spawn_type=1;
        if (sink) sink({EventType::gather,b.origin,1024,8,b});
        return; // Deferred gather owner receives the unscaled template.
    }
    // Match the existing playable DOS product's empty-ring repair. Original
    // CPU count-zero IDIV is retained as a separate negative Oracle control.
    if ((b.group==BG_RING || b.group==BG_RING_AIMED) && !b.count) return;
    if ((state_.clear_time && state_.clear_time<=17) || !inside(b.origin)) return;
    if (hit(b.origin,c.player)) { state_.player_hit=true;return; }
    if (!fixed_speed) {
        b.speed/=2;
        b.speed=byte(b.speed+(int(b.speed)*c.performance)/16);
        b.speed=std::clamp<std::uint8_t>(b.speed,8,128);
    }
    const bool pellet=b.spawn_type==1;
    const unsigned first=pellet ? 0 : pellet_count,end=pellet ? pellet_count : pool_size;
    const auto phase=b.spawn_type==4 ? Phase::cloud_forward : (b.spawn_type==5 ? Phase::cloud_backward : Phase::grazeable);
    const auto movement=special ? Movement::special :
        (((b.speed<64 || state_.clear_time) && b.group!=BG_STACK && b.group!=BG_STACK_AIMED) ? Movement::decelerate : Movement::regular);
    unsigned member=0;
    for (unsigned index=end;index>first;) {
        auto& e=state_.entities[--index];if (e.flag) continue;
        e.flag=1;e.age=0;e.position.current=b.origin;e.group=b.group;e.pattern=b.pattern;e.phase=phase;e.movement=movement;
        if (special) { e.special=b.special_motion;e.timer_or_turns=0;e.delta_or_angle=state_.special_angle; }
        else { e.timer_or_turns=32;e.delta_or_angle=byte(72-b.speed); }
        const bool complete=resolve(b,member,c.player,random,e.angle);
        if (b.pattern>=76) e.pattern+=directional_sprite_cel(e.angle);
        e.position.velocity=b.velocity;e.speed=e.final_speed=b.speed;
        if (complete) break;
        ++member;
    }
    b.speed=saved_speed;
    if (!special && c.rank==0) b.count=saved_count;
}
void System::release(const Template& saved,Context c,randring::SharedRandomRing& random,const Sink& sink) {
    // Gather stored the already rank-tuned template. Restore it wholesale
    // and run only the regular add wrapper, without applying rank twice.
    state_.scratch=saved;add(state_.scratch,c,random,false,false,sink);
}
void System::update_special(Entity& b,Context c) {
    const auto turn_done=[&] {
        b.speed=b.final_speed;
        if (b.timer_or_turns>=state_.special_parameter) b.movement=Movement::regular;
        velocity(b);
    };
    const auto bounce=[&](bool horizontal) {
        ++b.timer_or_turns;b.angle=byte(horizontal ? 128-b.angle : -b.angle);
        if (b.timer_or_turns>=state_.special_parameter) b.movement=Movement::regular;
        velocity(b);
    };
    switch (static_cast<Special>(b.special)) {
    case Special::decelerate_aim: case Special::decelerate_turn:
        if (b.speed) { velocity(b);--b.speed; }
        else {
            ++b.timer_or_turns;
            b.angle=static_cast<Special>(b.special)==Special::decelerate_aim ? motion::angle_to(b.position.current,c.player) : byte(b.angle+b.delta_or_angle);
            turn_done();
        }
        break;
    case Special::accelerate: velocity(b);b.speed=byte(b.speed+state_.special_parameter);break;
    case Special::decelerate_to_angle:
        if (b.speed) {
            velocity(b);b.speed=b.speed>1 ? byte(b.speed-2) : 0;
            if (b.speed<32) {
                const auto bits=byte(b.delta_or_angle-b.angle);const int difference=bits<128 ? bits : int(bits)-256;
                b.angle=byte(b.angle+difference/4);
            }
        } else { b.angle=b.delta_or_angle;b.speed=b.final_speed;b.movement=Movement::regular;velocity(b); }
        break;
    case Special::bounce_x: case Special::bounce_y: case Special::bounce_xy: case Special::bounce_x_top: {
        const auto p=b.position.current;
        if (b.special!=133 && (p.x<=0 || p.x>=6144)) bounce(true);
        // Both axes are tested even after the first bounce reaches its turn
        // limit. Corner impacts can therefore increment turns twice.
        if (b.special!=132 && (p.y<=0 || (b.special!=135 && p.y>=5888))) bounce(false);
        break;
    }
    case Special::gravity: if (c.frame_mod2) b.position.velocity.y=motion::wrap(std::int32_t(b.position.velocity.y)+state_.special_parameter);break;
    default: break;
    }
}
void System::update(Context c,const Sink& sink) {
    unsigned seen=0;
    state_.pellet_visible.fill(false);
    if (!state_.zap_frame) {
        for (unsigned index=pool_size;index;) {
            --index;auto& b=state_.entities[index];
            if (!b.flag) continue;
            if (b.flag==2) { b.flag=0;continue; }
            ++seen;
            if (state_.clear_time) {
                if (b.movement<Movement::decay) {
                    b.movement=Movement::decay;b.pattern=index>=pellet_count ? 112 : 108;
                    state_.score_delta+=b.age ? 100 : 10;
                } else {
                    b.movement=static_cast<Movement>(byte(unsigned(b.movement)+1));
                    if (b.movement>=Movement::decay_end) { b.position.update();b.flag=2;continue; }
                    if (unsigned(b.movement)%4==0) ++b.pattern;
                }
            }
            ++b.age;
            if (b.phase>=Phase::active) {
                if (b.phase==Phase::active) b.phase=Phase::grazeable;
                else {
                    if (b.phase==Phase::cloud_backward) {
                        b.position.previous=b.position.current;
                        b.position.current.x=motion::wrap(std::int32_t(b.position.current.x)-std::int32_t(b.position.velocity.x)*8);
                        b.position.current.y=motion::wrap(std::int32_t(b.position.current.y)-std::int32_t(b.position.velocity.y)*8);
                        b.phase=Phase::cloud_forward;
                    } else if (b.phase==Phase::cloud_forward) b.position.update();
                    else {
                        b.position.previous=b.position.current;
                        b.position.current.x=motion::wrap(std::int32_t(b.position.current.x)+b.position.velocity.x/3);
                        b.position.current.y=motion::wrap(std::int32_t(b.position.current.y)+b.position.velocity.y/3);
                    }
                    b.phase=static_cast<Phase>(byte(unsigned(b.phase)+1));
                    if (b.phase>=Phase::cloud_end) b.phase=Phase::active;
                    continue;
                }
            }
            if (b.movement==Movement::special) update_special(b,c);
            else if (b.movement==Movement::decelerate) {
                --b.timer_or_turns;
                const auto product=motion::wrap(int(b.timer_or_turns)*b.delta_or_angle);
                b.speed=byte(b.final_speed+product/32);
                if (!b.timer_or_turns) { b.speed=b.final_speed;b.movement=Movement::regular; }
                velocity(b);
            }
            b.position.update();
            if (!inside(b.position.current)) { b.flag=2;continue; }
            if (state_.clear_time) continue;
            if (!c.invincibility) {
                if (b.phase!=Phase::grazeable) {
                    if (hit(b.position.current,c.player)) { b.flag=2;state_.player_hit=true;continue; }
                } else if (distance(b.position.current.x,c.player.x,256)<=576 && distance(b.position.current.y,c.player.y,352)<=704) {
                    emit(sink,EventType::sparks,b.position.current,32,2);b.phase=Phase::grazed;
                    if (state_.graze<999) { ++state_.graze;state_.score_delta+=c.graze_score; }
                }
            }
            if (index<pellet_count) state_.pellet_visible[index]=true;
        }
        if (!c.turbo && seen>=unsigned(24+c.performance+c.rank*8) && !c.frame_mod2) state_.slowdown=2;
    } else {
        const unsigned pattern=72+state_.zap_frame/4;
        unsigned reward=1,step=1;const unsigned cap=c.rank==0 ? 1000 : (c.rank==4 ? 2000 : 1600);
        state_.bonus=0;
        for (unsigned index=pool_size;index;) {
            auto& b=state_.entities[--index];if (b.flag!=1) continue;
            b.position.velocity={};b.position.update();
            if (pattern<76) { b.pattern=static_cast<std::uint16_t>(pattern);continue; }
            state_.bonus+=reward;state_.score_delta+=reward;emit(sink,EventType::point_number,b.position.current,reward);
            reward=static_cast<std::uint16_t>(reward+step);step=static_cast<std::uint16_t>(step+3);reward=std::min(reward,cap);b.flag=2;
        }
        if (state_.bonus) emit(sink,EventType::bonus_popup);
        ++state_.zap_frame;if (pattern>=76) state_.zap_frame=0;
    }
    if (state_.clear_time) --state_.clear_time;
}
} // namespace th04::portable::bullet
