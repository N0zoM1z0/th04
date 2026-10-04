#include "yuuka6_foreground.hpp"
#include "yuuka6.hpp"
#include "yuuka6_entities.hpp"
#include "thick_lasers.hpp"

namespace th04::portable::yuuka6 {
namespace {
int pixels(motion::Subpixel value) {
    // SAR4 floors signed coordinates, whereas host signed division truncates.
    return value>=0 ? value/16 : -((-int(value)+15)/16);
}
}
void Foreground::prepare_render(System& system,std::uint16_t frame,
                                const laser::System& lasers,Entities& entities) {
    draws_.clear();auto& owner=system.state_;auto& boss=owner.boss;
    const auto sprite=[&](DrawKind kind,int x,int y,unsigned pattern,unsigned zoom=0) {
        draws_.push_back({kind,motion::wrap(x),motion::wrap(y),
                          static_cast<std::uint16_t>(pattern),0,0,0,
                          static_cast<std::uint16_t>(zoom)});
    };
    const int left=pixels(boss.position.current.x)-16;
    const int top=pixels(boss.position.current.y)-32;
    if(boss.phase==255) return;
    if(boss.phase==254) {
        sprite(DrawKind::zoom_sprite,left,top,boss.sprite,3);
        return; // The original bypasses every common rendering tail here.
    }
    if(owner.aux_flag) sprite(DrawKind::sprite,left+24,top+24,182+(frame%16)/4);
    if(boss.sprite) {
        const auto body=[&](int x,int y,std::uint8_t& damage,std::uint8_t& cycle) {
            // SUPER_PUT_1PLANE takes erase-mask0 and plane WORD FFCD:
            // this requests red, distinct from the custom crosses' FFC0 white.
            const auto kind=damage && !(cycle&1) ? DrawKind::red_sprite : DrawKind::sprite;
            sprite(kind,x,y,boss.sprite);sprite(kind,x+48,y,unsigned(boss.sprite)+1);
            cycle=static_cast<std::uint8_t>(cycle+(damage!=0));damage=0;
        };
        body(left,top,boss.damage,state_.body_flash);
        if(owner.mirror_state==2)
            body(pixels(owner.mirror.x)-16,pixels(owner.mirror.y)-32,
                 owner.mirror_damage,state_.mirror_flash);
    }
    // A hidden body preserves both damage bytes and their cycles, including
    // when mirror_state==2. It still executes the ordinary ordered tail.
    std::vector<orange::Draw> explosions;orange::prepare_explosions(boss,explosions);
    for(const auto& d:explosions)
        draws_.push_back({static_cast<DrawKind>(d.kind),d.left,d.top,d.pattern_or_radius,d.color});
    std::uint16_t color=0;
    for(const auto& d:lasers.draws()) {
        switch(d.kind) {
        case laser::DrawKind::color:
            color=d.color;draws_.push_back({DrawKind::color,0,0,0,color,0,0,d.mode});break;
        case laser::DrawKind::line:
            draws_.push_back({DrawKind::vertical_line,d.x,d.y,0,color,0,d.end_y});break;
        case laser::DrawKind::disc:
            draws_.push_back({DrawKind::disc,d.x,d.y,static_cast<std::uint16_t>(d.radius),color});break;
        case laser::DrawKind::rectangle:
            draws_.push_back({DrawKind::rectangle,d.x,d.y,0,color,d.end_x,d.end_y});break;
        case laser::DrawKind::disable:draws_.push_back({DrawKind::disable});break;
        }
    }
    // Unlike update(), Entities::prepare_render ages dying crosses. Preserve
    // its position after laser rendering; circle GROW leaves GRCG enabled.
    entities.prepare_render();
    for(const auto& d:entities.draws()) {
        switch(d.kind) {
        case EntityDrawKind::sprite:case EntityDrawKind::white_sprite:
            sprite(d.kind==EntityDrawKind::sprite ? DrawKind::sprite : DrawKind::white_sprite,
                   d.position.x,d.position.y,d.value);break;
        case EntityDrawKind::mode:draws_.push_back({DrawKind::mode,0,0,0,0,0,0,d.value});break;
        case EntityDrawKind::color:
            color=d.value;draws_.push_back({DrawKind::color,0,0,0,color});break;
        case EntityDrawKind::filled_circle:case EntityDrawKind::ring_circle:
            draws_.push_back({d.kind==EntityDrawKind::filled_circle ? DrawKind::disc : DrawKind::circle,
                              d.position.x,d.position.y,d.value,color});break;
        case EntityDrawKind::disable:draws_.push_back({DrawKind::disable});break;
        }
    }
}
} // namespace th04::portable::yuuka6
