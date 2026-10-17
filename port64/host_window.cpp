#include "host_window.hpp"
#include <chrono>
#include <filesystem>
#include <stdexcept>

namespace th04::portable::host_window {
std::int64_t now_ns(){return std::chrono::duration_cast<std::chrono::nanoseconds>(
    std::chrono::steady_clock::now().time_since_epoch()).count();}
void Schedule::completed(unsigned slowdown){
    if(!slowdown || steps_>=catchup_limit)throw std::logic_error("invalid host refresh admission");
    next_+=period_ns*slowdown;++steps_;++total_;
}
std::int64_t Schedule::resync(std::int64_t now,unsigned slowdown){
    if(!slowdown)throw std::logic_error("zero host slowdown");
    if(steps_!=catchup_limit || now<next_)return 0;
    const auto discarded=now-next_+1;next_=now+period_ns*slowdown;return discarded;
}
Input input(const Keys& k,bool focused){
    if(!focused)return {};
    return {std::uint16_t((k.up ? 1 : 0)|(k.down ? 2 : 0)|(k.left ? 4 : 0)|(k.right ? 8 : 0)|
        (k.shot ? 0x20 : 0)|(k.bomb ? 0x800 : 0)|(k.enter ? 0x1000 : 0)|
        (k.escape ? 0x2000 : 0)|(k.quit ? 0x4000 : 0)),k.shift};
}
pc98_input::Sample bios_input(const Keys& keys,bool focused) {
    pc98_input::Sample sample;if(!focused)return sample;
    sample.keys[0]=keys.escape ? 1 : 0;
    sample.keys[2]=keys.quit ? 1 : 0;
    sample.keys[3]=keys.enter ? 0x10 : 0;
    sample.keys[5]=std::uint8_t((keys.shot ? 2 : 0)|(keys.bomb ? 4 : 0));
    sample.keys[6]=keys.space ? 0x10 : 0;
    sample.keys[7]=std::uint8_t((keys.up ? 4 : 0)|(keys.down ? 0x20 : 0)|(keys.left ? 8 : 0)|(keys.right ? 0x10 : 0));
    sample.keys[8]=std::uint8_t((keys.up_left ? 4 : 0)|(keys.up_right ? 0x10 : 0));
    sample.keys[9]=std::uint8_t((keys.down_left ? 4 : 0)|(keys.down_right ? 0x10 : 0));
    sample.shift=keys.shift;return sample;
}
Trace::Trace(const std::string& directory,bool muted){
    if(directory.empty())return;
    if(!muted || std::filesystem::exists(directory))throw std::runtime_error("window trace needs muted fresh outputs");
    std::filesystem::create_directories(directory);
    stream_.open(std::filesystem::path(directory)/"window.tsv",std::ios::binary);
    input_stream_.open(std::filesystem::path(directory)/"input.tsv",std::ios::binary);
    if(!stream_ || !input_stream_)throw std::runtime_error("cannot create window/input trace");
    enabled_=true;epoch_=now_ns();
    stream_<<"TH04_WINDOW_TRACE 3 period_ns "<<period_ns<<" catchup_limit "<<catchup_limit<<" muted 1\n";
    stream_<<"# R seq begin_ns end_ns deadline_ns held shift focused before after scene program generation frame stage rank character shot x y bullets shots lives bombs misses invincibility audio_frames audio_opens audio_failed score_units credits power bombing respawn slow_frames run_frames score_digits_units score_delta advice_held advice_shift\n";
    stream_.flush();
    input_stream_<<"TH04_INPUT_TRACE 1 host_epoch_ns "<<epoch_<<"\n"
        <<"# I ordinal seq begin_ns end_ns op bios shift joystick_enabled pins before before_shift after after_shift focused scene program generation frame stage\n";
    input_stream_.flush();
}
void Trace::refresh(std::uint64_t seq,std::int64_t begin,std::int64_t end,std::int64_t deadline,
    Input in,bool focused,unsigned before,unsigned after,const Snapshot& s){
    if(!enabled_)return;
    ++refreshes_;
    stream_<<"R "<<seq<<' '<<begin-epoch_<<' '<<end-epoch_<<' '<<deadline-epoch_<<' '
        <<in.held<<' '<<in.shift<<' '<<focused<<' '<<before<<' '<<after<<' '<<s.scene<<' '
        <<s.program<<' '<<s.generation<<' '<<s.frame<<' '<<s.stage<<' '<<s.rank<<' '
        <<s.character<<' '<<s.shot_type<<' '<<s.x<<' '<<s.y<<' '<<s.bullets<<' '
        <<s.shots<<' '<<s.lives<<' '<<s.bombs<<' '<<s.misses<<' '<<s.invincibility<<' '
        <<s.audio_frames<<' '<<s.audio_opens<<' '<<s.audio_failed<<' '
        <<s.score_units<<' '<<s.credits<<' '<<s.power<<' '<<s.bombing<<' '<<s.respawn<<' '
        <<s.slow_frames<<' '<<s.run_frames<<' '<<s.score_digits_units<<' '<<s.score_delta<<' '<<s.advice_held<<' '<<s.advice_shift<<'\n';stream_.flush();
}
void Trace::input_poll(std::uint64_t seq,std::int64_t begin,std::int64_t end,
    const pc98_input::Observation& sample,bool focused,const Snapshot& s) {
    if(!enabled_)return;
    constexpr char digits[]="0123456789abcdef";
    input_stream_<<"I "<<input_polls_++<<' '<<seq<<' '<<begin-epoch_<<' '<<end-epoch_<<' '
        <<(sample.operation==pc98_input::Operation::reset ? 'R' : 'S')<<' ';
    for(const auto value:sample.physical.keys)input_stream_<<digits[value>>4]<<digits[value&15];
    input_stream_<<' '<<sample.physical.shift<<' '<<sample.physical.joystick_enabled<<' '
        <<unsigned(sample.physical.joystick_pins)<<' '<<sample.before.actions<<' '<<sample.before.shift<<' '
        <<sample.after.actions<<' '<<sample.after.shift<<' '<<focused<<' '<<s.scene<<' '<<s.program<<' '
        <<s.generation<<' '<<s.frame<<' '<<s.stage<<'\n';input_stream_.flush();
}
void Trace::present(std::uint64_t seq,std::int64_t begin,std::int64_t end,bool updated){
    if(!enabled_)return;
    ++presents_;
    stream_<<"P "<<seq<<' '<<begin-epoch_<<' '<<end-epoch_<<' '<<updated<<'\n';stream_.flush();
}
void Trace::resync(std::int64_t now,std::int64_t discarded,unsigned slowdown){
    if(!enabled_ || !discarded)return;
    ++resyncs_;
    stream_<<"D "<<now-epoch_<<' '<<discarded<<' '<<slowdown<<'\n';stream_.flush();
}
void Trace::finish(const Snapshot& s){
    if(!enabled_ || finished_)return;
    finished_=true;
    stream_<<"E "<<refreshes_<<' '<<presents_<<' '<<resyncs_<<' '<<s.audio_frames<<' '
        <<s.audio_opens<<' '<<s.audio_failed<<'\n';stream_.flush();
    input_stream_<<"E "<<input_polls_<<'\n';input_stream_.flush();
    if(!stream_ || !input_stream_)throw std::runtime_error("window/input trace write failed");
}
}
