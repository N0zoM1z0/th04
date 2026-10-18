#include "host_window.hpp"
#include <algorithm>
#include <chrono>
#include <filesystem>
#include <memory>
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
    return {std::uint16_t(((k.up||k.keypad_up) ? 1 : 0)|((k.down||k.keypad_down) ? 2 : 0)|
        ((k.left||k.keypad_left) ? 4 : 0)|((k.right||k.keypad_right) ? 8 : 0)|
        (k.shot ? 0x20 : 0)|(k.bomb ? 0x800 : 0)|(k.enter ? 0x1000 : 0)|
        (k.keypad_enter ? 0x1000 : 0)|(k.escape ? 0x2000 : 0)|(k.quit ? 0x4000 : 0)),k.shift||k.right_shift};
}
pc98_input::Sample bios_input(const Keys& keys,bool focused) {
    pc98_input::Sample sample;if(!focused)return sample;
    sample.keys[0]=keys.escape ? 1 : 0;
    sample.keys[2]=keys.quit ? 1 : 0;
    sample.keys[3]=(keys.enter||keys.keypad_enter) ? 0x10 : 0;
    sample.keys[5]=std::uint8_t((keys.shot ? 2 : 0)|(keys.bomb ? 4 : 0));
    sample.keys[6]=keys.space ? 0x10 : 0;
    sample.keys[7]=std::uint8_t((keys.up ? 4 : 0)|(keys.down ? 0x20 : 0)|(keys.left ? 8 : 0)|(keys.right ? 0x10 : 0));
    sample.keys[8]=std::uint8_t((keys.up_left ? 4 : 0)|(keys.keypad_up ? 8 : 0)|
        (keys.up_right ? 0x10 : 0)|(keys.keypad_left ? 0x40 : 0));
    sample.keys[9]=std::uint8_t((keys.keypad_right ? 1 : 0)|(keys.down_left ? 4 : 0)|
        (keys.keypad_down ? 8 : 0)|(keys.down_right ? 0x10 : 0));
    sample.shift=keys.shift||keys.right_shift;return sample;
}
Keyboard::Keyboard(std::int64_t epoch,Dispatch dispatch):dispatch_(std::move(dispatch)),last_ns_(epoch) {
    if(epoch<0 || !dispatch_)throw std::invalid_argument("invalid host keyboard clock/dispatch");
}
void Keyboard::available_cpu(pc98_keyboard::Device& device,pc98_keyboard::Time time) {
    if(const auto line=device.dispatch_irq(time)) {
        if(*line!=1)throw std::logic_error("default host keyboard has no handler for this IRQ");
        device.read_bios(time);device.end_irq(time);
    }
}
void Keyboard::advance(std::int64_t now) {
    using namespace pc98_keyboard;
    if(now<last_ns_)throw std::logic_error("host keyboard clock moved backward");
    const auto elapsed=std::uint64_t(now-last_ns_);
    // 576000 quanta/ms = 72/125 quanta/ns. Retain fractional quanta across
    // calls so splitting one elapsed interval does not change timer phase.
    const auto fraction=(elapsed%125)*72+remainder_;
    const auto delta=(elapsed/125)*72+fraction/125;
    if(delta>std::numeric_limits<Time>::max()-time_)throw std::overflow_error("host keyboard clock overflow");
    const auto target=time_+delta;
    for(;;) {
        const auto event=device_.receiver().next_event();
        const auto check=device_.dispatcher().next_event();
        const auto next=event && check ? std::optional<Time>{std::min(*event,*check)} : (event ? event : check);
        if(!device_.keyboard().wait_ticks() && next_tick_<=target && (!next || next_tick_<*next)) {
            const auto end=next && *next<=target ? *next-1 : target;
            const auto ticks=(end-next_tick_)/quanta_per_ms+1;
            next_tick_+=ticks*quanta_per_ms; // No countdown or scan byte can change.
            continue;
        }
        // Peripheral callbacks precede a simultaneous CPU check. Physical
        // host edges are applied only after advance() finishes this interval.
        if(event && *event<=target && *event<=next_tick_ && (!check || *event<=*check)) {
            device_.receive(*event);dispatch_(device_,*event);
        } else if(next_tick_<=target && (!check || next_tick_<=*check)) {
            device_.tick(next_tick_);dispatch_(device_,next_tick_);next_tick_+=quanta_per_ms;
        } else if(check && *check<=target) {
            device_.dispatch_event(*check);dispatch_(device_,*check);
        } else break;
    }
    dispatch_(device_,target);time_=target;last_ns_=now;remainder_=unsigned(fraction%125);
}
void Keyboard::set_key(unsigned i,bool down) {
    constexpr std::array<std::uint8_t,unsigned(HostKey::count)> scans{{
        0x3a,0x3d,0x3b,0x3c,0x29,0x1c,0x2a,0,0x10,0x70,0x42,0x44,0x4a,0x4c,0x34,
        0x43,0x4b,0x46,0x48,0x1c,0x70}};
    if(held_.at(i)!=down) {device_.key({std::uint16_t(i+1),scans.at(i)},down,time_);held_[i]=down;}
}
void Keyboard::key(HostKey key,bool down,std::int64_t now) {
    if(unsigned(key)>=held_.size())throw std::out_of_range("invalid host key identity");
    advance(now);if(focused_)set_key(unsigned(key),down);
}
void Keyboard::focus(bool focused,std::int64_t now) {
    advance(now);focused_=focused;
    if(!focused)for(unsigned i=0;i<held_.size();++i)set_key(i,false);
}
Keys Keyboard::keys() const {
    return {held_[0],held_[1],held_[2],held_[3],held_[4],held_[5],held_[6],held_[7],held_[8],held_[9],
        held_[10],held_[11],held_[12],held_[13],held_[14],held_[15],held_[16],held_[17],held_[18],held_[19],held_[20]};
}
void Keyboard::observe(const KeySample& sample) {
    focus(sample.focused,sample.time_ns);
    const auto& k=sample.keys;
    const std::array<bool,unsigned(HostKey::count)> values{{k.up,k.down,k.left,k.right,k.shot,k.enter,k.bomb,k.escape,k.quit,
        k.shift,k.up_left,k.up_right,k.down_left,k.down_right,k.space,k.keypad_up,k.keypad_down,
        k.keypad_left,k.keypad_right,k.keypad_enter,k.right_shift}};
    // Snapshot fixtures have no event order; reconcile them in a stable order.
    // Live windows instead call key() in host delivery order.
    for(unsigned i=0;i<held_.size();++i) {
        set_key(i,sample.focused && values[i]);
    }
}
pc98_input::ByteSource Keyboard::elapsed_source(std::function<std::int64_t()> clock,
    std::function<void(pc98_input::Operation)> begin) {
    if(!clock)throw std::invalid_argument("missing host keyboard clock source");
    const auto shared=std::make_shared<std::function<std::int64_t()>>(std::move(clock));
    return {std::move(begin),[this,shared](unsigned group) {
        advance((*shared)());return device_.matrix().at(group);
    },[this,shared] {advance((*shared)());return device_.shift();}};
}
pc98_input::ByteSource Keyboard::source(KeySource input,std::function<void(pc98_input::Operation)> begin) {
    if(!input)throw std::invalid_argument("missing host keyboard source");
    const auto shared=std::make_shared<KeySource>(std::move(input));
    return {std::move(begin),[this,shared](unsigned group) {
        observe((*shared)());return device_.matrix().at(group);
    },[this,shared] {observe((*shared)());return device_.shift();}};
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
