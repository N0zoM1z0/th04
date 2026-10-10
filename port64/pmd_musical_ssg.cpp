#include "pmd_musical_ssg.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::pmd {
namespace {
int signed_byte(unsigned v){return v<128 ? int(v) : int(v)-256;}
std::int16_t signed_word(unsigned v){v&=65535;return std::int16_t(v<32768 ? int(v) : int(v)-65536);}
constexpr std::array<unsigned,12> periods{{3816,3602,3400,3209,3029,2859,2698,2547,2404,2269,2142,2022}};
std::uint8_t rate_counter(unsigned rate,bool doubled){auto v=std::uint8_t(rate-16);if(doubled && (v&128))v=std::uint8_t(v*2);return v;}
std::int16_t proportional(std::uint16_t period,std::int16_t amount){
    const auto product=std::uint32_t(std::int32_t(signed_word(period))*amount)*16u;
    auto high=signed_word(product>>16);return signed_word(std::uint16_t(high)+(high<0 ? -1 : 1));
}
}
MusicalSsg::MusicalSsg(Sequence& sequence,SsgSink sink,Reset reset,Advance advance,
 std::function<std::uint16_t(unsigned)> random,std::function<std::uint8_t()> baseline):
 sequence_(sequence),sink_(std::move(sink)),reset_(std::move(reset)),advance_(std::move(advance)),random_(std::move(random)),timer_baseline_(std::move(baseline)){}
