#include "hud_titles.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
using namespace th04::portable;
int main(int argc,char** argv) {
    if(argc!=3 || std::string(argv[1])!="--vectors")return 2;
    std::ifstream source(argv[2],std::ios::binary);
    score_file::Bytes bb{std::istreambuf_iterator<char>(source),{}};
    if(bb.size()!=3072)throw std::invalid_argument("complete title masks required");
    score_file::Bytes out(bb.begin(),bb.begin()+2048),in(bb.begin()+2048,bb.end());in.resize(2048);
    titles::Graphics graphics(out,in);titles::Snapshot s;registration::TextPlane text;
    transition::Callback callback=transition::Callback::titles;
    std::array<std::array<std::uint8_t,32768>,4> planes{};
    unsigned stage=0,character=0,bgm=0,scrolling=0,mode=0;int scroll=0;std::string op;
    while(std::cin>>op) {
        if(op=="S") {
            std::cin>>stage>>character>>bgm>>scroll>>scrolling>>mode;s={};s.bgm_id=std::uint8_t(bgm);
            callback=mode ? transition::Callback::boss_titles : transition::Callback::titles;
            text={};score_file::Bytes seed(16384);
            for(unsigned i=0;i<seed.size();++i)seed[i]=std::uint8_t(i);
            text.load_memory(0xa0000,seed);
            for(unsigned p=0;p<4;++p)for(unsigned i=0;i<32768;++i)planes[p][i]=std::uint8_t(p*31+i*17+i/80);
        } else if(op=="F") {
            unsigned frame,boss,sprite,stage_id,bgm_id;int sl,bl,bossl;
            std::cin>>frame>>boss>>sprite>>stage_id>>bgm_id>>sl>>bl>>bossl>>mode;
            s.frame=std::uint8_t(frame);s.boss_frame=std::uint8_t(boss);s.sprite=std::uint8_t(sprite);
            s.stage_id=std::uint8_t(stage_id);s.bgm_id=std::uint8_t(bgm_id);
            s.stage_length=std::int16_t(sl);s.bgm_length=std::int16_t(bl);s.boss_length=std::int16_t(bossl);
            callback=mode ? transition::Callback::boss_titles : transition::Callback::titles;
        } else if(op=="B")titles::request_boss(s,callback,std::uint8_t(stage),std::uint8_t(character));
        else if(op!="U")return 2;
        if(!std::cin)return 2;
        const auto draws=titles::update(s,callback,text,std::uint8_t(stage),std::uint8_t(character),std::int16_t(scroll),scrolling!=0);
        graphics.raster(draws,0,[&](unsigned x,unsigned y,std::uint8_t color) {
            const auto at=y*80+x/8;const auto mask=std::uint8_t(0x80u>>(x&7));
            for(unsigned p=0;p<4;++p)planes[p][at]=std::uint8_t((planes[p][at]&~mask)|((color&(1u<<p)) ? mask : 0));
        });
        const auto pointer=callback==transition::Callback::titles ? 0x6446 : callback==transition::Callback::boss_titles ? 0x66a5 : 0x11be;
        std::cout<<+s.frame<<' '<<+s.boss_frame<<' '<<+s.sprite<<' '<<+s.stage_id<<' '<<+s.bgm_id<<' '
            <<s.stage_length<<' '<<s.bgm_length<<' '<<s.boss_length<<' '<<pointer;
        for(const auto& d:draws)std::cout<<'|'<<d.left<<' '<<d.top<<' '<<+d.sprite<<' '<<+d.color;
        std::cout<<'\n';const auto tram=text.physical_bytes(0xa0000,16384);
        std::cout.write(reinterpret_cast<const char*>(tram.data()),tram.size());
        for(const auto& plane:planes)std::cout.write(reinterpret_cast<const char*>(plane.data()),plane.size());
    }
}
