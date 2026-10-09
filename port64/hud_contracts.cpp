#include "hud.hpp"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
using namespace th04::portable;
namespace {
std::string hex(const std::string& text) {
    if(text.empty())return "-";
    std::ostringstream out;out<<std::hex<<std::setfill('0');
    for(unsigned char c:text)out<<std::setw(2)<<unsigned(c);return out.str();
}
registration::TextPlane initial_plane() {
    score_file::Bytes raw(8000);
    for(unsigned i=0;i<2000;++i) {
        const unsigned attr=(i*37+17)&65535;raw[i*2]=std::uint8_t(i*31&127);
        raw[4000+i*2]=std::uint8_t(attr);raw[4000+i*2+1]=std::uint8_t(attr>>8);
    }
    return registration::TextPlane(raw);
}
hud::Requests execute(char op,hud::Values& s,std::int16_t& previous,const int* v) {
    switch(op) {
    case 'L':return hud::lives(s.lives);
    case 'B':return hud::bombs(s.bombs);
    case 'P':return hud::points(s.points);
    case 'D':return hud::dream(s.dream);
    case 'G':return hud::graze(s.graze);
    case 'W':return hud::power(s.power,s.shot_level);
    case 'V':return hud::bar(std::uint16_t(v[12]),std::int16_t(v[13]),std::uint16_t(v[14]));
    case 'H':return hud::hp(std::int16_t(v[13]));
    case 'U':case 'R':return hud::hp_update(previous,std::int16_t(v[10]),std::int16_t(v[11]));
    case 'I':return hud::initialize(s);
    default:throw std::runtime_error("unknown HUD vector");
    }
}
}
int main(int argc,char** argv) {
    try {
        if((argc==3 || argc==5) && (std::string(argv[1])=="--vectors" || std::string(argv[1])=="--tram" || std::string(argv[1])=="--rgb" || std::string(argv[1])=="--argb")) {
            const bool argb=std::string(argv[1])=="--argb";
            const bool pixels=std::string(argv[1])=="--rgb" || argb,binary=std::string(argv[1])!="--vectors";
            if(pixels && argc!=5)throw std::runtime_error("HUD RGB requires gaiji and font inputs");
#ifdef _WIN32
            if(binary && _setmode(_fileno(stdout),_O_BINARY)==-1)throw std::runtime_error("cannot set HUD binary output");
#endif
            score_file::Bytes gaiji;std::unique_ptr<dialog::Font> font;
            if(pixels) {
                const auto read=[](const char* path) {
                    std::ifstream input(path,std::ios::binary);if(!input)throw std::runtime_error("cannot read HUD graphics input");
                    return score_file::Bytes(std::istreambuf_iterator<char>(input),{});
                };
                gaiji=read(argv[3]);font=std::make_unique<dialog::Font>(read(argv[4]));
            }
            std::ifstream file(argv[2]);if(!file)throw std::runtime_error("cannot open HUD vectors");
            std::string line;std::int16_t retained_previous=0;
            while(std::getline(file,line)) {
                std::istringstream in(line);char op;int v[31]{};in>>op;
                for(auto& value:v)if(!(in>>value))throw std::runtime_error("truncated HUD vector");
                hud::Values s;s.lives=std::uint8_t(v[0]);s.bombs=std::uint8_t(v[1]);
                s.character=std::uint8_t(v[2]);s.rank=std::uint8_t(v[3]);s.points=std::uint8_t(v[4]);
                s.dream=std::uint16_t(v[5]);s.graze=std::uint16_t(v[6]);s.power=std::uint8_t(v[7]);s.shot_level=std::uint8_t(v[8]);
                auto previous=op=='R' ? retained_previous : std::int16_t(v[9]);
                for(unsigned i=0;i<8;++i) {s.score.digits[i]=std::uint8_t(v[15+i]);s.score.hiscore[i]=std::uint8_t(v[23+i]);s.score.hud[i]=std::uint8_t(17+i*19);}
                const auto requests=execute(op,s,previous,v);retained_previous=previous;
                auto plane=initial_plane();hud::apply(plane,requests);
                if(binary) {const auto raw=plane.bytes();std::cout.write(reinterpret_cast<const char*>(raw.data()),std::streamsize(raw.size()));}
                else {
                    std::cout<<"S "<<previous;for(auto x:s.score.hud)std::cout<<' '<<+x;
                    for(const auto& r:requests)std::cout<<'|'<<int(r.kind)<<' '<<r.column<<' '<<r.row<<' '<<r.attribute<<' '<<+r.glyph<<' '<<hex(r.text);
                    std::cout<<'\n';
                }
                if(pixels) {
                    score_file::Bytes rgb(640*400*3);
                    for(unsigned i=0;i<rgb.size();++i)rgb[i]=std::uint8_t((i/3)*17+(i%3)*73);
                    if(argb) {
                        std::vector<std::uint32_t> frame(640*400);
                        for(unsigned i=0;i<frame.size();++i)frame[i]=0xff000000u | (std::uint32_t(rgb[i*3])<<16) | (std::uint32_t(rgb[i*3+1])<<8) | rgb[i*3+2];
                        plane.overlay(frame,gaiji,*font);
                        for(unsigned i=0;i<frame.size();++i) {
                            rgb[i*3]=std::uint8_t(frame[i]>>16);rgb[i*3+1]=std::uint8_t(frame[i]>>8);rgb[i*3+2]=std::uint8_t(frame[i]);
                            if((frame[i]>>24)!=255)throw std::runtime_error("HUD ARGB overlay changed opaque alpha");
                        }
                    } else plane.overlay(rgb,gaiji,*font);
                    std::cout.write(reinterpret_cast<const char*>(rgb.data()),std::streamsize(rgb.size()));
                }
            }
            return 0;
        }
        // Repainting/initial HUD ownership must not advance the HP animator.
        std::int16_t previous=0;
        for(int i=1;i<=128;++i) {hud::hp_update(previous,100,100);if(previous!=i)throw std::runtime_error("HP rise ownership changed");}
        hud::Values values;hud::initialize(values);
        if(previous!=128)throw std::runtime_error("hud_put reset retained HP");
        hud::hp_update(previous,0,100);if(previous)throw std::runtime_error("HP decrease must be immediate");
        for(const auto& r:hud::lives(0))if(r.glyph!=2)throw std::runtime_error("zero lives displayed an icon");
        if(std::uint8_t(hud::bar(22,0,0x41).front().text[0])!=0x2f)throw std::runtime_error("zero power bar lost original partial glyph");
        std::cout<<"hud=FIXED_WIDTH HP=RETAINED_PREVIOUS TRAM=GAIJI_AND_SJIS pointer_bits="<<sizeof(void*)*8<<'\n';return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
