#include "cutscene_scene.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace c=th04::portable::cutscene;
c::Bytes font() {
    c::Bytes bitmap(62+524288,255);
    std::fill_n(bitmap.begin(),62,0);
    const auto word=[&](unsigned at,unsigned n){bitmap[at]=std::uint8_t(n);bitmap[at+1]=std::uint8_t(n>>8);};
    word(0,0x4d42);word(10,62);word(14,40);word(18,2048);word(22,2048);word(26,1);word(28,1);
    return bitmap;
}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            std::ifstream in(argv[2]);if(!in)throw std::runtime_error("font vectors missing");
            int left,top;unsigned weight,color,seed;std::string hex;
            c::Assets assets;assets.font_bitmap=font();
            // Deterministic nonempty CGROM rows. The Oracle receives this
            // exact bitmap as an input adapter, never a native draw result.
            for(unsigned y=0;y<2048;++y)for(unsigned x=0;x<256;++x)
                assets.font_bitmap[62+(2047-y)*256+x]=std::uint8_t((x*37+y*53+19)&255);
            while(in>>left) {
                if(!(in>>top>>weight>>color>>seed>>hex) || weight>7 || hex.size()%2)
                    throw std::invalid_argument("font vector fields");
                std::string text;
                for(unsigned at=0;at<hex.size();at+=2)text.push_back(char(std::stoul(hex.substr(at,2),nullptr,16)));
                std::array<c::Bytes,2> pages;
                for(auto& page:pages) {
                    page.resize(640*400);
                    for(unsigned at=0;at<page.size();++at)page[at]=std::uint8_t((at*73+seed)&15);
                }
                c::Canvas canvas(assets,std::move(pages));canvas.put_text(left,top,text,color,weight);
                const auto& page=canvas.page(0);std::cout.write(reinterpret_cast<const char*>(page.data()),page.size());
            }
            if(!in.eof() || !std::cout)throw std::runtime_error("font vector stream failed");
            return 0;
        }
        if(argc!=1)throw std::invalid_argument("font address contracts CLI");
        c::Assets assets;assets.font_bitmap=font();
        std::fill(assets.font_bitmap.begin()+62,assets.font_bitmap.end(),0);
        c::Canvas alias(assets),zero(assets);
        alias.put_text(640,0,"AB",15,0);zero.put_text(0,1,"AB",15,0);
        if(alias.page(0)!=zero.page(0))throw std::runtime_error("font right-edge flat address");
        c::Canvas high_y(assets),low_y(assets);
        high_y.put_text(0,1024,"AB",15,0);low_y.put_text(0,0,"AB",15,0);
        if(high_y.page(0)!=low_y.page(0))throw std::runtime_error("font SHL truncation");
        c::Canvas joined(assets);joined.put_text(-8,0,"AB",15,0);
        if(joined.page(0)[8192*8]!=15 || joined.page(0)[0]!=0)
            throw std::runtime_error("font string DI continuity");
        std::cout<<"font address contracts PASS\n";return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
