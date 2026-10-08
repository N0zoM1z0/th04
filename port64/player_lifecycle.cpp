#include "player_lifecycle.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::player {
namespace {
void emit(LifeContext& c,LifeKind kind,int value=0) {if(c.sink)c.sink({kind,value});}
}
std::uint16_t input_from_host_actions(std::uint16_t keys) {
    return std::uint16_t((keys&15u) | (keys&0x20u) | (keys&0x800u ? 0x10u : 0) |
        (keys&0x1000u ? 0x2000u : 0) | (keys&0x2000u ? 0x1000u : 0));
}
void Lifecycle::update(std::uint16_t keys,bool shift,LifeContext& c) {
    auto& s=state_;auto& p=c.movement.mutable_position();
    if(s.invincibility)--s.invincibility;
    if(s.hit) {
        s.hit=0;
        if(!s.invincibility) {
            c.shots.limit_laser_time(33);
            s.miss_time=40;s.invincibility=192;s.respawn_time=72;
            p.velocity={};
        }
    }
    if(!s.respawn_time) {
        c.movement.update(keys,shift);
        if(c.shots.advance_trigger((keys&shot::input_shot)!=0)) {
            emit(c,LifeKind::fire);emit(c,LifeKind::sound,1);
        }
    } else {
        p.update();--s.respawn_time;
    }
    s.previous_options=s.options;
    s.options={motion::wrap(std::int32_t(p.current.x)-p.velocity.x),
               motion::wrap(std::int32_t(p.current.y)-p.velocity.y)};
    c.shots.set_options(s.options);
    if(keys&0x10u)bomb(c);
    if(s.miss_time)miss_update(c);
}
void Lifecycle::bomb(LifeContext& c) {
    auto& s=state_;
    if(s.bombing || !c.score.remaining_bombs || s.bombing_disabled)return;
    if(s.miss_time) {
        if(s.miss_time<=32)return;
        s.miss_time=0;s.hit=0;s.respawn_time=0;
    }
    --c.score.remaining_bombs;emit(c,LifeKind::hud_bombs);
    s.bombing=1;s.bomb_frame=0;s.invincibility=255;s.background=1;
    s.clear_time=192;emit(c,LifeKind::sound,13);
    s.pull_items=1;++s.bombs_used;
}
void Lifecycle::miss_update(LifeContext& c) {
    auto& s=state_;auto& p=c.movement.mutable_position();
    --s.miss_time;
    if(s.miss_time>32)return;
    if(s.miss_time==32) {
        p.velocity={};c.score.power_overflow=0;s.explosion_radius=0;
        emit(c,LifeKind::miss_items);
        c.score.power=std::uint8_t(c.score.power-std::min(unsigned(c.score.power)/4,16u));
        if(c.score.dream_items_collected)--c.score.dream_items_collected;
        constexpr unsigned dreams[]{0,100,200,400,600,800,1000,1280};
        if(c.score.dream_items_collected>=8)throw std::invalid_argument("invalid death dream index");
        c.score.dream_score=std::uint16_t(dreams[c.score.dream_items_collected]);
        emit(c,LifeKind::hud_dream);emit(c,LifeKind::shot_level);emit(c,LifeKind::sound,2);
        if(c.performance>=22)c.performance=21;
        emit(c,LifeKind::performance_lower,4);
        const auto lowered=std::uint8_t(c.performance-4);
        const int signed_value=lowered<128 ? lowered : int(lowered)-256;
        c.performance=signed_value<int(c.minimum) ? c.minimum : lowered;
        ++s.misses;
    }
    s.explosion_radius=std::uint16_t(s.explosion_radius+112);
    s.explosion_angle=std::uint8_t(s.explosion_angle+8);
    if(s.miss_time>=4)return;
    if(c.score.remaining_lives>1) {
        s.palette_tone=s.miss_time&1 ? 150 : 100;s.palette_changed=1;
    }
    if(s.miss_time)return;
    p.current=p.previous={192*16,368*16};p.velocity={0,-32};
    if(c.score.remaining_lives>1) {
        --c.score.remaining_lives;emit(c,LifeKind::hud_lives);
        c.score.remaining_bombs=c.credit_bombs;emit(c,LifeKind::hud_bombs);
        s.clear_time=32;return;
    }
    emit(c,LifeKind::game_over);
    if(!c.game_over)throw std::logic_error("last-life path requires game-over scene");
    s.quit=c.game_over();
}
void Lifecycle::render_bomb(LifeContext& c) {
    auto& s=state_;if(!s.bombing)return;
    const auto frame=s.bomb_frame;
    if(frame<32)emit(c,LifeKind::bomb_tiles,frame/4);
    else if(frame<48)emit(c,LifeKind::bomb_tiles,frame/2-8);
    else if(frame<176) {
        if(frame==48) {
            s.scroll_active=0;emit(c,LifeKind::scroll,0);s.background=2;
            s.palette_backup=s.palette14;s.palette14={240,176,192};
        }
        emit(c,LifeKind::character_bomb);
    } else if(frame<226) {
        if(frame==176) {
            emit(c,LifeKind::sound,15);s.scroll_active=1;s.pull_items=0;
        }
        s.palette14=s.palette_backup;s.background=1;
        s.palette_tone=std::uint16_t(200-(frame-176)*2);s.palette_changed=1;
        if(frame==177)emit(c,LifeKind::scroll,c.scroll_line);
    } else {
        s.bombing=0;s.palette_tone=100;s.palette_changed=1;s.circle_color=13;
    }
    ++s.bomb_frame;
}
} // namespace th04::portable::player
