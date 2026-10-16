#include "hud_titles.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::titles {
namespace {
// Shift-JIS display data from MAIN DGROUP1BBC/1BDC, independently checked
// through the original far-pointer tables and actual text_putsa instructions.
constexpr std::string_view stage_names[]{
    "\x8c\xb6\x96\xec\x81\x40\x81\x60\x20\x50\x68\x61\x6e\x74\x6f\x6d\x20\x4c\x61\x6e\x64\x20",
    "\x8c\xb6\x96\xe9\x81\x40\x81\x60\x20\x50\x68\x61\x6e\x74\x6f\x6d\x20\x4e\x69\x67\x68\x74",
    "\x8c\xcd\x8a\x89\x81\x40\x81\x60\x20\x4c\x61\x6b\x65\x20\x6f\x66\x20\x42\x6c\x6f\x6f\x64",
    "\x96\xbb\x97\x48\x81\x40\x81\x60\x20\x44\x61\x72\x6b\x6e\x65\x73\x73\x20",
    "\x96\xb2\x8c\xb6\x81\x40\x81\x60\x20\x44\x72\x65\x61\x6d\x20\x6f\x66\x20\x46\x72\x61\x69\x6c\x20\x47\x69\x72\x6c",
    "\x8c\xb6\x91\x7a\x81\x40\x81\x60\x20\x50\x68\x61\x6e\x74\x61\x73\x6d\x61\x67\x6f\x72\x69\x61\x20",
    "\x92\xc7\x8c\x82\x81\x40\x81\x60\x20\x52\x61\x73\x70\x62\x65\x72\x72\x79\x20\x54\x72\x61\x70\x20",
    "\x82\xb7\x82\xce\x82\xe7\x82\xb5\x82\xa2\x8c\x4e\x82\xc9\x90\xc3\x82\xa9\x82\xc8\x9d\xf7\x82\xe8\x82\xf0\x81\x40\x81\x60\x20\x50\x75\x63\x6b\x69\x73\x68\x20\x41\x6e\x67\x65\x6c",
};
constexpr std::string_view bgm_names[]{
    "\x57\x69\x74\x63\x68\x69\x6e\x67\x20\x44\x72\x65\x61\x6d",
    "\x53\x65\x6c\x65\x6e\x65\x27\x73\x20\x6c\x69\x67\x68\x74",
    "\x91\x95\x8f\xfc\x90\xed\x81\x40\x81\x60\x20\x44\x65\x63\x6f\x72\x61\x74\x69\x6f\x6e\x20\x42\x61\x74\x74\x6c\x65",
    "\x42\x72\x65\x61\x6b\x20\x74\x68\x65\x20\x53\x61\x62\x62\x61\x74\x68",
    "\x8d\x67\x8b\xbf\x8b\xc8\x81\x40\x81\x60\x20\x53\x63\x61\x72\x6c\x65\x74\x20\x50\x68\x6f\x6e\x65\x6d\x65",
    "\x42\x41\x44\x20\x41\x70\x70\x6c\x65\x21\x21",
    "\x97\xec\x90\xed\x81\x40\x81\x60\x20\x50\x65\x72\x64\x69\x74\x69\x6f\x6e\x20\x63\x72\x69\x73\x69\x73\x20",
    "\x83\x41\x83\x8a\x83\x58\x83\x7d\x83\x47\x83\x58\x83\x65\x83\x89",
    "\x90\xaf\x82\xcc\x8a\xed\x81\x40\x81\x60\x20\x43\x61\x73\x6b\x65\x74\x20\x6f\x66\x20\x53\x74\x61\x72\x20",
    "\x4c\x6f\x74\x75\x73\x20\x4c\x6f\x76\x65",
    "\x96\xb0\x82\xea\x82\xe9\x8b\xb0\x95\x7c\x81\x40\x81\x60\x20\x53\x6c\x65\x65\x70\x69\x6e\x67\x20\x54\x65\x72\x72\x6f\x72",
    "\x44\x72\x65\x61\x6d\x20\x4c\x61\x6e\x64",
    "\x97\x48\x96\xb2\x81\x40\x81\x60\x20\x49\x6e\x61\x6e\x69\x6d\x61\x74\x65\x20\x44\x72\x65\x61\x6d\x20",
    "\x8b\xd6\x82\xb6\x82\xb4\x82\xe9\x82\xf0\x82\xa6\x82\xc8\x82\xa2\x97\x56\x8b\x59\x20",
    "\x83\x81\x83\x43\x83\x68\x8c\xb6\x91\x7a\x81\x40\x81\x60\x20\x49\x63\x65\x6d\x69\x6c\x6b\x20\x4d\x61\x67\x69\x63\x20",
    "\x82\xa9\x82\xed\x82\xa2\x82\xa2\x88\xab\x96\x82\x81\x40\x81\x60\x20\x49\x6e\x6e\x6f\x63\x65\x6e\x63\x65",
    "\x8f\xad\x8f\x97\xe3\x59\x91\x7a\x8b\xc8\x81\x40\x81\x60\x20\x43\x61\x70\x72\x69\x63\x63\x69\x6f\x20",
};
}

