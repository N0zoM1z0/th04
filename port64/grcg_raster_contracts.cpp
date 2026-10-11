#include "grcg_raster.hpp"
#include "yuuka5.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace g=th04::portable::grcg;
namespace m=th04::portable::motion;
void word(std::vector<std::uint8_t>& bytes,int n) {
    bytes.push_back(std::uint8_t(n));bytes.push_back(std::uint8_t(unsigned(n)>>8));
}
int main(int argc,char** argv) {
    try {
        if(argc==3) {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            std::ifstream in(argv[2]);if(!in)throw std::runtime_error("GRCG vectors missing");
            const std::string mode=argv[1];int left,right,y;
            while(in>>left) {
                if(!(in>>right>>y))throw std::invalid_argument("incomplete GRCG vector");
                std::vector<std::uint8_t> bytes;
                if(mode=="--requests") {
                    g::circlefill({m::wrap(left),m::wrap(right)},std::uint16_t(y),[&](const auto& r){
                        bytes.push_back(std::uint8_t(r.kind));word(bytes,r.left);word(bytes,r.right);word(bytes,r.y);
                    });
                    const auto count=std::uint32_t(bytes.size()/7);
                    for(unsigned i=0;i<4;++i)std::cout.put(char(count>>(8*i)));
                } else {
                    bytes.resize(32000);
                    const auto pixel=[&](m::Point p){bytes[unsigned(p.y)*80+unsigned(p.x)/8]|=std::uint8_t(128u>>(p.x&7));};
                    if(mode=="--hline") {
                        if(const auto span=g::stage_hline(m::wrap(left),m::wrap(right),m::wrap(y)))
                            for(int x=span->left;x<=span->right;++x)pixel({std::int16_t(x),span->y});
                    } else if(mode=="--disc") {
                        for(auto p:th04::portable::yuuka5::disc_pixels({m::wrap(left),m::wrap(right)},std::uint16_t(y)))pixel(p);
                    } else throw std::invalid_argument("GRCG contracts CLI");
                }
                std::cout.write(reinterpret_cast<const char*>(bytes.data()),std::streamsize(bytes.size()));
            }
            if(!in.eof() || !std::cout)throw std::runtime_error("GRCG vector stream failed");
            return 0;
        }
        if(argc!=1)throw std::invalid_argument("GRCG contracts CLI");
        const auto wrapped=g::stage_hline(-32768,0,16);
        if(!wrapped || wrapped->left!=32 || wrapped->right!=415)
            throw std::runtime_error("GRCG clip must subtract before sorting");
        if(g::stage_hline(-1,31,16) || g::stage_hline(32,415,384))
            throw std::runtime_error("GRCG horizontal rejection");
        for(auto radius:{513u,32768u,65535u}) {
            unsigned calls=0;
            g::circlefill({224,200},std::uint16_t(radius),[&](const auto&){++calls;});
            if(!calls || calls>262140)throw std::runtime_error("GRCG WORD circle termination");
            (void)th04::portable::yuuka5::disc_pixels({224,200},std::uint16_t(radius));
        }
        std::cout<<"GRCG contracts PASS\n";return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
