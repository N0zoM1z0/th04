#include "player_bomb.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace b=th04::portable::bomb;
namespace p=th04::portable::player;
namespace m=th04::portable::motion;
namespace c=th04::portable::circle;
namespace r=th04::portable::randring;
using Character=th04::portable::application::Playchar;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool ok,const char* why) {if(!ok)throw std::runtime_error(why);}
Bytes read(const std::filesystem::path& path) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"Bomb asset missing");
    return {std::istreambuf_iterator<char>(in),{}};
}
Bytes unhex(const std::string& text,std::size_t size) {
    require(text.size()==size*2,"Bomb wire extent differs");Bytes result;
    for(std::size_t i=0;i<text.size();i+=2)result.push_back(std::uint8_t(std::stoul(text.substr(i,2),nullptr,16)));
    return result;
}
void hex(std::ostream& out,const Bytes& data) {
    const char* digits="0123456789abcdef";
    for(auto x:data)out<<digits[x>>4]<<digits[x&15];
}
int word(const Bytes& bytes,unsigned at) {return m::wrap(bytes[at]|unsigned(bytes[at+1])<<8);}
void word(Bytes& bytes,int value) {bytes.push_back(std::uint8_t(value));bytes.push_back(std::uint8_t(unsigned(value)>>8));}
struct Fixture {
    unsigned character=0,steps=0,cursor=0;
    p::LifeState life;b::Snapshot stars;c::Snapshot circles;
    std::uint16_t stage=0;std::uint8_t mod4=0;
};
Fixture parse(std::istream& in) {
    Fixture f;int frame,tone,changed,color,stage,mod4;std::string stars,circles;
    require(bool(in>>f.character>>f.steps>>frame>>stage>>mod4>>f.cursor>>tone>>changed>>color>>stars>>circles),"short Bomb fixture");
    require(f.character<2 && f.steps && f.steps<=256 && f.cursor<256,"invalid Bomb fixture");
    f.life.bomb_frame=std::uint8_t(frame);f.stage=std::uint16_t(stage);f.mod4=std::uint8_t(mod4);
    f.life.palette_tone=std::uint16_t(tone);f.life.palette_changed=std::uint8_t(changed);
    f.life.circle_color=std::uint8_t(color);f.circles.color=f.life.circle_color;
    const auto a=unhex(stars,288),d=unhex(circles,160);
    for(unsigned i=0;i<48;++i)f.stars.stars[i]={{m::Subpixel(word(a,i*6)),m::Subpixel(word(a,i*6+2))},a[i*6+4],a[i*6+5]};
    for(unsigned i=0;i<16;++i)f.circles.entities[i]={d[i*10],d[i*10+1],{m::Subpixel(word(d,i*10+2)),m::Subpixel(word(d,i*10+4))},m::Subpixel(word(d,i*10+6)),m::Subpixel(word(d,i*10+8))};
    return f;
}
void print(const Fixture& f,const b::Effect& effect,const r::SharedRandomRing& random,const c::System& circles) {
    Bytes a,d;
    for(const auto& star:effect.snapshot().stars) {word(a,star.center.x);word(a,star.center.y);a.push_back(star.angle);a.push_back(star.speed);}
    for(const auto& entity:circles.snapshot().entities) {d.push_back(entity.flag);d.push_back(entity.age);word(d,entity.center.x);word(d,entity.center.y);word(d,entity.radius);word(d,entity.delta);}
    std::cout<<"STATE "<<f.life.palette_tone<<' '<<unsigned(f.life.palette_changed)<<' '<<unsigned(f.life.circle_color)<<' '<<random.cursor()<<' ';
    hex(std::cout,a);std::cout<<' ';hex(std::cout,d);std::cout<<' '<<effect.draws().size();
    for(const auto& draw:effect.draws())std::cout<<' '<<int(draw.kind)<<' '<<draw.position.x<<' '<<draw.position.y<<' '<<draw.value;
    std::cout<<'\n';
}
Bytes screen(unsigned seed) {
    Bytes pixels(640*400);for(unsigned i=0;i<pixels.size();++i)pixels[i]=std::uint8_t((i*73+seed)&15);return pixels;
}
}
bool bomb_cli(int argc,char** argv) {
    if(argc!=3 || (std::string(argv[1])!="--bomb-vectors" && std::string(argv[1])!="--bomb-pixels"))return false;
    const bool pixels=std::string(argv[1])=="--bomb-pixels";
#ifdef _WIN32
    if(pixels)_setmode(_fileno(stdout),_O_BINARY);
#endif
    std::ifstream input(argv[2]);require(bool(input),"Bomb fixture file missing");
    std::array<std::unique_ptr<b::Graphics>,2> graphics;
    if(pixels) {
        const auto directory=std::filesystem::path(argv[2]).parent_path();const auto sprites=read(directory/"MIKO16.BFT");
        for(unsigned i=0;i<2;++i)graphics[i]=std::make_unique<b::Graphics>(read(directory/("BB"+std::to_string(i)+".BB")),read(directory/("BB"+std::to_string(i)+".CDG")),sprites);
    }
    char op;
    while(input>>op) {
        if(op=='T') {
            unsigned character,cel,line,seed;require(pixels && bool(input>>character>>cel>>line>>seed) && character<2,"invalid Bomb tile fixture");
            auto buffer=screen(seed);graphics[character]->tiles(cel,line,character ? 2 : 15,buffer);
            std::cout.write(reinterpret_cast<const char*>(buffer.data()),buffer.size());continue;
        }
        auto f=parse(input);unsigned seed=0;if(pixels)require(bool(input>>seed),"missing Bomb screen seed");
        require(op=='F' || op=='S' || op=='L',"unknown Bomb operation");
        b::Effect effect(f.stars);c::System circles(f.circles);r::SharedRandomRing random;
        unsigned index=0;random.fill([&] {return std::uint8_t(index++*73+19);});
        for(unsigned i=0;i<f.cursor;++i)random.next16();
        auto buffer=screen(seed);
        for(unsigned step=0;step<f.steps;++step) {
            b::Context context{f.life,random,circles,f.stage,f.mod4};
            if(op=='S')effect.render_stars(Character(f.character),context);else effect.render(Character(f.character),context);
            if(pixels) {graphics[f.character]->apply(effect.draws(),buffer);std::cout.write(reinterpret_cast<const char*>(buffer.data()),buffer.size());}
            else print(f,effect,random,circles);
            if(op=='L') {++f.life.bomb_frame;++f.stage;f.mod4=std::uint8_t(f.stage%4);}
        }
    }
    return true;
}
void bomb_contracts() {
    p::LifeState life;life.bomb_frame=48;c::System circles;r::SharedRandomRing random;
    unsigned index=0;random.fill([&] {return std::uint8_t(index++*73+19);});
    b::Effect effect;b::Context context{life,random,circles,123,0};
    effect.render(Character::reimu,context);
    require(effect.draws().size()==50 && life.palette_tone==196 && life.circle_color==9,"Bomb initialization differs");
    for(const auto& star:effect.snapshot().stars)require(star.center.x<2048 || star.center.x>4096,"Reimu exclusion band differs");
    const auto cursor=random.cursor();effect.draws();effect.draws();require(random.cursor()==cursor,"Bomb repaint consumed RNG");
    life.bomb_frame=84;effect.render(Character::reimu,context);
    require(effect.draws().size()==53 && circles.snapshot().entities[0].radius==4,"Bomb circle cadence differs");
    life.bomb_frame=120;context.stage_frame_mod4=1;effect.render(Character::marisa,context);
    require(effect.draws().size()==50,"retained frame-mod4 ignored");
    std::cout<<"TH04 Bomb character: PASS stars=48 fill_bands=94 cached_repaint=1 muted=1\n";
}
