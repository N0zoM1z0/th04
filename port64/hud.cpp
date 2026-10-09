#include "hud.hpp"
#include <iterator>
#include <stdexcept>

namespace th04::portable::hud {
namespace {
constexpr std::uint16_t white=0xe1,yellow=0xc1;
Request glyph(int x,int y,std::uint8_t value,std::uint16_t attr=white) {
    return {Kind::gaiji,x,y,attr,value,{}};
}
Request string(int x,int y,std::string value,std::uint16_t attr=white) {
    // gaiji_putsa stops on a wrapped zero byte, including malformed numerals.
    const auto end=value.find('\0');if(end!=std::string::npos)value.resize(end);
    return {Kind::gaiji_string,x,y,attr,0,std::move(value)};
}
void append(Requests& a,Requests b) {
    a.insert(a.end(),std::make_move_iterator(b.begin()),std::make_move_iterator(b.end()));
}
int signed_byte(std::uint8_t value) {return value<128 ? value : int(value)-256;}
Requests count(int row,std::uint16_t value) {
    std::string text;unsigned started=0;
    for(unsigned divisor=10000;divisor>1;divisor/=10) {
        const unsigned digit=value/divisor;value=std::uint16_t(value%divisor);started|=digit;
        text.push_back(char(started ? 0xa0+digit : 2));
    }
    text.push_back(char(0xa0+value));return {string(62,row,std::move(text))};
}
Requests icons(int row,int value,std::uint8_t icon,bool small) {
    Requests out;
    if(small) {
        int i=0;for(;i<value;++i)out.push_back(glyph(62+i*2,row,icon));
        for(;i<5;++i)out.push_back(glyph(62+i*2,row,2));
    } else {
        // Five full-width cells: space, space, multiplication sign, space, space.
        out.push_back({Kind::sjis,62,row,white,0,"\x81\x40\x81\x40\x81\x7e\x81\x40\x81\x40"});
        if(value>=10) {out.push_back(glyph(68,row,std::uint8_t(0xa0+value/10)));value%=10;}
        out.push_back(glyph(70,row,std::uint8_t(0xa0+value)));
    }
    return out;
}
std::string alphabet(const char* letters,unsigned cells) {
    std::string out;for(;*letters;++letters)out.push_back(char(0xaa+*letters-'A'));
    out.resize(cells,char(2));return out;
}
}
Requests lives(std::uint8_t value) {const int n=signed_byte(std::uint8_t(value-1));return icons(13,n,0xd4,n<6);}
Requests bombs(std::uint8_t value) {return icons(11,signed_byte(value),0xd3,value<=5);}
Requests points(std::uint8_t value) {return count(15,value);}
Requests dream(std::uint16_t value) {return count(17,std::uint16_t(unsigned(value)*10));}
Requests graze(std::uint16_t value) {return count(19,value);}
Requests bar(std::uint16_t row,std::int16_t value,std::uint16_t attr) {
    std::string text;
    if(value>=128)for(unsigned i=0;i<8;++i)text.push_back(char(0x30+i));
    else {
        // Subtracting 16 from values below -32752 wraps into a stack overflow
        // in the original. Keep that undefined input outside this safe owner.
        if(value<-32752)throw std::invalid_argument("HUD bar would overflow original stack");
        int remainder=int(value)-16;
        while(remainder>0) {text.push_back(char(0x2f));remainder-=16;}
        text.push_back(char(0x20+((unsigned(std::uint16_t(value))-1u)&15u)));
        text.resize(8,char(2));
    }
    return {string(56,row,std::move(text),attr)};
}
Requests power(std::uint8_t value,std::uint8_t level) {
    constexpr std::uint8_t colors[]{0x41,0x41,0x41,0x61,0x61,0x21,0x81,0xa1,0xc1,0xe1};
    if(level>=10)throw std::invalid_argument("HUD shot level exceeds original table");
    return bar(22,value,colors[level]);
}
Requests hp(std::int16_t value) {
    if(!value)return {string(61,8,std::string(3,char(2))),string(56,9,std::string(8,char(2)))};
    if(value<0 || value>=160)throw std::invalid_argument("HUD HP color exceeds original table");
    constexpr std::uint8_t colors[]{0x41,0x61,0xa1,0xc1,0xe1};
    Requests out{string(61,8,"\xea\xeb\xec",yellow)};append(out,bar(9,value,colors[value/32]));return out;
}
Requests hp_update(std::int16_t& previous,std::int16_t current,std::int16_t maximum) {
    int target=0;
    if(current>0) {
        if(current>=maximum)target=128;
        else {target=int(std::int32_t(current)*128/maximum);if(target<128)++target;}
    }
    if(previous<target)previous=std::int16_t(previous+1);
    if(previous>target)previous=std::int16_t(target);
    return hp(previous);
}
Requests initialize(Values& v) {
    if(v.character>1 || v.rank>4)throw std::invalid_argument("HUD character or rank exceeds observed rows");
    Requests out{string(60,3,"\xd6\xd7\xd8\xd9",yellow),string(61,5,"\xd7\xd8\xd9",yellow)};
    for(const auto& e:score::render(v.score))out.push_back(string(e.left,e.row,e.bytes,e.value));
    out.push_back(string(57,11,v.character==0 ? "\xda\xdb" : "\xe0\xe1",yellow));
    append(out,bombs(v.bombs));append(out,lives(v.lives));
    out.push_back(string(57,13,v.character==0 ? "\xdc\xdd" : "\xe2\xe3",yellow));
    out.push_back(glyph(58,15,0xe6,yellow));append(out,points(v.points));
    out.push_back(glyph(58,17,0xe7,yellow));append(out,dream(v.dream));
    out.push_back(glyph(58,19,0xe8,yellow));append(out,graze(v.graze));
    out.push_back(string(62,21,v.character==0 ? "\xde\xdf" : "\xe4\xe5",yellow));
    append(out,power(v.power,v.shot_level));
    constexpr const char* ranks[]{"EASY","NORMAL","HARD","LUNATIC","EXTRA"};
    const std::uint16_t color=v.rank==0 ? 0x81 : v.rank==1 ? 0xa1 : v.rank==2 ? 0x61 : 0x41;
    out.push_back(string(57,23,alphabet(ranks[v.rank],7),color));append(out,hp(0));return out;
}
void apply(registration::TextPlane& plane,const Requests& requests) {
    for(const auto& r:requests) {
        if(r.kind==Kind::gaiji)plane.put(r.column,r.row,r.glyph,r.attribute);
        else if(r.kind==Kind::gaiji_string)plane.put_string(r.column,r.row,r.text,r.attribute);
        else plane.put_sjis(r.column,r.row,r.text,r.attribute);
    }
}
} // namespace th04::portable::hud
