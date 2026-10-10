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
Trace::Trace(const std::string& directory,bool muted){
    if(directory.empty())return;
    if(!muted || std::filesystem::exists(directory))throw std::runtime_error("window trace needs muted fresh outputs");
    std::filesystem::create_directories(directory);
    stream_.open(std::filesystem::path(directory)/"window.tsv",std::ios::binary);
    if(!stream_)throw std::runtime_error("cannot create window trace");
    enabled_=true;epoch_=now_ns();
    stream_<<"TH04_WINDOW_TRACE 1 period_ns "<<period_ns<<" catchup_limit "<<catchup_limit<<" muted 1\n";
    stream_<<"# R seq begin_ns end_ns deadline_ns held shift focused before after scene program generation frame stage rank character shot x y bullets shots lives bombs misses invincibility audio_frames audio_opens audio_failed\n";
    stream_.flush();
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
        <<s.audio_frames<<' '<<s.audio_opens<<' '<<s.audio_failed<<'\n';stream_.flush();
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
    if(!stream_)throw std::runtime_error("window trace write failed");
}
}
