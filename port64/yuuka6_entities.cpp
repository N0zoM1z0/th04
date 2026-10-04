#include "yuuka6_entities.hpp"
namespace th04::portable::yuuka6 {
namespace {
int pixels(std::int16_t value) { return value>=0 ? value/16 : -((-int(value)+15)/16); }
void sound(const orange::Sink& sink,unsigned value) {
    if(sink) sink({orange::EventType::sound,{},static_cast<std::uint16_t>(value),0});
}
}
bool Entities::add_cross(motion::Point origin,std::uint8_t angle,std::uint8_t speed) {
    for(auto& slot:state_.slots) if(slot.flag==0) {
        slot.flag=1;slot.damage=0;slot.age=0;slot.angle=angle;slot.speed=speed;
        slot.hp=100;slot.center=origin;return true;
    }
    return false;
}
void Entities::add_safety_circle(motion::Point player,const orange::Sink& sink) {
    auto& circle=state_.slots.back();circle.flag=1;circle.age=0;circle.speed=8;
    // The last record's center uses screen pixels, unlike every cross's
    // subpixels. Keep all other velocity/HP/reserved/padding bytes intact.
    circle.center={motion::wrap(pixels(player.x)+32),motion::wrap(pixels(player.y)+16)};
    circle.filled_radius=8;circle.ring_distance=80;sound(sink,8);
}
void Entities::update(const EntityContext& c,bullet::System& bullets,spark::System& sparks,
                      randring::SharedRandomRing& random,const orange::Sink& sink) {
    state_.hit_radius={192,192};
    for(unsigned i=0;i<31;++i) {
        auto& cross=state_.slots[i];if(cross.flag!=1) continue;
        cross.velocity=motion::polar(cross.angle,cross.speed);
        cross.center.x=motion::wrap(std::int32_t(cross.center.x)+cross.velocity.x);
        cross.center.y=motion::wrap(std::int32_t(cross.center.y)+cross.velocity.y);
        if(cross.center.x<=-256 || cross.center.x>=6400 || cross.center.y>=6144 || cross.center.y<=-256)
            cross.flag=0;
        // Clearing an offscreen flag does not exit this iteration: contact,
        // homing and shots still execute, and a kill can resurrect it as16.
        const auto left=motion::wrap(std::int32_t(cross.center.x)-192);
        const auto top=motion::wrap(std::int32_t(cross.center.y)-192);
        if(static_cast<std::uint16_t>(std::int32_t(c.bullets.player.x)-left)<384 &&
           static_cast<std::uint16_t>(std::int32_t(c.bullets.player.y)-top)<384)
            state_.player_hit=1;
        if(cross.age<56) {
            const auto aim=motion::angle_to(cross.center,c.bullets.player);
            const auto delta=static_cast<std::uint8_t>(aim-cross.angle);
            // An exact heading still turns +1; a half turn takes -1.
            cross.angle=static_cast<std::uint8_t>(cross.angle+(delta<128 ? 1 : -1));
        }
        state_.hit_center=cross.center;
        if(sink) sink({orange::EventType::hit,state_.hit_center,192,192});
        cross.damage=motion::wrap(c.hit ? c.hit(state_.hit_center,state_.hit_radius) : 0);
        if(cross.damage!=0) sound(sink,4);
        cross.hp=motion::wrap(std::int32_t(cross.hp)-cross.damage);
        if(cross.hp<=0) {
            sound(sink,3);state_.score_delta+=3000u;cross.flag=16;cross.age=0;
            sparks.add_random(cross.center,64,8,random);
            if(sink) sink({orange::EventType::item,cross.center,3,0});
        }
        ++cross.age;
    }
    auto& circle=state_.slots.back();
    if(circle.flag==1) {
        if(circle.filled_radius<=128) circle.filled_radius=motion::wrap(std::int32_t(circle.filled_radius)+8);
        else circle.flag=2;
        return;
    }
    if(circle.flag!=2) return;
    // age is the circle's unsigned shrink_frame; speed is its color BYTE.
    // The grow->shrink frame changes only flag, not this clock or geometry.
    const auto clock=circle.age;
    if(clock<8) circle.ring_distance=motion::wrap(std::int32_t(circle.ring_distance)-8);
    else if(clock==8) circle.speed=9;
    else if(clock<16) circle.ring_distance=motion::wrap(std::int32_t(circle.ring_distance)-2);
    else if(clock<160) {
        circle.ring_distance=motion::wrap(std::int32_t(circle.ring_distance)+((clock&31)<16 ? 1 : -1));
        circle.speed=c.bullets.frame_mod2 ? 15 : 9;
        if(clock<=104) circle.filled_radius=motion::wrap(std::int32_t(circle.filled_radius)-1);
        if((clock&15)==0) {
            std::uint8_t angle_delta=192;auto& t=bullets.scratch();
            const auto fire=[&] {
                // Cross contact and spawn contact alias the original BYTE.
                // Detect this call's write before restoring the bullet bool,
                // so an incoming noncanonical127 becomes1 on new contact.
                const bool previous_hit=bullets.snapshot().player_hit;
                bullets.set_player_hit(false);bullets.add(t,c.bullets,random);
                const bool spawned_hit=bullets.snapshot().player_hit;
                if(spawned_hit) state_.player_hit=1;
                bullets.set_player_hit(previous_hit || spawned_hit);
            };
            if((clock&31)==0) {
                t.origin={c.boss_origin.x,motion::wrap(std::int32_t(c.boss_origin.y)+512)};
                t.spawn_type=2;t.pattern=60;t.group=44;t.count=32;t.speed=16;t.angle=0;
                bullet::tune(t,c.bullets.rank,c.bullets.performance);fire();angle_delta=64;
            }
            t.spawn_type=1;t.delta=12;
            auto angle=static_cast<std::uint8_t>(c.frame/5u);
            const auto length=motion::wrap(std::int32_t(circle.filled_radius)+4);
            for(unsigned i=0;i<8;++i,angle=static_cast<std::uint8_t>(angle+32u)) {
                t.angle=static_cast<std::uint8_t>(angle+angle_delta);
                const auto vector=motion::polar(angle,length);
                // The target first evaluates vector2_at in *pixel* units,
                // then subtracts32/16 before scaling by16. Those offsets are
                // literal subpixel constants applied to a pixel intermediate;
                // converting them to2/1 pixels would change the attack.
                t.origin={motion::wrap(std::int32_t(motion::wrap(std::int32_t(circle.center.x)+vector.x-32))*16),
                          motion::wrap(std::int32_t(motion::wrap(std::int32_t(circle.center.y)+vector.y-16))*16)};
                t.group=47;t.count=8;t.speed=16;fire();
                t.group=45;t.count=4;t.speed=48;fire();
            }
            sound(sink,3);
        }
    } else if(clock<176) {
        circle.ring_distance=motion::wrap(std::int32_t(circle.ring_distance)+16);
        circle.filled_radius=motion::wrap(std::int32_t(circle.filled_radius)-2);
    } else circle.flag=0;
    ++circle.age;
}
void Entities::prepare_render() {
    draws_.clear();
    for(unsigned i=0;i<31;++i) {
        auto& cross=state_.slots[i];if(cross.flag==0) continue;
        const motion::Point p{motion::wrap(pixels(cross.center.x)+16),motion::wrap(pixels(cross.center.y))};
        if(cross.flag==1) draws_.push_back({cross.damage==0 ? EntityDrawKind::sprite : EntityDrawKind::white_sprite,
                                          p,static_cast<std::uint16_t>(186+((cross.age>>1)&3))});
        else {
            draws_.push_back({EntityDrawKind::sprite,p,static_cast<std::uint16_t>(cross.flag/4)});
            ++cross.flag;if(cross.flag>=48) cross.flag=0;
        }
    }
    const auto& circle=state_.slots.back();if(circle.flag==0) return;
    draws_.push_back({EntityDrawKind::mode,{},0xC0});draws_.push_back({EntityDrawKind::color,{},2});
    draws_.push_back({EntityDrawKind::filled_circle,circle.center,static_cast<std::uint16_t>(circle.filled_radius)});
    if(circle.flag!=1) {
        draws_.push_back({EntityDrawKind::color,{},circle.speed});
        draws_.push_back({EntityDrawKind::ring_circle,circle.center,static_cast<std::uint16_t>(circle.ring_distance+circle.filled_radius)});
        draws_.push_back({EntityDrawKind::disable,{},0});
    }
    // GROW deliberately leaves GRCG enabled; only the ring path disables it.
}
} // namespace th04::portable::yuuka6
