#include "op_setup.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
using namespace th04::portable;
int main(int argc,char** argv) {
    try {
        if(argc==5 && std::string(argv[1])=="--pixels") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            const auto read=[](const std::string& p) {std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("setup asset missing");return Bytes(std::istreambuf_iterator<char>(f),{});};
            op_setup::Assets assets;assets.graphics.font_bitmap=read(argv[4]);
            assets.graphics.pictures.emplace("MS.PI",decode_pi(read(std::string(argv[3])+"/MS.PI")));
            assets.windows=read(std::string(argv[3])+"/MSWIN.BFT");
            std::ifstream input(argv[2]);unsigned effect,count;
            while(input>>effect>>count) {
                std::vector<std::array<std::uint16_t,2>> samples(count);
                for(auto& sample:samples) {unsigned a,b;if(!(input>>a>>b) || a>65535 || b>65535)throw std::runtime_error("setup pixel input");sample={std::uint16_t(a),std::uint16_t(b)};}
                op_setup::Renderer renderer(assets);op_setup::Scene scene([&](const op_setup::Event& e){renderer.apply(e);},effect);
                const auto snapshot=[&] {
                    const auto& canvas=renderer.canvas();
                    for(unsigned page=0;page<2;++page)std::cout.write(reinterpret_cast<const char*>(canvas.page(page).data()),256000);
                    std::cout.write(reinterpret_cast<const char*>(canvas.palette().data()),48);
                    const auto rgb=renderer.rgb(scene.tone());std::cout.write(reinterpret_cast<const char*>(rgb.data()),std::streamsize(rgb.size()));
                };
                snapshot();for(unsigned tick=1;tick<count && !scene.finished();++tick) {scene.advance(samples[tick][0],samples[tick][1]);snapshot();}
                if(!scene.finished())throw std::runtime_error("setup pixel input did not complete");
            }
            if(!std::cout)throw std::runtime_error("setup pixel stream failed");return 0;
        }
        if(argc==3 && std::string(argv[1])=="--replay") {
            std::ifstream input(argv[2]);if(!input)throw std::runtime_error("setup fixture missing");
            unsigned effect,count;
            while(input>>effect>>count) {
                std::vector<std::array<std::uint16_t,2>> samples(count);
                for(auto& sample:samples) {unsigned a,b;if(!(input>>a>>b) || a>65535 || b>65535)throw std::runtime_error("setup input pair");sample={std::uint16_t(a),std::uint16_t(b)};}
                op_setup::Scene scene([](const op_setup::Event& e) {
                    std::cout<<op_setup::kind_name(e.kind)<<' '<<e.tick<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' ';
                    if(e.data.empty())std::cout<<'-';else {const char* h="0123456789abcdef";for(auto v:e.data)std::cout<<h[v>>4]<<h[v&15];}
                    std::cout<<'\n';
                },effect);
                for(unsigned tick=1;tick<count && !scene.finished();++tick)scene.advance(samples[tick][0],samples[tick][1]);
                if(!scene.finished())throw std::runtime_error("setup fixture did not finish");
                std::cout<<"END "<<scene.ticks()<<' '<<scene.tone()<<' '<<scene.bgm()<<' '<<scene.se()<<' '<<scene.window_width()<<' '<<scene.window_height()<<'\n';
            }
            return 0;
        }
        if(argc!=1)throw std::runtime_error("setup contracts CLI");
        op_setup::Scene scene;
        for(unsigned i=0;i<11000;++i)scene.advance(0);
        if(scene.finished() || !scene.awaiting_input() || scene.submenu()!=0 || scene.selected()!=2)
            throw std::runtime_error("setup release/indefinite press wait");
        // Esc remains in setup; confirmation plus an arrow accepts the default.
        scene.advance(0x1000);scene.advance(0);scene.advance(0);scene.advance(0);
        if(scene.selected()!=2 || scene.finished())throw std::runtime_error("setup Esc exits");
        for(unsigned i=0;i<4;++i)scene.advance(0);
        scene.advance(0x2021);scene.advance(0);
        for(unsigned i=0;i<60;++i)scene.advance(0);
        if(scene.submenu()!=1 || scene.bgm()!=2 || !scene.awaiting_input())throw std::runtime_error("setup confirm/arrow priority");
        scene.advance(0x20);scene.advance(0);
        for(unsigned i=0;i<60 && !scene.finished();++i)scene.advance(0);
        if(!scene.finished() || scene.se()!=1 || scene.tone()!=0)throw std::runtime_error("setup completion");
        std::cout<<"setup contracts PASS\n";return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
