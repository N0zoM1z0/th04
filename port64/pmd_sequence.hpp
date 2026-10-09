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
struct Part {
    std::uint16_t position=0,loop=0;
    std::uint8_t length=1,loop_status=0,notes=0;
    std::uint8_t volume=0,transpose=0,master_transpose=0,instrument=0,mask=0;
    std::int16_t detune=0;
};
struct State {
    std::array<Part,11> parts{};
    std::uint16_t measure=0;
    std::uint8_t bar_length=96,bar_tick=0,timer_b=200,tempo=78;
    std::uint8_t fade=0,timer_a=0,loop_status=0,status=0;
    std::int8_t fade_speed=0;
    bool playing=false;
};
class Sequence {
public:
    explicit Sequence(Board board=Board::fm26,Sink sink={},SsgSink ssg={}):board_(board),sink_(std::move(sink)),effects_(std::move(ssg)){}
    void load(const Bytes&);
    void start();
    void stop();
    void fade(std::int8_t speed) {state_.fade_speed=speed;}
    void interrupt(std::uint8_t timer_status);
    const State& state() const {return state_;}
    const Bytes& music() const {return music_;}
    const SsgEffects& ssg_effects() const {return effects_;}
    void mirror_ssg(std::uint8_t address,std::uint8_t value) {effects_.mirror(address,value);}
    std::uint16_t status() const {return std::uint16_t(state_.status)*256+state_.loop_status;}
private:
    Board board_;Sink sink_;Bytes music_;State state_{};SsgEffects effects_;
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
    void rhythm();
    void timer_b();
    void set_timer_b(std::uint8_t);
    void set_tempo(std::uint8_t);
    void recover_ssg(unsigned,std::uint8_t);
};
}
