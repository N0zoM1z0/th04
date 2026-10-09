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

    for(auto v:music.fm3_detune())out<<' '<<v;
    out<<' '<<unsigned(music.fm3_detuned())<<' '<<unsigned(music.fm3_flags())<<' '<<unsigned(music.fm3_algorithm())<<' '<<unsigned(music.fm3_mode())<<' '<<unsigned(music.fm3_pending());
    const auto& m=music;const auto& state=m.sequence().state();
    for(unsigned n=0;n<3;++n){const unsigned p=size==96 ? n+3 : n+11;

        const auto& t=state.parts[p];const auto& s=m.parts()[p<6 ? p : p-5];
        out<<' '<<t.position<<' '<<t.loop<<' '<<unsigned(t.length)<<' '<<unsigned(t.loop_status)<<' '<<unsigned(t.notes)<<' '<<unsigned(t.volume)<<' '<<unsigned(t.transpose)<<' '<<unsigned(t.master_transpose)<<' '<<t.detune<<' '<<unsigned(t.instrument)<<' '<<unsigned(t.mask);
        out<<' '<<unsigned(s.gate)<<' '<<s.frequency<<' '<<s.slide<<' '<<s.slide_step<<' '<<s.slide_remainder<<' '<<unsigned(s.flags)<<' '<<unsigned(s.clock_flags)<<' '<<unsigned(s.temporary_volume)<<' '<<unsigned(s.pan)<<' '<<unsigned(s.carrier_mask)<<' '<<unsigned(s.slots)<<' '<<unsigned(s.voice_mask);
        for(auto v:s.total_levels)out<<' '<<unsigned(v);
        out<<' '<<unsigned(s.key_flags)<<' '<<unsigned(s.note)<<' '<<unsigned(s.last_note)<<' '<<unsigned(s.algorithm)<<' '<<unsigned(s.gate_amount)<<' '<<unsigned(s.gate_ratio)<<' '<<unsigned(s.gate_minimum)<<' '<<unsigned(s.gate_random)<<' '<<unsigned(s.hardware_delay)<<' '<<unsigned(s.hardware_counter)<<' '<<unsigned(s.key_delay)<<' '<<unsigned(s.key_counter)<<' '<<unsigned(s.key_mask);
        for(const auto& l:s.lfo)out<<' '<<l.value<<' '<<unsigned(l.delay)<<' '<<unsigned(l.speed)<<' '<<int(l.step)<<' '<<unsigned(l.count)<<' '<<unsigned(l.initial_delay)<<' '<<unsigned(l.initial_speed)<<' '<<int(l.initial_step)<<' '<<unsigned(l.initial_count)<<' '<<unsigned(l.shape)<<' '<<unsigned(l.mask)<<' '<<int(l.depth_step)<<' '<<unsigned(l.depth_speed)<<' '<<unsigned(l.initial_depth_speed)<<' '<<unsigned(l.depth_count)<<' '<<unsigned(l.initial_depth_count);
    }
    unsigned count=0;for(auto w:writes)if(owned(w))++count;out<<' '<<count;for(auto w:writes)if(owned(w))out<<' '<<unsigned(w.bank)<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);out<<'\n';
}
void contracts(){
    // This generated resource assigns each FM3 operator to a different track.
    for(Board board:{Board::fm26,Board::speakboard,Board::fm86}){
        Bytes song(27,0),effect(257,0);std::vector<FmWrite> writes;
        auto put=[&](unsigned at,unsigned value){song[at]=std::uint8_t(value);song[at+1]=std::uint8_t(value>>8);};
        for(unsigned n=0;n<11;++n){put(1+n*2,unsigned(song.size()-1));song.push_back(128);}
        put(23,unsigned(song.size()-1));song.insert(song.end(),{0,0});
        put(5,unsigned(song.size()-1));
        const unsigned primary=unsigned(song.size());
        song.insert(song.end(),{255,7,207,17,198,0,0,0,0,0,0,200,15,1,0,64,4,128});
        for(unsigned n=0;n<3;++n){
            put(primary+5+n*2,unsigned(song.size()-1));
            song.insert(song.end(),{207,std::uint8_t(32u<<n),255,7,std::uint8_t(65+n),4,128});
        }
        put(25,unsigned(song.size()-1));
        for(std::uint8_t id:{std::uint8_t(0),std::uint8_t(7)})
            song.insert(song.end(),{id,1,1,1,1,12,20,30,0,31,31,31,31,7,7,7,7,3,3,3,3,15,15,15,15,60});
        song.push_back(255);
        for(unsigned n=0;n<128;++n){effect[n*2]=0;effect[n*2+1]=1;}effect[256]=128;
        TimerPlayer player(board,[&](FmWrite w){writes.push_back(w);});player.load_music(song);player.load_effects(effect);player.start_music();writes.clear();player.interrupt(2);
        const auto& music=player.player().music();
        require(music.fm3_mode()==127 && music.fm3_flags()==15 && music.fm3_detuned(),"FM3 shared mode ownership");
        for(auto value:music.fm3_detune())require(value==1,"FM3 per-operator detune");
        for(unsigned n=0;n<3;++n){const unsigned p=board==Board::fm26 ? n+3 : n+11;
            require(music.sequence().state().parts[p].notes==1 && music.sequence().state().parts[p].volume==108,"FM3 extension parse");
        }
        unsigned frequencies=0;for(auto w:writes)if(w.bank==0 && (w.address==0xa2 || w.address==0xa8 || w.address==0xaa || w.address==0xa9))++frequencies;
        require(frequencies>=4,"FM3 independent operator pitches");
        player.start_effect(0);
        if(board==Board::fm26)require(music.fm3_mode()==63 && music.fm3_pending()==127,"FM26 borrowed mode");
        player.interrupt(1);require(!player.player().effects().state().active && music.fm3_mode()==127,"FM3 effect release mode");
        player.start_music();player.interrupt(2);
        const unsigned extra=board==Board::fm26 ? 3 : 11;
        require(music.sequence().state().parts[extra].notes==2,"FM3 restart preserves note counter");
    }
    std::cout<<"FM3 operator ownership, appended/alias tracks, special pitch, effect release and restart PASS\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}require(argc==7,"PMD FM3 player: music EFC board mirror operations output");const int board=std::stoi(argv[3]);require(board>=0 && board<=2,"timer board");
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
}catch(const std::exception& e){std::cerr<<"PMD FM3 player: "<<e.what()<<'\n';return 1;}}
