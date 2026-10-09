#include "op_music.hpp"
#include "random_lcg.hpp"
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>

using namespace th04::portable;
namespace music=op_music;
namespace {
void require(bool v,const char* s) {if(!v)throw std::runtime_error(s);}
score_file::Bytes unhex(const std::string& s) {
    if(s=="-")return {};require(!(s.size()%2),"odd music fixture");score_file::Bytes b;
    for(unsigned i=0;i<s.size();i+=2)b.push_back(score_file::Byte(std::stoul(s.substr(i,2),nullptr,16)));return b;
}
template<class T> void hex(const T& b) {
    constexpr char alphabet[]="0123456789abcdef";if(b.empty())std::cout<<'-';
    for(auto v:b)std::cout<<alphabet[unsigned(v)>>4]<<alphabet[unsigned(v)&15];
}
score_file::Bytes read(const std::string& path) {
    std::ifstream f(path,std::ios::binary);require(bool(f),"music asset missing");return {std::istreambuf_iterator<char>(f),{}};
}
score_file::Bytes polygons(const music::State& state) {
    score_file::Bytes b;
    for(const auto& p:state.polygons)for(int value:{int(p.center.x),int(p.center.y),int(p.velocity.x),int(p.velocity.y)}) {b.push_back(score_file::Byte(value));b.push_back(score_file::Byte(unsigned(value)>>8));}
    for(const auto& p:state.polygons)b.push_back(p.angle);
    for(const auto& p:state.polygons)b.push_back(p.angle_speed);
    return b;
}
void trace(const char* path,const char* dir=nullptr,const char* font=nullptr,const char* pixels=nullptr) {
    std::ifstream f(path);require(bool(f),"music fixtures missing");
    music::Assets assets;std::ofstream captures;
    if(dir) {
        const std::string prefix=std::string(dir)+"/";assets.graphics.font_bitmap=read(font);assets.graphics.gaiji=read(prefix+"GAMEFT.BFT");
        assets.graphics.pictures.emplace("MUSIC.PI",decode_pi(read(prefix+"MUSIC.PI")));captures.open(pixels,std::ios::binary);require(bool(captures),"music captures missing");
    }
    unsigned initialized,playing,index=0;std::uint32_t seed;std::string state,comments,keys;
    while(f>>initialized>>playing>>seed>>state>>comments>>keys) {
        const auto raw=unhex(state),input=unhex(keys);require(raw.size()==160 && !(input.size()%2),"music fixture state");
        music::State s;s.initialized=initialized!=0;s.playing=score_file::Byte(playing);
        for(unsigned i=0;i<16;++i) {
            auto& p=s.polygons[i];const auto word=[&](unsigned at){return motion::wrap(raw[at]|(unsigned(raw[at+1])<<8));};
            p.center={word(i*8),word(i*8+2)};p.velocity={word(i*8+4),word(i*8+6)};p.angle=raw[128+i];p.angle_speed=raw[144+i];
        }
        assets.comments=unhex(comments);rng::Lcg32 random(seed);unsigned draws=0;std::unique_ptr<music::Renderer> renderer;
        if(dir)renderer=std::make_unique<music::Renderer>(assets,std::array<score_file::Bytes,2>{score_file::Bytes(256000,1),score_file::Bytes(256000,2)});
        std::cout<<"CASE "<<index++<<'\n';
        music::Scene scene(s,assets,[&]{++draws;return random.next15();},[&](const music::Event& e) {
            std::cout<<music::kind_name(e.kind)<<' '<<e.tick<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' ';hex(e.data);std::cout<<'\n';if(renderer)renderer->apply(e);
        });
        const auto capture=[&] {
            if(!renderer)return;
            for(unsigned page=0;page<2;++page) {const auto& b=renderer->canvas().page(page);captures.write(reinterpret_cast<const char*>(b.data()),std::streamsize(b.size()));}
            const auto& p=renderer->canvas().palette();captures.write(reinterpret_cast<const char*>(p.data()),48);
            const auto rgb=renderer->rgb(scene.tone());captures.write(reinterpret_cast<const char*>(rgb.data()),std::streamsize(rgb.size()));
        };
        capture();while(!scene.finished() && scene.ticks()<input.size()/2) {
            const unsigned at=(scene.ticks()+1)*2;scene.advance(std::uint16_t(at+1<input.size() ? input[at]|(unsigned(input[at+1])<<8) : 0));capture();
        }
        require(scene.finished(),"music fixture never exited");
        std::cout<<"END "<<scene.ticks()<<' '<<scene.tone()<<' '<<random.state()<<' '<<draws<<' '<<s.initialized<<' '<<+s.playing<<' '<<+s.selected<<' '<<+s.page<<' '<<+s.comment_shown<<' '<<s.text_effect<<' ';
        hex(polygons(s));std::cout<<' ';hex(s.comment);std::cout<<'\n';
    }
    require(f.eof(),"short music fixture");
}
void fill(const char* path,const char* output) {
    std::ifstream f(path);std::ofstream o(output,std::ios::binary);require(bool(f)&&bool(o),"music fill fixtures missing");unsigned n;
    while(f>>n) {
        std::vector<motion::Point> points;int x,y;for(unsigned i=0;i<n;++i) {require(bool(f>>x>>y),"short polygon");points.push_back({motion::wrap(x),motion::wrap(y)});}points.push_back(points.front());
        score_file::Bytes page(256000);for(unsigned i=0;i<page.size();++i)page[i]=score_file::Byte((i*13+i/640)%16)&14;
        music::paint_polygon(page,points);o.write(reinterpret_cast<const char*>(page.data()),std::streamsize(page.size()));
    }
    require(f.eof(),"short polygon fixture");
}
void contracts() {
    music::Assets assets;assets.comments.assign(17600,' ');music::State state;rng::Lcg32 random;unsigned draws=0,delays=0;
    music::Scene scene(state,assets,[&]{++draws;return random.next15();},[&](const music::Event& e){delays+=e.kind==music::Kind::delay;});
    require(draws==96 && delays==1 && state.initialized,"Music first animation/RNG");
    scene.advance(0);scene.advance(2);require(state.selected==1,"Music down");
    scene.advance(2);scene.advance(2);require(state.selected==1,"Music held arrow repeated");
    scene.advance(0);scene.advance(0x1020);
    for(unsigned i=0;i<10;++i)scene.advance(0);
    require(state.playing==1 && !scene.finished(),"Music retained play/cancel sample");
    for(unsigned i=0;i<18;++i)scene.advance(0);
    require(scene.finished() && scene.tone()==0,"Music exit blackout");
    const auto before=draws;music::Scene again(state,assets,[&]{++draws;return random.next15();});
    require(again.state().selected==1 && draws==before,"Music process state reset on revisit");
    std::cout<<"Music Room input/revisit/RNG/fade contracts PASS\n";
}
}
int main(int argc,char** argv) {
    try {
        if(argc==1)contracts();else if(argc==3 && std::string(argv[1])=="--trace")trace(argv[2]);
        else if(argc==6 && std::string(argv[1])=="--pixels")trace(argv[2],argv[3],argv[4],argv[5]);
        else if(argc==4 && std::string(argv[1])=="--fill")fill(argv[2],argv[3]);
        else throw std::invalid_argument("Music contract arguments");return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
