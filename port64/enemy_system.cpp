#include "enemy_system.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::enemy {
namespace {
std::uint16_t difference(motion::Subpixel a,motion::Subpixel b,int add=0) {
    return static_cast<std::uint16_t>(std::int32_t(a)-b+add);
}
void velocity(Entity& entity) { entity.position.velocity=motion::polar(entity.angle,entity.speed); }
void emit(const Sink& sink,EventType type,motion::Point position={},unsigned value=0,unsigned count=0) {
    if (sink) sink({type,position,static_cast<std::uint16_t>(value),static_cast<std::uint16_t>(count),{}});
}
void fire(const Entity& entity,const Sink& sink,bool copy_entire_template=false) {
    if (!sink) return;
    auto bullet=entity.bullet;
    bullet.origin.x=motion::wrap(std::int32_t(bullet.origin.x)+entity.position.current.x);
    bullet.origin.y=motion::wrap(std::int32_t(bullet.origin.y)+entity.position.current.y);
    // Script FIRE assigns the used fields; autofire copies all 18 bytes.
    // Let the scratch owner retain unused fields for the script variant.
    sink({EventType::fire,bullet.origin,static_cast<std::uint16_t>(copy_entire_template),0,bullet});
}
bool move(Entity& entity,std::uint16_t& gone) {
    entity.position.update();
    const auto p=entity.position.current;
    if ((entity.clip_x && difference(p.x,0,256)>=6656) ||
        (entity.clip_y && difference(p.y,0,256)>=6400)) {
        ++gone;entity.flag=killed;return true;
    }
    return false;
}
} // namespace

