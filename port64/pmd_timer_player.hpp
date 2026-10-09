#pragma once
#include "pmd_fm_player.hpp"

namespace th04::portable::pmd {
// Resident timer register ownership around the musical/effect player. IRQs
// are still explicit inputs; this adapter does not invent hardware deadlines.
class TimerPlayer {
public:
    explicit TimerPlayer(Board board=Board::fm26,FmSink sink={},SsgSink ssg={});
    TimerPlayer(const TimerPlayer&)=delete;TimerPlayer& operator=(const TimerPlayer&)=delete;
    void load_music(const Bytes& bytes) {player_.load_music(bytes);}
    void load_effects(const Bytes& bytes) {player_.load_effects(bytes);}
    void start_music();
    void stop_music() {player_.stop_music();}
    void fade(std::int8_t speed) {player_.fade(speed);}
    void start_effect(unsigned id) {player_.start_effect(id);}
    void stop_effect() {player_.stop_effect();}
    void start_ssg_effect(unsigned id) {player_.start_ssg_effect(id);}
    void stop_ssg_effect() {player_.stop_ssg_effect();}
    void interrupt(std::uint8_t status);
    void mirror(std::uint8_t bank,std::uint8_t address,std::uint8_t value) {player_.mirror(bank,address,value);}
    const FmPlayer& player() const {return player_;}
private:
    FmSink sink_;FmPlayer player_;
    // The installed drivers have already committed this initial tempo.
    std::uint8_t committed_timer_b_=200;
    void write(std::uint8_t address,std::uint8_t value);
    void commit_tempo();
};
}
