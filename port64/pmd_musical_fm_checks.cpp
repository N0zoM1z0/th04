#include "pmd_musical_fm.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool ok,const char* s){if(!ok)throw std::runtime_error(s);}
bool owned(unsigned b,unsigned a){return (a>=48 && a<=182) || (b==0 && (a==34 || a==40));}
void row(std::ostream& out,const MusicalFm& m,const std::vector<FmWrite>& writes){
    const auto& seq=m.sequence();const auto& state=seq.state();
    out<<state.measure<<' '<<unsigned(state.fade)<<' '<<seq.status()<<' '<<unsigned(state.timer_b)<<' '<<unsigned(state.timer_a);
    for(unsigned p=0;p<6;++p){
        const auto& t=state.parts[p];const auto& s=m.parts()[p];
        out<<' '<<t.position<<' '<<t.loop<<' '<<unsigned(t.length)<<' '<<unsigned(t.loop_status)<<' '<<unsigned(t.notes)<<' '<<unsigned(t.volume)<<' '<<unsigned(t.transpose)<<' '<<unsigned(t.master_transpose)<<' '<<t.detune<<' '<<unsigned(t.instrument)<<' '<<unsigned(t.mask);
        out<<' '<<unsigned(s.gate)<<' '<<s.frequency<<' '<<s.slide<<' '<<s.slide_step<<' '<<s.slide_remainder<<' '<<unsigned(s.flags)<<' '<<unsigned(s.clock_flags)<<' '<<unsigned(s.temporary_volume)<<' '<<unsigned(s.pan)<<' '<<unsigned(s.carrier_mask)<<' '<<unsigned(s.slots)<<' '<<unsigned(s.voice_mask);
        for(auto v:s.total_levels)out<<' '<<unsigned(v);
        out<<' '<<unsigned(s.key_flags)<<' '<<unsigned(s.note)<<' '<<unsigned(s.last_note)<<' '<<unsigned(s.algorithm)<<' '<<unsigned(s.gate_amount)<<' '<<unsigned(s.gate_ratio)<<' '<<unsigned(s.gate_minimum)<<' '<<unsigned(s.gate_random)<<' '<<unsigned(s.hardware_delay)<<' '<<unsigned(s.hardware_counter)<<' '<<unsigned(s.key_delay)<<' '<<unsigned(s.key_counter)<<' '<<unsigned(s.key_mask);
        for(const auto& l:s.lfo)out<<' '<<l.value<<' '<<unsigned(l.delay)<<' '<<unsigned(l.speed)<<' '<<int(l.step)<<' '<<unsigned(l.count)<<' '<<unsigned(l.initial_delay)<<' '<<unsigned(l.initial_speed)<<' '<<int(l.initial_step)<<' '<<unsigned(l.initial_count)<<' '<<unsigned(l.shape)<<' '<<unsigned(l.mask)<<' '<<int(l.depth_step)<<' '<<unsigned(l.depth_speed)<<' '<<unsigned(l.initial_depth_speed)<<' '<<unsigned(l.depth_count)<<' '<<unsigned(l.initial_depth_count);
    }
    for(unsigned b=0;b<2;++b)for(unsigned a=0;a<256;++a)if(owned(b,a))out<<' '<<unsigned(m.registers()[b][a]);
    unsigned count=0;for(auto w:writes)if(owned(w.bank,w.address))++count;
    out<<' '<<count;for(auto w:writes)if(owned(w.bank,w.address))out<<' '<<unsigned(w.bank)<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
}
void contracts(){
    Bytes data(27,0);data[0]=0;for(unsigned p=0;p<13;++p){data[1+p*2]=33;data[2+p*2]=0;}data[1]=26;data[25]=34;
    // FM A has a four-tick note and a two-tick release gate.
    data.insert(data.end(),{254,2,64,4,15,2,128,128,255});
    MusicalFm m; m.load(data);m.start();m.interrupt(2);
    require(m.parts()[0].frequency!=0 && m.parts()[0].gate==2,"musical FM note/gate decode");
    const auto frequency=m.parts()[0].frequency;m.interrupt(1);require(m.parts()[0].frequency==frequency && m.sequence().state().parts[0].length==4,"Timer A advanced musical note");
    m.interrupt(2);m.interrupt(2);require(m.parts()[0].key_flags==255 && m.registers()[0][40]==0,"musical gate did not release before note end");
    m.stop();const auto notes=m.sequence().state().parts[0].notes;m.interrupt(3);require(m.sequence().state().parts[0].notes==notes,"stopped musical FM advanced");
    std::cout<<"Musical FM note/gate, Timer A independence and stopped-state PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}require(argc==6,"Musical FM trace: song board mirror operations output");
    const int board=std::stoi(argv[2]);require(board>=0 && board<=2,"musical FM board");
    std::ifstream file(argv[1],std::ios::binary),mirror(argv[3]),ops(argv[4]);std::ofstream out(argv[5],std::ios::binary);require(bool(file)&&bool(mirror)&&bool(ops)&&bool(out),"musical FM trace paths");
    Bytes bytes(std::istreambuf_iterator<char>(file),{});std::vector<FmWrite> writes;MusicalFm m(Board(board),[&](FmWrite w){writes.push_back(w);});m.load(bytes);
    for(unsigned b=0;b<2;++b)for(unsigned a=0;a<256;++a){unsigned v;require(bool(mirror>>v)&&v<=255,"musical FM mirror vector");m.mirror(std::uint8_t(b),std::uint8_t(a),std::uint8_t(v));}
    m.start();row(out,m,writes);char op;int value;
    while(ops>>op>>value){writes.clear();
        if(op=='I'){require(value>=0 && value<=3,"musical FM interrupt flags");m.interrupt(std::uint8_t(value));}
        else if(op=='F'){require(value>=-128 && value<=127,"musical FM fade speed");m.fade(std::int8_t(value));}
        else if(op=='S')m.stop();else if(op=='R')m.start();else throw std::invalid_argument("musical FM operation");row(out,m,writes);
    }
    require(ops.eof(),"musical FM operations parse");out.close();require(bool(out),"musical FM output");return 0;
}catch(const std::exception& e){std::cerr<<"Musical FM: "<<e.what()<<'\n';return 1;}}
