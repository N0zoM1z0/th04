#pragma once
#include "pmd_ssg_effects.hpp"
#include <array>
#include <cstdint>
#include <functional>
#include <vector>
#include <utility>

namespace th04::portable::pmd {
using Bytes=std::vector<std::uint8_t>;
enum class Board { fm26, fm86, speakboard };
enum class Kind { command, note, portamento, rhythm, end };
enum class StopReason { explicit_request, fade_complete };
// Shared original FM/SSG note arithmetic. The octave is an eight-bit value,
// rotated into the note byte after transposition, including octave underflow.
std::uint8_t transpose_note(std::uint8_t note,std::uint8_t part,std::uint8_t master);
// Decoded requests retain their musical order for the future chip consumer.
// This owner executes bytecode and Timer A/B state; it opens no audio device.
struct Event {
    Kind kind;
    unsigned part;
    std::uint16_t offset;
    std::uint8_t opcode;
    Bytes arguments;
};
using Sink=std::function<void(const Event&)>;
using TickSink=std::function<void(unsigned,bool)>;
struct Part {
    std::uint16_t position=0,loop=0;
    std::uint8_t length=1,loop_status=0,notes=0;
    std::uint8_t volume=0,transpose=0,master_transpose=0,instrument=0,mask=0;
    std::int16_t detune=0;
};
struct State {
    // Eleven primary works plus three FM86 extensions. FM26 aliases D-F.
    std::array<Part,14> parts{};
    std::uint16_t measure=0;
    std::uint8_t bar_length=96,bar_tick=0,timer_b=200,tempo=78;
    std::uint8_t fade=0,timer_a=0,loop_status=0,status=0;
    std::int8_t fade_speed=0;
    bool playing=false;
    bool musical_fade_requested=false,stop_pending=false,auto_stop_on_fade=true;
};
class Sequence {
public:
    explicit Sequence(Board board=Board::fm26,Sink sink={},SsgSink ssg={},TickSink tick={}):board_(board),sink_(std::move(sink)),effects_(std::move(ssg)),tick_(std::move(tick)){}
    void load(const Bytes&);
    void start();
    void stop(StopReason reason=StopReason::explicit_request);
    void fade(std::int8_t speed) {state_.fade_speed=speed;}
    void interrupt(std::uint8_t timer_status);
    void start_ssg_effect(unsigned id) {if(effects_.start(id))state_.parts[8].mask|=2;}
    void stop_ssg_effect() {effects_.stop();}
    const State& state() const {return state_;}
    const Bytes& music() const {return music_;}
    bool masked_parser(unsigned part) const {return parsing_masked_.at(part);}
    const SsgEffects& ssg_effects() const {return effects_;}
    void fm_effect_active(std::function<bool()> query) {fm_effect_active_=std::move(query);}
    void fm_effect_command(std::function<void(unsigned)> action) {fm_effect_command_=std::move(action);}
    // Negative fade underflow restores the hardware rhythm total before the
    // Timer A effect work. Reaching zero exactly does not take this path.
    void fade_restored(std::function<void()> action) {fade_restored_=std::move(action);}
    // Commit the final musical tempo before Timer A effects in a combined IRQ.
    void timer_b_completed(std::function<void()> action) {timer_b_completed_=std::move(action);}
    void activate_fm3(unsigned n,std::uint16_t offset) {
        if(!offset)return;
        const unsigned p=board_==Board::fm26 ? n+3 : n+11;
        auto& t=state_.parts.at(p);t.position=std::uint16_t(offset+1);get(t.position);
        t.length=1;t.volume=108;t.mask|=32;
    }
    void slots_mask(unsigned p,bool disabled) {
        auto& t=state_.parts.at(p);if(disabled)t.mask|=32;else t.mask&=223;
        parsing_masked_.at(p)=t.mask!=0;
    }
    void borrow_fm(unsigned p) {state_.parts.at(p).mask|=2;}
    void mirror_ssg(std::uint8_t address,std::uint8_t value) {effects_.mirror(address,value);}
    std::uint16_t status() const {return std::uint16_t(state_.status)*256+state_.loop_status;}
private:
    Board board_;Sink sink_;Bytes music_;State state_{};SsgEffects effects_;TickSink tick_;std::function<bool()> fm_effect_active_;
    std::function<void(unsigned)> fm_effect_command_;
    std::function<void()> fade_restored_;
    std::function<void()> timer_b_completed_;
    std::array<bool,14> parsing_masked_{};
    std::uint16_t rhythm_table_=0,rhythm_position_=0;
    std::uint8_t saved_timer_b_=200,saved_tempo_=78;
    std::uint8_t get(std::uint16_t) const;
    std::uint16_t word(std::uint16_t) const;
    std::uint8_t take(std::uint16_t&);
    std::uint16_t take_word(std::uint16_t&);
    void put(std::uint16_t,std::uint8_t);
    void emit(Kind,unsigned,std::uint16_t,std::uint8_t,Bytes={});
    bool command(unsigned,std::uint16_t&,std::uint8_t,std::uint16_t);
    void part(unsigned);
    void part_body(unsigned);
    void rhythm();
    void timer_b();
    void set_timer_b(std::uint8_t);
    void set_tempo(std::uint8_t);
    void recover_ssg(unsigned,std::uint8_t);
};
}
