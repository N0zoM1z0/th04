#include "maine_animation.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
using namespace th04::portable::maine;
unsigned run(unsigned index, int direction, int speed, bool trace) {
    Animation animation({{RequestKind::fade, 0, direction, speed}});
    if(trace)std::cout<<"CASE "<<index<<'\n';
    int previous=-1;
    for(unsigned tick=0;tick<3000000;++tick) {
        animation.advance(0);
        if(animation.tone()!=previous) {
            previous=animation.tone();
            if(trace)std::cout<<"TONE "<<tick<<' '<<previous<<'\n';
        }
        if(animation.status()==AnimationStatus::stopped) {
            if(animation.tone()!=(direction ? 100 : 0) || animation.event_count()!=1)
                throw std::runtime_error("palette final state");
            if(trace)std::cout<<"END "<<tick<<'\n';
            return tick;
        }
    }
    throw std::runtime_error("palette wait did not finish");
}
}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") {
            std::ifstream input(argv[2]);
            if(!input)throw std::runtime_error("palette vector input");
            int direction,speed;unsigned index=0;
            while(input>>direction>>speed) {
                if(direction!=0 && direction!=1)throw std::runtime_error("palette direction");
                run(index++,direction,speed,true);
            }
            if(!input.eof() || !std::cout)throw std::runtime_error("palette vector stream");
        } else if(argc==1) {
            for(int direction:{0,1})for(int speed:{0,1,2,4,16,32767,32768,65535,65536,131071,-1,-32768}) {
                const auto word=static_cast<std::uint16_t>(speed);
                const unsigned waits=word<0x8000u ? word : 0;
                if(run(0,direction,speed,false)!=1+17*waits)
                    throw std::runtime_error("palette signed WORD wait sequence");
            }
            std::cout<<"Palette animation contracts PASS\n";
        } else throw std::runtime_error("palette animation CLI");
        return 0;
    } catch(const std::exception& error) {
        std::cerr<<error.what()<<'\n';return 1;
    }
}
