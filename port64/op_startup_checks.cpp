#include "op_startup.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <sstream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
using namespace th04::portable;
namespace {
void hex(std::ostream& out,const Bytes& bytes) {
    const char* h="0123456789abcdef";if(bytes.empty())out<<'-';else for(auto v:bytes)out<<h[v>>4]<<h[v&15];
}
Bytes read(const std::string& name) {std::ifstream f(name,std::ios::binary);if(!f)throw std::runtime_error("startup asset missing");return Bytes(std::istreambuf_iterator<char>(f),{});}
op_startup::Assets load(const std::string& dir) {
    op_startup::Assets a;a.logo=decode_pi(read(dir+"/ZUN00.PI"));a.menu=decode_pi(read(dir+"/OP1.PI"));
    for(unsigned i=0;i<6;++i)a.slides[i]=decode_pi(read(dir+"/OP"+std::to_string(5-i)+"B.PI"));
    constexpr unsigned order[]={2,4,1,3};for(unsigned i=0;i<4;++i)a.fireworks[i]=read(dir+"/ZUN0"+std::to_string(order[i])+".BFT");return a;
}
Bytes state(const op_startup::Scene& scene,const op_startup::Renderer& renderer) {
    Bytes result;const auto byte=[&](unsigned v){result.push_back(std::uint8_t(v));};
    const auto word=[&](int v){const auto bits=std::uint16_t(v);byte(bits);byte(bits>>8);};
    for(const auto& p:scene.pyros()) {byte(p.alive);byte(p.age);word(p.origin.x);word(p.origin.y);word(p.previous_distance);word(p.distance);word(p.speed);byte(p.angle);byte(p.pattern);}
    const auto rng=scene.random_state();for(unsigned i=0;i<4;++i)byte(rng>>(i*8));
    result.insert(result.end(),scene.palette().begin(),scene.palette().end());
    result.insert(result.end(),renderer.dac().begin(),renderer.dac().end());byte(renderer.accessed());byte(renderer.shown());return result;
}
void require(bool value,const char* what) {if(!value)throw std::runtime_error(what);}
}
int main(int argc,char** argv) {
    try {
        if(argc==4 && (std::string(argv[1])=="--trace" || std::string(argv[1])=="--frames")) {
            const bool frames=std::string(argv[1])=="--frames";
#ifdef _WIN32
            if(frames)_setmode(_fileno(stdout),_O_BINARY);
#endif
            const auto assets=load(argv[3]);std::ifstream input(argv[2]);require(bool(input),"startup fixture missing");
            unsigned logo,demo,count,index=0;std::uint32_t seed;int measure_at;std::string palette_hex;
            while(input>>logo>>demo>>seed>>measure_at>>palette_hex>>count) {
                require(logo<2 && demo<2 && count && count<10000,"startup fixture bounds");
                std::vector<std::uint16_t> keys(count);for(auto& key:keys){unsigned value;require(bool(input>>value) && value<65536,"startup key sample");key=std::uint16_t(value);}
                require(palette_hex.size()==96,"startup initial palette width");op_startup::Palette initial_palette{};
                for(unsigned i=0;i<48;++i){const auto digit=[](char c)->unsigned{if(c>='0' && c<='9')return unsigned(c-'0');if(c>='a' && c<='f')return unsigned(c-'a'+10);throw std::runtime_error("startup palette hex");};initial_palette[i]=std::uint8_t(digit(palette_hex[i*2])*16+digit(palette_hex[i*2+1]));}
                unsigned tick=0,waits=0,captured=0;std::vector<std::string> states;
                op_startup::Renderer renderer(assets);
                if(!frames)std::cout<<"CASE "<<index<<'\n';
                op_startup::Scene scene(assets,logo!=0,demo!=0,[&](const op_startup::Event& e) {
                    renderer.apply(e);if(e.kind==op_startup::Kind::wait)++waits;
                    if(!frames) {
                        std::cout<<op_startup::kind_name(e.kind)<<' '<<e.tick<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' ';hex(std::cout,e.data);std::cout<<'\n';
                        if(e.kind==op_startup::Kind::palette_show) {std::cout<<"DAC "<<e.tick<<' ';hex(std::cout,Bytes(renderer.dac().begin(),renderer.dac().end()));std::cout<<'\n';}
                    }
                },[&]()->std::optional<std::uint16_t>{if(measure_at<0)return std::nullopt;return std::uint16_t(int(tick)<measure_at ? 0 : 2);},seed,keys[0],initial_palette);
                const auto snapshot=[&] {
                    if(frames) {
                        for(unsigned p=0;p<2;++p)std::cout.write(reinterpret_cast<const char*>(renderer.page(p).data()),256000);
                        std::cout.write(reinterpret_cast<const char*>(scene.palette().data()),48);
                        std::cout.write(reinterpret_cast<const char*>(renderer.dac().data()),48);
                        const auto rgb=renderer.rgb();std::cout.write(reinterpret_cast<const char*>(rgb.data()),std::streamsize(rgb.size()));
                    }
                    if(captured!=waits || scene.finished()) {
                        captured=waits;std::ostringstream out;out<<"STATE "<<scene.ticks()<<' ';hex(out,state(scene,renderer));states.push_back(out.str());
                    }
                };
                snapshot();for(tick=1;tick<count && !scene.finished();++tick){scene.advance(keys[tick]);snapshot();}
                require(scene.finished(),"startup fixture did not finish");
                if(!frames) {for(const auto& row:states)std::cout<<row<<'\n';std::cout<<"END "<<scene.ticks()<<' '<<scene.tone()<<' '<<scene.random_state()<<'\n';}
                ++index;
            }
            require(input.eof() && index && bool(std::cout),"startup fixture/stream error");return 0;
        }
        require(argc==1,"startup contracts CLI");
        op_startup::Assets assets;
        unsigned complete=0,stop=0,songs=0;op_startup::Scene title(assets,false,false,[&](const auto& e){complete+=e.kind==op_startup::Kind::complete;stop+=e.kind==op_startup::Kind::command && e.a==0x100;songs+=e.kind==op_startup::Kind::song;});
        for(unsigned i=0;i<1000 && !title.finished();++i)title.advance(0xffff);
        require(title.finished() && title.ticks()==175 && complete==1 && stop==1 && songs==1,"title waits/no skip");
        unsigned measure=0;op_startup::Scene logo(assets,true,false,{},[&](){return std::optional<std::uint16_t>(std::uint16_t(measure));});
        for(unsigned i=0;i<30;++i)logo.advance(0xffff);
        require(logo.logo_frame()==0 && logo.random_state()==1,"logo real measure wait");
        measure=2;for(unsigned i=0;i<1000 && !logo.finished();++i)logo.advance(0xffff);
        require(logo.finished() && logo.ticks()==308 && logo.logo_frame()==50,"logo skip fade order");
        std::cout<<"startup contracts PASS\n";return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
