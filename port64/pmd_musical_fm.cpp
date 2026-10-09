#include "pmd_musical_fm.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::pmd {
namespace {
int i8(unsigned v){return v<128 ? int(v) : int(v)-256;}
std::int16_t i16(unsigned v){v&=65535;return std::int16_t(v<32768 ? int(v) : int(v)-65536);}
constexpr std::array<unsigned,12> periods{{618,655,694,735,779,825,874,926,981,1040,1102,1167}};
constexpr std::array<unsigned,4> operators{{16,64,32,128}};
constexpr std::array<unsigned,8> carriers{{128,128,128,128,160,224,224,240}};
}
MusicalFm::MusicalFm(Board board,FmSink sink,SsgSink ssg):board_(board),sink_(std::move(sink)),
    sequence_(board,[this](const Event& e){event(e);},[this](SsgWrite w){ssg_.effect_write(w);},[this](unsigned p,bool before){tick(p,before);}),
    ssg_(sequence_,[this,sink=std::move(ssg)](SsgWrite w){registers_[0][w.address]=w.value;if(sink)sink(w);},
        [this](MusicalLfo& l){reset(l);},[this](MusicalLfo& l,unsigned n){return advance(l,n);},
        [this](unsigned limit){return random(limit);},[this]{return last_timer_a_;}),
    rhythm_(board,[this](FmWrite w){write(w.bank,w.address,w.value);}){
    attenuation_=initial_attenuation_=board==Board::fm26 ? 16 : 0;
    sequence_.fade_restored([this]{rhythm_.restore_total();});
}
std::uint8_t MusicalFm::read(unsigned at) const {return sequence_.music().at(at);}
std::uint16_t MusicalFm::word(unsigned at) const {return std::uint16_t(read(at))|std::uint16_t(read(at+1))*256;}
void MusicalFm::write(unsigned b,unsigned a,unsigned v){
    const FmWrite w{std::uint8_t(b),std::uint8_t(a),std::uint8_t(v)};
    if(!b && a<14){ssg_.raw_write(w.address,w.value);return;}
    registers_.at(b)[w.address]=w.value;if(sink_)sink_(w);
}
void MusicalFm::stop(StopReason reason){
    const bool busy=effect_busy_ && effect_busy_();
    for(unsigned b=0;b<(board_==Board::fm26 ? 1u : 2u);++b)
        for(unsigned slot=0;slot<4;++slot)for(unsigned c=0;c<3;++c){if(busy && c==2 && b==(board_==Board::fm26 ? 0u : 1u))continue;write(b,0x80+slot*4+c,255);}
    for(unsigned p=0;p<(board_==Board::fm26 ? 3u : 6u);++p){if(busy && p==(board_==Board::fm26 ? 2u : 5u))continue;keys_[hardware(p)]=0;write(0,0x28,p%3+(p>=3 ? 4 : 0));}
    ssg_.stop();sequence_.stop(reason);
}
void MusicalFm::start(){
    if(sequence_.music().empty())throw std::logic_error("FM music requires a resource");
    stop();parts_={};keys_={};parsed_note_={};tied_=temporary_=false;last_timer_a_=0;fm3_algorithm_=0;
    // The deferred FM26 mode survives song restart in the original resident.
    fm3_detune_={};fm3_mode_=63;fm3_flags_=0;
    for(unsigned p=6;p<9;++p){auto& e=parts_[p];e.slots=e.voice_mask=e.pan=e.key_flags=0;for(auto& l:e.lfo)l.depth_count=l.initial_depth_count=0;}
    sequence_.start();ssg_.start();attenuation_=initial_attenuation_;
    if(board_==Board::fm26)for(unsigned p=3;p<6;++p){part(p).slots=0;part(p).voice_mask=0;}
    // Original stereo initialization visits the primary bank first.
    for(unsigned b=0;b<(board_==Board::fm26 ? 1u : 2u);++b)
        for(unsigned c=0;c<3;++c){if(board_!=Board::fm26 && effect_busy_ && effect_busy_() && c==2 && b==(board_==Board::fm26 ? 0u : 1u))continue;write(b,0xb4+c,192);}
    write(0,0x22,0);rhythm_.start();
}
void MusicalFm::interrupt(std::uint8_t flags){
    if((flags&2) && sequence_.state().stop_pending)stop(StopReason::fade_complete);
    const auto timer=sequence_.state().timer_a;const bool playing=sequence_.state().playing;
    sequence_.interrupt(flags);if((flags&2) && playing)last_timer_a_=timer;
}
void MusicalFm::key(unsigned p,bool on){
    auto& s=part(p);if(s.note==255)return;
    if(on){keys_[hardware(p)]|=s.slots;if(s.key_counter)keys_[hardware(p)]&=s.key_mask;}
    else keys_[hardware(p)]&=std::uint8_t(~s.slots);
    write(0,0x28,keys_[hardware(p)]|channel(p)|(bank(p) ? 4 : 0));
}
void MusicalFm::silence(unsigned p){
    auto& s=part(p);
    for(unsigned slot=0;slot<4;++slot)if(s.voice_mask&(128u>>slot)){
        write(bank(p),0x40+channel(p)+slot*4,127);write(bank(p),0x80+channel(p)+slot*4,127);
    }
    const auto note=s.note;s.note=0;key(p,false);s.note=note;
}
void MusicalFm::voice(unsigned p,std::uint8_t id,bool restore){
    auto& s=part(p);
    if(word(1)!=26)throw std::invalid_argument("unrecovered external musical voice bank");
    unsigned at=word(25)+1;
    for(unsigned budget=0;;++budget){if(read(at)==id)break;if(read(at)==255 || budget>=255)throw std::out_of_range("musical FM voice not present");at+=26;}
    ++at;
    const auto algorithm=read(at+24);
    if(restore){if(fm3(p))s.algorithm=fm3_algorithm_;}
    else {
        s.algorithm=algorithm;
        if(fm3(p) && s.voice_mask){
            auto next=algorithm;
            if(!(s.slots&16))next=std::uint8_t((next&7)|(fm3_algorithm_&56));
            fm3_algorithm_=next;s.algorithm=next;
            // The masked FM3 dispatcher stores its surviving AL (voice ID),
            // while a separate global keeps the real FM3 algorithm.
            if(sequence_.state().parts[p].mask && s.voice_mask)s.algorithm=(s.slots&16) ? id : std::uint8_t(next&56);
        }
    }
    for(unsigned i=0;i<4;++i)s.total_levels[i]=read(at+4+i);
    if(sequence_.state().parts[p].mask && !restore)return;
    if(s.voice_mask)silence(p);
    else return;
    write(bank(p),0xb0+channel(p),s.algorithm);
    s.carrier_mask=std::uint8_t(carriers[s.algorithm&7]);
    for(auto& l:s.lfo)if(!(l.mask&15))l.mask=s.carrier_mask;
    for(unsigned i=0;i<4;++i)if(s.voice_mask&(128u>>i))write(bank(p),0x30+channel(p)+i*4,read(at+i));
    for(unsigned i=0;i<4;++i)if((s.voice_mask&(128u>>i)) && !(s.carrier_mask&operators[i]))write(bank(p),0x40+channel(p)+i*4,read(at+4+i));
    for(unsigned group=0;group<4;++group)for(unsigned i=0;i<4;++i)
        if(s.voice_mask&(128u>>i))write(bank(p),0x50+channel(p)+group*16+i*4,read(at+8+group*4+i));
}
void MusicalFm::borrow_effect(){
    if(board_==Board::fm26){fm3_pending_=fm3_mode_;fm3_mode_=63;}
    for(unsigned p=0;p<6;++p)if(p==5 || (board_==Board::fm26 && p>=2))sequence_.borrow_fm(p);
}
void MusicalFm::restore_effect_voice(){
    // Effect silence key-offs every slot on the shared hardware channel.
    keys_[board_==Board::fm26 ? 2 : 5]=0;
    if(!sequence_.state().playing)return;
    if(board_==Board::fm26){
        // FM26 aliases its three disabled D-F works as FM3 extensions.
        for(unsigned p=2;p<6;++p)restore_voice(p);
        fm3_mode_=fm3_pending_;
    }else restore_voice(5);
}
void MusicalFm::restore_voice(unsigned p){
    auto& s=part(p);
    if(!s.voice_mask)return;
    const auto levels=s.total_levels;
    voice(p,sequence_.state().parts[p].instrument,true);s.total_levels=levels;
    for(unsigned slot:{3u,1u,2u,0u})if((s.slots&operators[slot]) && !(s.carrier_mask&operators[slot]))
        write(bank(p),0x40+channel(p)+slot*4,s.total_levels[slot]);
    if(board_!=Board::fm26)write(bank(p),0xb4+channel(p),s.hardware_counter ? s.pan&192 : s.pan);
}
void MusicalFm::volume(unsigned p){
    const auto& s=part(p);if(!s.slots)return;
    unsigned value=s.temporary_volume ? s.temporary_volume-1 : sequence_.state().parts[p].volume;
    if(attenuation_)value=(value*std::uint8_t(0-attenuation_))>>8;
    const auto fade=sequence_.state().fade;if(fade>=2)value=(value*std::uint8_t(0-(fade/2)))>>8;
    const unsigned attenuation=std::uint8_t(~value);unsigned selected=s.slots&s.carrier_mask;
    for(unsigned slot:{3u,1u,2u,0u}){
        int level=(selected&operators[slot]) ? int(attenuation) : 128;
        if(attenuation!=255)for(unsigned l=0;l<2;++l)if((s.flags&(2u<<(l*4))) && (s.lfo[l].mask&s.slots&operators[slot])){
            selected|=operators[slot];const int amount=i8(std::uint8_t(s.lfo[l].value));
            level=std::clamp(level-amount,0,255);
        }
        if(selected&operators[slot])write(bank(p),0x40+channel(p)+slot*4,std::max(0,std::min(255,level+int(s.total_levels[slot]))-128));
    }
}
void MusicalFm::pitch(unsigned p){
    const auto& s=part(p);if(!s.frequency || !s.slots)return;
    const auto base=std::uint16_t((s.frequency&2047)+std::uint16_t(s.slide)+std::uint16_t(sequence_.state().parts[p].detune));
    auto period=[&](std::uint16_t value){
        int block=s.frequency&0x3800;
        for(unsigned budget=0;budget<128;++budget){
            if(value<32768 && value>=618){if(value<1236)break;block+=2048;if(block==16384){block=14336;value=std::min<std::uint16_t>(value,2047);break;}value-=618;}
            else{block-=2048;if(block<0){block=0;if(value>=32768 || value<8)value=8;break;}value+=618;}
        }
        return std::uint16_t(value)|std::uint16_t(block);
    };
    if(fm3(p) && fm3_mode_!=63){
        auto first=(s.lfo[0].mask&15) ? s.lfo[0].mask : std::uint8_t(240);
        auto second=(s.lfo[1].mask&15) ? s.lfo[1].mask : std::uint8_t(240);
        const std::array<unsigned,4> address{{0xa9,0xaa,0xa8,0xa2}};
        for(int slot=3;slot>=0;--slot)if(s.slots&(16u<<slot)){
            auto value=std::uint16_t(base+std::uint16_t(fm3_detune_[slot]));
            // Masks rotate only for an owned operator, as in the target.
            const bool a=first&128,b=second&128;first=std::uint8_t((first<<1)|(first>>7));second=std::uint8_t((second<<1)|(second>>7));
            if(a && (s.flags&1))value+=std::uint16_t(s.lfo[0].value);
            if(b && (s.flags&16))value+=std::uint16_t(s.lfo[1].value);
            const auto v=period(value);write(0,address[slot]+4,v>>8);write(0,address[slot],v&255);
        }
    }else{
        auto value=base;for(unsigned l=0;l<2;++l)if(s.flags&(1u<<(l*4)))value+=std::uint16_t(s.lfo[l].value);
        const auto v=period(value);write(bank(p),0xa4+channel(p),v>>8);write(bank(p),0xa0+channel(p),v&255);
    }
}
void MusicalFm::mode(unsigned p){
    if(!fm3(p))return;
    const auto& s=part(p);const unsigned bit=p==2 ? 1 : 2u<<(board_==Board::fm26 ? p-3 : p-11);
    // Full-slot secondary LFO mode is gated by the primary mask low nibble.
    // Preserve the target short circuit rather than a symmetric LFO test.
    const bool partial=s.slots && (s.slots!=240 || ((s.lfo[0].mask&15) && ((s.flags&1) || ((s.lfo[1].mask&15) && (s.flags&16)))));
    if(partial)fm3_flags_|=bit;else fm3_flags_&=std::uint8_t(~bit);
    const std::uint8_t next=(fm3_flags_ || fm3_detuned()) ? 127 : 63;
    if(board_==Board::fm26 && (sequence_.state().parts[p].mask&2)){fm3_pending_=next;return;}
    if(next==fm3_mode_)return;
    fm3_mode_=next;write(0,0x27,next&207);
    if(next!=63 && p!=2){
        const unsigned last=board_==Board::fm26 ? p : p-8;
        for(unsigned n=2;n<last;++n){const unsigned seq=n==2 ? 2 : board_==Board::fm26 ? n : n+8;if(!sequence_.state().parts[seq].mask)pitch(seq);}
    }
}
void MusicalFm::slots(unsigned p,std::uint8_t value){
    auto& s=part(p);const unsigned selected=value&15;
    s.carrier_mask=selected ? std::uint8_t(selected<<4) : carriers[(fm3(p) ? fm3_algorithm_ : s.algorithm)&7];
    const auto next=std::uint8_t(value&240);if(next==s.slots)return;
    s.slots=next;sequence_.slots_mask(p,!next);mode(p);
    if(fm3(p) && p!=2){
        const unsigned last=board_==Board::fm26 ? p : p-8;
        for(unsigned n=2;n<last;++n){const unsigned seq=n==2 ? 2 : board_==Board::fm26 ? n : n+8;if(!sequence_.state().parts[seq].mask && !(part(seq).key_flags&1))key(seq,true);}
    }
    // Logical slot bits become duplicated physical voice-parameter masks.
    s.voice_mask=0;for(unsigned i=0;i<4;++i)if(s.slots&operators[i])s.voice_mask|=std::uint8_t((128u>>i)|((128u>>i)>>4));
}
void MusicalFm::reset(MusicalLfo& l){
    l.value=0;l.delay=l.initial_delay;l.speed=l.initial_speed;l.step=l.initial_step;l.count=l.initial_count;l.depth_count=l.initial_depth_count;
    if(l.shape==2 || l.shape==3)l.speed=1;else ++l.speed;
}
std::uint16_t MusicalFm::random(unsigned limit){
    random_=std::uint16_t((unsigned(random_)*259+3)&32767);
    return std::uint16_t((unsigned(random_)*std::uint16_t(limit))/32767);
}
void MusicalFm::depth(MusicalLfo& l){
    if(--l.depth_speed)return;
    l.depth_speed=l.initial_depth_speed;
    if(!l.depth_count)return;
    if(!(l.depth_count&128))--l.depth_count;
    const bool negative=l.step<0;const auto v=std::uint8_t((negative ? -int(l.step) : int(l.step))+int(l.depth_step));
    int next=i8(v);
    if(v&128)next=l.depth_step<0 ? 0 : 127;
    l.step=std::int8_t(negative ? -next : next);
}
bool MusicalFm::advance(MusicalLfo& l,unsigned ticks){
    if(l.delay){--l.delay;return false;}const auto before=l.value;
    for(unsigned t=0;t<ticks;++t){
        if(l.speed!=1){if(l.speed!=255)--l.speed;continue;}l.speed=l.initial_speed;
        if(l.shape==0 || l.shape==4 || l.shape==5){
            const int step=l.shape==5 ? int(l.step)*std::abs(int(l.step)) : int(l.step);
            l.value=i16(std::uint16_t(l.value)+step);if(!l.value)depth(l);
            if(l.count!=255 && !--l.count){l.count=std::uint8_t(l.initial_count*(l.shape==4 ? 1 : 2));l.step=std::int8_t(i8(std::uint8_t(-int(l.step))));}
        }else if(l.shape==1){
            l.value=i16(std::uint16_t(l.value)+int(l.step));
            if(l.count!=255 && !--l.count){l.value=i16(std::uint16_t(-int(l.value)));depth(l);l.count=std::uint8_t(l.initial_count*2);}
        }else if(l.shape==2){
            l.value=i16(int(l.step)*i8(l.count));depth(l);l.step=std::int8_t(i8(std::uint8_t(-int(l.step))));
        }else if(l.shape==3){
            const unsigned range=unsigned(std::abs(int(l.step)))*l.count;
            l.value=i16(random(range*2)-range);depth(l);
        }else if(l.shape==6){
            if(l.count){if(l.count!=255)--l.count;l.value=i16(std::uint16_t(l.value)+int(l.step));}
        }else throw std::invalid_argument("unrecovered musical FM LFO shape");
    }
    return before!=l.value;
}
std::uint8_t MusicalFm::transpose(unsigned p,std::uint8_t note) const{
    if((note&15)==15)return note;
    const auto& track=sequence_.state().parts[p];int octave=note>>4,pitch=note&15;
    pitch+=i8(std::uint8_t(track.transpose+track.master_transpose));while(pitch<0){pitch+=12;--octave;}while(pitch>=12){pitch-=12;++octave;}
    return std::uint8_t((std::uint8_t(octave)<<4)|unsigned(pitch));
}
void MusicalFm::prepare(unsigned p,std::uint8_t n){
    auto& s=part(p);if((n&15)==12)n=s.last_note;s.last_note=n;
    const bool fresh=(n&15)!=15 && !tied_;if((n&15)!=15)s.slide=0;
    if(fresh){s.hardware_counter=s.hardware_delay;if(s.hardware_counter)write(bank(p),0xb4+channel(p),s.pan&192);s.key_counter=s.key_delay;}
    for(unsigned l=0;l<2;++l)if(s.flags&(3u<<(l*4))){
        if(fresh && !(s.flags&(4u<<(l*4))))reset(s.lfo[l]);
        const unsigned ticks=(s.clock_flags&(2u<<(l*4))) ? std::uint8_t(sequence_.state().timer_a-last_timer_a_) : 1;
        advance(s.lfo[l],ticks);
    }
}
void MusicalFm::frequency(unsigned p,std::uint8_t n){
    auto& s=part(p);if((n&15)==15){s.note=255;if(!(s.flags&17))s.frequency=0;return;}
    s.note=n;s.frequency=std::uint16_t(periods.at(n&15))|std::uint16_t((n>>1)&56)*256;
}
void MusicalFm::gate(unsigned p,unsigned duration,unsigned next){
    auto& s=part(p);if(read(next)==193){s.gate=0;return;}
    unsigned amount=std::uint8_t(s.gate_amount+((duration*s.gate_ratio)>>8));
    if(s.gate_random){const auto v=random((s.gate_random&127)+1);amount=(s.gate_random&128) ? unsigned(std::max(0,int(amount)-int(v))) : std::uint8_t(amount+v);}
    if(s.gate_minimum){if(duration<s.gate_minimum)amount=0;else amount=std::min(amount,duration-s.gate_minimum);}
    s.gate=std::uint8_t(amount);
}
void MusicalFm::note(unsigned p,const Event& e){
    auto& s=part(p);const auto& track=sequence_.state().parts[p];parsed_note_[index(p)]=true;
    if(sequence_.masked_parser(p)){s.frequency=0;s.note=s.last_note=255;s.key_flags=255;if(!temporary_)s.temporary_volume=0;tied_=temporary_=false;return;}
    s.flags&=247;
    unsigned duration=e.arguments.at(0),next=e.offset+2;
    if(e.kind==Kind::portamento){
        prepare(p,e.arguments.at(0));frequency(p,transpose(p,s.last_note));const auto begin=s.frequency;const auto first=s.note;
        frequency(p,transpose(p,e.arguments.at(1)));const auto end=s.frequency;s.frequency=begin;s.note=first;
        const int delta=((int(end&0x3800)-int(begin&0x3800))/2048)*618+int(end&2047)-int(begin&2047);
        duration=e.arguments.at(2);next=e.offset+4;if(!duration)throw std::invalid_argument("musical FM zero slide duration");
        s.slide_step=i16(delta/int(duration));s.slide_remainder=i16(delta%int(duration));s.flags|=8;
    }else {prepare(p,e.opcode);frequency(p,transpose(p,s.last_note));}
    gate(p,duration,next);
    if(s.temporary_volume && s.note!=255 && !temporary_)s.temporary_volume=0;
    volume(p);pitch(p);key(p,true);tied_=temporary_=false;s.key_flags=read(next)==251 ? 2 : 0;
}
void MusicalFm::command(unsigned p,const Event& e){
    auto& s=part(p);const auto& a=e.arguments;
    switch(e.opcode){
    case 255:voice(p,a.at(0));break;
    case 254:s.gate_amount=a.at(0);s.gate_random=0;break;
    case 251:tied_=true;break;
    case 242:case 191:{auto& l=s.lfo[e.opcode==191];l.initial_delay=a.at(0);l.initial_speed=a.at(1);l.initial_step=std::int8_t(i8(a.at(2)));l.initial_count=a.at(3);reset(l);break;}
    case 241:case 190:{const unsigned index=e.opcode==190,shift=index*4;auto v=a.at(0);if(v&248)v=1;s.flags=std::uint8_t((s.flags&~(7u<<shift))|((v&7)<<shift));reset(s.lfo[index]);break;}
    case 203:s.lfo[0].shape=a.at(0);break;
    case 188:s.lfo[1].shape=a.at(0);break;
    case 202:case 187:{const unsigned shift=e.opcode==187 ? 4 : 0;s.clock_flags=std::uint8_t((s.clock_flags&~(2u<<shift))|((a.at(0)&1)<<(shift+1)));break;}
    case 194:case 185:{auto& l=s.lfo[e.opcode==185];l.initial_delay=a.at(0);l.delay=a.at(0);reset(l);break;}
    case 214:case 189:{auto& l=s.lfo[e.opcode==189];l.depth_speed=l.initial_depth_speed=a.at(0);l.depth_step=std::int8_t(i8(a.at(1)));break;}
    case 183:{auto& l=s.lfo[(a.at(0)&128)!=0];const auto count=std::uint8_t(a.at(0)&127);l.depth_count=l.initial_depth_count=count ? count : 255;break;}
    case 197:case 186:{auto& l=s.lfo[e.opcode==186];l.mask=(a.at(0)&15) ? std::uint8_t((a.at(0)<<4)|15) : s.carrier_mask;break;}
    case 198:{for(unsigned n=0;n<3;++n){const auto offset=std::uint16_t(a.at(n*2))|std::uint16_t(a.at(n*2+1))*256;if(!offset)continue;sequence_.activate_fm3(n,offset);const unsigned target=board_==Board::fm26 ? n+3 : n+11;auto& e=part(target);e.key_flags=e.note=e.last_note=255;for(auto& l:e.lfo)l.depth_count=l.initial_depth_count=255;e.pan=part(2).pan;}break;}
    case 199:case 200:{if(fm3(p)){const auto value=std::uint16_t(a.at(1))|std::uint16_t(a.at(2))*256;for(unsigned n=0;n<4;++n)if(a.at(0)&(1u<<n))fm3_detune_[n]=i16(e.opcode==200 ? value : std::uint16_t(fm3_detune_[n])+value);mode(p);}break;}
    case 207:slots(p,a.at(0));break;
    case 196:s.gate_ratio=a.at(0);break;
    case 179:s.gate_minimum=a.at(0);break;
    case 177:s.gate_random=a.at(0);break;
    case 181:s.key_mask=std::uint8_t(((a.at(0)&15)^15)<<4);s.key_delay=s.key_counter=a.at(1);break;
    case 182:{
        // The26 masked decoder consumes B6 without updating disabled FM D-F.
        if(board_==Board::fm26 && p>=3 && !s.slots)break;
        // B6 rotates an absolute byte, but clamps a relative byte only after
        // its eight-bit addition. FM3's feedback belongs to operator1 and
        // uses the shared algorithm rather than the masked voice-ID field.
        const bool special=fm3(p);
        const auto previous=special ? fm3_algorithm_ : s.algorithm;
        auto value=a.at(0);unsigned feedback;
        if(value&128){
            if(!(value&64))value&=7;
            const auto sum=std::uint8_t(value+((previous>>3)&7));
            feedback=(sum&128) ? 0 : sum>=8 ? 56 : unsigned(sum)*8;
        }else feedback=std::uint8_t((unsigned(value)<<3)|(value>>5));
        if(special && !(s.slots&16))break;
        const auto algorithm=std::uint8_t((previous&7)|feedback);
        if(special)fm3_algorithm_=algorithm;
        write(bank(p),0xb0+channel(p),algorithm);s.algorithm=algorithm;
        break;
    }
    case 184:{
        // B8's logical operator order is1,2,3,4; the OPN addresses are
        // 40,48,44,4C. Masking suppresses hardware writes, not stored TL.
        const unsigned selected=(unsigned(a.at(0)&15)<<4)&s.slots;
        for(unsigned slot:{0u,2u,1u,3u})if(selected&operators[slot]){
            auto level=std::uint8_t(a.at(1)&127);
            if(a.at(0)&128){
                level=std::uint8_t(s.total_levels[slot]+a.at(1));
                if(level&128)level=(a.at(1)&128) ? 0 : 127;
            }
            s.total_levels[slot]=level;
            if(!sequence_.state().parts[p].mask)write(bank(p),0x40+channel(p)+slot*4,level);
        }
        break;
    }
    case 228:if(board_!=Board::fm26)s.hardware_delay=a.at(0);break;
    case 224:if(board_!=Board::fm26)write(0,34,a.at(0));break;
    case 222:case 221:{const unsigned v=sequence_.state().parts[p].volume;s.temporary_volume=std::uint8_t((e.opcode==222 ? std::min<unsigned>(127u,std::uint8_t(v+a.at(0))) : unsigned(std::max(0,int(v)-int(a.at(0)))))+1);temporary_=true;break;}
    case 236:if(board_!=Board::fm26){s.pan=std::uint8_t((s.pan&63)|((a.at(0)&3)<<6));if(!sequence_.state().parts[p].mask)write(bank(p),0xb4+channel(p),s.pan);}break;
    case 225:if(board_!=Board::fm26){s.pan=std::uint8_t((s.pan&192)|a.at(0));if(!sequence_.state().parts[p].mask)write(bank(p),0xb4+channel(p),s.pan);}break;
    case 195:if(board_!=Board::fm26){s.pan=std::uint8_t((s.pan&63)|(!a.at(0) ? 192 : (a.at(0)&128) ? 64 : 128));if(!sequence_.state().parts[p].mask)write(bank(p),0xb4+channel(p),s.pan);}break;
    case 233:case 235:case 234:case 232:case 230:case 229:break; // Hardware rhythm belongs to a separate voice owner.
    case 239:write(bank(p),a.at(0),a.at(1));break;
    case 218:case 253:case 252:case 250:case 249:case 248:case 247:case 246:case 245:case 244:case 243:case 231:case 227:case 226:case 223:case 220:case 219:case 213:case 212:case 211:case 210:case 178:case 193:break; // Bytecode/global state remains in Sequence.
    default:throw std::invalid_argument("unrecovered musical FM command "+std::to_string(e.opcode));
    }
}
void MusicalFm::event(const Event& e){
    rhythm_.event(e,sequence_.state());
    ssg_.event(e);
    if(e.kind==Kind::command && e.opcode==239 && e.part>=6 && e.part<=8){
        if(e.arguments.at(0)>=14)write(0,e.arguments.at(0),e.arguments.at(1));
        return;
    }
    if(e.kind==Kind::command && e.opcode==192){
        const auto sub=e.arguments.at(0);
        if((e.part<6 || e.part>=11) && sub<2){
            const auto mask=sequence_.state().parts[e.part].mask;
            if(sub==1 && mask==64)silence(e.part);
            else if(sub==0 && !mask)restore_voice(e.part);
        }
        if(sub==255)attenuation_=e.arguments.at(1);
        else if(sub==254){const int amount=i8(e.arguments.at(1));attenuation_=amount ? std::uint8_t(std::clamp(int(attenuation_)+amount,0,255)) : initial_attenuation_;}
        return;
    }
    if(e.part>=6 && e.part<11)return;
    if(e.kind==Kind::note || e.kind==Kind::portamento)note(e.part,e);
    else if(e.kind==Kind::command){command(e.part,e);if(e.opcode==197 || e.opcode==186 || e.opcode==241 || e.opcode==190)mode(e.part);}
    else if(e.kind==Kind::end)part(e.part).note=255;
}
void MusicalFm::tick(unsigned p,bool before){
    ssg_.tick(p,before);
    if(p>=6 && p<11)return;
    auto& s=part(p);const auto& track=sequence_.state().parts[p];
    if(before){
        parsed_note_[index(p)]=false;
        if(track.mask){s.key_flags=255;return;}
        if(!(s.key_flags&3) && std::uint8_t(track.length-1)<=s.gate){key(p,false);s.key_flags=255;}
        if(track.length==1)s.flags&=247;
        return;
    }
    if(parsed_note_[index(p)] || track.mask)return;
    if(s.hardware_counter && !--s.hardware_counter)write(bank(p),0xb4+channel(p),s.pan);
    if(s.key_counter && !--s.key_counter && !(s.key_flags&1))key(p,true);
    unsigned changed=s.flags&8;
    for(unsigned l=0;l<2;++l)if(s.flags&(3u<<(l*4))){
        const unsigned ticks=(s.clock_flags&(2u<<(l*4))) ? std::uint8_t(sequence_.state().timer_a-last_timer_a_) : 1;
        if(advance(s.lfo[l],ticks))changed|=s.flags&(3u<<(l*4));
    }
    if(changed&25){
        if(changed&8){s.slide=i16(std::uint16_t(s.slide)+s.slide_step);if(s.slide_remainder>0){--s.slide_remainder;s.slide=i16(std::uint16_t(s.slide)+1);}else if(s.slide_remainder<0){++s.slide_remainder;s.slide=i16(std::uint16_t(s.slide)-1);}}
        pitch(p);
    }
    if((changed&34) || sequence_.state().fade_speed)volume(p);
}
}
