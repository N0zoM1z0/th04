#include "pmd_fm_effects.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool b,const char* message){if(!b)throw std::runtime_error(message);}
void row(std::ostream& out,const FmEffects& p,const std::vector<FmWrite>& writes) {
    const auto& s=p.state();const auto& l=s.lfo;
    out<<s.active<<' '<<unsigned(s.effect)<<' '<<s.position<<' '<<s.loop<<' '
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
    for(auto v:p.borrowed_masks())out<<' '<<unsigned(v);
    for(const auto& bank:p.registers())for(auto v:bank)out<<' '<<unsigned(v);
    out<<' '<<writes.size();for(auto w:writes)out<<' '<<unsigned(w.bank)<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);
    out<<'\n';
}
void contracts() {
    Bytes resource(257,0);for(unsigned i=0;i<128;++i){resource[i*2]=0;resource[i*2+1]=1;}resource[256]=128;
    std::vector<FmWrite> writes;unsigned releases=0;FmEffects p(Board::fm86,[&](FmWrite w){writes.push_back(w);},[&](){++releases;});
    p.load(resource);p.start(0);require(p.state().active && p.borrowed_masks()[5]==2,"FM effect channel admission");
    p.timer_a();require(!p.state().active && p.state().effect==255 && releases==1,"FM empty effect release");
    const auto count=writes.size();p.timer_a();p.stop();require(writes.size()==count,"inactive FM effect writes");
    p.start(1);p.start(2);require(releases==2 && p.state().effect==2,"FM effect restart must release predecessor");
    bool rejected=false;try{p.start(127);}catch(const std::out_of_range&){rejected=true;}require(rejected,"FM voice-bank entry accepted as effect");
    std::cout<<"PMD FM effect channel, marker release, restart and admission PASS\n";
}
}
int main(int argc,char** argv) {
    try {
        if(argc==1){contracts();return 0;}
        require(argc==6,"FM trace: EFC board mirror operations output");
        const auto board=std::stoi(argv[2]);require(board>=0 && board<=2,"FM board");
        std::ifstream file(argv[1],std::ios::binary);require(bool(file),"FM EFC read");Bytes bytes(std::istreambuf_iterator<char>(file),{});
        std::vector<FmWrite> writes;FmEffects p(Board(board),[&](FmWrite w){writes.push_back(w);});p.load(bytes);
        std::ifstream mirror(argv[3]),ops(argv[4]);std::ofstream out(argv[5],std::ios::binary);require(bool(mirror)&&bool(ops)&&bool(out),"FM trace paths");
        for(unsigned bank=0;bank<2;++bank)for(unsigned reg=0;reg<256;++reg){unsigned value;require(bool(mirror>>value)&&value<=255,"FM mirror vector");p.mirror(std::uint8_t(bank),std::uint8_t(reg),std::uint8_t(value));}
        char op;int value;
        while(ops>>op>>value) {
            writes.clear();
            if(op=='P'){require(value>=0 && value<127,"FM effect index");p.start(unsigned(value));}
            else if(op=='S')p.stop();
            else if(op=='T'){require(value>=0 && value<=3,"FM timer status");if(value&1)p.timer_a();}
            else throw std::invalid_argument("FM operation");
            row(out,p,writes);
        }
        require(ops.eof(),"FM operation parse");out.close();require(bool(out),"FM trace write");return 0;
    }catch(const std::exception& e){std::cerr<<"PMD FM: "<<e.what()<<'\n';return 1;}
}