void MusicalSsg::mirror(std::uint8_t a,std::uint8_t v){registers_.at(a)=v;sequence_.mirror_ssg(a,v);}
void MusicalSsg::write(unsigned a,unsigned v){const SsgWrite w{std::uint8_t(a),std::uint8_t(v)};mirror(w.address,w.value);if(sink_)sink_(w);}
void MusicalSsg::effect_write(SsgWrite w){
    registers_.at(w.address)=w.value;
    // Both the built-in effect frame and its noise sweep publish this cache.
    // Musical noise stays separate while the effect owns the shared chip.
    if(w.address==6)previous_noise_=w.value;
    if(sink_)sink_(w);
}
void MusicalSsg::start(){
    parts_={};parsed_note_={};attenuation_=initial_attenuation_;noise_=0;tied_=temporary_=false;
    // Restarting music must preserve noise while an effect owns channel C.
    if(!sequence_.ssg_effects().state().priority){previous_noise_=0;write(6,0);}
}
void MusicalSsg::stop(){write(7,sequence_.ssg_effects().state().priority ? (registers_[7]&63)|155 : 191);}
unsigned MusicalSsg::clocks(const MusicalSsgPart& s,unsigned l) const {return (s.clock_flags&(2u<<(l*4))) ? std::uint8_t(sequence_.state().timer_a-timer_baseline_()) : 1;}
std::uint8_t MusicalSsg::transpose(unsigned p,std::uint8_t n) const {
    const auto& t=sequence_.state().parts[p+6];
    return transpose_note(n,t.transpose,t.master_transpose);
}
void MusicalSsg::frequency(unsigned p,std::uint8_t n){
    auto& s=parts_[p];if((n&15)==15){s.note=255;if(!(s.flags&17))s.frequency=0;return;}
    s.note=n;const auto period=periods.at(n&15);const unsigned octave=n>>4;
    s.frequency=std::uint16_t(period>>octave);if(octave && (period&(1u<<(octave-1))))++s.frequency;
}
void MusicalSsg::pitch(unsigned p){
    const auto& s=parts_[p];if(!s.frequency)return;auto value=std::uint16_t(s.frequency+std::uint16_t(s.slide));const auto detune=sequence_.state().parts[p+6].detune;
    std::int16_t lfo=0;for(unsigned l=0;l<2;++l)if(s.flags&(1u<<(l*4)))lfo=signed_word(std::uint16_t(lfo)+std::uint16_t(s.lfo[l].value));
    if(s.clock_flags&1){if(detune)value-=std::uint16_t(proportional(value,detune));if(lfo)value-=std::uint16_t(proportional(value,lfo));}
    else value=std::uint16_t(value-std::uint16_t(detune)-std::uint16_t(lfo));
    if(value>=4096)value=(value&32768) ? 0 : 4095;
    write(p*2,value&255);write(p*2+1,value>>8);
}
void MusicalSsg::volume(unsigned p){
    const auto& s=parts_[p];const auto& e=s.envelope;if(e.mode==3 || (e.mode==255 && !e.phase))return;
    unsigned v=s.temporary_volume ? s.temporary_volume-1 : sequence_.state().parts[p+6].volume;
    if(attenuation_)v=(v*std::uint8_t(0-attenuation_))>>8;
    const auto fade=sequence_.state().fade;if(fade)v=(v*std::uint8_t(0-fade))>>8;
    if(v){
        if(e.mode==255)v=e.level ? (std::uint8_t(v*std::uint8_t(e.level+1))+8)>>4 : 0;
        else {v=std::uint8_t(v+e.level);if(v&128)v=0;v=std::min(v,15u);}
        if(v){int level=int(v);for(unsigned l=0;l<2;++l)if(s.flags&(2u<<(l*4)))level=signed_word(std::uint16_t(level)+std::uint16_t(s.lfo[l].value));v=unsigned(std::clamp(level,0,15));}
    }
    write(8+p,v);
}
void MusicalSsg::key(unsigned p){
    const auto& s=parts_[p];if(s.note==255)return;const unsigned selected=(1u<<p)|(8u<<p);
    write(7,(registers_[7]|selected)&~(selected&s.mixer));
    if(noise_!=previous_noise_ && (sequence_.ssg_effects().state().effect&128)){write(6,noise_);previous_noise_=noise_;}
}
void MusicalSsg::release(unsigned p){auto& s=parts_[p];if(s.note==255)return;if(s.envelope.mode==255)s.envelope.phase=4;else s.envelope.mode=2;}
void MusicalSsg::start_envelope(SsgEnvelope& e){
    if(e.mode!=255){e.mode=0;e.level=0;e.attack=e.attack_counter;if(!e.attack){e.mode=1;e.level=e.decay;}e.sustain=e.sustain_counter;e.release=e.release_counter;}
    else {e.attack_counter=rate_counter(e.attack,false);e.decay_counter=rate_counter(e.decay,true);e.sustain_counter=rate_counter(e.sustain,true);e.release_counter=std::uint8_t(e.release*2-16);e.level=e.initial_level;e.phase=1;envelope_tick(e);}
}
void MusicalSsg::envelope_tick(SsgEnvelope& e){
    if(e.mode!=255){
        if(!e.mode){if(!--e.attack){e.mode=1;e.level=e.decay;}return;}
        auto& count=e.mode==2 ? e.release : e.sustain;const auto initial=e.mode==2 ? e.release_counter : e.sustain_counter;
        if(!count){if(e.mode==2)e.level=241;return;}if(--count)return;count=initial;--e.level;if(e.level<241 && e.level>=15)e.level=241;return;
    }
    if(!e.phase)return;
    const unsigned index=e.phase-1;std::uint8_t* counts[]{&e.attack_counter,&e.decay_counter,&e.sustain_counter,&e.release_counter};const unsigned rates[]{e.attack,e.decay,e.sustain,e.release};auto& count=*counts[std::min(index,3u)];const auto step=std::uint8_t(count-1);
    if(step&128){if(rates[std::min(index,3u)])++count;return;}
    const unsigned amount=count;
    if(e.phase==1){e.level=std::uint8_t(e.level+amount);if(e.level>=15){e.level=15;++e.phase;if(e.sustain_level==15)++e.phase;}else count=rate_counter(e.attack,false);}
    else if(e.phase==2){if(amount>e.level || std::uint8_t(e.level-amount)<e.sustain_level){e.level=e.sustain_level;++e.phase;}else {e.level-=amount;count=rate_counter(e.decay,true);}}
    else {e.level=std::uint8_t(std::max(0,int(e.level)-int(amount)));count=e.phase==3 ? rate_counter(e.sustain,true) : std::uint8_t(e.release*2-16);}
}
bool MusicalSsg::envelope(SsgEnvelope& e,unsigned count){const auto before=e.level;for(unsigned n=0;n<count;++n)envelope_tick(e);return before!=e.level;}
void MusicalSsg::prepare(unsigned p,std::uint8_t note){
    auto& s=parts_[p];if((note&15)==12)note=s.last_note;s.last_note=note;
    const bool fresh=(note&15)!=15 && !tied_;if((note&15)!=15)s.slide=0;if(fresh)start_envelope(s.envelope);
    for(unsigned l=0;l<2;++l)if(s.flags&(3u<<(l*4))){if(fresh && !(s.flags&(4u<<(l*4))))reset_(s.lfo[l]);advance_(s.lfo[l],clocks(s,l));}
}
void MusicalSsg::gate(unsigned p,unsigned duration,unsigned next){
    auto& s=parts_[p];if(sequence_.music().at(next)==193){s.gate=0;return;}
    unsigned value=std::uint8_t(s.gate_amount+((duration*s.gate_ratio)>>8));if(s.gate_random){auto r=random_((s.gate_random&127)+1);value=(s.gate_random&128) ? unsigned(std::max(0,int(value)-int(r))) : std::uint8_t(value+r);}
    if(s.gate_minimum)value=duration<s.gate_minimum ? 0 : std::min(value,duration-s.gate_minimum);
    s.gate=std::uint8_t(value);
}
void MusicalSsg::note(unsigned p,const Event& e){
    auto& s=parts_[p];parsed_note_[p]=true;const auto& track=sequence_.state().parts[p+6];
    if(sequence_.masked_parser(p+6)){s.frequency=0;s.note=s.last_note=255;s.key_flags=255;if(!temporary_)s.temporary_volume=0;tied_=temporary_=false;return;}
    s.flags&=247;unsigned duration=e.arguments.at(0),next=e.offset+2;
    if(e.kind==Kind::portamento){prepare(p,e.arguments.at(0));frequency(p,transpose(p,s.last_note));const auto begin=s.frequency;const auto first=s.note;frequency(p,transpose(p,e.arguments.at(1)));const int delta=signed_word(s.frequency-begin);s.frequency=begin;s.note=first;duration=e.arguments.at(2);next=e.offset+4;if(!duration)throw std::invalid_argument("SSG zero portamento duration");s.slide_step=signed_word(delta/int(duration));s.slide_remainder=signed_word(delta%int(duration));s.flags|=8;}
    else {prepare(p,e.opcode);frequency(p,transpose(p,s.last_note));}
    gate(p,duration,next);if(s.temporary_volume && s.note!=255 && !temporary_)s.temporary_volume=0;volume(p);pitch(p);key(p);tied_=temporary_=false;s.key_flags=sequence_.music().at(next)==251 ? 2 : 0;
}
void MusicalSsg::command(unsigned p,const Event& e){
    auto& s=parts_[p];auto& v=s.envelope;const auto& a=e.arguments;
    switch(e.opcode){
    case 254:s.gate_amount=a.at(0);s.gate_random=0;break;
    case 251:tied_=true;break;
    case 242:case 191:{auto& l=s.lfo[e.opcode==191];l.initial_delay=a.at(0);l.initial_speed=a.at(1);l.initial_step=std::int8_t(signed_byte(a.at(2)));l.initial_count=a.at(3);reset_(l);break;}
    case 241:case 190:{unsigned l=e.opcode==190,shift=l*4;auto value=a.at(0);if(value&248)value=1;s.flags=std::uint8_t((s.flags&~(7u<<shift))|((value&7)<<shift));reset_(s.lfo[l]);break;}
    case 203:s.lfo[0].shape=a.at(0);break;case 188:s.lfo[1].shape=a.at(0);break;
    case 202:case 187:{unsigned shift=(e.opcode==187)*4;s.clock_flags=std::uint8_t((s.clock_flags&~(2u<<shift))|((a.at(0)&1)<<(shift+1)));break;}
    case 194:case 185:{auto& l=s.lfo[e.opcode==185];l.initial_delay=a.at(0);l.delay=a.at(0);reset_(l);break;}
    case 214:case 189:{auto& l=s.lfo[e.opcode==189];l.depth_speed=l.initial_depth_speed=a.at(0);l.depth_step=std::int8_t(signed_byte(a.at(1)));break;}
    case 183:{auto& l=s.lfo[(a.at(0)&128)!=0];const auto count=std::uint8_t(a.at(0)&127);l.depth_count=l.initial_depth_count=count ? count : 255;break;}
    case 196:s.gate_ratio=a.at(0);break;case 179:s.gate_minimum=a.at(0);break;case 177:s.gate_random=a.at(0);break;
    case 240:v.attack=v.attack_counter=a.at(0);v.decay=a.at(1);v.sustain=v.sustain_counter=a.at(2);v.release=v.release_counter=a.at(3);if(v.mode==255){v.mode=2;v.level=241;}break;
    case 205:v.attack=a.at(0)&31;v.decay=a.at(1)&31;v.sustain=a.at(2)&31;v.release=a.at(3)&15;v.sustain_level=std::uint8_t((a.at(3)>>4)^15);v.initial_level=a.at(4)&15;if(v.mode!=255){v.mode=255;v.phase=4;v.level=0;}break;
    case 201:s.clock_flags=std::uint8_t((s.clock_flags&251)|((a.at(0)&1)<<2));break;
    case 204:s.clock_flags=std::uint8_t((s.clock_flags&254)|(a.at(0)&1));break;
    case 238:noise_=a.at(0);break;case 208:noise_=std::uint8_t(std::clamp(signed_byte(std::uint8_t(noise_+a.at(0))),0,31));break;
    case 237:s.mixer=a.at(0);break;
    case 222:case 221:{unsigned volume=sequence_.state().parts[p+6].volume;s.temporary_volume=std::uint8_t((e.opcode==222 ? std::min<unsigned>(15,std::uint8_t(volume+a.at(0))) : unsigned(std::max(0,int(volume)-int(a.at(0)))))+1);temporary_=true;break;}
    case 192:if(a.at(0)==1 && sequence_.state().parts[p+6].mask==64){const auto bits=(1u<<p)|(8u<<p);write(7,registers_[7]|bits);}break;
    case 239:if(a.at(0)<14)write(a.at(0),a.at(1));break;
    case 255:case 253:case 252:case 250:case 249:case 248:case 247:case 246:case 245:case 244:case 243:case 236:case 235:case 234:case 233:case 232:case 231:case 230:case 229:case 228:case 227:case 226:case 225:case 224:case 223:case 220:case 219:case 218:case 217:case 216:case 215:case 213:case 212:case 211:case 210:case 209:case 207:case 206:case 200:case 199:case 198:case 197:case 195:case 193:case 186:case 184:case 182:case 181:case 180:case 178:break;
    default:throw std::invalid_argument("unrecovered musical SSG command "+std::to_string(e.opcode));
    }
}
void MusicalSsg::event(const Event& e){
    if(e.kind==Kind::command && e.opcode==192){const auto sub=e.arguments.at(0);if(sub==253)attenuation_=e.arguments.at(1);else if(sub==252){const int amount=signed_byte(e.arguments.at(1));attenuation_=amount ? std::uint8_t(std::clamp(int(attenuation_)+amount,0,255)) : initial_attenuation_;}}
    if(e.part<6 || e.part>8)return;
    const unsigned p=e.part-6;
    if(e.kind==Kind::note || e.kind==Kind::portamento)note(p,e);else if(e.kind==Kind::command)command(p,e);else parts_[p].note=255;
}
void MusicalSsg::tick(unsigned part,bool before){
    if(part<6 || part>8)return;
    const unsigned p=part-6;auto& s=parts_[p];const auto& track=sequence_.state().parts[part];
    if(before){parsed_note_[p]=false;if(track.mask){s.key_flags=255;return;}if(!(s.key_flags&3) && std::uint8_t(track.length-1)<=s.gate){release(p);s.key_flags=255;}if(track.length==1)s.flags&=247;return;}
    if(parsed_note_[p] || track.mask)return;
    unsigned changed=s.flags&8;
    for(unsigned l=0;l<2;++l)if(s.flags&(3u<<(l*4)))if(advance_(s.lfo[l],clocks(s,l)))changed|=s.flags&(3u<<(l*4));
    if(changed&25){if(changed&8){s.slide=signed_word(std::uint16_t(s.slide)+s.slide_step);if(s.slide_remainder>0){--s.slide_remainder;s.slide=signed_word(std::uint16_t(s.slide)+1);}else if(s.slide_remainder<0){++s.slide_remainder;s.slide=signed_word(std::uint16_t(s.slide)-1);}}pitch(p);}
    const unsigned count=(s.clock_flags&4) ? std::uint8_t(sequence_.state().timer_a-timer_baseline_()) : 1;
    if(envelope(s.envelope,count) || (changed&34) || sequence_.state().fade_speed)volume(p);
}
}