bool run_script(Entity& e,const stage::Program::Bytes& script,Context context,
                randring::SharedRandomRing& random,std::uint16_t& gone,const Sink& sink) {
    // Valid STD scripts chain setup operations until one timed instruction
    // yields. A bounded budget rejects malformed immediate infinite loops.
    for (unsigned instructions=0;instructions<4096;++instructions) {
        const auto byte=[&](unsigned delta) -> std::uint8_t {
            const auto at=std::int32_t(e.ip)+static_cast<std::int32_t>(delta);
            if (e.ip<0 || at<0 || static_cast<std::size_t>(at)>=script.size()) {
                throw std::out_of_range("enemy bytecode operand exceeds script");
            }
            return script[static_cast<std::size_t>(at)];
        };
        const auto word=[&](unsigned delta) { return motion::wrap(unsigned(byte(delta)) | (unsigned(byte(delta+1))<<8)); };
        const auto signed_byte=[&](unsigned delta) { return int(byte(delta))<128 ? int(byte(delta)) : int(byte(delta))-256; };
        const auto opcode=static_cast<Opcode>(byte(0));
        unsigned length=0,duration=0;
        bool timed=false;
        switch (opcode) {
        case Opcode::kill: e.flag=killed;return true;
        case Opcode::move_set_angle_speed:
            if (!e.instruction_frame) { e.angle=byte(1);e.speed=byte(2);velocity(e); }
            if (move(e,gone)) return true;
            length=4;duration=byte(3);timed=true;break;
        case Opcode::move_current_velocity:
            if (!e.instruction_frame) velocity(e);
            if (move(e,gone)) return true;
            length=2;duration=byte(1);timed=true;break;
        case Opcode::move_set_speed:
            if (!e.instruction_frame) { e.speed=byte(1);velocity(e); }
            if (move(e,gone)) return true;
            length=3;duration=byte(2);timed=true;break;
        case Opcode::move_turn: case Opcode::move_turn_with_acceleration:
            if (!e.instruction_frame) { e.angle=byte(1);e.speed=byte(2);e.angle_delta=byte(3); }
            velocity(e);
            if (opcode==Opcode::move_turn_with_acceleration) {
                e.position.velocity.x=motion::wrap(std::int32_t(e.position.velocity.x)+signed_byte(4));
                e.position.velocity.y=motion::wrap(std::int32_t(e.position.velocity.y)+signed_byte(5));
                length=7;duration=byte(6);
            } else { length=5;duration=byte(4); }
            if (move(e,gone)) return true;
            e.angle=static_cast<std::uint8_t>(e.angle+e.angle_delta);timed=true;break;
        case Opcode::wait:
            if (!e.instruction_frame) e.position.previous=e.position.current;
            length=2;duration=byte(1);timed=true;break;
        case Opcode::move_cosine_x: case Opcode::move_cosine_y:
            if (!e.instruction_frame) { e.angle=0;e.angle_delta=byte(2); }
            e.position.velocity={motion::polar(e.angle,byte(1)).x,static_cast<motion::Subpixel>(signed_byte(3))};
            if (opcode==Opcode::move_cosine_y) std::swap(e.position.velocity.x,e.position.velocity.y);
            if (move(e,gone)) return true;
            e.angle=static_cast<std::uint8_t>(e.angle+e.angle_delta);
            length=5;duration=byte(4);timed=true;break;
        case Opcode::aim_at_player:
            e.angle=static_cast<std::uint8_t>(byte(1)+motion::angle_to(e.position.current,context.player));
            e.speed=byte(2);velocity(e);length=3;break;
        case Opcode::add_move_angle: e.angle=static_cast<std::uint8_t>(e.angle+byte(1));velocity(e);length=2;break;
        case Opcode::move_with_scroll:
            if (!e.instruction_frame) e.position.velocity.x=0;
            e.position.velocity.y=context.scroll_delta;
            if (move(e,gone)) return true;
            length=2;duration=byte(1);timed=true;break;
        case Opcode::add_move_speed: e.speed=motion::wrap(std::int32_t(e.speed)+signed_byte(1));velocity(e);length=2;break;
        case Opcode::move_turn_current: case Opcode::move_turn_accel_current:
            velocity(e);
            if (opcode==Opcode::move_turn_accel_current) {
                e.position.velocity.x=motion::wrap(std::int32_t(e.position.velocity.x)+signed_byte(1));
                e.position.velocity.y=motion::wrap(std::int32_t(e.position.velocity.y)+signed_byte(2));
                length=4;duration=byte(3);
            } else { length=2;duration=byte(1); }
            if (move(e,gone)) return true;
            e.angle=static_cast<std::uint8_t>(e.angle+e.angle_delta);timed=true;break;
        case Opcode::activate:
            e.flag=alive;e.pattern=byte(1);e.hp=word(2);e.score=word(4);
            e.can_be_damaged=e.player_collision=1;length=6;break;
        case Opcode::randomize_move_angle: e.angle=static_cast<std::uint8_t>(random.next16());length=1;break;
        case Opcode::set_move_angle_speed: case Opcode::set_mirrored_angle_speed:
            e.angle=byte(1);e.speed=byte(2);
            if (opcode==Opcode::set_mirrored_angle_speed && !e.left_half) e.angle=static_cast<std::uint8_t>(128-e.angle);
            velocity(e);length=3;break;
        case Opcode::set_move_speed: e.speed=byte(1);velocity(e);length=2;break;
        case Opcode::fire: fire(e,sink);length=1;break;
        case Opcode::set_bullet_template:
            e.autofire=0;e.bullet.spawn_type=byte(1);e.bullet.origin={word(2),word(4)};
            e.bullet.group=byte(6);e.bullet.angle=byte(7);e.bullet.speed=byte(8);
            e.bullet.pattern=byte(9);e.bullet.count=byte(10);length=11;break;
        case Opcode::set_bullet_spawn_type: e.bullet.spawn_type=byte(1);length=2;break;
        case Opcode::set_bullet_offset:
            if (!e.instruction_frame) e.position.previous=e.position.current;
            e.bullet.origin={word(1),word(3)};length=5;break;
        case Opcode::set_bullet_angle: e.bullet.angle=byte(1);length=2;break;
        case Opcode::add_bullet_angle: e.bullet.angle=static_cast<std::uint8_t>(e.bullet.angle+byte(1));length=2;break;
        case Opcode::set_bullet_speed: e.bullet.speed=byte(1);length=2;break;
        case Opcode::add_bullet_speed: e.bullet.speed=static_cast<std::uint8_t>(e.bullet.speed+byte(1));length=2;break;
        case Opcode::set_bullet_group: e.bullet.group=byte(1);length=2;break;
        case Opcode::set_bullet_count: e.bullet.count=byte(1);length=2;break;
        case Opcode::set_bullet_sprite: e.bullet.pattern=byte(1);length=2;break;
        case Opcode::autofire_on: e.autofire=1;length=1;break;
        case Opcode::set_autofire_interval: {
            // 16-bit TC4J intermediate multiplication and signed /32.
            int interval=byte(1);
            if (context.performance>16) {
                const auto product=motion::wrap((context.performance-16)*interval);
                interval=std::max(16,int(byte(1))-product/32);
            } else if (context.performance<16) {
                const auto product=motion::wrap((16-context.performance)*interval);
                interval=std::min(255,int(byte(1))+product/32);
            }
            e.autofire_interval=static_cast<std::uint8_t>(context.rank==0 ? 255 : interval);length=2;break;
        }
        case Opcode::randomize_bullet_angle: e.bullet.angle=static_cast<std::uint8_t>(random.next16());length=1;break;
        case Opcode::autofire_off: e.autofire=0;length=1;break;
        case Opcode::set_bullet_spread_angle: e.bullet.delta=byte(1);length=2;break;
        case Opcode::loop_to_offset: case Opcode::loop_back:
            if (e.loop>=byte(2)) { e.loop=0;length=3;break; }
            ++e.loop;
            e.ip=opcode==Opcode::loop_to_offset ? byte(1) : motion::wrap(std::int32_t(e.ip)-byte(1));
            continue;
        case Opcode::enable_x_clip: e.clip_x=1;length=1;break;
        case Opcode::enable_y_clip: e.clip_y=1;length=1;break;
        case Opcode::enable_xy_clip: e.clip_x=e.clip_y=1;length=1;break;
        case Opcode::set_animation: e.animation_cels=byte(1);e.frames_per_cel=byte(2);length=3;break;
        case Opcode::play_sound_effect: emit(sink,EventType::sound,{},byte(1));length=2;break;
        case Opcode::set_sprite: e.pattern=byte(1);length=2;break;
        case Opcode::disable_damage_and_autofire: e.can_be_damaged=e.autofire=0;length=1;break;
        case Opcode::enable_damage_lunatic_autofire: e.can_be_damaged=1;e.autofire=context.rank==3;length=1;break;
        case Opcode::set_position: case Opcode::add_position:
            e.position.previous=e.position.current;
            if (opcode==Opcode::set_position) e.position.current={word(1),word(3)};
            else e.position.current={motion::wrap(std::int32_t(e.position.current.x)+word(1)),
                                     motion::wrap(std::int32_t(e.position.current.y)+word(3))};
            length=5;timed=true;break;
        case Opcode::disable_player_collision: e.player_collision=0;length=1;break;
        case Opcode::enable_player_collision: e.player_collision=1;length=1;break;
        case Opcode::add_sprite: e.pattern=static_cast<std::uint8_t>(e.pattern+byte(1));length=2;break;
        case Opcode::set_tile_ring: emit(sink,EventType::tile_ring,e.position.current,byte(1));length=2;break;
        default: throw std::invalid_argument("undefined enemy opcode");
        }
        if (timed) {
            // A duration N performs N+1 updates, then yields without running
            // the next opcode until the next gameplay frame.
            if (e.instruction_frame>=duration) { e.instruction_frame=0;e.ip=motion::wrap(std::int32_t(e.ip)+length); }
            else ++e.instruction_frame;
            return false;
        }
        e.ip=motion::wrap(std::int32_t(e.ip)+length);
    }
    throw std::invalid_argument("enemy immediate instruction budget exceeded");
}

