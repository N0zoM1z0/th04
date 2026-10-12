#include "super_kernel.hpp"
namespace th04::portable::sprite::super {
void put(std::uint16_t left,std::uint16_t top,std::uint16_t size,
         const Read& read,const Write& write,const Port& port) {
    const unsigned width=size>>8,rows=(size&255u) ? size&255u : 256u;
    const unsigned shift=left&7u,mask=255u>>shift;
    auto origin=std::uint16_t(unsigned(top)*80u+(left>>3));
    const bool odd=(origin&1u)!=0,odd_width=(width&1u)!=0;
    if(odd)--origin;
    const auto words=std::uint8_t((width>>1)-unsigned(odd && !odd_width));
    const auto stride=std::uint8_t((odd ? (odd_width ? 79u : 78u) : 80u)-width);
    std::uint16_t source=0;
    const auto take=[&](unsigned count){const auto value=read(source,count);source=std::uint16_t(source+count);return value;};
    const auto rotate=[&](std::uint16_t value){return shift ? std::uint16_t((unsigned(value)>>shift)|(unsigned(value)<<(16u-shift))) : value;};
    const auto pass=[&] {
        auto destination=origin;
        for(unsigned row=0;row<rows;++row) {
            unsigned carry=0;
            const auto store=[&](unsigned count,std::uint16_t value){write(destination,count,value);destination=std::uint16_t(destination+count);};
            if(odd) {
                const auto first=rotate(take(1));carry=first>>8;
                store(2,std::uint16_t((first&255u)<<8));
            }
            // Only the even-destination/even-width kernel enters its WORD
            // loop unconditionally: CH=0 decrements through256 iterations.
            const unsigned count=(!odd && !odd_width && !words) ? 256u : unsigned(words);
            for(unsigned word=0;word<count;++word) {
                const auto value=rotate(take(2));
                const unsigned low=value&mask,next=(value&255u)^low;
                store(2,std::uint16_t((value&0xff00u)|low|carry));carry=next;
            }
            if(odd_width!=odd) {
                const auto last=rotate(take(1));
                store(2,std::uint16_t(last|carry));
                if(!odd)--destination;
            } else {
                write(destination,1,std::uint16_t(carry));
            }
            destination=std::uint16_t(int(destination)+std::int8_t(stride));
        }
    };
    port(0x7c,0xc0);for(unsigned tile=0;tile<4;++tile)port(0x7e,0);
    pass();
    port(0x7c,0xce);for(unsigned tile=0;tile<4;++tile)port(0x7e,255);
    pass();port(0x7c,0xcd);pass();port(0x7c,0xcb);pass();port(0x7c,0xc7);pass();port(0x7c,0);
}
}
