#include "playfield_shake.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable;
int main(int argc,char** argv) {
    try {
        if(argc==3) {
            std::ifstream input(argv[1]);std::ofstream output(argv[2]);
            int x,y,time,redraw;unsigned mod2,mod4;
            while(input>>x>>y>>time>>redraw>>mod2>>mod4) {
                playfield::Shake state{std::int16_t(x),std::int16_t(y),std::int16_t(time),std::int8_t(redraw)};
                const auto draw=playfield::update(state,std::uint8_t(mod2),std::uint8_t(mod4));
                output<<state.x<<' '<<state.y<<' '<<state.time<<' '<<int(state.redraw)<<' '
                    <<draw.x<<' '<<draw.y<<' '<<draw.invalidate<<'\n';
            }
            if(!input.eof() || !output)throw std::runtime_error("shake fixture stream failure");
            return 0;
        }
        playfield::Shake state;state.time=12;
        for(unsigned frame=0;frame<14;++frame) {
            const auto draw=playfield::update(state,std::uint8_t(frame&1),std::uint8_t(frame&3));
            if(state.x || state.y || state.time!=int(frame<12 ? 11-frame : 0) ||
               draw.invalidate!=(frame<13) || bool(draw.x)!=(frame<12))throw std::runtime_error("shake duration/cleanup");
        }
        // A complete labelled physical page proves scroll-wrap, retained edge
        // strips and immutability of every pixel outside the EGC rectangle.
        for(unsigned scroll:{0u,1u,34u,399u})for(int dx:{-2,0,2})for(int dy:{-2,0,2}) {
            std::vector<std::uint32_t> page(640*400);
            for(unsigned at=0;at<page.size();++at)page[at]=at;
            const auto original=page;playfield::move(page,scroll,{std::int16_t(dx),std::int16_t(dy),false});
            for(unsigned physical=0;physical<400;++physical)for(int x=0;x<640;++x) {
                const unsigned at=((physical+400-scroll)%400)*640+unsigned(x);
                int sx=x,sy=int(physical);
                if(x>=32 && x<416) {
                    if(sy-dy>=0 && sy-dy<400)sy-=dy;
                    if(sx-dx>=32 && sx-dx<416)sx-=dx;
                }
                const unsigned source=((unsigned(sy)+400-scroll)%400)*640+unsigned(sx);
                if(page[at]!=original[source])throw std::runtime_error("shake complete pixel invariant");
            }
        }
        std::cout<<"shake invariants pass\n";return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
