#include "stage5.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::stage5 {
Setup prepare(orange::Snapshot boss,midboss::Snapshot midboss,unsigned rank) {
    // MAIN 13A9:A932 runs boss_reset, then overwrites only these setup fields.
    // HP/endHP/angle, additional[1..15] and explosion metadata are retained.
    boss.phase=0;boss.mode=0;boss.patterns_or_bonus=0;boss.phase_frame=0;boss.damage=0;
    boss.position.velocity={};boss.small[0].alive=boss.small[1].alive=0;boss.timed_out=1;
    boss.position.current=boss.position.previous={3072,1024};
    boss.sprite=128;boss.hitbox_radius={416,416};
    constexpr std::uint8_t interval[]{144,160,168,180};
    boss.additional[0]=interval[rank<4 ? rank : 1];
    midboss.active=false;midboss.hp=0;midboss.start_frame=60000;
    return {boss,midboss,{5120,640,3040}};
}

std::vector<StarDraw> Stars::update(std::uint8_t phase,int line,bool scrolling) {
    std::vector<StarDraw> draws;
    if(phase>=1 && phase<254) return draws;
    for(unsigned i=0;i<centers.size();++i) {
        auto& center=centers[i];center=motion::wrap(int(center)+64);
        if(center>=6400) center=motion::wrap(int(center)-6400);
        // Preserve signed WORD addition and SAR, then one 400-row correction.
        // The original does not use an unrestricted modulo for malformed state.
        const int subpixel=motion::wrap(int(center)-384);
        int top=subpixel>=0 ? subpixel/16 : -(15-subpixel)/16;
        if(scrolling) top=motion::wrap(top+line);
        if(top<0) top+=400;else if(top>=400) top-=400;
        draws.push_back({48+int(i)*128,top});
    }
    return draws;
}
std::array<StarInvalidation,3> Stars::invalidations() const {
    std::array<StarInvalidation,3> result;
    for(unsigned i=0;i<centers.size();++i)
        result[i]={{static_cast<motion::Subpixel>(1024+int(i)*2048),motion::wrap(int(centers[i])-64)},96,80};
    return result;
}
StarPlane::StarPlane(const std::vector<std::uint8_t>& cdg) {
    const auto word=[&](unsigned at) { return unsigned(cdg.at(at))|(unsigned(cdg.at(at+1))<<8); };
    if(cdg.size()!=3856 || word(0)!=960 || word(2)!=96 || word(4)!=80 || word(8)!=3 || cdg[10]!=1 || cdg[11]!=0)
        throw std::invalid_argument("Stage5 star CDG geometry changed");
    std::copy_n(cdg.begin()+16,960,blue_.begin());
}
void StarPlane::raster(int left,int top,unsigned display_line,
                      const std::function<std::uint8_t(unsigned,unsigned)>& read,
                      const std::function<void(unsigned,unsigned,std::uint8_t)>& write) const {
    if(left<0 || left>544 || left%8 || top<0 || top>=400 || display_line>=400)
        throw std::out_of_range("Stage5 star plane placement");
    // CDG rows are bottom-up. The original OR-dword producer wraps physical
    // rows at 32000 bytes; the host display origin is a separate transformation.
    for(unsigned y=0;y<80;++y) {
        const auto screen_y=(unsigned(top)+y+400-display_line)%400;
        for(unsigned x=0;x<96;++x) if(blue_[(79-y)*12+x/8]&(0x80u>>(x%8))) {
            const auto screen_x=unsigned(left)+x;
            write(screen_x,screen_y,static_cast<std::uint8_t>(read(screen_x,screen_y)|8u));
        }
    }
}
} // namespace th04::portable::stage5