bool System::add(stage::Spawn spawn,Context context,randring::SharedRandomRing& random) {
    for (auto& e:state_.entities) {
        if (e.flag!=free) continue;
        e.flag=first_frame;e.instruction_frame=e.loop=e.age=0;e.ip=0;e.script=spawn.script;
        if (spawn.position.x==15984) spawn.position.x=static_cast<motion::Subpixel>(random.next16_mod(6144));
        if (spawn.position.y==15984) spawn.position.y=static_cast<motion::Subpixel>(random.next16_mod(5888));
        e.position.current=spawn.position;e.item=spawn.item;e.damaged=0;e.autofire=context.rank==3;
        e.clip_x=e.clip_y=0;e.animation_cels=1;e.frames_per_cel=4;e.cel=0;
        e.can_be_damaged=e.player_collision=0;e.left_half=spawn.position.x<3072;
        e.autofire_frame=static_cast<std::uint8_t>(random.next16());e.autofire_interval=128;
        e.bullet.group=0x41;e.bullet.spawn_type=1;e.bullet.speed=42;e.bullet.origin={0,0};
        // Reuse preserves fields not explicitly initialized by enemies_add.
        return true;
    }
    return false; // No random draw when the pool is full.
}
void System::update(const stage::Program& program,Context context,randring::SharedRandomRing& random,
                    shot::System& shots,const Sink& sink) {
    state_.homing_target.reset();
    for (auto& e:state_.entities) {
        if (e.flag==free) continue;
        if (e.flag==killed) { e.flag=free;continue; }
        if (e.flag>=kill_animation) {
            e.position.update();++e.flag;
            e.pattern=static_cast<std::uint8_t>((e.flag-kill_animation)/4+4);
            if (e.pattern>=12) e.flag=killed;
            continue;
        }
        // The original caller ignores the VM's return value. A script KILL
        // or clip can therefore still reach the rest of this frame's update.
        run_script(e,program.script(e.script),context,random,state_.gone,sink);
        bool kill=e.player_collision && difference(e.position.current.x,context.player.x,192)<384 &&
                  difference(e.position.current.y,context.player.y,192)<384;
        if (kill) state_.player_hit=true;
        if (!kill && e.can_be_damaged && e.hp!=-1 &&
            difference(e.position.current.x,0,256)<6656 && difference(e.position.current.y,0,256)<6144) {
            if (e.position.current.y<=context.player.y && (!state_.homing_target ||
                e.position.current.y>state_.homing_target->y)) state_.homing_target=e.position.current;
            const auto hit=shots.hittest(e.position.current,{256,192},
                {context.bombing,false,context.frame_mod2,context.frame_mod4});
            state_.score_delta+=hit.damage;
            for (unsigned i=0;i<hit.spark_count;++i) emit(sink,EventType::sparks,hit.sparks[i],128,1);
            const auto damage=static_cast<std::uint8_t>(hit.damage);
            if (damage) {
                if (e.hp==-2) emit(sink,EventType::sound,{},10);
                else if (damage<e.hp) { e.hp=motion::wrap(std::int32_t(e.hp)-damage);e.damaged=1; }
                else kill=true;
            }
        }
        if (kill) {
            e.flag=kill_animation;e.animation_cels=1;e.can_be_damaged=e.player_collision=0;
            e.position.velocity={0,0};
            emit(sink,EventType::drop,e.position.current,e.item);
            emit(sink,EventType::sound,{},3);
            state_.score_delta+=static_cast<std::uint16_t>(e.score);
            emit(sink,EventType::sparks,e.position.current,64,8);
            ++state_.gone;++state_.killed_count;continue;
        }
        if (e.autofire) {
            ++e.autofire_frame;
            if (e.autofire_frame>=e.autofire_interval && e.position.current.y<4864 &&
                (difference(e.position.current.x,context.player.x,768)>=1536 ||
                 difference(e.position.current.y,context.player.y,768)>=1536)) {
                e.autofire_frame=0;fire(e,sink,true);
            }
        }
        ++e.age;
    }
}
void System::prepare_render() {
    for (unsigned i=0;i<pool_size;++i) {
        auto& e=state_.entities[i];auto& draw=render_[i];draw.visible=false;
        if ((e.flag!=alive && e.flag<kill_animation) || e.position.previous.y<=-256 || e.position.previous.y>=6144) continue;
        auto pattern=e.pattern;
        if (e.animation_cels>1) {
            if (!e.frames_per_cel) throw std::domain_error("zero enemy animation divisor");
            if (e.age%e.frames_per_cel==0 && ++e.cel>=e.animation_cels) e.cel=0;
            pattern=static_cast<std::uint8_t>(pattern+e.cel);
        }
        const auto x=e.position.current.x;
        const int left=16+(x>=0 ? x/16 : -((-int(x)+15)/16));
        if (left<=0 || left>=416 || e.position.current.y<=-256 || e.position.current.y>=6144) continue;
        draw={true,e.damaged!=0,pattern,e.position.current};
        // Animation and damage flash are simulation-owned once-per-frame
        // events; extra host paint messages must not advance either one.
        e.damaged=0;
    }
}
} // namespace th04::portable::enemy
