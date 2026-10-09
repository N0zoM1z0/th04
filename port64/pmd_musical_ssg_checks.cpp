#include "pmd_trace_state.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool value,const char* s){if(!value)throw std::runtime_error(s);}
void row(std::ostream& out,const MusicalFm& m,unsigned size,const std::vector<SsgWrite>& writes){
    write_ssg_music_state(out,m,size);out<<' '<<writes.size();for(auto w:writes)out<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
}
void contract(){
    Bytes data(27,0);const Bytes phrase{240,0,254,2,1,64,4,128};unsigned empty=27;
    for(unsigned p=0;p<12;++p){data[1+p*2]=std::uint8_t(empty-1);data[2+p*2]=0;}data[1]=26;data[13]=27;data[25]=std::uint8_t(27+phrase.size());data.push_back(128);data.insert(data.end(),phrase.begin(),phrase.end());data.push_back(255);
    MusicalFm music;music.load(data);music.start();music.interrupt(2);
    require(music.ssg().registers()[0]==239 && music.ssg().registers()[1]==0,"SSG octave period");require(music.ssg().registers()[8]==6,"SSG signed normal envelope");require((music.ssg().registers()[7]&9)==8,"SSG mixer admission");
    for(unsigned n=0;n<4;++n)music.interrupt(2);require(music.ssg().parts()[0].envelope.mode==2,"SSG release boundary");music.stop();require(music.ssg().registers()[7]==191,"SSG stopped mixer");
    std::cout<<"Shared musical SSG period, signed envelope and release PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contract();return 0;}require(argc==6,"SSG musical trace: song board mirror operations output");const int board=std::stoi(argv[2]);require(board>=0 && board<=2,"SSG musical board");
    std::ifstream song(argv[1],std::ios::binary),mirror(argv[3]),ops(argv[4]);std::ofstream out(argv[5],std::ios::binary);require(bool(song)&&bool(mirror)&&bool(ops)&&bool(out),"SSG musical trace paths");
    Bytes data(std::istreambuf_iterator<char>(song),{});std::vector<SsgWrite> writes;MusicalFm music(Board(board),{},[&](SsgWrite w){writes.push_back(w);});music.load(data);
    for(unsigned bank=0;bank<2;++bank)for(unsigned a=0;a<256;++a){unsigned v;require(bool(mirror>>v)&&v<=255,"SSG musical mirror");music.mirror(std::uint8_t(bank),std::uint8_t(a),std::uint8_t(v));}
    music.start();row(out,music,board ? 98 : 96,writes);char op;int v;
    while(ops>>op>>v){writes.clear();if(op=='I'){require(v>=0 && v<=3,"SSG musical IRQ");music.interrupt(std::uint8_t(v));}else if(op=='S')music.stop();else if(op=='R')music.start();else if(op=='F'){require(v>=-128 && v<=127,"SSG fade");music.fade(std::int8_t(v));}else throw std::invalid_argument("SSG musical operation");row(out,music,board ? 98 : 96,writes);}
    require(ops.eof(),"SSG musical operation parse");out.close();require(bool(out),"SSG musical trace output");return 0;
}catch(const std::exception& e){std::cerr<<"Musical SSG: "<<e.what()<<'\n';return 1;}}
