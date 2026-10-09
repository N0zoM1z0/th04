#include "pmd_fm_player.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool ok,const char* s){if(!ok)throw std::runtime_error(s);}
bool owned(unsigned b,unsigned a){return (a>=48 && a<=182) || (b==0 && (a==34 || a==40));}
void row(std::ostream& out,const FmPlayer& player,const std::vector<FmWrite>& writes){
    const auto& m=player.music();const auto& seq=m.sequence();const auto& state=seq.state();
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
    const auto& s=player.effects().state();const auto& l=s.lfo;
    out<<' '<<s.active<<' '<<unsigned(s.effect)<<' '<<s.position<<' '<<s.loop<<' '
       <<unsigned(s.ticks)<<' '<<unsigned(s.gate)<<' '<<s.frequency<<' '<<s.detune<<' '
       <<l.value<<' '<<s.slide<<' '<<s.slide_step<<' '<<s.slide_remainder<<' '
       <<unsigned(s.volume)<<' '<<unsigned(s.transpose)<<' '<<unsigned(l.delay)<<' '
       <<unsigned(l.speed)<<' '<<int(l.step)<<' '<<unsigned(l.count)<<' '
       <<unsigned(l.initial_delay)<<' '<<unsigned(l.initial_speed)<<' '<<int(l.initial_step)<<' '
       <<unsigned(l.initial_count)<<' '<<unsigned(s.lfo_flags)<<' '<<unsigned(s.pan)<<' '
       <<unsigned(s.instrument)<<' '<<unsigned(s.loop_status)<<' '<<unsigned(s.carrier_mask);
    for(auto v:s.total_levels)out<<' '<<unsigned(v);
    out<<' '<<unsigned(s.slots)<<' '<<unsigned(s.voice_mask)<<' '<<unsigned(l.shape)<<' '
       <<unsigned(s.key_flags)<<' '<<unsigned(s.lfo_mask)<<' '<<unsigned(s.gate_amount)<<' '
       <<unsigned(s.note)<<' '<<unsigned(s.algorithm)<<' '<<unsigned(s.notes)<<' '
       <<unsigned(s.last_note)<<' '<<unsigned(s.master_transpose);
    unsigned count=0;for(auto w:writes)if(owned(w.bank,w.address))++count;
    out<<' '<<count;for(auto w:writes)if(owned(w.bank,w.address))out<<' '<<unsigned(w.bank)<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
}
void contracts(){
    Bytes data(27,0);const unsigned empty=35,voice=36;
    for(unsigned p=0;p<12;++p){data[1+2*p]=empty-1;data[2+2*p]=0;}data[1]=26;data[5]=26;data[25]=voice-1;
    data.insert(data.end(),{255,0,64,8,68,8,128,128,128});
    data.push_back(0);for(unsigned i=0;i<25;++i)data.push_back(0);data.push_back(255);
    Bytes effects(257,0);for(unsigned i=0;i<128;++i)effects[2*i+1]=1;effects[256]=128;
    FmPlayer p;p.load_music(data);p.load_effects(effects);p.start_music();p.interrupt(2);
    p.start_effect(0);require(p.music().sequence().state().parts[2].mask==2,"FM admission mask");
    p.interrupt(1);require(!p.effects().state().active && p.music().sequence().state().parts[2].mask==2,"FM mask released before musical boundary");
    for(unsigned i=0;i<8;++i)p.interrupt(2);
    require(!p.music().sequence().state().parts[2].mask,"FM mask not recovered at musical boundary");
    require(!p.effects().borrowed_masks()[2],"FM occupation mirror stayed borrowed");
    p.start_effect(0);p.stop_music();p.stop_effect();require(!p.effects().state().active && !p.music().sequence().state().playing,"FM stop ownership");
    std::cout<<"FM music/effect occupation, delayed recovery and independent stop PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}require(argc==7,"FM player trace: music EFC board mirror operations output");
    const int board=std::stoi(argv[3]);require(board>=0 && board<=2,"FM player board");
    std::ifstream song(argv[1],std::ios::binary),effect(argv[2],std::ios::binary),mirror(argv[4]),ops(argv[5]);std::ofstream out(argv[6],std::ios::binary);
    require(bool(song)&&bool(effect)&&bool(mirror)&&bool(ops)&&bool(out),"FM player trace paths");
    Bytes music(std::istreambuf_iterator<char>(song),{}),effects(std::istreambuf_iterator<char>(effect),{});std::vector<FmWrite> writes;
    FmPlayer p(Board(board),[&](FmWrite w){writes.push_back(w);});p.load_music(music);p.load_effects(effects);
    for(unsigned b=0;b<2;++b)for(unsigned a=0;a<256;++a){unsigned v;require(bool(mirror>>v)&&v<=255,"FM player mirror vector");p.mirror(std::uint8_t(b),std::uint8_t(a),std::uint8_t(v));}
    char op;int value;while(ops>>op>>value){writes.clear();
        if(op=='R')p.start_music();else if(op=='M')p.stop_music();else if(op=='S')p.stop_effect();
        else if(op=='P'){require(value>=0 && value<127,"FM player effect ID");p.start_effect(unsigned(value));}
        else if(op=='F'){require(value>=-128 && value<=127,"FM player fade");p.fade(std::int8_t(value));}
        else if(op=='I'){require(value>=0 && value<=3,"FM player IRQ");p.interrupt(std::uint8_t(value));}
        else throw std::invalid_argument("FM player operation");row(out,p,writes);
    }require(ops.eof(),"FM player operation parse");out.close();require(bool(out),"FM player trace write");return 0;
}catch(const std::exception& e){std::cerr<<"FM player: "<<e.what()<<'\n';return 1;}}
