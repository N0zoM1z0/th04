#include "player_bomb.hpp"
#include "yuuka6_background.hpp"
#include <stdexcept>

namespace th04::portable::bomb {
namespace {
int pixel(std::int16_t value) {
    return value>=0 ? value/16 : -((-int(value)+15)/16);
}
void require(bool ok,const char* why) {if(!ok)throw std::invalid_argument(why);}
bool reimu(application::Playchar character) {
    require(character==application::Playchar::reimu || character==application::Playchar::marisa,
            "invalid Bomb character");
    return character==application::Playchar::reimu;
}
}
void Effect::render(application::Playchar character,Context& c) {
    const bool first=reimu(character);auto& life=c.life;const auto frame=life.bomb_frame;
    draws_.clear();
    draws_.push_back({Kind::fill_bands,{},first ? 15 : 1});
    draws_.push_back({Kind::picture,{32,56},0});
    if(frame<=80) {
        life.circle_color=first ? 9 : 15;c.circles.set_color(life.circle_color);
        life.palette_tone=std::uint16_t(196-(int(frame)-48)*3);life.palette_changed=1;
    } else if(frame<=160 && !c.stage_frame_mod4) {
        const auto circle=[&](motion::Point center) {
            draws_.push_back({Kind::circle,center,0});c.circles.add(center,true);
        };
        if(first) {
            const auto angle=std::uint8_t(c.stage_frame<<2);
            const auto center=[&](std::uint8_t a) {
                const auto vector=motion::polar(a,128*16);
                return motion::Point{motion::wrap(192*16+vector.x),motion::wrap(184*16+vector.y)};
            };
            circle(center(angle));circle(center(std::uint8_t(128-angle)));
        } else {
            int x=(int(frame)-80)*4;const int y=(161-int(frame))*3+40;
            if(frame<120)x+=int(c.random.next16_mod((frame-80)*8))-(int(frame)-64)*4;
            else x+=int(c.random.next16_mod((161-frame)*8))-(161-int(frame))*4;
            circle({motion::wrap(x*16),motion::wrap(y*16)});
        }
        draws_.push_back({Kind::sound,{},9});
    }
    stars(character,c);
}
void Effect::render_stars(application::Playchar character,Context& c) {
    draws_.clear();stars(character,c);
}
void Effect::stars(application::Playchar character,Context& c) {
    const bool first=reimu(character);
    if(c.life.bomb_frame==48) {
        for(auto& star:state_.stars) {
            star.center={motion::Subpixel(c.random.next16_mod(6144)),
                         motion::Subpixel(c.random.next16_mod(5888))};
            if(first) {
                star.angle=0xc0;
                while(star.center.x>=2048 && star.center.x<=4096)
                    star.center.x=motion::Subpixel(c.random.next16_mod(6144));
                const int distance=star.center.x<=3072 ? 2080-star.center.x : star.center.x-4064;
                star.speed=std::uint8_t(distance/9);
            } else {
                star.angle=0xe0;star.speed=std::uint8_t(c.random.next16_and(127)+160);
            }
        }
    }
    for(unsigned index=0;index<state_.stars.size();++index) {
        auto& star=state_.stars[index];const auto vector=motion::polar(star.angle,star.speed);
        star.center={motion::wrap(int(star.center.x)+vector.x),motion::wrap(int(star.center.y)+vector.y)};
        if(star.center.x<=-128 || star.center.x>=6272 || star.center.y<=-128 || star.center.y>=6144) {
            if(first)star.center.y=6144;
            else if(index&1)star.center={-128,motion::Subpixel(c.random.next16_mod(5888))};
            else star.center={motion::Subpixel(c.random.next16_mod(6144)),6016};
        }
        draws_.push_back({Kind::star,{motion::wrap(pixel(star.center.x)+24),
                                   motion::wrap(pixel(star.center.y)+8)},first ? 14 : 8});
    }
}
Graphics::Graphics(Bytes bb,Bytes cdg,const Bytes& sprites)
    :bb_(std::move(bb)),cdg_bytes_(std::move(cdg)),picture_(cdg_bytes_),sprites_(sprites) {
    require(bb_.size()==2048,"Bomb BB extent differs");
    require(picture_.layout==CdgSheet::colors_only && picture_.width==384 &&
            picture_.height==274 && picture_.image_count==1,"Bomb CDG geometry differs");
    require(sprites_.width()==16 && sprites_.height()==16 && sprites_.count()>92,"Bomb star sprite is absent");
    for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16;++x)
        if(sprites_.pixel(92,x,y))star_mask_[y*2+x/8]|=std::uint8_t(128u>>(x&7));
}
void Graphics::tiles(unsigned cel,unsigned line,std::uint8_t color,Bytes& pixels) const {
    require(pixels.size()==640*400 && cel<16 && line<400,"invalid Bomb tile destination");
    for(unsigned row=0;row<23;++row)for(unsigned col=0;col<24;++col) {
        if(!(bb_[cel*128+row*4+col/8]&(128u>>(col&7))))continue;
        for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16;++x)
            pixels[((16+row*16+line+y)%400)*640+32+col*16+x]=color&15;
    }
}
void Graphics::apply(const std::vector<Draw>& draws,Bytes& pixels) const {
    require(pixels.size()==640*400,"incomplete Bomb pixel destination");
    for(const auto& draw:draws) {
        if(draw.kind==Kind::fill_bands) {
            // Target fill wrapper retains the central384x274 CDG rectangle.
            for(unsigned y=16;y<384;++y)if(y<56 || y>=330)
                for(unsigned x=32;x<416;++x)pixels[y*640+x]=draw.value&15;
        } else if(draw.kind==Kind::picture) {
            require(draw.position.x==32 && draw.position.y==56 && !draw.value,"invalid Bomb picture request");
            for(unsigned y=0;y<274;++y)for(unsigned x=0;x<384;++x) {
                unsigned color=0;
                for(unsigned plane=0;plane<4;++plane)if(picture_.bit(0,plane,x,y))color|=1u<<plane;
                pixels[(y+56)*640+x+32]=std::uint8_t(color);
            }
        } else if(draw.kind==Kind::star) {
            yuuka6::raster_mono(star_mask_,draw.position.x,draw.position.y,std::uint8_t(draw.value),
                [&](int x,int y,std::uint8_t color) {pixels[y*640+x]=color;});
        }
    }
}
} // namespace th04::portable::bomb
