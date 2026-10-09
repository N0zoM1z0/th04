#include "sound_control.hpp"
#include <algorithm>
#include <stdexcept>
#include <utility>

namespace th04::portable::sound {
namespace {
constexpr std::array<std::uint8_t,17> priority{{0,0,32,16,2,18,18,64,16,17,2,18,32,32,32,32,0}};
constexpr std::array<std::uint8_t,17> duration{{0,0,36,16,4,16,8,48,80,17,4,11,80,80,80,32,0}};
}
const std::array<std::uint8_t,17>& Control::priorities(){return priority;}
const std::array<std::uint8_t,17>& Control::durations(){return duration;}
const char* kind_name(Kind k){switch(k){case Kind::interrupt:return "int";case Kind::open:return "open";case Kind::read:return "read";case Kind::close:return "close";case Kind::beep_file:return "beep_file";case Kind::beep:return "beep";}throw std::logic_error("sound request kind");}
void Control::emit(Kind k,std::uint16_t a,std::uint16_t b,std::string name) const {if(sink_)sink_({k,a,b,std::move(name)});}
std::uint16_t Control::determine(std::uint16_t requested_bgm,std::uint16_t requested_se,Drivers drivers){
    state_.interrupt_if_midi=0x60;state_.midi_possible=0;state_.bgm=state_.se=0;
    unsigned probe=drivers.pmd;
    if(requested_bgm==3){probe=drivers.mmd;if(drivers.mmd){state_.midi_possible=1;state_.interrupt_if_midi=0x61;}}
    emit(Kind::interrupt,0x60,std::uint16_t(0x900|probe));
    const auto type=std::uint8_t(drivers.type_reply);
    state_.bgm=type==255 ? 0 : type==0 ? 1 : 2;
    state_.se=requested_se==1 ? std::uint8_t(state_.bgm!=0) : requested_se==2 ? 2 : 0;
    if(requested_bgm==0)state_.bgm=0;
    else if(requested_bgm==3 && state_.midi_possible)state_.bgm=3;
    else if(requested_bgm==1 && state_.bgm)state_.bgm=1;
    return state_.bgm;
}
std::uint16_t Control::command(std::uint16_t argument,std::uint16_t incoming_ax,std::uint16_t reply){
    if(!state_.bgm)return incoming_ax;
    emit(Kind::interrupt,state_.bgm==3 ? 0x61 : 0x60,argument);return reply;
}
void Control::reset(){state_.frame=0;state_.playing=255;}
void Control::play(std::uint16_t effect){
    if(!state_.se)return;
    // The original indexes DS beyond its tables for unsupported WORD values.
    // Native entrypoints reject that undefined ownership surface explicitly.
    if(effect>=priority.size() || (state_.playing!=255 && state_.playing>=priority.size()))throw std::out_of_range("sound effect index");
    if(state_.playing==255)state_.playing=std::uint8_t(effect);
    else if(priority[state_.playing]<=priority[effect]){state_.playing=std::uint8_t(effect);state_.frame=0;}
}
void Control::update(){
    if(!state_.se || state_.playing==255)return;
    if(state_.playing>=duration.size())throw std::out_of_range("sound effect duration index");
    if(!state_.frame){if(state_.se==2)emit(Kind::beep,state_.playing);else emit(Kind::interrupt,0x60,std::uint16_t(0xc00|state_.playing));}
    state_.frame=std::uint8_t(state_.frame+1);
    if(duration[state_.playing]<state_.frame)reset();
}
void Control::load(const std::array<std::uint8_t,13>& base,std::uint16_t function){
    const auto end=std::find(base.begin()+1,base.end(),0);
    const auto n=unsigned(end-base.begin());
    if(base[0]==0 || n>8)throw std::invalid_argument("sound resource base must fit 8.3");
    state_.filename=base;state_.filename[n+4]=0;state_.filename[n]='.';
    if(function==0xb00){state_.filename[n+1]='e';state_.filename[n+2]='f';if(!state_.se)return;state_.filename[n+3]=state_.se==2 ? 's' : 'c';}
    else{
        if(!state_.bgm)return;
        if(state_.bgm>3)throw std::out_of_range("sound music mode");
        command(0x100,0,0);
        const char* ext=state_.bgm==3 ? "mmd" : state_.bgm==2 ? "m86" : "m26";
        std::copy_n(ext,3,state_.filename.begin()+n+1);
    }
    const std::string name(state_.filename.begin(),state_.filename.begin()+n+4);
    if(function==0xb00 && state_.se==2){emit(Kind::beep_file,0,0,name);return;}
    emit(Kind::open,0,0,name);
    emit(Kind::interrupt,((function>>8)==6 && state_.bgm==3) ? 0x61 : 0x60,function);
    emit(Kind::read,0x5000);emit(Kind::close);
}
}
