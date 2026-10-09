#include "pmd_sequence.hpp"
#include <algorithm>
#include <stdexcept>
#include <string>

namespace th04::portable::pmd {
namespace {
std::int16_t signed_word(std::uint16_t value) {
    return std::int16_t(value<32768 ? int(value) : int(value)-65536);
}
int signed_byte(std::uint8_t value) {return value<128 ? int(value) : int(value)-256;}
}
std::uint8_t Sequence::get(std::uint16_t at) const {
    if(at>=music_.size())throw std::out_of_range("PMD music read at "+std::to_string(at));
    return music_[at];
}
std::uint16_t Sequence::word(std::uint16_t at) const {
    return std::uint16_t(get(at)) | std::uint16_t(get(std::uint16_t(at+1)))*256;
}
std::uint8_t Sequence::take(std::uint16_t& at) {const auto value=get(at);++at;return value;}
std::uint16_t Sequence::take_word(std::uint16_t& at) {const auto value=word(at);at+=2;return value;}
void Sequence::put(std::uint16_t at,std::uint8_t value) {get(at);music_[at]=value;}
void Sequence::emit(Kind k,unsigned p,std::uint16_t at,std::uint8_t op,Bytes args) {
    if(sink_)sink_({k,p,at,op,std::move(args)});
}
void Sequence::load(const Bytes& bytes) {
    if(bytes.size()<25 || bytes.size()>8192 || bytes[0]!=0)
        throw std::invalid_argument("PMD requires bounded PC-98 M26/M86 data");
    const auto header=std::uint16_t(bytes[1]) | std::uint16_t(bytes[2])*256;
    if(header!=24 && header!=26)throw std::invalid_argument("PMD part header");
    // Validate every directory entry before replacing the current resource.
    for(unsigned p=0;p<12+(header==26);++p) {
        const auto at=1+2*p;const unsigned offset=unsigned(bytes.at(at))+256u*bytes.at(at+1)+1;
        if(offset>=bytes.size())throw std::out_of_range("PMD directory outside music");
    }
    music_=bytes;
}
void Sequence::set_timer_b(std::uint8_t value) {
    state_.timer_b=saved_timer_b_=value;
    const unsigned divisor=std::uint8_t(0-value);
    unsigned tempo=255;
    if(divisor>=18) {tempo=4396/divisor;if((4396%divisor)&128)++tempo;}
    state_.tempo=saved_tempo_=std::uint8_t(tempo);
}
void Sequence::set_tempo(std::uint8_t value) {
    state_.tempo=saved_tempo_=std::max<std::uint8_t>(18,value);
    const unsigned divisor=state_.tempo;
    const unsigned rounded=4396/divisor+(((4396%divisor)&128) ? 1 : 0);
    state_.timer_b=saved_timer_b_=std::uint8_t(0-rounded);
}
void Sequence::start() {
    if(music_.empty())throw std::logic_error("PMD start requires music");
    const auto old=state_.parts;state_=State{};state_.playing=true;set_timer_b(200);
    for(unsigned p=0;p<11;++p) {
        auto& track=state_.parts[p];track.notes=old[p].notes;
        track.mask=old[p].mask&15;
        track.position=std::uint16_t(word(std::uint16_t(1+2*p))+1);
        if(get(track.position)==0x80)track.position=0;
        track.volume=p<6 ? 108 : p<9 ? 8 : p==9 && board_!=Board::fm26 ? 128 : p==10 ? 15 : 0;
        if(board_==Board::fm26 && p>=3 && p<6)track.mask=32;
        if(board_==Board::speakboard && p==9)track.mask=4;
    }
    rhythm_table_=std::uint16_t(word(23)+1);rhythm_position_=0;
}
void Sequence::stop() {
    state_.playing=false;state_.fade_speed=0;state_.fade=255;state_.loop_status=255;
}
bool Sequence::command(unsigned p,std::uint16_t& at,std::uint8_t op,std::uint16_t offset) {
    auto& track=state_.parts[p];const bool fm=p<6;
    // Only recovered commands enter the native decoder. Unrecognized bytecode
    // fails at this boundary instead of altering the original resource.
    Bytes args;
    auto byte=[&]() {auto value=take(at);args.push_back(value);return value;};
    auto integer=[&]() {const auto low=byte();return std::uint16_t(low)|std::uint16_t(byte())*256;};
    bool duration=false;
    switch(op) {
    case 0xff: {auto value=byte();if(fm || p==9)track.instrument=value;break;}
    case 0xfe:case 0xb3:case 0xc4:byte();break;
    case 0xfd:track.volume=byte();break;
    case 0xfc: {
        const auto mode=byte();
        if(mode<251)set_timer_b(mode);
        else {
            const auto amount=byte();
            if(mode==255)set_tempo(amount);
            else if(mode==254)set_timer_b(std::uint8_t(std::clamp(int(saved_timer_b_)+signed_byte(amount),0,250)));
            else set_tempo(std::uint8_t(std::clamp(int(saved_tempo_)+signed_byte(amount),18,255)));
        }
        break;
    }
    case 0xfb:case 0xc1:break;
    case 0xfa:track.detune=signed_word(integer());break;
    case 0xf9: {const auto end=integer();put(std::uint16_t(end+2),0);break;}
    case 0xf8: {
        const auto count=byte();const auto counter_at=at;auto count_now=byte();const auto begin=integer();
        if(count) {++count_now;put(counter_at,count_now);}
        else track.loop_status=1;
        if(!count || count_now!=count)at=std::uint16_t(begin+3);
        break;
    }
    case 0xf7: {
        const auto end=integer();
        if(std::uint8_t(get(std::uint16_t(end+1))-1)==get(std::uint16_t(end+2)))at=std::uint16_t(end+5);
        break;
    }
    case 0xf6:track.loop=at;break;
    case 0xf5:track.transpose=byte();break;
    case 0xb2:if(p!=10)track.master_transpose=byte();else byte();break;
    case 0xe7: {const auto value=byte();if(p!=10)track.transpose+=value;break;}
    case 0xf4:track.volume=std::min<unsigned>(fm ? 127 : p==9 ? 255 : 15,unsigned(track.volume)+(fm ? 4 : 1));break;
    case 0xf3:track.volume=std::uint8_t(std::max(0,int(track.volume)-(fm ? 4 : 1)));break;
    case 0xe3:track.volume=std::min<unsigned>(fm ? 127 : p==9 ? 255 : 15,std::uint8_t(track.volume+byte()));break;
    case 0xe2: {const auto value=byte();track.volume=std::uint8_t(std::max(0,int(track.volume)-int(value)));break;}
    case 0xdf:state_.bar_length=byte();break;
    case 0xdc:state_.status=byte();break;
    case 0xdb:state_.status+=byte();break;
    case 0xd5:track.detune=signed_word(std::uint16_t(std::uint16_t(track.detune)+integer()));break;
    case 0xc0: {
        const auto sub=byte();
        if(sub<2) {if(sub)track.mask|=64;else track.mask&=~64;}
        else if(sub>=247)byte();
        else throw std::invalid_argument("unrecovered PMD extended command");
        break;
    }
    case 0xda:
        if(p==10 || p==9)byte();
        else if(track.mask)byte();
        else {byte();byte();track.length=byte();++track.notes;duration=true;}
        break;
    case 0xf2:case 0xbf:case 0xf0:
        for(unsigned n=0;n<4;++n)byte();break;
    case 0xef:case 0xd6:case 0xce:case 0xcd:case 0xc8:case 0xc7:case 0xc6:case 0xc3:case 0xbd:case 0xb8:case 0xb5:case 0xb4: {
        unsigned size=op==0xce || op==0xc6 ? 6 : op==0xcd ? 5 : op==0xc8 || op==0xc7 ? 3 : op==0xb4 ? 10 : 2;
        if(op==0xd6 && p==10)size=2;
        for(unsigned n=0;n<size;++n)byte();break;
    }
    case 0xf1:case 0xee:case 0xed:case 0xec:case 0xeb:case 0xea:case 0xe9:case 0xe8:
    case 0xe6:case 0xe4:case 0xe1:case 0xe0:case 0xde:case 0xdd:case 0xd9:case 0xd8:
    case 0xd7:case 0xd4:case 0xd3:case 0xd2:case 0xd1:case 0xd0:case 0xcf:case 0xcc:
    case 0xcb:case 0xca:case 0xc9:case 0xc5:case 0xc2:case 0xbe:case 0xbc:case 0xbb:
    case 0xba:case 0xb9:case 0xb7:case 0xb6:byte();break;
    case 0xb1:
        if(board_==Board::fm26)throw std::invalid_argument("PMD26 has no random gate command");
        byte();break;
    case 0xe5:byte();byte();break;
    default:throw std::invalid_argument("unrecovered PMD command "+std::to_string(op));
    }
    emit(duration ? Kind::portamento : Kind::command,p,offset,op,std::move(args));
    return duration;
}
void Sequence::part(unsigned p) {
    if(!state_.parts[p].position)return;
    if(tick_)tick_(p,true);
    part_body(p);
    if(tick_)tick_(p,false);
}
void Sequence::part_body(unsigned p) {
    auto& track=state_.parts[p];if(!track.position)return;
    --track.length;if(track.length)return;
    auto at=track.position;
    for(unsigned budget=0;budget<8192;++budget) {
        const auto offset=at;const auto op=take(at);
        if(op<0x80 || op==0xda)recover_ssg(p,op);
        if(op==0x80) {
            track.position=offset;track.loop_status=3;emit(Kind::end,p,offset,op);
            if(!track.loop)return;
            at=track.loop;track.loop_status=1;continue;
        }
        if(op<0x80) {
            track.length=take(at);++track.notes;
            emit(Kind::note,p,offset,op,{track.length});
            // C1 immediately after a sounding note overrides its release gate.
            if(!track.mask && get(at)==0xc1)++at;
            track.position=at;return;
        }
        if(command(p,at,op,offset)) {if(get(at)==0xc1)++at;track.position=at;return;}
    }
    throw std::runtime_error("PMD command loop exhausted");
}
void Sequence::rhythm() {
    auto& track=state_.parts[10];if(!track.position)return;
    --track.length;if(track.length)return;
    auto at=track.position;
    for(unsigned budget=0;budget<8192;++budget) {
        if(!rhythm_position_ || get(rhythm_position_)==0xff) {
            const auto offset=at;const auto op=take(at);
            if(op==0x80) {
                track.position=offset;track.loop_status=3;emit(Kind::end,10,offset,op);
                if(!track.loop){rhythm_position_=0;return;}
                at=track.loop;track.loop_status=1;continue;
            }
            if(op>=0x80) {command(10,at,op,offset);continue;}
            track.position=at;rhythm_position_=std::uint16_t(word(std::uint16_t(rhythm_table_+2*op))+1);
        }
        const auto offset=rhythm_position_;const auto op=take(rhythm_position_);
        if(op>=0xc0) {command(10,rhythm_position_,op,offset);continue;}
        Bytes args;
        if(op&0x80)args.push_back(take(rhythm_position_));
        track.length=take(rhythm_position_);args.push_back(track.length);++track.notes;
        if((op&0x80) && !track.mask && !state_.fade) {
            const unsigned mask=((unsigned(op)&0x3f)<<8)|args[0];
            if(mask) {
                unsigned effect=0;while(!(mask&(1u<<effect)))++effect;
                if(effects_.start(effect))state_.parts[8].mask|=2;
            }
        }
        emit(Kind::rhythm,10,offset,op,std::move(args));return;
    }
    throw std::runtime_error("PMD rhythm command loop exhausted");
}
void Sequence::timer_b() {
    if(!state_.playing)return;
    // The original player visits SSG before FM. Global tempo/bar commands in
    // later parts replace earlier commands in the same interrupt.
    for(unsigned p=6;p<9;++p)part(p);
    if(board_!=Board::fm26)for(unsigned p=3;p<6;++p)part(p);
    for(unsigned p=0;p<3;++p)part(p);
    if(board_==Board::fm26)for(unsigned p=3;p<6;++p)part(p);
    rhythm();if(board_!=Board::fm26)part(9);
    std::uint8_t combined=3;
    for(unsigned p=0;p<11;++p)if(state_.parts[p].position && !(p==9 && board_==Board::fm26))combined&=state_.parts[p].loop_status;
    if(combined) {
        for(auto& p:state_.parts)if(p.loop_status!=3)p.loop_status=0;
        if(combined==3)state_.loop_status=255;
        else {++state_.loop_status;if(state_.loop_status==255)state_.loop_status=1;}
    }
    ++state_.bar_tick;
    if(state_.bar_tick==state_.bar_length){state_.bar_tick=0;++state_.measure;}
}
void Sequence::interrupt(std::uint8_t flags) {
    if(flags>3)throw std::invalid_argument("PMD timer status");
    if(flags&2)timer_b();
    if(flags&1) {
        ++state_.timer_a;
        if(!(state_.timer_a&7) && state_.fade_speed) {
            const int next=int(state_.fade)+state_.fade_speed;
            state_.fade=std::uint8_t(std::clamp(next,0,255));
            if(next<0 || next>255)state_.fade_speed=0;
        }
        effects_.timer_a();
    }
}
void Sequence::recover_ssg(unsigned p,std::uint8_t note) {
    if(p<6 || p>8)return;
    auto& mask=state_.parts[p].mask;
    if(!(mask&1) && (mask&2) && effects_.state().priority<2 && (note&15)!=15) {
        if(effects_.state().priority==1)effects_.stop();
        mask&=~2;
    }
}
}
