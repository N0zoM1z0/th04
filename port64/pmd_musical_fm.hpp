#pragma once
#include "pmd_fm_effects.hpp"

namespace th04::portable::pmd {
struct MusicalLfo : FmLfo {
    std::int8_t depth_step=0;
    std::uint8_t depth_speed=0,initial_depth_speed=0;
    std::uint8_t depth_count=255,initial_depth_count=255,mask=0;
};
struct MusicalFmPart {
    std::uint16_t frequency=0;
    std::int16_t slide=0,slide_step=0,slide_remainder=0;
    std::array<MusicalLfo,2> lfo{};
    std::uint8_t gate=0,gate_amount=0,gate_ratio=0,gate_minimum=0,gate_random=0;
    std::uint8_t flags=0,clock_flags=0,temporary_volume=0;
    std::uint8_t pan=192,carrier_mask=0,slots=240,voice_mask=255;
    std::array<std::uint8_t,4> total_levels{};
    std::uint8_t key_flags=255,note=255,last_note=255,algorithm=0;
    std::uint8_t hardware_delay=0,hardware_counter=0;
    std::uint8_t key_delay=0,key_counter=0,key_mask=0;
};
// Musical FM state and register requests join the attested bytecode owner.
// Interrupt flags are explicit inputs; this owner never opens an audio device.
class MusicalFm {
public:
    explicit MusicalFm(Board board=Board::fm26,FmSink sink={});
    MusicalFm(const MusicalFm&)=delete;
    MusicalFm& operator=(const MusicalFm&)=delete;
    MusicalFm(MusicalFm&&)=delete;
    MusicalFm& operator=(MusicalFm&&)=delete;
    void attenuation(std::uint8_t value) {attenuation_=initial_attenuation_=value;}
    void load(const Bytes& bytes) {sequence_.load(bytes);}
    void start();void stop();void fade(std::int8_t speed) {sequence_.fade(speed);}
    void interrupt(std::uint8_t flags);
    void mirror(std::uint8_t bank,std::uint8_t address,std::uint8_t value) {registers_.at(bank)[address]=value;}
    void effects_active(std::function<bool()> query) {effect_busy_=query;sequence_.fm_effect_active(std::move(query));}
    void borrow_effect();
    void restore_effect_voice();
    const Sequence& sequence() const {return sequence_;}
    const std::array<MusicalFmPart,6>& parts() const {return parts_;}
    const std::array<std::array<std::uint8_t,256>,2>& registers() const {return registers_;}
private:
    Board board_;FmSink sink_;Sequence sequence_;std::function<bool()> effect_busy_;std::uint8_t fm3_algorithm_=0;
    std::array<MusicalFmPart,6> parts_{};
    std::array<std::array<std::uint8_t,256>,2> registers_{};
    std::array<std::uint8_t,6> keys_{};
    std::array<bool,6> parsed_note_{};
    std::uint8_t last_timer_a_=0;std::uint16_t random_=0;
    bool tied_=false,temporary_=false;
    std::uint8_t attenuation_=0,initial_attenuation_=0;
    unsigned bank(unsigned p) const {return p/3;}
    unsigned channel(unsigned p) const {return p%3;}
    std::uint8_t read(unsigned) const;
    std::uint16_t word(unsigned) const;
    void write(unsigned,unsigned,unsigned);
    void event(const Event&);void tick(unsigned,bool);
    void silence(unsigned);void key(unsigned,bool);void voice(unsigned,std::uint8_t,bool restore=false);
    void volume(unsigned);void pitch(unsigned);
    void reset(MusicalLfo&);bool advance(MusicalLfo&,unsigned);
    void depth(MusicalLfo&);std::uint16_t random(unsigned);
    std::uint8_t transpose(unsigned,std::uint8_t) const;
    void prepare(unsigned,std::uint8_t);void frequency(unsigned,std::uint8_t);
    void gate(unsigned,unsigned,unsigned);
    void note(unsigned,const Event&);void command(unsigned,const Event&);
};
}
