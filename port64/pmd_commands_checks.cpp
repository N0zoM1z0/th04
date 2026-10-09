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
    const auto& state=player.music().sequence().state();
    out<<' '<<unsigned(std::uint8_t(state.fade_speed))<<' '<<state.musical_fade_requested<<' '<<(state.stop_pending ? 2 : 0)<<' '<<state.playing<<' '<<state.auto_stop_on_fade;
    unsigned count=0;for(auto w:writes)if(owned(w))++count;
    out<<' '<<count;for(auto w:writes)if(owned(w))out<<' '<<unsigned(w.bank)<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
}
Bytes song(unsigned part,const Bytes& program){
    Bytes data(27,0);auto word=[&](unsigned at,unsigned value){data.at(at)=value&255;data.at(at+1)=value>>8;};
    for(unsigned p=0;p<11;++p){word(1+2*p,data.size()-1);if(p==part)data.insert(data.end(),program.begin(),program.end());else data.push_back(128);}
    word(23,data.size()-1);const unsigned table=data.size();data.push_back((table+1)&255);data.push_back((table+1)>>8);data.push_back(128);word(25,data.size()-1);data.push_back(255);return data;
}
void contracts(){
    Sequence s;s.load(song(0,{210,127,64,64,128}));s.start();s.interrupt(2);
    for(unsigned n=0;n<24;++n)s.interrupt(1);
    require(s.state().musical_fade_requested && s.state().stop_pending && s.state().playing,"fade deferred request");
    s.interrupt(0);s.interrupt(1);require(s.state().playing,"fade consumed without Timer B");
    s.interrupt(2);require(!s.state().playing && s.state().musical_fade_requested && !s.state().stop_pending,"fade completion marker");
    s.stop();require(!s.state().musical_fade_requested,"explicit stop marker");
    unsigned fm=0;Sequence masked;masked.fm_effect_command([&](unsigned id){fm+=id;});
    masked.load(song(6,{192,1,212,11,211,4,210,0,64,2,128}));masked.start();masked.interrupt(2);
    require(!fm && !masked.ssg_effects().state().priority && masked.state().musical_fade_requested,"musical mask versus global fade");
    Sequence trigger;trigger.load(song(6,{212,11,64,2,212,0,65,2,128}));trigger.start();trigger.interrupt(2);
    require(trigger.ssg_effects().state().priority==2 && (trigger.state().parts[8].mask&2),"musical SSG trigger");
    trigger.interrupt(2);trigger.interrupt(2);require(!trigger.ssg_effects().state().priority,"musical SSG stop");
    std::cout<<"Musical effect mask guards and deferred fade stop PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}require(argc==7,"PMD commands trace: music EFC board mirror operations output");const int board=std::stoi(argv[3]);require(board>=0 && board<=2,"combined board");
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
}catch(const std::exception& e){std::cerr<<"PMD commands: "<<e.what()<<'\n';return 1;}}
