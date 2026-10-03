#include "score.hpp"
#include <algorithm>

namespace th04::portable::score {
std::uint32_t numeric_units(const Digits& digits) {
    std::uint32_t result=0,power=1;
    for(unsigned i=1;i<8;++i) { result+=unsigned(digits[i])*power;power*=10; }
    return result;
}
std::vector<Event> render(Snapshot& s) {
    std::vector<Event> events;
    for(unsigned row:{4u,6u}) {
        const auto& digits=row==4 ? s.hiscore : s.digits;
        std::string glyphs;
        for(unsigned i=0;i<8;++i) { s.hud[i]=static_cast<std::uint8_t>(digits[7-i]+0xa0);glyphs.push_back(static_cast<char>(s.hud[i])); }
        const auto terminator=glyphs.find('\0');
        if(terminator!=std::string::npos) glyphs.resize(terminator);
        events.push_back({Kind::gaiji,56,row,0xe1,glyphs});
    }
    return events;
}
std::vector<Event> extend(Snapshot& s) {
    bool reached=false;
    switch(s.extends) {
    case 0:reached=s.digits[6]>=3;break;
    case 1:reached=s.digits[6]>=8;break;
    case 2:reached=s.digits[7]>=1 && s.digits[6]>=5;break;
    case 3:reached=s.digits[7]>=2 && s.digits[6]>=2;break;
    case 4:reached=s.digits[7]>=3;break;
    default:break;
    }
    if(!reached) return {};
    std::vector<Event> events{{Kind::performance_raise,0,0,4,{}}};
    s.performance=std::min(static_cast<std::uint8_t>(s.performance+4),s.maximum);
    ++s.extends;
    // Even at the life cap the extend index and performance change first.
    // Sound, HUD, bullet clear and popup only occur when a life is granted.
    if(s.lives<=99) {
        ++s.lives;s.bullet_clear=std::max<std::uint8_t>(s.bullet_clear,20);
        events.push_back({Kind::hud_lives,0,0,0,{}});
        s.popup_id=1;s.popup_callback=true;
        events.push_back({Kind::sound,0,0,7,{}});
    }
    return events;
}
std::vector<Event> update(Snapshot& s) {
    if(!s.delta) return {};
    // The target compares the full frame-delta dword, but only writes its low
    // word. Keep the high half even for injected abnormal states; valid MAIN
    // initializes it to zero. Subtraction later uses the complete dword.
    if(s.frame_delta>s.delta) s.frame_delta=(s.frame_delta&0xffff0000u)|(s.delta&65535u);
    const auto proposed=std::max<std::uint32_t>(1,std::min<std::uint32_t>(s.delta>>5,6111));
    const auto low=static_cast<std::uint16_t>(s.frame_delta);
    if(low<proposed) s.frame_delta=(s.frame_delta&0xffff0000u)|proposed;
    auto remaining=static_cast<std::uint16_t>(s.frame_delta);
    constexpr unsigned divisors[]{10000,1000,100,10};
    for(unsigned i=0;i<4;++i) { s.temporary[4-i]=static_cast<std::uint8_t>(remaining/divisors[i]);remaining=static_cast<std::uint16_t>(remaining%divisors[i]); }
    s.temporary[0]=static_cast<std::uint8_t>(remaining);
    // Only five temporary digits are overwritten. The next two retain their
    // previous values. This is observable in independently injected controls.
    for(unsigned i=0;i<6;++i) {
        const unsigned a=s.temporary[i],b=s.digits[i+1];
        const auto sum=static_cast<std::uint8_t>(a+b);
        const bool adjust=(sum&15)>9 || (a&15)+(b&15)>15;
        // AAA acts on AX (AH is zero before each iteration). A low-byte carry
        // during +0106h can yield AH=2 for nondecimal injected input bytes.
        const auto adjusted=static_cast<std::uint16_t>(unsigned(sum)+(adjust ? 0x106 : 0));
        s.digits[i+1]=static_cast<std::uint8_t>(adjusted&15);
        s.digits[i+2]=static_cast<std::uint8_t>(s.digits[i+2]+(adjusted>>8));
    }
    s.digits[7]=static_cast<std::uint8_t>(s.digits[7]+s.temporary[6]);
    bool confirmed=s.hiscore_popup_shown!=0;
    if(!confirmed) {
        // Descending byte comparison includes the continues digit; equality
        // also confirms the high score. Do not clamp the high decimal byte.
        confirmed=true;
        for(unsigned i=8;i-- > 0;) {
            if(s.hiscore[i]!=s.digits[i]) { confirmed=s.hiscore[i]<s.digits[i];break; }
        }
    }
    if(confirmed) s.hiscore=s.digits;
    if(!s.hiscore_popup_shown && confirmed) { s.hiscore_popup_shown=1;s.popup_id=0;s.popup_callback=true; }
    s.delta-=s.frame_delta;
    auto events=render(s);s.unused=0;
    const auto extra=extend(s);events.insert(events.end(),extra.begin(),extra.end());
    return events;
}
} // namespace th04::portable::score
