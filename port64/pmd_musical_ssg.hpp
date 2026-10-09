#pragma once
#include "pmd_musical_lfo.hpp"
namespace th04::portable::pmd {
// Normal envelopes reuse counters; extended envelopes use rates and phases.
// Both retain eight-bit arithmetic from the driver, including signed levels.
struct SsgEnvelope {
    std::uint8_t mode=3,phase=0;
    std::uint8_t attack=0,decay=0,sustain=0,release=0;
    std::uint8_t sustain_level=0,initial_level=0;
    std::uint8_t attack_counter=0,decay_counter=0,sustain_counter=0,release_counter=0,level=0;
};
struct MusicalSsgPart {
    std::uint16_t frequency=0;
    std::int16_t slide=0,slide_step=0,slide_remainder=0;
    std::array<MusicalLfo,2> lfo{};
    SsgEnvelope envelope;
    std::uint8_t gate=0,gate_amount=0,gate_ratio=0,gate_minimum=0,gate_random=0;
    std::uint8_t flags=0,clock_flags=0,temporary_volume=0,mixer=7;
    std::uint8_t key_flags=255,note=255,last_note=255;
};
// One sequence owns FM, SSG and built-in effects. Callbacks share the original
// musical random stream and Timer A baseline; there is no second music clock.
class MusicalSsg {
public:
    using Reset=std::function<void(MusicalLfo&)>;
    using Advance=std::function<bool(MusicalLfo&,unsigned)>;
    MusicalSsg(Sequence&,SsgSink,Reset,Advance,std::function<std::uint16_t(unsigned)>,std::function<std::uint8_t()>);
    void start();void stop();
    void event(const Event&);void tick(unsigned,bool);
    void effect_write(SsgWrite);
    void raw_write(std::uint8_t address,std::uint8_t value) {write(address,value);}
    void mirror(std::uint8_t address,std::uint8_t value);
    const std::array<MusicalSsgPart,3>& parts() const {return parts_;}
    const std::array<std::uint8_t,14>& registers() const {return registers_;}
    std::uint8_t attenuation() const {return attenuation_;}
    std::uint8_t initial_attenuation() const {return initial_attenuation_;}
    std::uint8_t noise() const {return noise_;}
    std::uint8_t previous_noise() const {return previous_noise_;}
private:
    Sequence& sequence_;SsgSink sink_;Reset reset_;Advance advance_;
    std::function<std::uint16_t(unsigned)> random_;std::function<std::uint8_t()> timer_baseline_;
    std::array<MusicalSsgPart,3> parts_{};
    std::array<std::uint8_t,14> registers_{};
    std::array<bool,3> parsed_note_{};
    std::uint8_t attenuation_=0,initial_attenuation_=0,noise_=0,previous_noise_=0;
    bool tied_=false,temporary_=false;
    void write(unsigned,unsigned);
    unsigned clocks(const MusicalSsgPart&,unsigned) const;
    std::uint8_t transpose(unsigned,std::uint8_t) const;
    void frequency(unsigned,std::uint8_t);void pitch(unsigned);void volume(unsigned);void key(unsigned);
    void release(unsigned);void prepare(unsigned,std::uint8_t);void note(unsigned,const Event&);
    void command(unsigned,const Event&);void gate(unsigned,unsigned,unsigned);
    void start_envelope(SsgEnvelope&);bool envelope(SsgEnvelope&,unsigned);void envelope_tick(SsgEnvelope&);
};
}
