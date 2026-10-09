#include "op_ranking.hpp"
#include "random_lcg.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>

using namespace th04::portable;
namespace sf=score_file;
namespace {
void require(bool v,const char* s) {if(!v)throw std::runtime_error(s);}
sf::Bytes unhex(const std::string& s) {
    if(s=="-")return {};require(!(s.size()%2),"odd ranking fixture");sf::Bytes b;
    for(unsigned i=0;i<s.size();i+=2)b.push_back(sf::Byte(std::stoul(s.substr(i,2),nullptr,16)));return b;
}
template<class T> void hex(const T& b) {
    constexpr char alphabet[]="0123456789abcdef";if(b.empty())std::cout<<'-';
    for(auto v:b)std::cout<<alphabet[v>>4]<<alphabet[v&15];
}
sf::Bytes read(const std::string& path) {
    std::ifstream f(path,std::ios::binary);require(bool(f),"ranking asset missing");return {std::istreambuf_iterator<char>(f),{}};
}
void trace(const char* path,const char* asset_dir=nullptr,const char* font_path=nullptr,const char* pixels=nullptr) {
    std::ifstream f(path);require(bool(f),"ranking fixtures missing");
    std::unique_ptr<op_ranking::Assets> assets;std::ofstream captures;
    if(asset_dir) {
        assets=std::make_unique<op_ranking::Assets>();const std::string dir=std::string(asset_dir)+"/";
        assets->graphics.font_bitmap=read(font_path);assets->graphics.gaiji=read(dir+"GAMEFT.BFT");
        for(const auto* name:{"HI01.PI","OP1.PI"})assets->graphics.pictures.emplace(name,decode_pi(read(dir+name)));
        assets->numerals=read(dir+"SCNUM.BFT");assets->rank_labels=read(dir+"HI_M.BFT");
        captures.open(pixels,std::ios::binary);require(bool(captures),"ranking capture output missing");
    }
    unsigned configured,rank,extra,present,index=0;std::uint32_t seed;std::string first,second,flags,file,keys;
    while(f>>configured>>rank>>extra>>present>>seed>>first>>second>>flags>>file>>keys) {
        const auto a=unhex(first),b=unhex(second),c=unhex(flags),input=unhex(keys);
        require(a.size()==196 && b.size()==196 && c.size()==10 && !(input.size()%2),"ranking fixture shape");
        op_score::Snapshot s;std::copy(a.begin(),a.end(),s.first.begin());std::copy(b.begin(),b.end(),s.second.begin());
        s.rank=sf::Byte(rank);s.extra_unlocked=sf::Byte(extra);
        for(unsigned col=0;col<2;++col)for(unsigned r=0;r<5;++r)s.cleared[col][r]=c[col*5+r];
        op_score::State state(s);sf::File score(present,unhex(file));rng::Lcg32 random(seed);unsigned draws=0;
        std::unique_ptr<op_ranking::Renderer> renderer;
        if(assets)renderer=std::make_unique<op_ranking::Renderer>(*assets,
            std::array<sf::Bytes,2>{sf::Bytes(256000,1),sf::Bytes(256000,2)});
        std::cout<<"CASE "<<index++<<'\n';
        const auto observer=[&](const op_ranking::Event& e) {
            std::cout<<op_ranking::kind_name(e.kind)<<' '<<e.tick<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' ';hex(e.data);std::cout<<'\n';
            if(renderer)renderer->apply(e);
        };
        op_ranking::Scene scene(state,score,sf::Byte(configured),[&]{++draws;return random.next15();},{},observer);
        const auto capture=[&] {
            if(!renderer)return;
            for(unsigned page=0;page<2;++page) {
                const auto& bytes=renderer->canvas().page(page);captures.write(reinterpret_cast<const char*>(bytes.data()),std::streamsize(bytes.size()));
            }
            const auto& palette=renderer->canvas().palette();captures.write(reinterpret_cast<const char*>(palette.data()),48);
            const auto rgb=renderer->rgb(0,scene.tone());captures.write(reinterpret_cast<const char*>(rgb.data()),std::streamsize(rgb.size()));
        };
        // Every refresh, including the constructor's initial display, is
        // captured. Only explicitly valid fixture patterns enter this mode.
        capture();
        while(!scene.finished() && scene.ticks()<1000) {
            const unsigned at=(scene.ticks()+1)*2;
            const auto held=std::uint16_t(at+1<input.size() ? unsigned(input[at])|(unsigned(input[at+1])<<8) : 0);
            scene.advance(held);capture();
        }
        require(scene.finished(),"ranking fixture never exited");
        const auto& result=state.snapshot();std::cout<<"END "<<scene.ticks()<<' '<<scene.tone()<<' '<<random.state()<<' '<<draws<<' '<<score.present()<<' '<<+result.rank<<' '<<+result.extra_unlocked<<' ';
        hex(result.first);std::cout<<' ';hex(result.second);std::cout<<' ';for(const auto& col:result.cleared)hex(col);std::cout<<' ';hex(score.bytes());std::cout<<'\n';
    }
    require(f.eof(),"short ranking fixture");
}
void contracts() {
    sf::File file;op_score::State state;unsigned close=0,tone_events=0;
    op_ranking::Scene scene(state,file,2,[]{return 1;},[&](const sf::Operation& e){close+=e.kind==sf::IO::close;},
        [&](const op_ranking::Event& e){tone_events+=e.kind==op_ranking::Kind::tone;});
    for(unsigned t=1;t<=36;++t)scene.advance(t==36 ? 0x20 : 0);
    require(close==1 && state.snapshot().rank==2,"ranking recreate close boundary");
    scene.advance(0x20);for(unsigned t=38;t<=73;++t)scene.advance(0x20);
    require(scene.phase()==op_ranking::Phase::release && !scene.finished(),"ranking skipped held-key release");
    scene.advance(0);require(!scene.finished(),"ranking sampled release after delay");scene.advance(0);
    require(scene.finished() && tone_events==72,"ranking ordered fades/release");
    std::cout<<"OP ranking fade/recreate/release contracts PASS\n";
}
}
int main(int argc,char** argv) {
    try {
        if(argc==1)contracts();else if(argc==3 && std::string(argv[1])=="--trace")trace(argv[2]);
        else if(argc==6 && std::string(argv[1])=="--pixels")trace(argv[2],argv[3],argv[4],argv[5]);
        else throw std::invalid_argument("OP ranking arguments");return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
