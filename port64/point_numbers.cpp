#include "point_numbers.hpp"
#include <stdexcept>

namespace th04::portable::pointnum {
static int pixels(motion::Subpixel value) {
    return value>=0 ? value/16 : -((-int(value)+15)/16);
}
void System::initialize() {state_.white_cursor=state_.yellow_cursor=0;}
void System::add(motion::Point center,std::uint16_t points,bool yellow,bool times_two) {
    auto& cursor=yellow ? state_.yellow_cursor : state_.white_cursor;
    if(cursor>=ring_size)throw std::logic_error("point-number ring cursor outside pool");
    auto& entry=state_.entities[(yellow ? ring_size : 0)+cursor];
    cursor=std::uint8_t(cursor==ring_size-1 ? 0 : cursor+1);
    entry.flag=1;entry.age=0;entry.center=center;entry.width=0;entry.times_two=times_two;
    // The leading cell is a BYTE quotient, even for values above9999.
    for(int i=digits-1,power=1000;i>=0;--i,power/=10) {
        entry.decimal[unsigned(i)]=std::uint8_t(points/power);points=std::uint16_t(points%power);
    }
    // Previous Y and padding deliberately survive a ring overwrite.
}
void System::update() {
    state_.first_yellow=0;unsigned next=0;
    for(unsigned index=0;index<count;++index) {
        auto& e=state_.entities[index];
        if(!e.flag)continue;
        if(e.flag==2) {e.flag=0;continue;}
        e.previous_y=e.center.y;
        if(e.age>=24)e.center.y=motion::wrap(std::int32_t(e.center.y)-8);
        if(e.center.y<=-64) {e.flag=2;continue;}
        e.age=std::uint8_t(e.age+1);
        if(e.age>36) {e.flag=2;continue;}
        state_.alive[next++]=std::uint16_t(index+1);
        if(index>=ring_size && !state_.first_yellow)state_.first_yellow=std::uint16_t(index+1);
    }
    state_.alive[next]=0; // Original leaves the unused list tail untouched.
}
void System::prepare_render(bool scrolling,std::uint16_t scroll_line) {
    draws_.clear();std::uint8_t color=15;
    for(auto pointer:state_.alive) {
        if(!pointer)break;
        if(pointer>count)throw std::logic_error("point-number list outside pool");
        auto& e=state_.entities[pointer-1];
        if(pointer==state_.first_yellow)color=11;
        int left=pixels(e.center.x)+12;
        const auto y=motion::wrap(std::int32_t(e.center.y)+192);
        auto top=motion::wrap(pixels(y)+(scrolling ? scroll_line : 0));
        if(top<0)top=motion::wrap(int(top)+400);
        else if(top>=400)top=motion::wrap(int(top)-400);
        unsigned length=digits;
        while(length && !e.decimal[length-1]) {left+=4;--length;}
        // Original's all-zero/invalid digit path overruns the glyph table.
        // Reject that path explicitly
        // rather than inventing a display and claiming original parity.
        if(!length)throw std::domain_error("original zero point-number render has no bounded glyph extent");
        for(unsigned i=length;i--;) {
            if(e.decimal[i]>=12)throw std::domain_error("original point-number digit exceeds font");
            draws_.push_back({left,top,e.decimal[i],color});left+=8;
        }
        draws_.push_back({left,top,0,color});left+=8;
        e.width=std::uint16_t((length+1)*8);
        if(e.times_two) {
            e.width+=16;
            draws_.push_back({left,top,10,color});
            draws_.push_back({left+8,top,11,color});
        }
    }
}
Font::Font(const std::vector<std::uint8_t>& main) {
    const auto word=[&](std::size_t at) {
        if(at+2>main.size())throw std::invalid_argument("short point-number MAIN asset");
        return unsigned(main[at])|(unsigned(main[at+1])<<8);
    };
    // Explicitly supported Japanese MAIN topology. Modified/relinked files
    // must not silently supply a different table at this original address.
    if(main.size()!=156258 || word(0)!=0x5a4d || word(8)!=384 ||
       word(6)!=1136 || word(6145)!=0x2134)
        throw std::invalid_argument("unsupported point-number MAIN asset topology");
    const std::size_t at=6144+0x2134*16+0x098a;
    if(at+12*128>main.size())throw std::invalid_argument("short point-number font");
    for(unsigned glyph=0;glyph<12;++glyph)for(unsigned y=0;y<8;++y) {
        rows_[glyph][y]=main[at+glyph*128+y*2];
        // Check every pre-shifted image against the unshifted asset row.
        for(unsigned shift=0;shift<8;++shift) {
            const auto row=rows_[glyph][y];
            const unsigned expected=(row>>shift)|((row<<(8-shift)&255)<<8);
            if(word(at+glyph*128+shift*16+y*2)!=expected)
                throw std::invalid_argument("point-number preshift asset disagreement");
        }
    }
}
bool Font::pixel(unsigned glyph,unsigned x,unsigned y) const {
    if(glyph>=12 || x>=8 || y>=8)throw std::out_of_range("point-number glyph coordinate");
    return (rows_[glyph][y]&(128u>>x))!=0;
}
void raster(const Font& font,const Draw& draw,const PixelSink& put) {
    if(draw.top<0 || draw.top>=400)throw std::out_of_range("point-number row outside VRAM");
    for(unsigned y=0;y<8;++y)for(unsigned x=0;x<8;++x)if(font.pixel(draw.glyph,x,y)) {
        // GRCG writes are linear; a byte crossing the right edge continues
        // in the next scanline. Vertical wrap belongs to the glyph kernel.
        const int linear=((draw.top+int(y))%400)*640+draw.left+int(x);
        if(linear>=0 && linear<640*400)put(linear%640,linear/640,draw.color);
    }
}
} // namespace th04::portable::pointnum
