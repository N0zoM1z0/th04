#include "dialog.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
namespace d=th04::portable::dialog;
namespace {
void require(bool ok,const char* why) { if(!ok) throw std::runtime_error(why); }
d::Bytes read(const char* path) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"cannot read dialog fixture");return {std::istreambuf_iterator<char>(in),{}};
}
void print(const d::Event& e) {
    std::cout<<int(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' ';
    if(e.name.empty()) std::cout<<'-';
    else { constexpr char digits[]="0123456789abcdef";for(unsigned char c:e.name) std::cout<<digits[c>>4]<<digits[c&15]; }
    std::cout<<'\n';
}
void trace(const char* path,unsigned held,unsigned scenes) {
    d::Script script(read(path));
    for(unsigned scene=0;scene<scenes;++scene) {
        script.begin();unsigned frame=0;
        while(script.status()!=d::Status::stopped && frame++<100000) {
            const auto input=script.status()==d::Status::release ? 0 : script.status()==d::Status::press ? 1 : held;
            script.advance(static_cast<std::uint16_t>(input),print);
        }
        require(script.status()==d::Status::stopped,"native dialog failed to stop");
        std::cout<<"END "<<script.offset()<<' '<<script.cursor().x<<' '<<script.cursor().y<<' '<<script.side()<<' '<<script.number_default()<<'\n';
    }
}
void contracts() {
    const std::string text="0\x82\xa0\\$\\#1\\#\\#";
    d::Script script(d::Bytes(text.begin(),text.end()));script.begin();
    std::vector<d::Event> events;const auto sink=[&](const d::Event& e) { events.push_back(e); };
    script.advance(1,sink);require(script.status()==d::Status::release,"held key must not dismiss dialog wait");
    const auto offset=script.offset();for(unsigned i=0;i<10;++i) script.advance(1,sink);
    require(script.offset()==offset && script.status()==d::Status::release,"wait release has no timeout");
    script.advance(0,sink);require(script.status()==d::Status::press,"release and press are separate samples");
    script.advance(0,sink);require(script.status()==d::Status::press,"zero press budget is unbounded");
    script.advance(1,sink);script.advance(0,sink);
    require(script.status()==d::Status::stopped,"outer stop ends scene");
    script.begin();script.advance(0,sink);require(script.status()==d::Status::stopped && script.side()==1,"inner stop resumes outer parser at retained cursor");
    const std::string short_text="0\x82";d::Script malformed(d::Bytes(short_text.begin(),short_text.end()));malformed.begin();
    bool rejected=false;try { malformed.advance(0,sink); }catch(const std::invalid_argument&) { rejected=true; }
    require(rejected,"truncated glyph rejects bounded native read");
    d::Font empty({});require(!empty.present() && !empty.pixel(0x82a0,0,0),"absent font is explicit");
}
}
int main(int argc,char** argv) {
    static_assert(sizeof(void*)==8,"dialog requires x64");
    if(argc==5 && std::string(argv[1])=="--trace") { trace(argv[2],std::stoul(argv[3]),std::stoul(argv[4]));return 0; }
    if(argc==2 && std::string(argv[1])=="--gates") {
        for(unsigned speed=0;speed<256;++speed) for(unsigned page:{0,1,2}) {
            std::cout<<speed<<' '<<page<<' '<<d::stage_gate(static_cast<std::uint8_t>(speed),static_cast<std::uint8_t>(page))<<'\n';
        }
        return 0;
    }
    if(argc==3 && std::string(argv[1])=="--font-pixels") {
        d::Font font(read(argv[2]));
        for(unsigned sjis:{0x82a0,0x8146,0xe8cb,0x9682,0x97c0,0x8db9}) for(unsigned y=0;y<16;++y) for(unsigned x=0;x<16;++x) std::cout<<font.pixel(static_cast<std::uint16_t>(sjis),x,y);
        std::cout<<'\n';return 0;
    }
    contracts();std::cout<<"Dialog contracts PASS\n";
}
