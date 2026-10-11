#include "cutscene_scene.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace c=th04::portable::cutscene;
namespace {
c::Assets assets(unsigned padding) {
    c::Assets result;
    result.font_bitmap.resize(62+524288,255);
    std::fill_n(result.font_bitmap.begin(),62,0);
    const auto word=[&](unsigned at,unsigned n){result.font_bitmap[at]=std::uint8_t(n);result.font_bitmap[at+1]=std::uint8_t(n>>8);};
    word(0,0x4d42);word(10,62);word(14,40);word(18,2048);word(22,2048);word(26,1);word(28,1);
    result.gaiji.resize(32+padding+8192,255);
    result.gaiji[28]=std::uint8_t(padding);result.gaiji[29]=std::uint8_t(padding>>8);
    for(unsigned glyph=0;glyph<256;++glyph)for(unsigned row=0;row<16;++row)for(unsigned half=0;half<2;++half)
        result.gaiji[32+padding+glyph*32+row*2+half]=std::uint8_t(glyph*17+row*29+half*113+7);
    return result;
}
std::string bytes(const std::string& hex) {
    if(hex=="-")return {};
    if(hex.size()%2)throw std::invalid_argument("gaiji vector hex");
    std::string result;
    for(unsigned at=0;at<hex.size();at+=2)result.push_back(char(std::stoul(hex.substr(at,2),nullptr,16)));
    return result;
}
}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            std::ifstream in(argv[2]);if(!in)throw std::invalid_argument("gaiji vectors missing");
            std::string mode,hex;int left,top,step;unsigned color,seed,padding;
            while(in>>mode) {
                if(!(in>>left>>top>>step>>color>>seed>>padding>>hex) || padding>65535)
                    throw std::invalid_argument("gaiji vector fields");
                auto input=assets(padding);std::array<c::Bytes,2> pages;
                for(auto& page:pages) {
                    page.resize(640*400);
                    for(unsigned at=0;at<page.size();++at)page[at]=std::uint8_t((at*73+seed)&15);
                }
                c::Canvas canvas(input,std::move(pages));const auto text=bytes(hex);
                if(mode=="putc" && text.size()==1)
                    canvas.apply({c::Kind::gaiji,left,top,static_cast<unsigned char>(text[0]),int(color)});
                else if(mode=="puts")canvas.put_gaiji(left,top,text,step,color);
                else throw std::invalid_argument("gaiji vector mode");
                const auto& page=canvas.page(0);std::cout.write(reinterpret_cast<const char*>(page.data()),page.size());
            }
            if(!in.eof() || !std::cout)throw std::runtime_error("gaiji vector stream failed");
            return 0;
        }
        if(argc!=1)throw std::invalid_argument("gaiji address contracts CLI");
        const auto input=assets(17);c::Canvas edge(input),row(input);
        edge.put_gaiji(640,0,std::string{char(1),char(2)},16,15);
        row.put_gaiji(0,1,std::string{char(1),char(2)},16,15);
        if(edge.page(0)!=row.page(0))throw std::runtime_error("gaiji right-edge address");
        c::Canvas wrapped(input),zero(input);
        wrapped.put_gaiji(0,4096,std::string(1,char(1)),16,15);
        zero.put_gaiji(0,0,std::string(1,char(1)),16,15);
        if(wrapped.page(0)!=zero.page(0))throw std::runtime_error("gaiji WORD row address");
        c::Canvas putc(input),puts(input);
        putc.apply({c::Kind::gaiji,83,31,0x80,5});puts.put_gaiji(83,31,std::string(1,char(0x80)),16,5);
        if(putc.page(0)!=puts.page(0))throw std::runtime_error("gaiji putc/puts shared consumer");
        std::cout<<"gaiji address contracts PASS\n";return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
