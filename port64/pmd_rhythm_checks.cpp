#include "pmd_trace_state.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pmd;
namespace {
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
bool owned(FmWrite w){return owns_fm_write(w.bank,w.address) || (!w.bank && (w.address<14 || (w.address>=16 && w.address<32)));}
void row(std::ostream& out,const FmPlayer& player,unsigned size,const std::vector<FmWrite>& writes){
    const auto& music=player.music();write_fm_player_state(out,player);out<<' ';write_ssg_music_state(out,music,size);
    const auto& s=music.sequence().state();out<<' '<<unsigned(std::uint8_t(s.fade_speed))<<' '<<s.musical_fade_requested<<' '<<(s.stop_pending ? 2 : 0)<<' '<<s.playing<<' '<<s.auto_stop_on_fade;
    const auto& t=s.parts[10];out<<' '<<t.position<<' '<<t.loop<<' '<<unsigned(t.length)<<' '<<unsigned(t.loop_status)<<' '<<unsigned(t.notes)<<' '<<unsigned(t.volume)<<' '<<unsigned(t.transpose)<<' '<<unsigned(t.master_transpose)<<' '<<t.detune<<' '<<unsigned(t.instrument)<<' '<<unsigned(t.mask);
    const auto& r=music.rhythm().state();out<<' '<<unsigned(r.attenuation)<<' '<<unsigned(r.initial_attenuation)<<' '<<unsigned(r.mask)<<' '<<r.enabled<<' '<<unsigned(r.active)<<' '<<unsigned(r.total)<<' '<<r.request;
    for(auto v:r.levels)out<<' '<<unsigned(v);for(auto v:r.starts)out<<' '<<unsigned(v);for(auto v:r.stops)out<<' '<<unsigned(v);
    for(unsigned a=16;a<32;++a)out<<' '<<unsigned(music.registers()[0][a]);
    unsigned count=0;for(auto w:writes)if(owned(w))++count;out<<' '<<count;for(auto w:writes)if(owned(w))out<<' '<<unsigned(w.bank)<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
}
void contracts(){
    State music;std::vector<FmWrite> writes;Rhythm r(Board::fm86,[&](FmWrite w){writes.push_back(w);});r.start();writes.clear();
    r.event({Kind::rhythm,10,0,128,{128,2}},music);require(writes.size()==3 && writes[1].address==16 && writes[1].value==132 && writes[2].value==8,"rhythm retrigger order");
    writes.clear();music.parts[10].mask=64;r.event({Kind::rhythm,10,0,128,{1,2}},music);require(writes.empty() && !r.state().request,"masked rhythm request");
    r.event({Kind::command,0,0,235,{1}},music);r.event({Kind::command,0,0,235,{129}},music);require(r.state().starts[0]==1 && r.state().stops[0]==1 && !r.state().active,"explicit rhythm counters");
    r.start();require(r.state().starts[0]==1 && r.state().stops[0]==1,"rhythm counters across restart");
    std::cout<<"Hardware rhythm retrigger, mask and retained counters PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}require(argc==7,"PMD rhythm: music EFC board mirror operations output");const int board=std::stoi(argv[3]);require(board>=0 && board<=2,"rhythm board");
    std::ifstream song(argv[1],std::ios::binary),effect(argv[2],std::ios::binary),mirror(argv[4]),ops(argv[5]);std::ofstream out(argv[6],std::ios::binary);require(bool(song)&&bool(effect)&&bool(mirror)&&bool(ops)&&bool(out),"rhythm paths");
    Bytes data(std::istreambuf_iterator<char>(song),{}),effects(std::istreambuf_iterator<char>(effect),{});std::vector<FmWrite> writes;FmPlayer p(Board(board),[&](FmWrite w){writes.push_back(w);},[&](SsgWrite w){writes.push_back({0,w.address,w.value});});p.load_music(data);p.load_effects(effects);
    for(unsigned bank=0;bank<2;++bank)for(unsigned a=0;a<256;++a){unsigned v;require(bool(mirror>>v)&&v<=255,"rhythm mirror");p.mirror(std::uint8_t(bank),std::uint8_t(a),std::uint8_t(v));}
    char op;int v;while(ops>>op>>v){writes.clear();
        if(op=='R')p.start_music();else if(op=='M')p.stop_music();else if(op=='S')p.stop_effect();else if(op=='H')p.stop_ssg_effect();
        else if(op=='P'){require(v>=0 && v<127,"rhythm FM effect ID");p.start_effect(unsigned(v));}
        else if(op=='G'){require(v>=0 && v<40,"rhythm SSG effect ID");p.start_ssg_effect(unsigned(v));}
        else if(op=='F'){require(v>=-128 && v<=127,"rhythm fade");p.fade(std::int8_t(v));}
        else if(op=='I'){require(v>=0 && v<=3,"rhythm IRQ");p.interrupt(std::uint8_t(v));}
        else throw std::invalid_argument("rhythm operation");row(out,p,board ? 98 : 96,writes);
    }
    require(ops.eof(),"rhythm operation parse");out.close();require(bool(out),"rhythm output");return 0;
}catch(const std::exception& e){std::cerr<<"PMD rhythm: "<<e.what()<<'\n';return 1;}}
