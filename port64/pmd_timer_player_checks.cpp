#include "pmd_trace_state.hpp"
#include "pmd_timer_player.hpp"
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
void contracts(){
    std::vector<FmWrite> writes;TimerPlayer p(Board::fm86,[&](FmWrite w){writes.push_back(w);});
    Bytes song(30,128);song[0]=0;
    for(unsigned at=1;at<27;at+=2){song[at]=26;song[at+1]=0;}
    song[25]=28;song[29]=255;p.load_music(song);p.start_music();
    require(writes.size()>=3,"missing timer initialization");
    const auto n=writes.size();require(writes[n-3].address==0x25 && writes[n-2].address==0x24 && writes[n-1].address==0x27 && writes[n-1].value==0x3f,"timer initialization order");
    writes.clear();p.interrupt(0);require(writes.empty(),"empty IRQ must not acknowledge");
    p.stop_music();writes.clear();p.interrupt(1);
    require(writes.size()==1 && writes[0].address==0x27 && p.player().music().sequence().state().timer_a==1,"resident timer survives music stop");
    bool rejected=false;try{p.interrupt(4);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"timer flag admission");
    std::cout<<"Resident timer startup order, no-status IRQ and stopped Timer A PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}require(argc==7,"PMD timer player: music EFC board mirror operations output");const int board=std::stoi(argv[3]);require(board>=0 && board<=2,"timer board");
    std::ifstream song(argv[1],std::ios::binary),effect(argv[2],std::ios::binary),mirror(argv[4]),ops(argv[5]);std::ofstream out(argv[6],std::ios::binary);require(bool(song)&&bool(effect)&&bool(mirror)&&bool(ops)&&bool(out),"timer paths");
    Bytes data(std::istreambuf_iterator<char>(song),{}),effects(std::istreambuf_iterator<char>(effect),{});std::vector<FmWrite> writes;TimerPlayer p(Board(board),[&](FmWrite w){writes.push_back(w);},[&](SsgWrite w){writes.push_back({0,w.address,w.value});});p.load_music(data);p.load_effects(effects);
    for(unsigned bank=0;bank<2;++bank)for(unsigned a=0;a<256;++a){unsigned v;require(bool(mirror>>v)&&v<=255,"timer mirror");p.mirror(std::uint8_t(bank),std::uint8_t(a),std::uint8_t(v));}
    char op;int v;while(ops>>op>>v){writes.clear();
        if(op=='R')p.start_music();else if(op=='M')p.stop_music();else if(op=='S')p.stop_effect();else if(op=='H')p.stop_ssg_effect();
        else if(op=='P'){require(v>=0 && v<127,"timer FM effect ID");p.start_effect(unsigned(v));}
        else if(op=='G'){require(v>=0 && v<40,"timer SSG effect ID");p.start_ssg_effect(unsigned(v));}
        else if(op=='F'){require(v>=-128 && v<=127,"timer fade");p.fade(std::int8_t(v));}
        else if(op=='I'){require(v>=0 && v<=3,"timer IRQ");p.interrupt(std::uint8_t(v));}
        else throw std::invalid_argument("timer operation");row(out,p.player(),board ? 98 : 96,writes);
    }
    require(ops.eof(),"timer operation parse");out.close();require(bool(out),"timer output");return 0;
}catch(const std::exception& e){std::cerr<<"PMD timer player: "<<e.what()<<'\n';return 1;}}
