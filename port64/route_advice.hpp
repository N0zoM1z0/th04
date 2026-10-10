#pragma once
#include "main_state.hpp"
#include <algorithm>
#include <cmath>

namespace th04::portable::route_advice {
// Diagnostic key candidate only. A const observer never changes gameplay or
// supplies window input. OS delivery and the independent route verdict remain
// necessary; this policy is not evidence of original player behavior.
struct Advice {std::uint16_t held=0;bool shift=false;};
inline Advice observe(const gameplay::State& s) {
    const auto& p=s.player().position();
    Advice result;double danger=1e20;
    double target_x=192*16,target_y=304*16;
    if(s.boss_active())target_x=s.boss_snapshot().position.current.x;
    else {
        double distance=1e20;
        for(const auto& item:s.items().entities())if(item.flag==th04::portable::item::Flag::alive) {
            const auto q=item.position.current;
            if(q.y<16*220 || q.y>16*345)continue;
            const double dx=q.x-p.current.x,dy=q.y-p.current.y;
            const double d=dx*dx+dy*dy;
            if(d<distance){distance=d;target_x=q.x;target_y=std::max<int>(q.y,16*240);}
        }
    }
    double best=1e30;unsigned chosen=0;bool focused=false;
    for(unsigned focus=0;focus<2;++focus)for(unsigned move=0;move<9;++move) {
        const int dx=int(move%3)-1,dy=int(move/3)-1;
        const double speed=(dx && dy ? 48.0 : 64.0)/(focus ? 2 : 1);
        double risk=0,minimum=1e20;
        for(unsigned f=1;f<=12;++f) {
            const double x=std::clamp(p.current.x+dx*speed*f,128.0,6016.0);
            const double y=std::clamp(p.current.y+dy*speed*f,128.0,5632.0);
            for(const auto& b:s.bullets().snapshot().entities) {
                if(!b.flag || unsigned(b.phase)>=3)continue;
                const double bx=b.position.current.x+double(b.position.velocity.x)*f;
                const double by=b.position.current.y+double(b.position.velocity.y)*f;
                const double ax=bx-x,ay=by-y,d=ax*ax+ay*ay;
                minimum=std::min(minimum,d);
                if(d<256.0*256)risk+=1000000.0/(1+d)*(13-f);
            }
            for(const auto& e:s.enemies().snapshot().entities) {
                if(!e.flag || !e.player_collision)continue;
                const double ex=e.position.current.x+double(e.position.velocity.x)*f;
                const double ey=e.position.current.y+double(e.position.velocity.y)*f;
                const double ax=ex-x,ay=ey-y,d=ax*ax+ay*ay;
                minimum=std::min(minimum,d);
                if(std::abs(ax)<512 && std::abs(ay)<512)risk+=2000000.0/(1+d)*(13-f);
            }
            const double tx=(x-target_x)/16,ty=(y-target_y)/16;
            risk+=(tx*tx+ty*ty)*0.002;
        }
        if(risk<best){best=risk;chosen=move;focused=focus;danger=minimum;}
    }
    const int dx=int(chosen%3)-1,dy=int(chosen/3)-1;
    result.held=shot::input_shot|std::uint16_t(dx<0 ? player::left : dx>0 ? player::right : 0)|
        std::uint16_t(dy<0 ? player::up : dy>0 ? player::down : 0);result.shift=focused;
    if(danger<256.0*256 && !s.life().invincibility && !s.life().bombing && s.score().remaining_bombs)result.held|=0x800;
    return result;
}
}
