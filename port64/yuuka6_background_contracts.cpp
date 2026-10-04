#include "yuuka6_background.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
namespace y=th04::portable::yuuka6;
namespace m=th04::portable::motion;
namespace r=th04::portable::randring;
using Bytes=std::vector<std::uint8_t>;
namespace {
void require(bool ok,const char* why) { if(!ok) throw std::runtime_error(why); }
Bytes decode(const std::string& text,unsigned length) {
    require(text.size()==length*2,"invalid background wire extent");Bytes v;
    for(unsigned i=0;i<length;++i) v.push_back(static_cast<std::uint8_t>(std::stoul(text.substr(i*2,2),nullptr,16)));
    return v;
}
unsigned read_word(const Bytes& v,unsigned at) { return v.at(at)|(unsigned(v.at(at+1))<<8); }
void word(Bytes& v,unsigned n) { v.push_back(n&255);v.push_back((n>>8)&255); }
void hex(const Bytes& v) { constexpr char d[]="0123456789abcdef";for(auto n:v) std::cout << d[n>>4] << d[n&15];std::cout << ' '; }
y::CheckerboardState board(const std::string& raw) { auto v=decode(raw,8);return {static_cast<std::uint16_t>(read_word(v,0)),static_cast<std::uint16_t>(read_word(v,2)),static_cast<std::uint16_t>(read_word(v,4)),v[6],v[7]}; }
Bytes board(const y::CheckerboardState& s) { Bytes v;word(v,s.segment);word(v,s.bottom);word(v,s.top);v.push_back(s.dark_x);v.push_back(s.passes);return v; }
void print(const y::Background& owner,const r::SharedRandomRing& random) {
    const auto& s=owner.state();Bytes v;for(const auto& q:s.shapes) { word(v,q.position.x);word(v,q.position.y);v.push_back(q.angle);v.push_back(q.speed); }hex(v);hex(board(owner.checkerboard().state()));
    std::cout << +s.state << ' ' << +s.fade << ' ' << +s.palette_latch << ' ' << s.pattern << ' ' << s.flyout_speed << ' ' << int(s.clip) << ' ' << random.cursor() << ' ';
    for(auto n:s.palette_zero) std::cout << +n << ' ';
    std::cout << +s.palette_changed << ' ' << s.current_bb << ' ' << s.boss_bb << ' ' << owner.draws().size();
    for(const auto& d:owner.draws()) std::cout << ' ' << int(d.kind) << ' ' << d.position.x << ' ' << d.position.y << ' ' << d.value;
    std::cout << '\n';
}
std::pair<std::uint8_t,std::int16_t> sequence(int step) {
    if(step<3) return {0,static_cast<std::int16_t>(step)};
    if(step<35) return {1,static_cast<std::int16_t>(step-3)};
    if(step<291) return {2,static_cast<std::int16_t>(step-35)};
    constexpr std::uint8_t phases[]{3,5,7,9,11,13,15,254};
    const unsigned index=(step-291)/160;return {phases[index<8 ? index : 7],static_cast<std::int16_t>((step-291)%160)};
}
void vectors(const char* path) {
    std::ifstream in(path);require(bool(in),"cannot open background fixtures");char op;
    while(in>>op) {
        int steps=0,phase=0,clock=0,st=0,fade=0,latch=0,pattern=0,speed=0,clip=0,cursor=0,pr=0,pg=0,pb=0,changed=0,bossbb=0,currentbb=0;std::string shapes,checker;
        require(bool(in>>steps>>phase>>clock>>st>>fade>>latch>>pattern>>speed>>clip>>cursor>>pr>>pg>>pb>>changed>>bossbb>>currentbb>>shapes>>checker),"short background fixture");
        require(steps>0 && steps<=2000 && phase>=0 && phase<=255 && clip>=0 && clip<=2 && cursor>=0 && cursor<=255,"invalid background execution bounds");
        require(op=='B' || op=='U' || op=='C' || op=='S',"unknown background operation");
        y::BackgroundState s;s.state=st;s.fade=fade;s.palette_latch=latch;s.pattern=pattern;s.flyout_speed=speed;s.clip=static_cast<y::ShapeClip>(clip);s.palette_zero={static_cast<std::uint8_t>(pr),static_cast<std::uint8_t>(pg),static_cast<std::uint8_t>(pb)};s.palette_changed=changed;s.boss_bb=bossbb;s.current_bb=currentbb;
        const auto raw=decode(shapes,342);for(unsigned i=0;i<57;++i) s.shapes[i]={{m::wrap(read_word(raw,i*6)),m::wrap(read_word(raw,i*6+2))},raw[i*6+4],raw[i*6+5]};
        r::SharedRandomRing random;unsigned draw=0;random.fill([&] { return static_cast<std::uint8_t>(draw++*73u+19u); });for(int i=0;i<cursor;++i) random.next16();
        if(op=='C') { y::Background::clip_shape(s.shapes[0],s.clip,s.flyout_speed);y::Background owner(s,board(checker));print(owner,random);continue; }
        y::Background owner(s,board(checker));
        for(int step=0;step<steps;++step) {
            if(op=='U') owner.update_particles(static_cast<std::uint8_t>(phase),random);
            else {
                const auto p=op=='S' ? sequence(step) : std::make_pair(static_cast<std::uint8_t>(phase),m::wrap(clock+step));owner.prepare_render(p.first,p.second,random);
            }
            print(owner,random);
        }
    }
    require(in.eof(),"malformed background fixture");
}
Bytes screen(unsigned seed) { Bytes v(256000);for(unsigned i=0;i<v.size();++i) v[i]=static_cast<std::uint8_t>((i*73u+seed)&15);return v; }
void stores(Bytes& pixels,const y::Checkerboard& checker) {
    for(const auto& s:checker.stores()) for(int byte=0;byte<4;++byte) {
        const auto at=s.offset+byte;if(at<0 || at>=32000) continue;
        for(unsigned bit=0;bit<8;++bit) pixels[unsigned(at)*8+bit]=s.color;
    }
}
void pixel_vectors(const char* path) {
#ifdef _WIN32
    _setmode(_fileno(stdout),_O_BINARY);
#endif
    std::ifstream in(path);require(bool(in),"cannot open background pixel fixtures");char op;
    while(in>>op) {
        if(op=='K') {
            int steps=0,seed=0;std::string raw;require(bool(in>>steps>>seed>>raw),"short checker pixel fixture");require(steps>0 && steps<=64,"invalid checker frame count");y::Checkerboard checker(board(raw));auto pixels=screen(seed);
            for(int step=0;step<steps;++step) { checker.prepare_render();stores(pixels,checker);const auto state=board(checker.state());std::cout.write(reinterpret_cast<const char*>(state.data()),state.size());std::cout.write(reinterpret_cast<const char*>(pixels.data()),pixels.size()); }
        } else {
            require(op=='M',"unknown background pixel operation");int x=0,yy=0,color=0,seed=0;std::string raw;require(bool(in>>x>>yy>>color>>seed>>raw),"short mono fixture");const auto v=decode(raw,32);std::array<std::uint8_t,32> mask;std::copy(v.begin(),v.end(),mask.begin());auto pixels=screen(seed);
            y::raster_mono(mask,m::wrap(x),m::wrap(yy),static_cast<std::uint8_t>(color),[&](int px,int py,std::uint8_t c) { pixels[py*640+px]=c; });std::cout.write(reinterpret_cast<const char*>(pixels.data()),pixels.size());
        }
    }
    require(in.eof(),"malformed background pixel fixture");
}
void contracts() {
    y::BackgroundState s;s.shapes.back()={{-12345,23456},129,255};s.palette_latch=123;s.clip=y::ShapeClip::center;y::Background owner(s);r::SharedRandomRing random;unsigned draw=0;random.fill([&]{return static_cast<std::uint8_t>(draw++);});owner.prepare_render(0,2,random);
    require(owner.state().shapes.back().position.x==-12345 && owner.state().palette_latch==123 && owner.state().clip==y::ShapeClip::center,"initialization erased retained background metadata");
    require(random.cursor()==112,"background initialization RNG consumption differs");
    y::BackgroundShape q{{-128,6144},17,255};y::Background::clip_shape(q,y::ShapeClip::center,256);require(q.position.x==3072 && q.position.y==2944 && q.speed==0,"center respawn BYTE/threshold differs");
    owner.prepare_render(2,0,random);const auto fade=owner.state().fade;owner.draws();owner.draws();require(owner.state().fade==fade,"cached background repaint advanced state");
    bool rejected=false;try { y::Background::clip_shape(q,y::ShapeClip::none,16); } catch(const std::domain_error&) { rejected=true; }require(rejected,"missing clip callback silently accepted");
}
} // namespace
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") { vectors(argv[2]);return 0; }
        if(argc==3 && std::string(argv[1])=="--pixels") { pixel_vectors(argv[2]);return 0; }
        require(argc==1,"usage: Yuuka6 background contracts [--vectors FILE | --pixels FILE]");contracts();std::cout << "Stage 6 Yuuka background contracts PASS\n";return 0;
    } catch(const std::exception& e) { std::cerr << "Yuuka6 background: " << e.what() << '\n';return 1; }
}
