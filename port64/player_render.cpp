#include "player_render.hpp"
#include <stdexcept>

namespace th04::portable::player {
namespace {
int pixel(std::int16_t n) {return n>=0 ? n/16 : -((-int(n)+15)/16);}
std::int16_t physical(std::int16_t y,const LifeState& life,std::uint16_t line) {
    auto result=motion::wrap(pixel(y)+(life.scroll_active ? line : 0));
    if(result<0)result=motion::wrap(int(result)+400);
    else if(result>=400)result=motion::wrap(int(result)-400);
    return result;
}
}
std::vector<RenderDraw> render_requests(const LifeState& life,const motion::Motion& position,
    std::uint8_t level,std::uint16_t option,std::uint8_t mod4,std::uint16_t line) {
    std::vector<RenderDraw> draws;
    if(!life.miss_time || life.miss_time>32) {
        const auto pattern=std::uint16_t(position.velocity.x<0 ? 1 : position.velocity.x ? 2 : 0);
        draws.push_back({life.invincibility && !mod4 ? RenderKind::white : RenderKind::sprite,
            motion::wrap(pixel(position.current.x)+16),
            physical(motion::wrap(int(position.current.y)-128),life,line),pattern});
        if(level>=2) {
            const auto top=physical(motion::wrap(int(life.options.y)+128),life,line);
            const auto left=motion::wrap(pixel(life.options.x));
            draws.push_back({RenderKind::option,left,top,option});
            draws.push_back({RenderKind::option,motion::wrap(int(left)+48),top,option});
        }
        return draws;
    }
    if(life.miss_time<=1)return draws;
    auto radius=motion::wrap(life.explosion_radius);auto angle=life.explosion_angle;
    for(unsigned i=0;i<8;++i,angle=std::uint8_t(angle+64)) {
        if(i==4) {radius=motion::Subpixel(radius/2);angle=std::uint8_t(-angle);}
        const auto offset=motion::polar(angle,radius);
        const motion::Point point{motion::wrap(int(position.current.x)+offset.x),
                                  motion::wrap(int(position.current.y)+offset.y)};
        if(point.y<-128 || point.y>=6016 || point.x<-128 || point.x>=6272)continue;
        draws.push_back({RenderKind::sprite,motion::wrap(pixel(point.x)+8),
            physical(motion::wrap(int(point.y)-128),life,line),3});
    }
    return draws;
}
void render_pixels(const std::vector<RenderDraw>& draws,const sprite::Sheet& player,
    const sprite::Sheet& explosion,const sprite::Sheet& options,std::vector<std::uint8_t>& indexed) {
    if(indexed.size()!=640*400 || player.width()!=32 || player.height()!=48 || player.count()!=3 ||
       explosion.width()!=48 || explosion.height()!=48 || explosion.count()!=1 ||
       options.width()!=16 || options.height()!=16 || options.count()<12)
        throw std::invalid_argument("invalid player renderer input geometry");
    for(const auto& draw:draws) {
        const sprite::Sheet* sheet=&player;unsigned image=draw.pattern;
        if(draw.kind==RenderKind::option) {
            if(draw.pattern<28 || draw.pattern>=28+options.count())throw std::invalid_argument("invalid option pattern");
            sheet=&options;image=draw.pattern-28;
        } else if(draw.pattern==3) {sheet=&explosion;image=0;}
        else if(draw.pattern>=3)throw std::invalid_argument("invalid player pattern");
        // Valid gameplay requests fit the physical visible plane. Reject
        // invalid kernel inputs rather than silently inventing clipping.
        if(draw.left<0 || int(draw.left)+int(sheet->width())>640 || draw.top<0 || draw.top>=400)
            throw std::invalid_argument("player draw outside visible kernel domain");
        for(unsigned y=0;y<sheet->height();++y)for(unsigned x=0;x<sheet->width();++x) {
            auto color=sheet->pixel(image,x,y);if(!color)continue;
            if(draw.kind==RenderKind::white)color=15;
            indexed[((unsigned(draw.top)+y)%400)*640+unsigned(draw.left)+x]=color;
        }
    }
}
} // namespace th04::portable::player
