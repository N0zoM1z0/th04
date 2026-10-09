#include "pmd_rhythm.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::pmd {
namespace {
struct Instrument {unsigned voice,pan,level;bool retrigger;};
// Musical drum bits select an OPN rhythm voice, pan and level. Several bits
// use the same physical voice; the eighth bit stops voice 2 before voice 3.
constexpr std::array<Instrument,11> instruments{{
    {0,3,31,false},{1,3,31,false},{4,1,31,false},{4,3,31,false},
    {4,2,31,false},{5,3,19,false},{1,3,31,false},{3,2,28,true},
    {2,2,29,false},{2,3,31,false},{2,1,30,false}
}};
unsigned scale(unsigned value,unsigned amount){return amount ? value*(256-amount)/256 : value;}
}
void Rhythm::write(unsigned address,unsigned value){if(sink_)sink_({0,std::uint8_t(address),std::uint8_t(value)});}
std::uint8_t& Rhythm::indexed(unsigned index){
    if(index==0)return state_.active;
    if(index==7)return state_.total;
    return state_.levels.at(index-1);
}
void Rhythm::total(std::uint8_t fade){write(17,scale(state_.total,fade));}
void Rhythm::start(){
    state_.attenuation=state_.initial_attenuation;state_.active=0;state_.request=0;
    if(!state_.enabled)return;
    state_.levels.fill(207);state_.total=std::uint8_t(scale(48,state_.attenuation));
    write(16,255);write(17,state_.total);
}
void Rhythm::event(const Event& e,const State& music){
    if(e.kind==Kind::command && e.opcode==192){
        if(e.arguments.at(0)==249)state_.attenuation=e.arguments.at(1);
        else if(e.arguments.at(0)==248){const auto v=e.arguments.at(1);const int delta=v<128 ? int(v) : int(v)-256;state_.attenuation=v ? std::uint8_t(std::clamp(int(state_.attenuation)+delta,0,255)) : state_.initial_attenuation;}
        return;
    }
    if(e.kind==Kind::command && e.opcode==239 && e.part==10){write(e.arguments.at(0),e.arguments.at(1));return;}
    if(e.kind==Kind::rhythm){
        state_.request=(e.opcode&128) && !music.parts[10].mask ? std::uint16_t(((e.opcode&63)<<8)|e.arguments.at(0)) : 0;
        if(!state_.request || !state_.enabled)return;
        for(unsigned i=0;i<instruments.size();++i)if(state_.request&(1u<<i)){
            const auto& instrument=instruments[i];write(24+instrument.voice,(instrument.pan<<6)|instrument.level);
            unsigned key=((1u<<instrument.voice)|(instrument.retrigger ? 128u : 0u))&state_.mask;if(!key)continue;
            if(instrument.retrigger){write(16,132);key=8&state_.mask;if(!key)continue;}
            write(16,key);
        }
        if(music.fade)total(music.fade);
        return;
    }
    if(e.kind!=Kind::command || !state_.enabled)return;
    const auto& a=e.arguments;
    switch(e.opcode){
    case 235:{const auto key=std::uint8_t(a.at(0)&state_.mask);if(!key)break;
        if(music.fade)total(music.fade);
        if(!(key&128))for(unsigned i=0;i<6;++i)if(key&(1u<<i))write(24+i,state_.levels[i]);
        write(16,key);
        for(unsigned i=0;i<6;++i)if(key&(1u<<i)){if(key&128)++state_.stops[i];else ++state_.starts[i];}
        if(key&128)state_.active&=std::uint8_t(~key);else state_.active|=key;
        break;}
    case 234:case 233:{const unsigned index=a.at(0)>>5;auto& v=indexed(index);v=std::uint8_t(e.opcode==234 ? (v&192)|(a.at(0)&31) : (v&31)|((a.at(0)&3)<<6));write(23+index,v);break;}
    case 229:{const unsigned index=a.at(0);auto& v=indexed(index);auto level=std::uint8_t((v&31)+a.at(1));if(level>=32)level=(level&128) ? 0 : 31;v=std::uint8_t((v&224)|level);write(23+index,v);break;}
    case 232:state_.total=std::uint8_t(scale(a.at(0),state_.attenuation));total(music.fade);break;
    case 230:{auto value=std::uint8_t(state_.total+a.at(0));if(value>=64)value=(value&128) ? 0 : 63;state_.total=value;total(music.fade);break;}
    default:break;
    }
}
}
