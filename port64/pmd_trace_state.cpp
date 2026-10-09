#include "pmd_trace_state.hpp"
#include <ostream>
namespace th04::portable::pmd {
bool owns_fm_write(unsigned b,unsigned a){return (a>=48 && a<=182) || (b==0 && (a==34 || a==40));}
namespace {
std::vector<unsigned> work(const MusicalFm& music,unsigned part,unsigned size){
    const auto& t=music.sequence().state().parts[part+6];const auto& s=music.ssg().parts()[part];const auto& e=s.envelope;
    std::vector<unsigned> result(size,0);auto word=[&](unsigned at,unsigned v){result.at(at)=v&255;result.at(at+1)=(v>>8)&255;};
    word(0,t.position);word(2,t.loop);result[4]=t.length;result[5]=s.gate;word(6,s.frequency);word(8,std::uint16_t(t.detune));word(12,std::uint16_t(s.slide));word(14,std::uint16_t(s.slide_step));word(16,std::uint16_t(s.slide_remainder));
    result[18]=t.volume;result[19]=t.transpose;result[28]=s.flags;result[29]=s.temporary_volume;result[46]=s.clock_flags;result[48]=s.mixer;result[49]=t.instrument;result[50]=t.loop_status;result[59]=t.mask;result[60]=s.key_flags;result[62]=s.gate_amount;result[63]=s.gate_ratio;
    result[33]=e.mode;result[34]=e.phase;result[35]=e.attack;result[36]=e.decay;result[37]=e.sustain;result[38]=e.release;result[39]=e.sustain_level;result[40]=e.initial_level;result[41]=e.attack_counter;result[42]=e.decay_counter;result[43]=e.sustain_counter;result[44]=e.release_counter;result[45]=e.level;
    result[85]=s.note;result[90]=t.notes;result[91]=s.gate_minimum;result[94]=s.last_note;result[95]=t.master_transpose;if(size>96)result[96]=s.gate_random;
    for(unsigned n=0;n<2;++n){const auto& l=s.lfo[n];unsigned at=n ? 68 : 20;word(n ? 66 : 10,std::uint16_t(l.value));result[at]=l.delay;result[at+1]=l.speed;result[at+2]=std::uint8_t(l.step);result[at+3]=l.count;result[at+4]=l.initial_delay;result[at+5]=l.initial_speed;result[at+6]=std::uint8_t(l.initial_step);result[at+7]=l.initial_count;result[n ? 76 : 30]=std::uint8_t(l.depth_step);result[n ? 77 : 31]=l.depth_speed;result[n ? 78 : 32]=l.initial_depth_speed;result[n ? 79 : 58]=l.shape;result[n ? 80 : 61]=l.mask;result[81+n*2]=l.depth_count;result[82+n*2]=l.initial_depth_count;}
    return result;
}
}
void write_fm_player_state(std::ostream& out,const FmPlayer& player){
    const auto& m=player.music();const auto& seq=m.sequence();const auto& state=seq.state();
    out<<state.measure<<' '<<unsigned(state.fade)<<' '<<seq.status()<<' '<<unsigned(state.timer_b)<<' '<<unsigned(state.timer_a);
    for(unsigned p=0;p<6;++p){
        const auto& t=state.parts[p];const auto& s=m.parts()[p];
        out<<' '<<t.position<<' '<<t.loop<<' '<<unsigned(t.length)<<' '<<unsigned(t.loop_status)<<' '<<unsigned(t.notes)<<' '<<unsigned(t.volume)<<' '<<unsigned(t.transpose)<<' '<<unsigned(t.master_transpose)<<' '<<t.detune<<' '<<unsigned(t.instrument)<<' '<<unsigned(t.mask);
        out<<' '<<unsigned(s.gate)<<' '<<s.frequency<<' '<<s.slide<<' '<<s.slide_step<<' '<<s.slide_remainder<<' '<<unsigned(s.flags)<<' '<<unsigned(s.clock_flags)<<' '<<unsigned(s.temporary_volume)<<' '<<unsigned(s.pan)<<' '<<unsigned(s.carrier_mask)<<' '<<unsigned(s.slots)<<' '<<unsigned(s.voice_mask);
        for(auto v:s.total_levels)out<<' '<<unsigned(v);
        out<<' '<<unsigned(s.key_flags)<<' '<<unsigned(s.note)<<' '<<unsigned(s.last_note)<<' '<<unsigned(s.algorithm)<<' '<<unsigned(s.gate_amount)<<' '<<unsigned(s.gate_ratio)<<' '<<unsigned(s.gate_minimum)<<' '<<unsigned(s.gate_random)<<' '<<unsigned(s.hardware_delay)<<' '<<unsigned(s.hardware_counter)<<' '<<unsigned(s.key_delay)<<' '<<unsigned(s.key_counter)<<' '<<unsigned(s.key_mask);
        for(const auto& l:s.lfo)out<<' '<<l.value<<' '<<unsigned(l.delay)<<' '<<unsigned(l.speed)<<' '<<int(l.step)<<' '<<unsigned(l.count)<<' '<<unsigned(l.initial_delay)<<' '<<unsigned(l.initial_speed)<<' '<<int(l.initial_step)<<' '<<unsigned(l.initial_count)<<' '<<unsigned(l.shape)<<' '<<unsigned(l.mask)<<' '<<int(l.depth_step)<<' '<<unsigned(l.depth_speed)<<' '<<unsigned(l.initial_depth_speed)<<' '<<unsigned(l.depth_count)<<' '<<unsigned(l.initial_depth_count);
    }
    for(unsigned b=0;b<2;++b)for(unsigned a=0;a<256;++a)if(owns_fm_write(b,a))out<<' '<<unsigned(m.registers()[b][a]);
    const auto& s=player.effects().state();const auto& l=s.lfo;
    out<<' '<<s.active<<' '<<unsigned(s.effect)<<' '<<s.position<<' '<<s.loop<<' '
       <<unsigned(s.ticks)<<' '<<unsigned(s.gate)<<' '<<s.frequency<<' '<<s.detune<<' '
       <<l.value<<' '<<s.slide<<' '<<s.slide_step<<' '<<s.slide_remainder<<' '
       <<unsigned(s.volume)<<' '<<unsigned(s.transpose)<<' '<<unsigned(l.delay)<<' '
       <<unsigned(l.speed)<<' '<<int(l.step)<<' '<<unsigned(l.count)<<' '
       <<unsigned(l.initial_delay)<<' '<<unsigned(l.initial_speed)<<' '<<int(l.initial_step)<<' '
       <<unsigned(l.initial_count)<<' '<<unsigned(s.lfo_flags)<<' '<<unsigned(s.pan)<<' '
       <<unsigned(s.instrument)<<' '<<unsigned(s.loop_status)<<' '<<unsigned(s.carrier_mask);
    for(auto v:s.total_levels)out<<' '<<unsigned(v);
    out<<' '<<unsigned(s.slots)<<' '<<unsigned(s.voice_mask)<<' '<<unsigned(l.shape)<<' '
       <<unsigned(s.key_flags)<<' '<<unsigned(s.lfo_mask)<<' '<<unsigned(s.gate_amount)<<' '
       <<unsigned(s.note)<<' '<<unsigned(s.algorithm)<<' '<<unsigned(s.notes)<<' '
       <<unsigned(s.last_note)<<' '<<unsigned(s.master_transpose);
}
void write_ssg_music_state(std::ostream& out,const MusicalFm& m,unsigned size){
    const auto& seq=m.sequence();const auto& state=seq.state();const auto& ssg=m.ssg();const auto& effect=seq.ssg_effects().state();
    out<<state.measure<<' '<<unsigned(state.fade)<<' '<<seq.status()<<' '<<unsigned(state.timer_b)<<' '<<unsigned(state.timer_a)<<' '<<unsigned(ssg.attenuation())<<' '<<unsigned(ssg.initial_attenuation())<<' '<<unsigned(ssg.noise())<<' '<<unsigned(ssg.previous_noise());
    for(unsigned p=0;p<3;++p)for(auto v:work(m,p,size))out<<' '<<v;
    out<<' '<<effect.resource<<' '<<effect.next_frame<<' '<<effect.tone<<' '<<effect.tone_step<<' '<<unsigned(effect.ticks)<<' '<<unsigned(effect.noise)<<' '<<int(effect.noise_step)<<' '<<unsigned(effect.noise_interval)<<' '<<unsigned(effect.noise_counter)<<' '<<unsigned(effect.priority)<<' '<<unsigned(effect.effect);
    for(auto v:ssg.registers())out<<' '<<unsigned(v);
}
}
