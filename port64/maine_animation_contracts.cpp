#include "maine_animation.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
using namespace th04::portable::maine;
int main(int argc,char** argv) {
    try {
#ifndef TH04_ANIMATION_LEGACY
        if(argc==1) {
            Animation zero({{RequestKind::delay,0},{RequestKind::text,99}});
            zero.advance(0);
            if(zero.status()!=AnimationStatus::stopped || zero.event_count()!=2)
                throw std::runtime_error("zero delay admitted a phantom refresh");
            for(int speed:{0,-1,32768,65536}) {
                Animation fade({{RequestKind::fade,0,1,speed},{RequestKind::text,99}});
                unsigned shows=0;fade.advance(0);fade.advance(0,{},[&](int){++shows;});
                if(fade.status()!=AnimationStatus::stopped || shows!=18 || fade.tone()!=100)
                    throw std::runtime_error("nonpositive signed WORD fade speed waited");
            }
            Animation negative({{RequestKind::delay,-1},{RequestKind::text,99}});
            negative.advance(0);
            for(unsigned i=0;i<65534;++i)negative.advance(0);
            if(negative.status()!=AnimationStatus::delay)throw std::runtime_error("negative WORD delay ended early");
            negative.advance(0);
            if(negative.status()!=AnimationStatus::stopped)throw std::runtime_error("negative WORD delay did not finish");
            std::cout<<"MAINE animation WORD and zero wait boundaries PASS\n";return 0;
        }
#endif
        if(argc!=3)throw std::invalid_argument("use --vectors or --boundary-vectors FILE");
        const bool palette=std::string(argv[1])=="--vectors";
        if(!palette && std::string(argv[1])!="--boundary-vectors")throw std::invalid_argument("vector mode");
        std::ifstream input(argv[2]);if(!input)throw std::runtime_error("vector file");
        std::string kind;int argument,direction;
        while(input>>kind>>argument>>direction) {
            if(kind!="D" && kind!="F")throw std::invalid_argument("operation");
            Animation animation({{RequestKind::tone,31},
                kind=="D" ? Request{RequestKind::delay,argument} : Request{RequestKind::fade,0,direction,argument},
                {RequestKind::text,99}});
            unsigned elapsed=0;
            do {
#ifndef TH04_ANIMATION_LEGACY
                if(palette)animation.advance(0,{},[&](int tone){std::cout<<"P "<<elapsed<<' '<<tone<<'\n';});
                else
#endif
                animation.advance(0);
                if(animation.status()==AnimationStatus::stopped)break;
                if(++elapsed>600000)throw std::runtime_error("animation does not terminate");
            } while(true);
            std::cout<<"N "<<elapsed<<' '<<animation.tone()<<' '<<animation.event_count()<<'\n';
        }
        if(!input.eof())throw std::invalid_argument("incomplete row");
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
