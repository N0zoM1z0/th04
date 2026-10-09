#pragma once
#include "pmd_sequence.hpp"
#include <array>
#include <cstdint>
#include <functional>
#include <vector>

namespace th04::portable::pmd {
struct FmWrite {std::uint8_t bank,address,value;};
using FmSink=std::function<void(FmWrite)>;
struct FmLfo {
    std::uint8_t delay=0,speed=0,count=0;
    std::int8_t step=0;
    std::uint8_t initial_delay=0,initial_speed=0,initial_count=0;
    std::int8_t initial_step=0;
    std::int16_t value=0;
    std::uint8_t shape=0;
};
struct FmEffectState {
    bool active=false;
    std::uint8_t effect=255;
    std::uint16_t position=0,loop=0;
    std::uint8_t ticks=0,gate=0,gate_amount=0;
    std::uint16_t frequency=0;
    std::int16_t detune=0,slide=0,slide_step=0,slide_remainder=0;
    std::uint8_t volume=0,transpose=0,master_transpose=0;
    FmLfo lfo{};
    std::uint8_t lfo_flags=0,loop_status=0,instrument=0;
    std::uint8_t carrier_mask=0,lfo_mask=0;
    std::array<std::uint8_t,4> total_levels{};
    std::uint8_t algorithm=0,pan=0,slots=0,voice_mask=0;
    std::uint8_t key_flags=0,note=0,last_note=0,notes=0;
};
// An independent Timer A owner for external EFC scripts. Logical register
// writes feed the future chip; no device, executable bytes or trace playback.
// The caller owns musical channel restoration through the release callback.
class FmEffects {
public:
    explicit FmEffects(Board board=Board::fm26,FmSink sink={},std::function<void()> release={}):
        board_(board),sink_(std::move(sink)),release_(std::move(release)){}
    void load(const Bytes&);
    void start(unsigned);
    void stop();
    void timer_a(std::int8_t musical_fade_speed=0);
    void mirror(std::uint8_t bank,std::uint8_t address,std::uint8_t value) {registers_.at(bank)[address]=value;}
    const FmEffectState& state() const {return state_;}
    const std::array<std::array<std::uint8_t,256>,2>& registers() const {return registers_;}
    const Bytes& resource() const {return effects_;}
    const std::array<std::uint8_t,6>& borrowed_masks() const {return masks_;}
    void musical_masks(const std::array<std::uint8_t,6>& value) {masks_=value;}
private:
    Board board_;FmSink sink_;std::function<void()> release_;
    FmEffectState state_{};Bytes effects_;
    std::array<std::array<std::uint8_t,256>,2> registers_{};
    std::array<std::uint8_t,6> masks_{};
    std::uint8_t keys_=0;bool tied_=false;
    std::uint8_t read(std::uint16_t) const;
    std::uint16_t word(std::uint16_t) const;
    std::uint8_t take();std::uint16_t take_word();
    void write(unsigned bank,unsigned address,unsigned value);
    unsigned bank() const {return board_==Board::fm26 ? 0 : 1;}
    void key(bool);
    void silence_voice();void voice(std::uint8_t);void volume();void pitch();
    void reset_lfo();bool update_lfo();
    std::uint8_t transpose(std::uint8_t) const;
    void prepare_note(std::uint8_t);void frequency(std::uint8_t);
    void finish_note();bool command(std::uint8_t);
};
}
