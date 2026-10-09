#include "pmd_pcm.hpp"
#include <fstream>
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
