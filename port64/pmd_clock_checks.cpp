#include "pmd_trace_state.hpp"
#include "pmd_clock.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
bool owned(FmWrite w){return owns_fm_write(w.bank,w.address) || (!w.bank && (w.address<14 || (w.address>=16 && w.address<32) || (w.address>=0x24 && w.address<=0x27)));}
void row(std::ostream& out,const FmPlayer& player,unsigned size,const std::vector<FmWrite>& writes){
    const auto& music=player.music();write_fm_player_state(out,player);out<<' ';write_ssg_music_state(out,music,size);
    const auto& s=music.sequence().state();out<<' '<<unsigned(std::uint8_t(s.fade_speed))<<' '<<s.musical_fade_requested<<' '<<(s.stop_pending ? 2 : 0)<<' '<<s.playing<<' '<<s.auto_stop_on_fade;
    const auto& t=s.parts[10];out<<' '<<t.position<<' '<<t.loop<<' '<<unsigned(t.length)<<' '<<unsigned(t.loop_status)<<' '<<unsigned(t.notes)<<' '<<unsigned(t.volume)<<' '<<unsigned(t.transpose)<<' '<<unsigned(t.master_transpose)<<' '<<t.detune<<' '<<unsigned(t.instrument)<<' '<<unsigned(t.mask);
    const auto& r=music.rhythm().state();out<<' '<<unsigned(r.attenuation)<<' '<<unsigned(r.initial_attenuation)<<' '<<unsigned(r.mask)<<' '<<r.enabled<<' '<<unsigned(r.active)<<' '<<unsigned(r.total)<<' '<<r.request;
    for(auto v:r.levels)out<<' '<<unsigned(v);for(auto v:r.starts)out<<' '<<unsigned(v);for(auto v:r.stops)out<<' '<<unsigned(v);
    for(unsigned a=16;a<32;++a)out<<' '<<unsigned(music.registers()[0][a]);
    for(unsigned a=0x24;a<=0x27;++a)out<<' '<<unsigned(music.registers()[0][a]);
    unsigned count=0;for(auto w:writes)if(owned(w))++count;out<<' '<<count;for(auto w:writes)if(owned(w))out<<' '<<unsigned(w.bank)<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
}
void clockrow(std::ostream& out,const ClockedPlayer& p,unsigned size,std::uint8_t flags,const std::vector<FmWrite>& writes){
    const auto& t=p.timers();out<<t.cycles()<<' '<<unsigned(t.status())<<' '<<t.deadline(0)<<' '<<t.deadline(1)<<' '<<p.interrupts()<<' '<<unsigned(flags)<<' ';
    row(out,p.player(),size,writes);
}
void contracts(){
    OpnTimers t(Board::fm86);t.write(0x29,131);t.write(0x24,255);t.write(0x25,3);t.write(0x26,255);t.write(0x27,15);
    require(t.deadline(0)==144 && t.deadline(1)==2304,"default timer quantum");
    t.advance(100,{});t.write(0x26,254);t.write(0x27,63);
    require(t.deadline(0)==144 && t.deadline(1)==2304,"ack/tempo preserve deadlines");
    unsigned both=0;t.advance(2204,[&](std::uint8_t flags){if(flags==3)++both;t.write(0x27,63);});
    require(both==1 && t.deadline(1)==6912,"coincident status and old deadline reload");
    t.write(0x27,0);t.advance(144*7,{});t.write(0x27,10);
    require(t.deadline(1)==t.cycles()+(32-7)*144,"free-running B initial divider phase");
    t.write(0x29,0);unsigned calls=0;t.advance(10000,[&](std::uint8_t){++calls;});
    require(!calls && t.status()==2,"IRQ mask retains status");
    t.write(0x27,32);require(t.status()==0 && !t.deadline(1),"stop and clear B");
    ClockedPlayer a(Board::fm26,3993600),b(Board::fm26,3993600);
    a.advance_ns(999999999);for(unsigned n=0;n<999;++n)b.advance_ns(1000000);b.advance_ns(999999);
    require(a.timers().cycles()==b.timers().cycles() && a.fraction()==b.fraction() && a.interrupts()==b.interrupts(),"nanosecond partition invariance");
    const auto before=a.timers().cycles();const auto count=a.interrupts();a.advance_ns(0);a.stop_music();
    require(before==a.timers().cycles() && count==a.interrupts(),"zero time and stop preserve clock");
    a.advance_ns(100000000);require(a.interrupts()>count,"resident IRQ after song stop");
    bool rejected=false;try{a.advance_ns(1000000001);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"bounded host step");
    std::cout<<"Continuous resident OPN clocks, reload phase, simultaneous flags and rational time PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}require(argc==7,"PMD clock: music EFC board mirror operations output");const int board=std::stoi(argv[3]);require(board>=0 && board<=2,"clock board");
    std::ifstream song(argv[1],std::ios::binary),effect(argv[2],std::ios::binary),mirror(argv[4]),ops(argv[5]);std::ofstream out(argv[6],std::ios::binary);require(bool(song)&&bool(effect)&&bool(mirror)&&bool(ops)&&bool(out),"clock paths");
    char op;std::uint64_t hz;require(bool(ops>>op>>hz) && op=='Q' && hz>0 && hz<=1000000000,"explicit master frequency");
    Bytes data(std::istreambuf_iterator<char>(song),{}),effects(std::istreambuf_iterator<char>(effect),{});std::vector<FmWrite> writes;
    ClockedPlayer p(Board(board),std::uint32_t(hz),[&](FmWrite w){writes.push_back(w);},[&](SsgWrite w){writes.push_back({0,w.address,w.value});});p.load_music(data);p.load_effects(effects);
    for(unsigned bank=0;bank<2;++bank)for(unsigned a=0;a<256;++a){unsigned v;require(bool(mirror>>v)&&v<=255,"clock mirror");p.mirror(std::uint8_t(bank),std::uint8_t(a),std::uint8_t(v));}
    p.on_interrupt([&](std::uint64_t,std::uint8_t flags){clockrow(out,p,board ? 98 : 96,flags,writes);writes.clear();});
    std::int64_t v;while(ops>>op>>v){writes.clear();
        if(op=='R')p.start_music();else if(op=='M')p.stop_music();else if(op=='S')p.stop_effect();else if(op=='H')p.stop_ssg_effect();
        else if(op=='P'){require(v>=0 && v<127,"clock FM effect ID");p.start_effect(unsigned(v));}
        else if(op=='G'){require(v>=0 && v<40,"clock SSG effect ID");p.start_ssg_effect(unsigned(v));}
        else if(op=='F'){require(v>=-128 && v<=127,"clock fade");p.fade(std::int8_t(v));}
        else if(op=='A'){require(v>=0 && v<=1000000000,"clock nanoseconds");p.advance_ns(std::uint64_t(v));}
        else if(op=='C'){require(v>=0 && v<=1000000000,"clock cycles");p.advance_cycles(std::uint64_t(v));}
        else throw std::invalid_argument("clock operation");clockrow(out,p,board ? 98 : 96,0,writes);
    }
    require(ops.eof(),"clock operation parse");out.close();require(bool(out),"clock output");return 0;
}catch(const std::exception& e){std::cerr<<"PMD clock: "<<e.what()<<'\n';return 1;}}
