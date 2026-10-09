#include "pmd_musical_fm.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool value,const char* s){if(!value)throw std::runtime_error(s);}
std::vector<unsigned> work(const MusicalFm& music,unsigned part,unsigned size){
    const auto& t=music.sequence().state().parts[part+6];const auto& s=music.ssg().parts()[part];const auto& e=s.envelope;
    std::vector<unsigned> result(size,0);auto word=[&](unsigned at,unsigned v){result.at(at)=v&255;result.at(at+1)=(v>>8)&255;};
    word(0,t.position);word(2,t.loop);result[4]=t.length;result[5]=s.gate;word(6,s.frequency);word(8,std::uint16_t(t.detune));word(12,std::uint16_t(s.slide));word(14,std::uint16_t(s.slide_step));word(16,std::uint16_t(s.slide_remainder));
    result[18]=t.volume;result[19]=t.transpose;result[28]=s.flags;result[29]=s.temporary_volume;result[46]=s.clock_flags;result[48]=s.mixer;result[49]=t.instrument;result[50]=t.loop_status;result[59]=t.mask;result[60]=s.key_flags;result[62]=s.gate_amount;result[63]=s.gate_ratio;
    result[33]=e.mode;result[34]=e.phase;result[35]=e.attack;result[36]=e.decay;result[37]=e.sustain;result[38]=e.release;result[39]=e.sustain_level;result[40]=e.initial_level;result[41]=e.attack_counter;result[42]=e.decay_counter;result[43]=e.sustain_counter;result[44]=e.release_counter;result[45]=e.level;
    result[85]=s.note;result[90]=t.notes;result[91]=s.gate_minimum;result[94]=s.last_note;result[95]=t.master_transpose;if(size>96)result[96]=s.gate_random;
    for(unsigned n=0;n<2;++n){const auto& l=s.lfo[n];unsigned at=n ? 68 : 20;word(n ? 66 : 10,std::uint16_t(l.value));result[at]=l.delay;result[at+1]=l.speed;result[at+2]=std::uint8_t(l.step);result[at+3]=l.count;result[at+4]=l.initial_delay;result[at+5]=l.initial_speed;result[at+6]=std::uint8_t(l.initial_step);result[at+7]=l.initial_count;result[n ? 76 : 30]=std::uint8_t(l.depth_step);result[n ? 77 : 31]=l.depth_speed;result[n ? 78 : 32]=l.initial_depth_speed;result[n ? 79 : 58]=l.shape;result[n ? 80 : 61]=l.mask;result[81+n*2]=l.depth_count;result[82+n*2]=l.initial_depth_count;}
    return result;
}
void row(std::ostream& out,const MusicalFm& m,unsigned size,const std::vector<SsgWrite>& writes){
    const auto& seq=m.sequence();const auto& state=seq.state();const auto& ssg=m.ssg();const auto& effect=seq.ssg_effects().state();
    out<<state.measure<<' '<<unsigned(state.fade)<<' '<<seq.status()<<' '<<unsigned(state.timer_b)<<' '<<unsigned(state.timer_a)<<' '<<unsigned(ssg.attenuation())<<' '<<unsigned(ssg.initial_attenuation())<<' '<<unsigned(ssg.noise())<<' '<<unsigned(ssg.previous_noise());
    for(unsigned p=0;p<3;++p)for(auto v:work(m,p,size))out<<' '<<v;
    out<<' '<<effect.resource<<' '<<effect.next_frame<<' '<<effect.tone<<' '<<effect.tone_step<<' '<<unsigned(effect.ticks)<<' '<<unsigned(effect.noise)<<' '<<int(effect.noise_step)<<' '<<unsigned(effect.noise_interval)<<' '<<unsigned(effect.noise_counter)<<' '<<unsigned(effect.priority)<<' '<<unsigned(effect.effect);
    for(auto v:ssg.registers())out<<' '<<unsigned(v);out<<' '<<writes.size();for(auto w:writes)out<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
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
