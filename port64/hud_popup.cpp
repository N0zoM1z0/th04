#include "hud_popup.hpp"
#include <algorithm>
#include <stdexcept>
#include <string>

namespace th04::portable::popup {
namespace {
std::string label(unsigned id) {
    // Each popup occupies a contiguous semantic label in the loaded gaiji bank.
    const unsigned first[]{0x40,0x48,0x58,0x50},length[]{8,5,4,8};
    if(id>=4)throw std::invalid_argument("invalid MAIN popup ID");
    std::string out;for(unsigned i=0;i<length[id];++i)out+=char(first[id]+i);return out;
}
void wipe(registration::TextPlane& text,int row) {text.put_sjis(4,row,std::string(48,' '),0xe1);}
void points(registration::TextPlane& text,std::uint32_t value) {
    std::string digits;bool leading=true;
    for(std::uint32_t divisor=1000000;divisor>1;divisor/=10) {
        const auto digit=value/divisor;value%=divisor;leading=leading && !digit;
        digits+=char(leading ? 2 : std::uint8_t(0xa0u+digit));
    }
    digits+=char(std::uint8_t(0xa0u+value));digits+=char(0xa0);text.put_string(28,2,digits,0xe1);
}
}
void request(Snapshot& s,Kind id,std::uint32_t bonus) {
    s.requested=std::uint8_t(id);s.active=true;
    if(id==Kind::bonus)s.bonus=bonus;
}
void update(Snapshot& s,registration::TextPlane& text) {
    if(!s.active)return;
    if(s.requested!=s.current && s.frame>=64) {wipe(text,2);wipe(text,23);s.frame=0;}
    if(!s.frame) {
        s.current=s.requested;const auto source=label(s.current);s.length=std::int16_t(source.size());
        std::fill_n(s.shift.begin(),8,2);s.shift[std::size_t(s.length)]=0;
        s.left=std::int16_t(52-s.length*2);s.destination=std::int16_t(s.requested==2 ? 16 : 28-s.length);s.reached=false;
    }
    if(s.frame>=128) {wipe(text,2);s.frame=0;s.active=false;return;}
    const auto source=label(s.current);
    if(s.frame<s.length-1) {
        for(int i=0;i<s.length-1;++i)s.shift[std::size_t(i)]=s.shift[std::size_t(i+1)];
        s.shift[std::size_t(s.length-1)]=std::uint8_t(source[s.frame]);
        text.put_string(s.left,2,std::string(s.shift.begin(),s.shift.begin()+s.length),0xe1);
    } else if(s.left>s.destination) {
        text.put_string(s.left,2,source,0xe1);
        const int right=s.left+s.length*2;if(right<=50)text.put_character(right,2,0x2020,0xe1);
        s.left=std::int16_t(s.left-2);
    } else {
        if(!s.reached) {s.reached=true;wipe(text,2);}
        text.put_string(s.destination,2,source,0xe1);
        if(s.current==2)points(text,s.bonus);
    }
    ++s.frame;
}
} // namespace th04::portable::popup
