#include "gengetsu_render.hpp"
namespace th04::portable::gengetsu_render {
std::vector<Draw> prepare(gengetsu::Snapshot& owner,std::uint16_t frame,std::uint8_t amplitude_adjacent) {
    auto& s=owner.boss;std::vector<Draw> result;
    const auto pixels=[](int n){return n>=0 ? n/16 : -((-n+15)/16);};
    const int x=pixels(s.position.current.x),top=pixels(s.position.current.y)-32,left=x-16;
    const auto body=[&](unsigned kind) {
        result.push_back({kind,motion::wrap(left),motion::wrap(top),s.sprite});
        result.push_back({kind,motion::wrap(left+48),motion::wrap(top),std::uint16_t(unsigned(s.sprite)+1)});
    };
    if(s.sprite) {
        if(s.phase<254) {
            if(owner.wave_amplitude) {
                const auto amp=std::uint16_t(unsigned(owner.wave_amplitude)|(unsigned(amplitude_adjacent)<<8));
                result.push_back({11,motion::wrap(left),motion::wrap(top),s.sprite,0,0,0,0,
                    motion::wrap(80-int(owner.wave_amplitude)),amp,s.angle});
                result.push_back({11,motion::wrap(left+48),motion::wrap(top),std::uint16_t(unsigned(s.sprite)+1),0,0,0,0,
                    motion::wrap(80-int(owner.wave_amplitude)),amp,s.angle});
                s.angle=std::uint8_t(s.angle+4);
            } else if(!s.damage) {
                body(0);
                if(owner.bomb_invincibility && (owner.bomb_invincibility>=32 || owner.bomb_invincibility%2)) {
                    result.push_back({0,motion::wrap(x-15),motion::wrap(top),136});
                    result.push_back({0,motion::wrap(x+33),motion::wrap(top),137});
                }
            } else {
                ++owner.flash;body(owner.flash%2 ? 0 : 1);s.damage=0;
            }
        } else if(s.phase==254)result.push_back({10,motion::wrap(left),motion::wrap(top),s.sprite,0,0,0,3});
    }
    std::vector<orange::Draw> explosions;orange::prepare_explosions(s,explosions);
    for(const auto& d:explosions)result.push_back({unsigned(d.kind),d.left,d.top,d.pattern_or_radius,d.color});
    const laser::System lasers(owner.lasers);
    std::uint16_t laser_color=0;
    for(const auto& d:lasers.draws()) {
        if(d.kind==laser::DrawKind::color){laser_color=d.color;result.push_back({5,0,0,0,d.color,0,0,d.mode});}
        else if(d.kind==laser::DrawKind::line)result.push_back({8,d.x,d.y,0,laser_color,0,d.end_y});
        else if(d.kind==laser::DrawKind::disc)result.push_back({6,d.x,d.y,std::uint16_t(d.radius),laser_color});
        else if(d.kind==laser::DrawKind::rectangle)result.push_back({7,d.x,d.y,0,laser_color,d.end_x,d.end_y});
        else result.push_back({9});
    }
    if(s.phase==5 && s.mode==1 && s.phase_frame>=32 && s.phase_frame<96) {
        const std::uint16_t color=frame%2 ? 9 : 15;
        result.push_back({5,0,0,0,color,0,0,192});
        for(const auto& column:owner.columns)
            result.push_back({8,motion::wrap(int(column.position.x)/16+32),16,0,color,0,383});
    }
    return result;
}
}

namespace th04::portable::gengetsu {
void System::prepare_render(std::uint16_t frame,std::uint8_t amplitude_adjacent) {
    draws_=gengetsu_render::prepare(state_,frame,amplitude_adjacent);
}
}
