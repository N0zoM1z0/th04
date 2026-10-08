#include "player_render.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace p=th04::portable::player;
namespace m=th04::portable::motion;
namespace {
void require(bool ok,const char* why) {if(!ok)throw std::runtime_error(why);}
std::vector<std::uint8_t> read(const std::filesystem::path& path) {
    std::ifstream f(path,std::ios::binary);require(bool(f),"player sprite missing");
    return {std::istreambuf_iterator<char>(f),{}};
}
}
bool player_render_cli(int argc,char** argv) {
    if(argc!=3 || (std::string(argv[1])!="--player-render-vectors" &&
                  std::string(argv[1])!="--player-render-pixels"))return false;
    const bool pixels=std::string(argv[1])=="--player-render-pixels";
#ifdef _WIN32
    if(pixels)_setmode(_fileno(stdout),_O_BINARY);
#endif
    std::ifstream input(argv[2]);require(bool(input),"player render fixture missing");
    std::vector<th04::portable::sprite::Sheet> sheets;
    if(pixels) {
        const auto directory=std::filesystem::path(argv[2]).parent_path();
        for(const auto* name:{"MIKO.BFT","MARI.BFT","MIKOD.BFT","MIKO16.BFT"})sheets.emplace_back(read(directory/name));
    }
    int character,x,y,vx,miss,inv,radius,angle,ox,oy,level,pattern,mod4,scroll,line,seed;
    while(input>>character) {
        require(bool(input>>x>>y>>vx>>miss>>inv>>radius>>angle>>ox>>oy>>level>>pattern>>mod4>>scroll>>line>>seed),"short player render fixture");
        require(character==0 || character==1,"invalid player render character");
        p::LifeState life;life.miss_time=std::uint8_t(miss);life.invincibility=std::uint8_t(inv);
        life.explosion_radius=std::uint16_t(radius);life.explosion_angle=std::uint8_t(angle);
        life.options={m::Subpixel(ox),m::Subpixel(oy)};life.scroll_active=std::uint8_t(scroll);
        m::Motion position;position.current={m::Subpixel(x),m::Subpixel(y)};position.velocity.x=m::Subpixel(vx);
        const auto draws=p::render_requests(life,position,std::uint8_t(level),std::uint16_t(pattern),std::uint8_t(mod4),std::uint16_t(line));
        if(pixels) {
            std::vector<std::uint8_t> screen(640*400);
            for(unsigned i=0;i<screen.size();++i)screen[i]=std::uint8_t((i*73+seed)&15);
            p::render_pixels(draws,sheets[character],sheets[2],sheets[3],screen);
            std::cout.write(reinterpret_cast<const char*>(screen.data()),screen.size());
        } else {
            std::cout<<"D "<<draws.size();
            for(const auto& draw:draws)std::cout<<' '<<int(draw.kind)<<' '<<draw.left<<' '<<draw.top<<' '<<draw.pattern;
            std::cout<<'\n';
        }
    }
    return true;
}
void player_render_contracts() {
    p::LifeState life;m::Motion position;position.current={3072,5120};
    life.options={3072,5120};life.miss_time=1;
    require(p::render_requests(life,position,4,38,0,399).empty(),"death frame1 drew a player");
    life.miss_time=2;life.explosion_radius=257;life.explosion_angle=37;
    require(p::render_requests(life,position,4,38,0,399).size()==8,"death rings missing");
    life.miss_time=0;life.invincibility=192;
    const auto draws=p::render_requests(life,position,2,38,0,399);
    require(draws.size()==3 && draws[0].kind==p::RenderKind::white && draws[0].top==311 &&
            draws[1].left==192 && draws[2].left==240,"invincible player/options differ");
    require(p::render_requests(life,position,2,38,1,399)[0].kind==p::RenderKind::sprite,"wrong blink phase");
    life.scroll_active=0;require(p::render_requests(life,position,0,38,0,399)[0].top==312,"disabled scroll still added a line");
    std::cout<<"TH04 player rendering: PASS death_rings=8 blank_frame=1 retained_phase=1 muted=1\n";
}
