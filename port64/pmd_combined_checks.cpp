#include "pmd_trace_state.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
bool owned(FmWrite w){return owns_fm_write(w.bank,w.address) || (!w.bank && w.address<14);}
void row(std::ostream& out,const FmPlayer& player,unsigned size,const std::vector<FmWrite>& writes){
    write_fm_player_state(out,player);out<<' ';write_ssg_music_state(out,player.music(),size);
    unsigned count=0;for(auto w:writes)if(owned(w))++count;
    out<<' '<<count;for(auto w:writes)if(owned(w))out<<' '<<unsigned(w.bank)<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
}
void contracts(){
    Bytes data(27,0);for(unsigned p=0;p<12;++p)data[1+2*p]=26;
    data[13]=27;data[25]=35;data.push_back(128);data.insert(data.end(),{240,0,254,2,1,64,8,128});data.push_back(255);
    std::vector<FmWrite> writes;FmPlayer p(Board::fm26,[&](FmWrite w){writes.push_back(w);},[&](SsgWrite w){writes.push_back({0,w.address,w.value});});
    p.load_music(data);p.start_music();p.interrupt(3);require(p.music().ssg().registers()[0]==239,"combined SSG pitch");
    p.start_ssg_effect(0);require(p.music().sequence().state().parts[8].mask==2,"combined SSG admission");
    p.stop_ssg_effect();require(p.music().sequence().state().parts[8].mask==2,"combined premature SSG recovery");
    bool fm=false,ssg=false;for(auto w:writes){fm|=owns_fm_write(w.bank,w.address);ssg|=!w.bank && w.address<14;}
    require(fm && ssg,"combined request surface");std::cout<<"Combined FM/SSG requests and delayed effect occupation PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}require(argc==7,"combined trace: music EFC board mirror operations output");const int board=std::stoi(argv[3]);require(board>=0 && board<=2,"combined board");
    std::ifstream song(argv[1],std::ios::binary),effect(argv[2],std::ios::binary),mirror(argv[4]),ops(argv[5]);std::ofstream out(argv[6],std::ios::binary);require(bool(song)&&bool(effect)&&bool(mirror)&&bool(ops)&&bool(out),"combined paths");
    Bytes music(std::istreambuf_iterator<char>(song),{}),effects(std::istreambuf_iterator<char>(effect),{});std::vector<FmWrite> writes;FmPlayer p(Board(board),[&](FmWrite w){writes.push_back(w);},[&](SsgWrite w){writes.push_back({0,w.address,w.value});});p.load_music(music);p.load_effects(effects);
    for(unsigned bank=0;bank<2;++bank)for(unsigned a=0;a<256;++a){unsigned v;require(bool(mirror>>v)&&v<=255,"combined mirror");p.mirror(std::uint8_t(bank),std::uint8_t(a),std::uint8_t(v));}
    char op;int v;while(ops>>op>>v){writes.clear();
        if(op=='R')p.start_music();else if(op=='M')p.stop_music();else if(op=='S')p.stop_effect();else if(op=='H')p.stop_ssg_effect();
        else if(op=='P'){require(v>=0 && v<127,"combined FM effect ID");p.start_effect(unsigned(v));}
        else if(op=='G'){require(v>=0 && v<40,"combined SSG effect ID");p.start_ssg_effect(unsigned(v));}
        else if(op=='F'){require(v>=-128 && v<=127,"combined fade");p.fade(std::int8_t(v));}
        else if(op=='I'){require(v>=0 && v<=3,"combined IRQ");p.interrupt(std::uint8_t(v));}
        else throw std::invalid_argument("combined operation");row(out,p,board ? 98 : 96,writes);
    }
    require(ops.eof(),"combined operation parse");out.close();require(bool(out),"combined trace output");return 0;
}catch(const std::exception& e){std::cerr<<"Combined PMD: "<<e.what()<<'\n';return 1;}}
