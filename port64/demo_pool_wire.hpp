#pragma once
#include "main_state.hpp"
#include <algorithm>
#include <ostream>
#include <stdexcept>

// Explicit original record layouts. No host packing, inactive-slot filtering,
// or expected target bytes. Only enemy script IDs need pointer translation.
namespace th04::portable::demo_wire {
struct Writer {
    std::vector<std::uint8_t> data;
    template<class T> void byte(T v) {data.push_back(std::uint8_t(v));}
    template<class T> void word(T v) {byte(v);byte(std::uint16_t(v)>>8);}
    void point(motion::Point p) {word(p.x);word(p.y);}
    void movement(const motion::Motion& m) {point(m.current);point(m.previous);point(m.velocity);}
    void bullet(const enemy::BulletTemplate& b) {
        byte(b.spawn_type);byte(b.pattern);point(b.origin);point(b.velocity);
        byte(b.group);byte(b.angle);byte(b.speed);byte(b.count);byte(b.delta);
        byte(b.unused_1);byte(b.special_motion);byte(b.unused_2);
    }
    template<class Pool,class Encode> void pool(const Pool& entries,unsigned stride,Encode encode) {
        for(const auto& e:entries) {
            const auto before=data.size();encode(e);
            if(data.size()!=before+stride)throw std::logic_error("demo pool wire stride");
        }
    }
};
// Nine complete pools, in the original initialization owner's clear order.
inline void pools(std::ostream& output,unsigned demo,const gameplay::State& state,const stage::Program& program) {
    Writer w;w.word(demo);w.word(state.frames());
    w.pool(state.shots().snapshot().entities,18,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.age);w.movement(e.position);w.word(e.pattern);w.byte(e.damage);w.byte(e.unused_angle);
    });
    w.pool(state.enemies().snapshot().entities,64,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.age);w.movement(e.position);w.byte(e.pattern);w.byte(e.unused_1);
        w.word(e.hp);w.word(e.unused_2);w.word(e.score);
        w.word(e.script==0xffff ? 0 : program.original_script_offset(e.script));
        w.word(e.ip);w.byte(e.instruction_frame);w.byte(e.loop);w.word(e.speed);
        w.byte(e.angle);w.byte(e.angle_delta);w.byte(e.clip_x);w.byte(e.clip_y);w.byte(e.unused_3);
        w.byte(e.item);w.byte(e.damaged);w.byte(e.animation_cels);w.byte(e.frames_per_cel);w.byte(e.cel);
        w.byte(e.can_be_damaged);w.byte(e.autofire);w.byte(e.player_collision);w.byte(e.left_half);
        w.bullet(e.bullet);w.byte(e.autofire_frame);w.byte(e.autofire_interval);
    });
    w.pool(state.sparks().snapshot().entities,16,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.age);w.movement(e.center);w.word(e.angle);
    });
    w.pool(state.bullets().snapshot().entities,26,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.age);w.movement(e.position);
        w.byte(e.group);w.byte(e.unused);w.byte(e.speed);w.byte(e.angle);w.byte(e.phase);w.byte(e.movement);
        w.byte(e.special);w.byte(e.final_speed);w.byte(e.timer_or_turns);w.byte(e.delta_or_angle);w.word(e.pattern);
    });
    const auto custom_begin=w.data.size();
    w.pool(state.yuuka6_entities().snapshot().slots,26,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.angle);w.point(e.center);for(auto byte:e.unused_position)w.byte(byte);
        w.point(e.velocity);w.word(e.age);w.word(e.filled_radius);w.word(e.ring_distance);
        w.word(e.hp);w.word(e.damage);w.byte(e.speed);w.byte(e.padding);
    });
    if(state.kurumi_active()) {
        // Both systems own views of the same832-byte target pool. Keep the
        // full backing extent, then encode all six actual Stage2 ray records,
        // including free flags, retained coordinates and unused bytes.
        const auto* kurumi=state.kurumi();
        if(!kurumi)throw std::logic_error("active Kurumi has no custom-entity owner");
        Writer rays;
        rays.pool(kurumi->snapshot().rays,26,[&](const auto& e) {
            rays.byte(e.flag);rays.byte(e.unused);rays.point(e.target);
            rays.point(e.origin);rays.point(e.velocity);
            for(auto byte:e.padding)rays.byte(byte);
        });
        if(rays.data.size()!=6*26 || custom_begin+rays.data.size()>w.data.size())
            throw std::logic_error("Kurumi custom-entity view extent");
        std::copy(rays.data.begin(),rays.data.end(),w.data.begin()+custom_begin);
    }
    w.pool(state.circles().snapshot().entities,10,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.age);w.point(e.center);w.word(e.radius);w.word(e.delta);
    });
    w.pool(state.items().entities(),20,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.unused);w.movement(e.position);w.byte(e.type);w.byte(e.unknown);
        w.word(e.pattern);w.word(e.pulled_to_player);
    });
    w.pool(state.point_numbers().snapshot().entities,16,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.age);w.point(e.center);w.word(e.previous_y);
        for(auto digit:e.decimal)w.byte(digit);w.word(e.width);w.byte(e.times_two);w.byte(e.padding);
    });
    w.pool(state.gathers().snapshot().entities,42,[&](const auto& e) {
        w.byte(e.flag);w.byte(e.color);w.movement(e.center);w.word(e.radius);w.word(e.ring_points);
        w.byte(e.angle);w.byte(e.angle_delta);w.bullet(e.bullet);w.word(e.previous_radius);w.word(e.radius_delta);
    });
    if(w.data.size()!=4+24952)throw std::logic_error("demo pool frame extent");
    output.write(reinterpret_cast<const char*>(w.data.data()),std::streamsize(w.data.size()));
    if(!output)throw std::runtime_error("demo pool write failed");
}
}
