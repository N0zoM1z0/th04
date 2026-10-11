#include "grcg_raster.hpp"
#include <algorithm>

namespace th04::portable::grcg {
void circlefill(motion::Point center,std::uint16_t radius,const Sink& sink) {
    if(!radius) {sink({Kind::point,center.x,center.x,center.y});return;}
    std::uint16_t x=radius,y=0;
    auto error=motion::wrap(radius);
    const auto span=[&](std::uint16_t half,int offset) {
        sink({Kind::horizontal_line,motion::wrap(int(center.x)-half),
              motion::wrap(int(center.x)+half),motion::wrap(int(center.y)+offset)});
    };
    do {
        span(x,-int(y));span(x,y);
        error=motion::wrap(int(error)-(int(y)*2+1));
        if(error<0) {
            span(y,-int(x));span(y,x);
            x=std::uint16_t(x-1u);
            error=motion::wrap(int(error)+int(x)*2);
        }
        y=std::uint16_t(y+1u);
    } while(x>=y);
}
std::optional<Request> stage_hline(std::int16_t left,std::int16_t right,std::int16_t y) {
    if(std::uint16_t(int(y)-16)>367)return std::nullopt;
    auto lower=motion::wrap(int(left)-32),upper=motion::wrap(int(right)-32);
    if(lower<0 && upper<0)return std::nullopt;
    if(lower>upper)std::swap(lower,upper);
    lower=std::max<std::int16_t>(0,lower);
    upper=std::min<std::int16_t>(383,upper);
    if(motion::wrap(int(upper)-lower)<0)return std::nullopt;
    return Request{Kind::horizontal_line,std::int16_t(lower+32),std::int16_t(upper+32),y};
}
bool stage_pset(motion::Point p) {return p.x>=32 && p.x<=415 && p.y>=16 && p.y<=383;}
}
