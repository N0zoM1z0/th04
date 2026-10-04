#include "cutscene.hpp"
#include "cutscene_scene.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <iomanip>
#include <stdexcept>
#include <sstream>
#include <set>

using namespace th04::portable;
namespace {
void require(bool value,const char* reason) { if(!value) throw std::runtime_error(reason); }
void event(const cutscene::Event& e) {
    std::cout<<cutscene::kind_name(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' '<<e.e<<' ';
    if(e.name.empty()) std::cout<<'-';
    else for(unsigned char c:e.name) std::cout<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(c);
    std::cout<<std::dec<<'\n';
}
void trace(const char* path,unsigned held) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"script input missing");
    cutscene::Bytes bytes((std::istreambuf_iterator<char>(in)),{});
    cutscene::Script script(std::move(bytes));script.begin();
    unsigned ticks=0;
    while(script.status()!=cutscene::Status::stopped && ++ticks<1000000) {
        // Original differential adapters complete waits at the consumer
        // boundary. Explicit release/press here does the same without
        // changing the next outer iteration's supplied held input.
        if(script.status()==cutscene::Status::release) script.advance(0,event);
        else if(script.status()==cutscene::Status::press) script.advance(0x20,event);
        else if(script.status()==cutscene::Status::measure) script.complete_measure_wait();
        else script.advance(static_cast<std::uint16_t>(held),event);
    }
    require(script.status()==cutscene::Status::stopped,"script did not terminate");
    std::cout<<"END "<<script.offset()<<' '<<script.x()<<' '<<script.y()<<' '<<script.interval()<<' '
             <<unsigned(script.color())<<' '<<script.weight()<<' '<<script.number_default()<<'\n';
}
cutscene::Bytes read(const std::string& path) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"render asset missing");
    return cutscene::Bytes((std::istreambuf_iterator<char>(in)),{});
}
void write(const std::string& path,const cutscene::Bytes& bytes) {
    std::ofstream out(path,std::ios::binary);require(bool(out),"render output cannot open");
    out.write(reinterpret_cast<const char*>(bytes.data()),static_cast<std::streamsize>(bytes.size()));
    require(bool(out),"render output failed");
}
void render(const char* asset_dir,const char* name,unsigned held,const char* font_path,const char* checkpoints,const char* output) {
    const std::string directory(asset_dir),destination(output);
    cutscene::Assets assets;assets.font_bitmap=read(font_path);assets.gaiji=read(directory+"/GAMEFT.BFT");
    assets.scripts.emplace(name,read(directory+"/"+name));
    for(unsigned i=0;i<17;++i) {
        std::ostringstream filename;filename<<"ED"<<std::setw(2)<<std::setfill('0')<<i<<".PI";
        assets.pictures.emplace(filename.str(),decode_pi(read(directory+"/"+filename.str())));
    }
    cutscene::Scene scene(assets,name);
    std::ifstream positions(checkpoints);require(bool(positions),"render checkpoints missing");
    std::set<unsigned> captures;unsigned n;
    while(positions>>n) captures.insert(n);
    require(!captures.empty(),"render checkpoints are empty");
    std::ofstream states(destination+"/states.txt");require(bool(states),"render states cannot open");
    unsigned index=0,ticks=0;
    const auto observe=[&](const cutscene::Event&) {
        if(captures.count(index)) {
            write(destination+"/"+std::to_string(index)+"-0.bin",scene.page(0));
            write(destination+"/"+std::to_string(index)+"-1.bin",scene.page(1));
            write(destination+"/"+std::to_string(index)+".pal",cutscene::Bytes(scene.palette().begin(),scene.palette().end()));
            states<<index<<' '<<scene.shown_page()<<' '<<scene.access_page()<<' '<<scene.scroll()<<' '<<scene.script().tone()<<'\n';
            captures.erase(index);
        }
        ++index;
    };
    while(scene.script().status()!=cutscene::Status::stopped && ++ticks<1000000) {
        if(scene.script().status()==cutscene::Status::release) scene.advance(0,observe);
        else if(scene.script().status()==cutscene::Status::press) scene.advance(0x20,observe);
        else if(scene.script().status()==cutscene::Status::measure) scene.script().complete_measure_wait();
        else scene.advance(static_cast<std::uint16_t>(held),observe);
    }
    require(scene.script().status()==cutscene::Status::stopped && captures.empty(),"render did not reach every checkpoint");
    std::cout<<"Rendered "<<name<<" events="<<index<<" ticks="<<ticks<<'\n';
}
void glyphs(const char* font_path,const char* fixtures,const char* output) {
    cutscene::Assets assets;assets.font_bitmap=read(font_path);assets.scripts.emplace("TEST",cutscene::Bytes{'\\','$'});
    std::ifstream input(fixtures);require(bool(input),"glyph fixtures missing");
    unsigned weight,color,x,y,glyph,index=0;
    while(input>>weight>>color>>x>>y>>glyph) {
        cutscene::Scene scene(assets,"TEST");
        scene.apply({cutscene::Kind::text,int(x),int(y),int(glyph),int(color),int(weight)});
        write(std::string(output)+"/glyph-"+std::to_string(index++)+".bin",scene.page(0));
    }
    require(index>0,"no glyph fixtures");
    std::cout<<"Original font-effect controls: "<<index<<" fixtures\n";
}
void decode(const char* image,const char* output) {
    const auto pi=decode_pi(read(image));cutscene::Bytes data;
    for(unsigned value:{pi.width,pi.height}) for(unsigned i=0;i<4;++i) data.push_back(static_cast<std::uint8_t>(value>>(i*8)));
    data.insert(data.end(),pi.palette.begin(),pi.palette.end());data.insert(data.end(),pi.pixels.begin(),pi.pixels.end());
    write(output,data);
}
void contracts() {
    require(cutscene::script_name(0,0,false)=="_ED000.TXT","Reimu A good route");
    require(cutscene::script_name(1,1,true)=="_ED111.TXT","Marisa B bad route");
    cutscene::Script script({'\\','k','2','\\','$'});script.begin();
    script.advance(0,{});require(script.status()==cutscene::Status::release,"wait releases first");
    for(unsigned i=0;i<30;++i) script.advance(0x20,{});
    require(script.status()==cutscene::Status::release,"release cannot time out");
    script.advance(0,{});require(script.status()==cutscene::Status::press,"release advances to press");
    script.advance(0,{});require(script.status()==cutscene::Status::press,"press budget retains first frame");
    script.advance(0,{});require(script.status()==cutscene::Status::running,"finite press budget expires");
    script.advance(0,{});require(script.status()==cutscene::Status::stopped,"stop owns cleanup");
    cutscene::Script fast({'\\','w','m','3',',','4','\\','$'});fast.begin();fast.advance(cutscene::input_cancel,{});
    require(fast.status()==cutscene::Status::stopped,"Escape skips measure waits");
    cutscene::Script music({'\\','w','m','3',',','4','\\','$'});music.begin();music.advance(0,{});
    require(music.status()==cutscene::Status::delay,"box mask delays precede music wait");
    for(unsigned i=0;i<20 && music.status()!=cutscene::Status::measure;++i) music.advance(0,{});
    require(music.status()==cutscene::Status::measure,"music owner holds measure boundary");
    for(unsigned i=0;i<100;++i) music.advance(0x20,{});
    require(music.status()==cutscene::Status::measure,"key input is not song progress");
    music.complete_measure_wait();music.advance(0,{});
    require(music.status()==cutscene::Status::stopped,"explicit sound progress resumes script");
    bool malformed=false;
    try { cutscene::Script bad({0x82});bad.begin();bad.advance(0,{}); }
    catch(const std::invalid_argument&) { malformed=true; }
    require(malformed,"native buffer bounds reject truncated glyphs");
    std::cout<<"MAINE cutscene lifecycle contracts: PASS\n";
}
}
int main(int argc,char** argv) {
    try {
        if(argc==4 && std::string(argv[1])=="--trace") trace(argv[2],std::stoul(argv[3]));
        else if(argc==4 && std::string(argv[1])=="--decode") decode(argv[2],argv[3]);
        else if(argc==8 && std::string(argv[1])=="--render") render(argv[2],argv[3],std::stoul(argv[4]),argv[5],argv[6],argv[7]);
        else if(argc==5 && std::string(argv[1])=="--glyphs") glyphs(argv[2],argv[3],argv[4]);
        else if(argc==1) contracts();
        else throw std::invalid_argument("usage: cutscene-contracts [--trace SCRIPT HELD | --render ASSETS SCRIPT HELD FONT CHECKPOINTS OUTPUT]");
        return 0;
    } catch(const std::exception& error) { std::cerr<<error.what()<<'\n';return 1; }
}
