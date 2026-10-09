#include "pmd_timer_player.hpp"
#include <stdexcept>

namespace th04::portable::pmd {
TimerPlayer::TimerPlayer(Board board,FmSink sink,SsgSink ssg)
    :sink_(std::move(sink)),player_(board,[this](FmWrite w){if(sink_)sink_(w);},std::move(ssg)) {
    player_.effect_released([this,board]{
        if(board==Board::fm26 && player_.music().sequence().state().playing)write(0x27,0x0f);
    });
    player_.timer_b_completed([this]{commit_tempo();});
}
void TimerPlayer::write(std::uint8_t address,std::uint8_t value) {
    player_.mirror(0,address,value);
    if(sink_)sink_({0,address,value});
}
void TimerPlayer::commit_tempo() {
    const auto next=player_.music().sequence().state().timer_b;
    if(next!=committed_timer_b_) {write(0x26,next);committed_timer_b_=next;}
}
void TimerPlayer::start_music() {
    player_.start_music();
    commit_tempo();
    write(0x25,0);write(0x24,0);write(0x27,0x3f);
}
void TimerPlayer::interrupt(std::uint8_t status) {
    if(status>3)throw std::invalid_argument("PMD timer status");
    if(!status)return;
    write(0x27,0x3f);
    player_.interrupt(status);
}
}
