#include "staff_roll.hpp"
#include "cdg_image.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <set>
#include <stdexcept>

using namespace th04::portable;
namespace {
void require(bool value,const char* why) { if(!value)throw std::runtime_error(why); }
Bytes read(const std::string& path) {
    std::ifstream f(path,std::ios::binary);require(bool(f),"Staff Roll input missing");
    return Bytes(std::istreambuf_iterator<char>(f),{});
}
void write(const std::string& path,const Bytes& bytes) {
    std::ofstream f(path,std::ios::binary);require(bool(f),"Staff Roll output missing");
    f.write(reinterpret_cast<const char*>(bytes.data()),std::streamsize(bytes.size()));
    require(bool(f),"Staff Roll output failed");
}
staff::Assets assets(const char* directory) {
    staff::Assets a;
    for(unsigned i=1;i<=2;++i) {
        const auto name="SFF"+std::to_string(i)+".PI";
        a.pictures.emplace(name,decode_pi(read(std::string(directory)+"/"+name)));
    }
    for(unsigned i=1;i<=9;++i)for(const auto suffix:{".CDG","B.CDG"}) {
        const auto name="SFF"+std::to_string(i)+suffix;
        a.sprites.emplace(name,read(std::string(directory)+"/"+name));
    }
    return a;
}
void event(const staff::Event& e) {
    std::cout<<staff::kind_name(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' '<<(e.name.empty() ? "-" : e.name)<<'\n';
}
}
void staff_trace(const char* directory,unsigned angle) {
    const auto a=assets(directory);
    const staff::Script script([&](const std::string& name) {
        const CdgSheet sheet(a.sprites.at(name));return staff::Dimensions{sheet.width,sheet.height};
    },static_cast<std::uint8_t>(angle));
    for(const auto& e:script.requests())event(e);
    std::cout<<"END "<<unsigned(script.angle())<<'\n';
}
void staff_render(const char* directory,const char* positions,const char* destination) {
    const auto a=assets(directory);staff::Scene scene(a);
    std::ifstream f(positions);require(bool(f),"Staff Roll checkpoints missing");
    std::set<unsigned> wanted;unsigned position;
    while(f>>position)wanted.insert(position);
    require(!wanted.empty(),"Staff Roll checkpoints empty");
    std::ofstream states(std::string(destination)+"/states.txt");require(bool(states),"Staff Roll states cannot open");
    while(scene.status()!=staff::Status::stopped && scene.ticks()<100000)scene.advance([&](const staff::Event& e) {
        const unsigned index=unsigned(scene.event_count()-1);
        if(!wanted.erase(index))return;
        const auto prefix=std::string(destination)+"/"+std::to_string(index);
        write(prefix+"-0.bin",scene.page(0));write(prefix+"-1.bin",scene.page(1));
        write(prefix+".pal",Bytes(scene.palette().begin(),scene.palette().end()));
        states<<index<<' '<<scene.shown_page()<<' '<<scene.access_page()<<' '<<scene.tone()<<' '
              <<scene.background_alive()<<' '<<scene.live_slots()<<' '<<staff::kind_name(e.kind)<<'\n';
    });
    require(scene.status()==staff::Status::stopped && wanted.empty(),"Staff Roll did not reach every checkpoint");
    require(!scene.background_alive() && !scene.live_slots() && scene.tone()==0,"Staff Roll lifetime incomplete");
    std::cout<<"Staff Roll render: events="<<scene.event_count()<<" ticks="<<scene.ticks()<<" progression=verdict_pending\n";
}
void staff_kernels(const char* directory,const char* fixtures,const char* destination) {
    const auto a=assets(directory);std::ifstream in(fixtures);require(bool(in),"Staff Roll kernel fixtures missing");
    std::string kind,name;int x,y,c,d;unsigned index=0;
    while(in>>kind>>name>>x>>y>>c>>d) {
        std::array<Bytes,2> pages{Bytes(640*400),Bytes(640*400,9)};
        for(unsigned at=0;at<640*400;++at)pages[0][at]=std::uint8_t((at*13+(at/640)*7)&15);
        staff::Scene scene(a,std::move(pages));
        if(kind=="bg") {
            scene.apply({staff::Kind::snap});scene.apply({staff::Kind::access,1});
            scene.apply({staff::Kind::bg_rect,x,y,c,d});
        } else {
            scene.apply({staff::Kind::cdg_load,0,0,0,0,name});
            scene.apply({kind=="put" ? staff::Kind::cdg_put : staff::Kind::plane,x,y,0,c});
        }
        write(std::string(destination)+"/"+std::to_string(index++)+".bin",scene.page(kind=="bg" ? 1 : 0));
    }
    require(index>0 && in.eof(),"Staff Roll kernel fixture parse failed");
    std::cout<<"Staff Roll direct graphics-kernel controls: "<<index<<'\n';
}
void staff_contracts() {
    staff::Assets a;
    PiImage picture;picture.width=640;picture.height=400;picture.pixels.resize(128000,0x22);
    a.pictures.emplace("SFF1.PI",picture);a.pictures.emplace("SFF2.PI",picture);
    Bytes sheet(16+4*32*5,0xff);
    const auto word=[&](unsigned at,unsigned v) { sheet[at]=v&255;sheet[at+1]=(v>>8)&255; };
    word(0,128);word(2,32);word(4,32);word(6,31*80);word(8,1);sheet[10]=1;sheet[11]=1;
    for(unsigned i=1;i<=9;++i)for(const auto suffix:{".CDG","B.CDG"})a.sprites.emplace("SFF"+std::to_string(i)+suffix,sheet);
    staff::Scene inactive(a);
    while(inactive.status()!=staff::Status::stopped && inactive.ticks()<10000)inactive.advance();
    require(inactive.status()==staff::Status::stopped && !inactive.background_alive() && !inactive.live_slots() &&
            inactive.tone()==0 && inactive.page(0)==inactive.page(1),"Staff Roll fallback/resource/page lifetime differs");
    staff::Scene active(a);active.set_audio_active(true);
    while(active.status()!=staff::Status::measure && active.ticks()<1000)active.advance();
    require(active.status()==staff::Status::measure,"active Staff Roll must wait for song measure3");
    const auto count=active.event_count();const auto page=active.page(0);
    for(unsigned i=0;i<99;++i)active.advance();
    require(active.event_count()==count && active.page(0)==page,"elapsed host time fabricated song progression");
    active.report_song_measure(2);active.advance();require(active.status()==staff::Status::measure,"measure below unsigned goal resumed");
    active.report_song_measure(65535);
    while(active.status()!=staff::Status::stopped && active.ticks()<10000)active.advance();
    require(active.status()==staff::Status::stopped && !active.live_slots(),"reported sound progress did not resume all Staff Roll owners");
    bool rejected=false;try { CdgSheet malformed(Bytes(16)); }catch(const std::invalid_argument&) { rejected=true; }
    require(rejected,"invalid CDG geometry must fail closed");
    std::cout<<"Staff Roll graphics, sound-wait and lifetime contracts: PASS\n";
}
