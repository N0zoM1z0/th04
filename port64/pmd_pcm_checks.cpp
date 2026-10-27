#include "pmd_pcm.hpp"
#include <fstream>
#include <cmath>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool v,const char* text){if(!v)throw std::runtime_error(text);}
void contracts(){
    std::vector<StereoSample> whole,parts;
    OpnPcm a(Board::fm26,4000000,{},[&](StereoSample v){whole.push_back(v);});
    OpnPcm b(Board::fm26,4000000,{},[&](StereoSample v){parts.push_back(v);});
    for(auto w:std::vector<FmWrite>{{0,0,132},{0,1,0},{0,7,62},{0,8,15}}){a.write(0,w);b.write(0,w);}
    a.advance_to(400000);for(unsigned at=400;at<=400000;at+=400)b.advance_to(at);
    require(whole.size()==4800 && parts.size()==whole.size(),"48 kHz count");
    bool heard=false;for(unsigned i=0;i<whole.size();++i){require(whole[i].left==parts[i].left && whole[i].right==parts[i].right,"PCM time partitions");require(whole[i].left==whole[i].right,"OPN mono routing");heard|=whole[i].left!=0;}
    require(heard,"SSG oscillator must produce PCM");auto before=a.samples();a.advance_to(400000);require(a.samples()==before,"zero time must not duplicate PCM");
    for(unsigned channel=1;channel<3;++channel){
        std::vector<StereoSample> values;OpnPcm c(Board::fm26,4000000,{},[&](StereoSample v){values.push_back(v);});
        c.write(0,{0,std::uint8_t(2*channel),132});c.write(0,{0,7,std::uint8_t(63^(1u<<channel))});c.write(0,{0,std::uint8_t(8+channel),15});
        c.write(0,{1,std::uint8_t(8+channel),0}); // absent bank cannot mute real SSG
        c.advance_to(400000);require(values.size()==whole.size(),"SSG B/C sample count");
        for(unsigned n=0;n<values.size();++n)require(values[n].left==whole[n].left && values[n].right==whole[n].right,"three SSG channel routing and absent bank");
    }
    bool rejected=false;try{OpnPcm missing(Board::fm86,8000000,{});}catch(const std::invalid_argument&){rejected=true;}require(rejected,"OPNA ROM required");
    rejected=false;try{a.write(400000,{0,0x2f,0});}catch(const std::invalid_argument&){rejected=true;}require(rejected,"prescaler admission");
    // An IRQ can key-off then key-on at one logical timestamp. A short
    // decaying note must restart, while repeated key-on alone must not.
    for(const auto board:{Board::fm26,Board::speakboard}) {
        const std::uint32_t hz=board==Board::fm26?3993600:7987200;
        auto phrase=[&](bool release){
            std::vector<StereoSample> values;
            OpnPcm chip(board,hz,board==Board::fm26?Bytes{}:Bytes(8192),[&](auto v){values.push_back(v);});
            chip.write(0,{0,0x29,0x83});chip.write(0,{0,7,63});
            for(unsigned slot=0;slot<4;++slot)
                for(auto w:std::vector<FmWrite>{{0,std::uint8_t(0x30+4*slot),1},{0,std::uint8_t(0x40+4*slot),std::uint8_t(slot==3?0:127)},{0,std::uint8_t(0x50+4*slot),31},{0,std::uint8_t(0x60+4*slot),24},{0,std::uint8_t(0x70+4*slot),0},{0,std::uint8_t(0x80+4*slot),0xff}})chip.write(0,w);
            for(auto w:std::vector<FmWrite>{{0,0xb0,7},{0,0xb4,192},{0,0xa4,0x24},{0,0xa0,0x12},{0,0x28,128}})chip.write(0,w);
            chip.advance_to(hz/5);
            if(release)chip.write(hz/5,{0,0x28,0});
            chip.write(hz/5,{0,0x28,128});chip.advance_to(hz*2/5);return values;
        };
        const auto repeated=phrase(true),held=phrase(false);
        auto energy=[](const auto& values,unsigned start){double sum=0;for(unsigned i=start;i<start+480;++i)sum+=double(values[i].left)*values[i].left;return sum;};
        const auto first=energy(repeated,96),second=energy(repeated,9600+96),continued=energy(held,9600+96);
        require(first>1e6 && second>first*0.8 && second<first*1.25,"same-timestamp key-off/on must retrigger the FM envelope");
        require(continued<first*0.01,"held FM key must not retrigger");
    }
    // Independent OPNA tone calibration: a single full-level FM carrier and
    // one SSG square have an RMS ratio near 0.39, not the old ~1.88.
    auto tone=[](bool fm,unsigned period){
        std::vector<StereoSample> values;OpnPcm chip(Board::speakboard,7987200,Bytes(8192),[&](auto v){values.push_back(v);});
        chip.write(0,{0,0x29,0x83});chip.write(0,{0,7,63});
        if(fm){
            for(unsigned slot=0;slot<4;++slot)for(auto w:std::vector<FmWrite>{{0,std::uint8_t(0x30+4*slot),1},{0,std::uint8_t(0x40+4*slot),std::uint8_t(slot==3?0:127)},{0,std::uint8_t(0x50+4*slot),31},{0,std::uint8_t(0x60+4*slot),0},{0,std::uint8_t(0x70+4*slot),0},{0,std::uint8_t(0x80+4*slot),15}})chip.write(0,w);
            for(auto w:std::vector<FmWrite>{{0,0xb0,7},{0,0xb4,192},{0,0xa4,0x24},{0,0xa0,0x12},{0,0x28,128}})chip.write(0,w);
        }else for(auto w:std::vector<FmWrite>{{0,0,std::uint8_t(period)},{0,1,std::uint8_t(period>>8)},{0,7,62},{0,8,15}})chip.write(0,w);
        chip.advance_to(7987200/2);return values;
    };
    const auto fm=tone(true,0),ssg=tone(false,284),high=tone(false,23);
    auto rms=[](const auto& values){double sum=0;for(unsigned n=4800;n<values.size();++n)sum+=double(values[n].left)*values[n].left;return std::sqrt(sum/(values.size()-4800));};
    const double ratio=rms(ssg)/rms(fm);require(ratio>0.34 && ratio<0.44,"OPNA SSG masks the musical FM level");
    auto amplitude=[&](double hz){double re=0,im=0;const auto size=high.size()-4800;constexpr double pi=3.14159265358979323846;
        for(unsigned n=0;n<size;++n){const double weight=0.5-0.5*std::cos(2*pi*n/(size-1)),angle=2*pi*hz*n/48000;re+=weight*high[n+4800].left*std::cos(angle);im+=weight*high[n+4800].left*std::sin(angle);}return std::sqrt(re*re+im*im);};
    const double fundamental=7987200.0/(64*23),folded=48000-7*fundamental;
    require(amplitude(folded)/amplitude(fundamental)<0.0031623,"SSG high harmonic folds into audible noise");
    std::cout<<"CPU-only OPN PCM, SSG tone, 48 kHz count and time partition contracts PASS\n";
}
Bytes read(const char* name){std::ifstream f(name,std::ios::binary);require(bool(f),"PCM input");return Bytes(std::istreambuf_iterator<char>(f),{});}
void write(std::ostream& out,StereoSample sample){for(auto v:{sample.left,sample.right}){const auto word=std::uint16_t(v);out.put(char(word&255));out.put(char(word>>8));}}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}
    require(argc==9,"PMD PCM: music EFC board mirror operations ROM installation output");
    const auto music=read(argv[1]),effects=read(argv[2]),rom=read(argv[6]);const int board=std::stoi(argv[3]);require(board>=0 && board<=2,"PCM board");
    std::ifstream mirror(argv[4]),ops(argv[5]),initial(argv[7]);std::ofstream out(argv[8],std::ios::binary);require(bool(mirror)&&bool(ops)&&bool(initial)&&bool(out),"PCM trace paths");
    char op;std::uint64_t hz;require(bool(ops>>op>>hz) && op=='Q' && hz>=48000 && hz<=1000000000,"PCM frequency");
    PcmPlayer p(Board(board),std::uint32_t(hz),rom,[&](StereoSample v){write(out,v);});p.load_music(music);p.load_effects(effects);
    for(unsigned bank=0;bank<2;++bank)for(unsigned a=0;a<256;++a){unsigned v;require(bool(mirror>>v)&&v<=255,"PCM source mirror");p.mirror(std::uint8_t(bank),std::uint8_t(a),std::uint8_t(v));}
    unsigned bank,address,value;while(initial>>bank>>address>>value){require(bank<2 && address<256 && value<256,"PCM installation register");p.initialize({std::uint8_t(bank),std::uint8_t(address),std::uint8_t(value)});}require(initial.eof(),"PCM installation parse");
    std::int64_t v;while(ops>>op>>v){
        if(op=='R')p.start_music();else if(op=='M')p.stop_music();else if(op=='S')p.stop_effect();else if(op=='H')p.stop_ssg_effect();
        else if(op=='P'){require(v>=0 && v<127,"PCM FM effect ID");p.start_effect(unsigned(v));}
        else if(op=='G'){require(v>=0 && v<40,"PCM SSG effect ID");p.start_ssg_effect(unsigned(v));}
        else if(op=='F'){require(v>=-128 && v<=127,"PCM fade");p.fade(std::int8_t(v));}
        else if(op=='A'){require(v>=0 && v<=1000000000,"PCM nanoseconds");p.advance_ns(std::uint64_t(v));}
        else if(op=='C'){require(v>=0 && v<=1000000000,"PCM cycles");p.advance_cycles(std::uint64_t(v));}
        else throw std::invalid_argument("PCM operation");
    }
    require(ops.eof(),"PCM operation parse");out.close();require(bool(out),"PCM output");return 0;
}catch(const std::exception& e){std::cerr<<"PMD PCM: "<<e.what()<<'\n';return 1;}}
