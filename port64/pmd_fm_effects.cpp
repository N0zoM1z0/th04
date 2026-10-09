#include "pmd_fm_effects.hpp"
#include <algorithm>
#include <stdexcept>
#include <string>

namespace th04::portable::pmd {
namespace {
int signed_byte(unsigned value) {return value<128 ? int(value) : int(value)-256;}
std::int16_t signed_word(unsigned value) {value&=65535;return std::int16_t(value<32768 ? int(value) : int(value)-65536);}
constexpr std::array<std::uint16_t,12> note_periods{{618,655,694,735,779,825,874,926,981,1040,1102,1167}};
// The target carrier mask orders physical operators 1,3,2,4.
constexpr std::array<std::uint8_t,4> operator_bits{{0x10,0x40,0x20,0x80}};
constexpr std::array<std::uint8_t,8> carriers{{0x80,0x80,0x80,0x80,0xa0,0xe0,0xe0,0xf0}};
}
std::uint8_t FmEffects::read(std::uint16_t at) const {
    if(at>=effects_.size())throw std::out_of_range("PMD EFC read at "+std::to_string(at));
    return effects_[at];
}
std::uint16_t FmEffects::word(std::uint16_t at) const {return std::uint16_t(read(at))|std::uint16_t(read(std::uint16_t(at+1)))*256;}
std::uint8_t FmEffects::take() {const auto value=read(state_.position);++state_.position;return value;}
std::uint16_t FmEffects::take_word() {const auto value=word(state_.position);state_.position+=2;return value;}
void FmEffects::load(const Bytes& data) {
    if(data.size()<257 || data.size()>2048)throw std::invalid_argument("bounded PMD EFC required");
    for(unsigned i=0;i<128;++i) {
        const auto at=unsigned(data[i*2])+256u*data[i*2+1];
        if(at>=data.size())throw std::out_of_range("PMD EFC directory");
    }
    effects_=data;
}
void FmEffects::write(unsigned b,unsigned address,unsigned value) {
    const FmWrite w{std::uint8_t(b),std::uint8_t(address),std::uint8_t(value)};
    registers_.at(b)[w.address]=w.value;if(sink_)sink_(w);
}
void FmEffects::key(bool on) {
    if(state_.note==255)return;
    if(on)keys_|=state_.slots;else keys_&=std::uint8_t(~state_.slots);
    write(0,0x28,keys_|(board_==Board::fm26 ? 2 : 6));
}
void FmEffects::silence_voice() {
    for(unsigned slot=0;slot<4;++slot) {
        write(bank(),0x42+slot*4,127);write(bank(),0x82+slot*4,127);
    }
    const auto note=state_.note;state_.note=0;key(false);state_.note=note;
}
void FmEffects::start(unsigned id) {
    if(effects_.empty() || id>=127)throw std::out_of_range("PMD FM effect index/resource");
    if(state_.active)stop();
    state_=FmEffectState{};state_.active=true;state_.effect=std::uint8_t(id);
    state_.position=word(std::uint16_t(id*2));state_.ticks=1;state_.volume=108;
    state_.slots=240;state_.voice_mask=255;tied_=false;
    for(unsigned p=0;p<6;++p)if(p==5 || (board_==Board::fm26 && p>=2))masks_[p]|=2;
    if(board_!=Board::fm26) {state_.pan=192;write(1,0xb6,192);}
}
void FmEffects::stop() {
    if(!state_.active)return;
    state_.effect=255;state_.active=false;silence_voice();if(release_)release_();
}
void FmEffects::voice(std::uint8_t id) {
    state_.instrument=id;
    auto at=word(254);
    for(unsigned budget=0;budget<80;++budget) {
        const auto name=read(at);
        if(name==255)throw std::out_of_range("PMD EFC voice not present");
        if(name==id)break;
        at=std::uint16_t(at+26);
        if(budget==79)throw std::runtime_error("PMD EFC voice search exhausted");
    }
    ++at;silence_voice();state_.algorithm=read(std::uint16_t(at+24));
    write(bank(),0xb2,state_.algorithm);
    state_.carrier_mask=carriers[state_.algorithm&7];
    if(!(state_.lfo_mask&15))state_.lfo_mask=state_.carrier_mask;
    for(unsigned slot=0;slot<4;++slot)write(bank(),0x32+slot*4,read(std::uint16_t(at+slot)));
    for(unsigned slot=0;slot<4;++slot)if(!(state_.carrier_mask&operator_bits[slot]))write(bank(),0x42+slot*4,read(std::uint16_t(at+4+slot)));
    for(unsigned i=0;i<16;++i)write(bank(),0x52+i*4,read(std::uint16_t(at+8+i)));
    for(unsigned i=0;i<4;++i)state_.total_levels[i]=read(std::uint16_t(at+4+i));
}
void FmEffects::volume() {
    const auto attenuation=std::uint8_t(~state_.volume);
    // Target emits carriers in physical operator order 4,3,2,1.
    for(unsigned slot:{3u,1u,2u,0u})if(state_.carrier_mask&operator_bits[slot]) {
        int level=attenuation;
        if((state_.lfo_flags&2) && (state_.lfo_mask&operator_bits[slot]) && attenuation!=255)
            level=std::clamp(level-int(state_.lfo.value),0,255);
        level=std::min(255,level+int(state_.total_levels[slot]));
        write(bank(),0x42+slot*4,std::max(0,level-128));
    }
}
void FmEffects::pitch() {
    if(!state_.frequency || !state_.slots)return;
    int block=state_.frequency&0x3800;
    auto value=std::uint16_t((state_.frequency&2047)+std::uint16_t(state_.slide)+std::uint16_t(state_.detune));
    if(state_.lfo_flags&1)value+=std::uint16_t(state_.lfo.value);
    for(unsigned budget=0;budget<128;++budget) {
        if(value<32768 && value>=618) {
            if(value<1236)break;
            block+=2048;
            if(block==16384) {block=14336;value=std::min<std::uint16_t>(value,2047);break;}
            value-=618;
        } else {
            block-=2048;
            if(block<0) {block=0;if(value>=32768 || value<8)value=8;break;}
            value+=618;
        }
    }
    const auto period=std::uint16_t(value)|std::uint16_t(block);
    write(bank(),0xa6,period>>8);write(bank(),0xa2,period&255);
}
void FmEffects::reset_lfo() {
    auto& l=state_.lfo;l.value=0;l.delay=l.initial_delay;l.speed=l.initial_speed;
    l.step=l.initial_step;l.count=l.initial_count;
    if(l.shape==2 || l.shape==3)l.speed=1;else ++l.speed;
}
bool FmEffects::update_lfo() {
    auto& l=state_.lfo;
    if(l.delay) {--l.delay;return false;}
    if(l.speed!=1) {if(l.speed!=255)--l.speed;return false;}
    l.speed=l.initial_speed;const auto before=l.value;
    if(l.shape!=0)throw std::invalid_argument("unrecovered FM EFC LFO shape");
    l.value=signed_word(std::uint16_t(l.value)+int(l.step));
    if(l.count!=255) {
        --l.count;
        if(!l.count) {l.count=std::uint8_t(l.initial_count*2);l.step=std::int8_t(signed_byte(std::uint8_t(-int(l.step))));}
    }
    return l.value!=before;
}
std::uint8_t FmEffects::transpose(std::uint8_t note) const {
    if(note==15)return note;
    int octave=note>>4,pitch=note&15;const int amount=signed_byte(std::uint8_t(state_.transpose+state_.master_transpose));
    pitch+=amount;
    while(pitch<0){pitch+=12;--octave;}while(pitch>=12){pitch-=12;++octave;}
    return std::uint8_t((std::uint8_t(octave)<<4)|unsigned(pitch));
}
void FmEffects::prepare_note(std::uint8_t note) {
    if((note&15)==12)note=state_.last_note;
    state_.last_note=note;
    if((note&15)!=15) {
        state_.slide=0;
        if(!tied_ && (state_.lfo_flags&3) && !(state_.lfo_flags&4))reset_lfo();
    }
    if(state_.lfo_flags&3)update_lfo();
}
void FmEffects::frequency(std::uint8_t note) {
    if((note&15)==15) {state_.note=255;if(!(state_.lfo_flags&1))state_.frequency=0;return;}
    state_.note=note;
    state_.frequency=note_periods.at(note&15)|std::uint16_t((note>>1)&0x38)*256;
}
void FmEffects::finish_note() {
    state_.gate=state_.gate_amount;
    if(read(state_.position)==0xc1) {++state_.position;state_.gate=0;}
    volume();pitch();key(true);++state_.notes;tied_=false;state_.key_flags=0;
    if(read(state_.position)==0xfb)state_.key_flags=2;
}
bool FmEffects::command(std::uint8_t opcode) {
    switch(opcode) {
    case 0xff:voice(take());break;
    case 0xfd:state_.volume=take();break;
    case 0xfe:state_.gate_amount=take();break;
    case 0xfb:tied_=true;break;
    case 0xfa:state_.detune=signed_word(take_word());break;
    case 0xf9: {const auto end=take_word();read(std::uint16_t(end+1));effects_[std::uint16_t(end+1)]=0;break;}
    case 0xf8: {
        const auto count=take();const auto at=state_.position;auto current=take();
        const auto begin=take_word();if(count) {++current;effects_[at]=current;}
        else state_.loop_status=1;
        if(!count || current!=count)state_.position=std::uint16_t(begin+2);
        break;
    }
    case 0xf7: {const auto end=take_word();if(std::uint8_t(read(end)-1)==read(std::uint16_t(end+1)))state_.position=std::uint16_t(end+4);break;}
    case 0xf6:state_.loop=state_.position;break;
    case 0xf5:state_.transpose=take();break;
    case 0xf4:state_.volume=std::min<unsigned>(127,std::uint8_t(state_.volume+4));break;
    case 0xf3:state_.volume=std::uint8_t(std::max(0,int(state_.volume)-4));break;
    case 0xf2: {
        auto& l=state_.lfo;l.initial_delay=take();l.initial_speed=take();l.initial_step=std::int8_t(signed_byte(take()));l.initial_count=take();reset_lfo();break;
    }
    case 0xf1: {auto v=take();if(v&248)v=1;state_.lfo_flags=(state_.lfo_flags&248)|(v&7);reset_lfo();break;}
    case 0xc1:break;
    case 0xda: {
        const auto note=take();prepare_note(note);frequency(transpose(note));const auto begin=state_.frequency;const auto first=state_.note;
        frequency(transpose(take()));const auto end=state_.frequency;state_.frequency=begin;state_.note=first;
        const int delta=((int(end&0x3800)-int(begin&0x3800))/2048)*618+int(end&2047)-int(begin&2047);
        state_.ticks=take();if(!state_.ticks)throw std::invalid_argument("PMD EFC zero portamento duration");
        state_.slide_step=signed_word(delta/int(state_.ticks));state_.slide_remainder=signed_word(delta%int(state_.ticks));state_.lfo_flags|=8;finish_note();return true;
    }
    default:throw std::invalid_argument("unrecovered PMD EFC command "+std::to_string(opcode));
    }
    return false;
}
void FmEffects::timer_a(std::int8_t musical_fade_speed) {
    if(!state_.active)return;
    --state_.ticks;
    if(!(state_.key_flags&3) && state_.ticks<=state_.gate) {key(false);state_.key_flags=255;}
    if(!state_.ticks) {
        state_.lfo_flags&=247;
        for(unsigned budget=0;budget<2048;++budget) {
            const auto at=state_.position;const auto op=take();
            if(op==128) {
                state_.position=at;state_.loop_status=3;state_.note=255;
                if(state_.loop) {state_.position=state_.loop;state_.loop_status=1;continue;}
                // The original still advances enabled LFOs at this marker.
                break;
            }
            if(op<128) {prepare_note(op);frequency(transpose(state_.last_note));state_.ticks=take();finish_note();return;}
            if(command(op))return;
            if(budget==2047)throw std::runtime_error("PMD EFC command loop exhausted");
        }
    }
    bool changed=false;if(state_.lfo_flags&3)changed=update_lfo();
    if((state_.lfo_flags&8) || (changed && (state_.lfo_flags&1))) {
        if(state_.lfo_flags&8) {
            state_.slide=signed_word(std::uint16_t(state_.slide)+state_.slide_step);
            if(state_.slide_remainder>0){--state_.slide_remainder;state_.slide=signed_word(std::uint16_t(state_.slide)+1);}
            else if(state_.slide_remainder<0){++state_.slide_remainder;state_.slide=signed_word(std::uint16_t(state_.slide)-1);}
        }
        pitch();
    }
    // The shared driver parser refreshes effect TLs during musical fades,
    // even when the effect's LFO and resulting register value stay unchanged.
    if((changed && (state_.lfo_flags&2)) || musical_fade_speed)volume();
    if(!state_.ticks && read(state_.position)==128)stop();
}
}
