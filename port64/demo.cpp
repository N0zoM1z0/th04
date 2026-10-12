#include "demo.hpp"
#include <stdexcept>

namespace th04::portable::demo {
Replay::Replay(std::vector<std::uint8_t> bytes):bytes_(std::move(bytes)) {
    if(bytes_.size()!=frames*2)throw std::invalid_argument("TH04 replay needs two 4000-byte banks");
}
Sample Replay::sample(std::uint16_t frame,std::uint16_t input,std::uint8_t shift) const {
    if(input)return {input,shift,false,true};
    if(frame>=frames)throw std::out_of_range("TH04 replay frame outside its banks");
    // The last callback writes both input globals before ending at frame3996.
    return {bytes_[frame],bytes_[frame+frames],true,frame>=frames-4};
}
std::string Replay::filename(unsigned number) {
    if(number<1 || number>4)throw std::invalid_argument("TH04 demo number");
    return "DEMO"+std::to_string(number)+".REC";
}
bool Idle::tick(bool options,std::uint16_t input) {
    if(!options && count_>=640)return true;
    if(input)count_=0;
    else {
        const auto next=std::uint16_t(std::uint16_t(count_)+1u);
        count_=next<32768 ? std::int16_t(next) : std::int16_t(int(next)-65536);
    }
    return false;
}
std::uint16_t host_input(std::uint8_t input) {
    // Replay bytes have original BOMB bit0x10; the host frontend uses0x800.
    return std::uint16_t((input&0x0f)|(input&0x20)|(input&0x10 ? 0x800 : 0));
}
Fade::Fade(unsigned speed,PaletteSink sink,ToneSink stores)
    :left_(1),palette_sink_(std::move(sink)),tone_sink_(std::move(stores)) {
    // The original truncates speed to WORD and skips group waits when its
    // signed value is nonpositive. The initial refresh is unconditional.
    const auto word=std::uint16_t(speed);
    speed_=word<0x8000 ? unsigned(word) : 0;
    if(tone_sink_)tone_sink_(0,tone_);
}
void Fade::advance() {
    if(finished())return;
    ++ticks_;
    if(--left_)return;
    do {
        if(index_>=0) {
            tone_=std::int16_t(tone_-6);
            if(tone_sink_)tone_sink_(ticks_,tone_);
            if(tone_<0) {
                tone_=0;if(tone_sink_)tone_sink_(ticks_,tone_);
            }
        }
        ++index_;left_=speed_;
        if(palette_sink_)palette_sink_(ticks_,tone_);
    } while(!speed_ && !finished());
}
}
