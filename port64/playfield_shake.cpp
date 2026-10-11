#include "playfield_shake.hpp"
#include <stdexcept>
#include <cstdlib>
namespace th04::portable::playfield {
namespace {
std::int16_t decrement(std::int16_t value) {
    const unsigned next=(unsigned(std::uint16_t(value))+65535u)&65535u;
    return std::int16_t(next<32768 ? int(next) : int(next)-65536);
}
template<class Pixel> void move_page(std::vector<Pixel>& page,unsigned line,Shift shift) {
    if(page.size()!=640*400 || line>=400)throw std::invalid_argument("shake page extent/scroll");
    if(std::abs(int(shift.x))>384 || std::abs(int(shift.y))>400)throw std::invalid_argument("shake move extent");
    const auto at=[&](int x,int y) {return ((unsigned(y)+400-line)%400)*640+unsigned(x);};
    // The vectors contain visible rows. Translate to physical row coordinates
    // for each EGC move, including the rows crossing the GDC wrap boundary.
    for(int axis=0;axis<2;++axis) {
        const int delta=axis==0 ? shift.x : shift.y;if(!delta)continue;
        const auto source=page;
        for(int y=0;y<400;++y)for(int x=32;x<416;++x) {
            const int sx=x-(axis==0 ? delta : 0),sy=y-(axis==1 ? delta : 0);
            if(sx>=32 && sx<416 && sy>=0 && sy<400)page[at(x,y)]=source[at(sx,sy)];
        }
    }
}
}
Shift update(Shake& state,std::uint8_t mod2,std::uint8_t mod4) {
    if(state.time) {
        state.x=mod2==0 ? -2 : 2;state.y=mod4<=1 ? -2 : 2;
        state.time=decrement(state.time);
    }
    Shift result{state.x,state.y,false};
    if(state.x || state.y)state.redraw=2;
    if(state.redraw) {
        const unsigned next=(unsigned(std::uint8_t(state.redraw))+255u)&255u;
        state.redraw=std::int8_t(next<128 ? int(next) : int(next)-256);
        result.invalidate=true;state.x=state.y=0;
    }
    return result;
}
void move(std::vector<std::uint8_t>& page,unsigned line,Shift shift) {move_page(page,line,shift);}
void move(std::vector<std::uint32_t>& page,unsigned line,Shift shift) {move_page(page,line,shift);}
}
