#include "stage4.hpp"
#include <stdexcept>
namespace th04::portable::stage4 {
unsigned carpet_image(unsigned level,unsigned x) {
    if(level>2 || x>=24) throw std::out_of_range("carpet image table coordinate");
    unsigned base=level==0 ? 0 : (level==1 ? 34 : 37);
    if(x==3 || x==5) return 48+level*2;
    if(x==18 || x==20) return 49+level*2;
    if(level && (x==0 || x==23)) return base+2;
    if(level && (x==1 || x==22)) return base+1;
    return base;
}
unsigned carpet_animation(unsigned cel,unsigned x) {
    if(cel>=8 || x>=24) throw std::out_of_range("carpet animation table coordinate");
    // Most columns follow edge distance. Original DATA is asymmetric: cel5
    // leaves only the left column2 already lit; its right counterpart stays2.
    const unsigned edge=x<12 ? x : 23-x;
    if(cel==0) return 2;
    if(cel==7) return edge==0 ? 1 : 0;
    const unsigned left=13-cel*2;
    if(edge<left) {
        if(cel==5 && x==2) return 0;
        return 2;
    }
    return edge<=left+1 ? 1 : 0;
}
CarpetUpdate update_carpet(CarpetState& s,Ring& ring,std::uint16_t frame,unsigned scroll_line) {
    CarpetUpdate out;if(!s.active) return out;
    if(s.cel<0 || s.cel>=8 || s.level>2 || scroll_line>=400) throw std::out_of_range("carpet callback state");
    out.invalidate_top=true;
    auto& row=ring[scroll_line/16];
    for(unsigned x=0;x<24;++x) if(carpet_animation(unsigned(s.cel),x)==2) row[x]=carpet_image(s.level,x);
    if(frame<=1) {
        for(auto& r:ring) for(unsigned x=0;x<24;++x) r[x]=carpet_image(0,x);
        s.level=0;out.invalidate_all=true;
    } else if((s.level==0 && frame>=1664) || s.level==1) {
        for(unsigned x=0;x<24;++x) if(carpet_animation(unsigned(s.cel),x)==1) {
            for(auto& r:ring) r[x]=carpet_image(unsigned(s.level)+1,x);
            for(unsigned y=0;y<50;++y) out.dirty[y*24+x]=1;
        }
        if(frame%4==0) { ++s.cel;if(s.cel>7) { ++s.level;s.cel=0; } }
    } else if(s.level==2) s.active=false;
    return out;
}
} // namespace th04::portable::stage4
