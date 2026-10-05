#include "congratulations.hpp"
#include "verdict.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>

namespace {
namespace m=th04::portable::maine;
namespace c=th04::portable::cutscene;
Bytes read(const std::filesystem::path& path) {
    std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("congratulations asset is missing");
    return Bytes(std::istreambuf_iterator<char>(f),{});
}
void write(const std::filesystem::path& p,const Bytes& b) {
    std::ofstream f(p,std::ios::binary);if(!f)throw std::runtime_error("congratulations output is missing");
    f.write(reinterpret_cast<const char*>(b.data()),std::streamsize(b.size()));
}
void request(const m::Request& e) {
    static constexpr char hex[]="0123456789abcdef";
    std::cout<<th04::portable::verdict::kind_name(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' '<<e.e<<' ';
    if(e.data.empty())std::cout<<'-';
    else for(unsigned char b:e.data)std::cout<<hex[b>>4]<<hex[b&15];
    std::cout<<'\n';
}
bool held(int relative,unsigned profile) {
    if(profile==0)return relative>=8;
    if(profile==1)return relative<5 || relative>=15;
    if(profile==2)return (relative<12 && relative!=6) || relative>=20;
    if(profile==3)return (relative>=2 && relative<6) || relative>=15;
    return relative==8 || relative>=20;
}
}
void congratulations_trace() {
    for(unsigned character=0;character<2;++character)for(unsigned rank=0;rank<5;++rank) {
        std::cout<<"CASE "<<character<<' '<<rank<<'\n';
        for(const auto& e:m::congratulations_requests(character,rank))request(e);
        for(unsigned profile=0;profile<5;++profile) {
            std::cout<<"CLOCK "<<character<<' '<<rank<<' '<<profile<<'\n';
            m::Animation animation(m::congratulations_requests(character,rank));
            int previous=-1;std::vector<std::pair<unsigned,int>> palette;
            for(unsigned tick=0;tick<500;++tick) {
                animation.advance(held(int(tick)-18,profile)?0x20:0,[&](const auto& e) {std::cout<<tick<<' ';request(e);});
                if(animation.tone()!=previous) {previous=animation.tone();palette.emplace_back(tick,previous);}
                if(animation.status()==m::AnimationStatus::stopped) {
                    for(const auto& p:palette)std::cout<<"PALETTE "<<p.first<<' '<<p.second<<'\n';
                    std::cout<<"STOP "<<tick<<'\n';break;
                }
                if(tick==499)throw std::runtime_error("congratulations clock did not finish");
            }
        }
    }
}
void congratulations_render(const char* assets_dir,const char* font,const char* output_dir) {
    const std::filesystem::path assets_path(assets_dir),out(output_dir);
    std::filesystem::create_directories(out);c::Assets assets;assets.font_bitmap=read(font);
    // These are real supplied PI images; no cutscene script is manufactured.
    for(unsigned character=0;character<2;++character)for(unsigned rank=0;rank<5;++rank) {
        auto name=m::congratulations_picture(character,rank);name[7]='P';name[8]='I';
        assets.pictures.emplace(name,decode_pi(read(assets_path/name)));
    }
    std::ofstream states(out/"states.txt");
    for(unsigned character=0;character<2;++character)for(unsigned rank=0;rank<5;++rank) {
        const unsigned index=character*5+rank;
        m::Congratulations scene(assets,character,rank,{Bytes(640*400,3),Bytes(640*400,9)});
        for(unsigned i=0;i<100 && scene.animation().status()!=m::AnimationStatus::release;++i)scene.advance(0x20);
        if(scene.animation().status()!=m::AnimationStatus::release || scene.animation().tone()!=100)
            throw std::runtime_error("congratulations did not reach its visible wait");
        const auto& canvas=scene.canvas();
        for(unsigned p=0;p<2;++p)write(out/(std::to_string(index)+"-"+std::to_string(p)+".bin"),canvas.page(p));
        write(out/(std::to_string(index)+".pal"),Bytes(canvas.palette().begin(),canvas.palette().end()));
        states<<index<<' '<<canvas.shown_page()<<' '<<canvas.access_page()<<' '
            <<scene.animation().tone()<<' '<<scene.animation().event_count()<<'\n';
        const auto pages=std::array<Bytes,2>{canvas.page(0),canvas.page(1)};
        for(unsigned i=0;i<10;++i)scene.advance(0x20);
        if(canvas.page(0)!=pages[0] || canvas.page(1)!=pages[1] || scene.animation().status()!=m::AnimationStatus::release)
            throw std::runtime_error("congratulations held input changed its pages/wait");
        scene.advance(0);scene.advance(0);scene.advance(0x20);
        for(unsigned i=0;i<100 && scene.animation().status()!=m::AnimationStatus::stopped;++i)scene.advance(0x20);
        if(scene.animation().status()!=m::AnimationStatus::stopped || scene.animation().tone()!=0)
            throw std::runtime_error("congratulations did not finish its original blackout");
    }
    std::cout<<"Congratulations graphics and lifetime: 10 complete-picture controls PASS\n";
}