std::string_view stage_name(unsigned id) {return stage_names[id<8 ? id : throw std::out_of_range("stage title ID")];}
std::string_view bgm_name(unsigned id) {return bgm_names[id<17 ? id : throw std::out_of_range("BGM title ID")];}

void request_boss(Snapshot& s,transition::Callback& callback,std::uint8_t stage,std::uint8_t character) {
    s.bgm_id=std::uint8_t(stage*2u+2u);
    if(stage==3 && character)s.bgm_id=16;
    callback=transition::Callback::boss_titles;
}
std::vector<Draw> update(Snapshot& s,transition::Callback& callback,registration::TextPlane& text,
    std::uint8_t stage,std::uint8_t character,std::int16_t scroll,bool scrolling) {
    std::vector<Draw> draws;
    const bool boss=callback==transition::Callback::boss_titles;
    if(!boss && callback!=transition::Callback::titles)return draws;
    auto& frame=boss ? s.boss_frame : s.frame;
    const auto wipe=[&] {
        for(int row=1;row<24;++row)for(int left=4;left<52;++left)text.put_character(left,row,32,0xe1);
    };
    const auto dissolve=[&](int left,int y,int length,unsigned color) {
        const int right=(left-1+length)*8;
        if(scrolling)y+=scroll;
        if(y<0)y+=400;else if(y>=400)y-=400;
        for(int x=(left-1)*8;x<right;x+=16)
            draws.push_back({std::uint16_t(x),std::uint16_t(y),s.sprite,std::uint8_t(color)});
    };
    const auto put_bgm=[&](int length) {
        text.put(48-length,23,3,0xc1);
        text.put_sjis(51-length,23,std::string(bgm_name(s.bgm_id)),0xe1);
    };
    const auto draw=[&] {
        const int length=boss ? s.boss_length : s.bgm_length;
        if(!boss)dissolve(stage>=5 ? 17 : 21,168,stage>=5 ? 22 : 14,11);
        dissolve(48-length,360,2,11);
        dissolve(51-length,360,length,15);
        if(!boss)dissolve(28-s.stage_length/2,200,s.stage_length,15);
    };
    if(frame>=192) {
        if(frame==192) {wipe();s.sprite=0;}
        else if(!(frame&1u))++s.sprite;
        if(s.sprite>=16) {
            if(frame&1u) {
                callback=transition::Callback::none;frame=0;
                if(!boss)s.sprite=0;
                return draws;
            }
        } else draw();
    } else {
        if(!frame) {
            s.sprite=16;
            if(boss)s.boss_length=std::int16_t(bgm_name(s.bgm_id).size());
            else {
                s.stage_id=std::uint8_t(stage+1u);s.bgm_id=std::uint8_t(stage*2u+1u);
                if(!stage && !character)s.stage_id=s.bgm_id=0;
                s.stage_length=std::int16_t(stage_name(s.stage_id).size());
                s.bgm_length=std::int16_t(bgm_name(s.bgm_id).size());
            }
        }
        if(s.sprite>=16) {
            if(s.sprite==22) {
                if(!boss) {
                    std::string label;
                    if(stage==5)label="\xaf\xb2\xb7\xaa\xb5\x02\xbc\xbd\xaa\xb0\xae";
                    else if(stage==6)label="\xae\xc1\xbd\xbb\xaa\x02\xbc\xbd\xaa\xb0\xae";
                    else {label="\xbc\xbd\xaa\xb0\xae\x02";label+=char(0xa1+stage);}
                    text.put_string(stage>=5 ? 17 : 21,11,label,0xc1);
                    text.put_sjis(28-s.stage_length/2,13,std::string(stage_name(s.stage_id)),0xe1);
                }
                put_bgm(boss ? s.boss_length : s.bgm_length);
            }
            draw();
            if(frame && !(frame&3u) && ++s.sprite>=24)s.sprite=0;
        }
    }
    ++frame;return draws;
}
Graphics::Graphics(const score_file::Bytes& out,const score_file::Bytes& in) {
    if(out.size()!=2048 || in.size()!=2048)throw std::invalid_argument("TXT.BB/TXT2.BB extent");
    std::copy(out.begin(),out.end(),masks_.begin());
    // MAIN0AAF:6A61 reads only BB_SIZE/2 bytes from the second file.
    std::copy_n(in.begin(),1024,masks_.begin()+2048);
}
void Graphics::raster(const std::vector<Draw>& draws,unsigned line,const Pixel& pixel) const {
    if(line>=400)throw std::out_of_range("title display line");
    for(const auto& d:draws) {
        if(d.sprite>=24 || d.top>=400 || d.left>=640)throw std::out_of_range("title dissolve request");
        for(unsigned y=0;y<32;++y)for(unsigned byte=0;byte<4;++byte) {
            const auto mask=masks_[unsigned(d.sprite)*128+y*4+byte];
            const auto top=(unsigned(d.top)+y+400-line)%400;
            for(unsigned bit=0;bit<8;++bit)if(mask&(0x80u>>bit)) {
                const unsigned x=(unsigned(d.left)&~7u)+byte*8+bit;
                if(x<640)pixel(x,top,d.color);
            }
        }
    }
}
} // namespace th04::portable::titles
