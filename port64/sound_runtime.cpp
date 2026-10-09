#include "sound_runtime.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::sound {
Runtime::Runtime(Beeper::Reader reader,ActionSink actions,Sink requests,Samples samples,bool clock8,
                 std::shared_ptr<ResidentPmd> resident,StereoSamples stereo)
    :reader_(std::move(reader)),actions_(std::move(actions)),requests_(std::move(requests)),samples_(std::move(samples)),
     resident_(std::move(resident)),stereo_(std::move(stereo)),
     beeper_(clock8),pcm_(beeper_),control_({},[this](const Request& q){consume(q);}) {}
void Runtime::consume(const Request& q) {
    if(requests_)requests_(q);
    auto result=beeper_.consume(q,reader_);
    if(!result && resident_)result=resident_->consume(q,reader_);
    if(result) {
        if(q.kind==Kind::interrupt)reply_=std::uint16_t(*result);
        else resource_result_=*result;
    } else ++unsupported_;
}
void Runtime::configure(std::uint16_t bgm,std::uint16_t se,Drivers drivers) {
    if(resident_)drivers=resident_->drivers();
    control_.determine(bgm,se,drivers);
}
std::uint16_t Runtime::command(std::uint16_t argument,std::uint16_t incoming_ax) {
    reply_=incoming_ax;control_.command(argument,incoming_ax,0);return reply_;
}
std::optional<std::uint16_t> Runtime::song_measure() {
    if(!resident_ || !control_.state().bgm)return std::nullopt;
    flush_refresh();return command(0x500);
}
void Runtime::flush_refresh() {
    if(refreshing_ && pending_) {const auto ns=pending_;pending_=0;advance(ns);}
}
void Runtime::handle(const Action& a) {
    if(actions_)actions_(a);
    switch(a.kind) {
    case ActionKind::play:control_.play(a.value);break;
    case ActionKind::update:
        // Original MAIN waits and switches pages before snd_se_update. Extend
        // requests emitted by its later score drain remain queued next frame.
        flush_refresh();
        control_.update();break;
    case ActionKind::reset:control_.reset();break;
    case ActionKind::immediate_update:control_.update();break;
    case ActionKind::force:control_.reset();control_.play(a.value);control_.update();break;
    case ActionKind::command:command(a.value);break;
    case ActionKind::load: {
        if(a.name.empty() || a.name.size()>8)throw std::invalid_argument("sound runtime base name");
        std::array<std::uint8_t,13> base{};std::copy(a.name.begin(),a.name.end(),base.begin());control_.load(base,a.value);break;
    }
    }
}
void Runtime::advance(std::uint64_t ns) {
    // Bounded refresh admission prevents host multiplication overflow. Rational
    // accumulation makes render partitioning independent of refresh cadence.
    if(ns>1000000000ull)throw std::out_of_range("sound refresh exceeds one second");
    if(resident_) {
        auto values=resident_->advance(ns);
        // One application PCM epoch supplies both channel counts. The beeper
        // remains process-local; its reset/sample phase is an explicit adapter.
        const auto beep=pcm_.render(values.size());if(samples_)samples_(beep);
        for(std::size_t i=0;i<values.size();++i) {
            const auto mix=[&](std::int16_t fm) {
                return std::int16_t(std::clamp(int(fm)+int(beep[i]),-32768,32767));
            };
            values[i]={mix(values[i].left),mix(values[i].right)};
        }
        if(stereo_)stereo_(values);return;
    }
    const auto numerator=fraction_+ns*48000ull;fraction_=numerator%1000000000ull;
    const auto values=pcm_.render(std::size_t(numerator/1000000000ull));if(samples_)samples_(values);
}
void Runtime::begin_refresh(std::uint64_t ns) {
    if(refreshing_ || ns>1000000000ull)throw std::logic_error("sound refresh admission");
    refreshing_=true;pending_=ns;
}
void Runtime::end_refresh() {
    if(!refreshing_)throw std::logic_error("sound refresh was not begun");
    if(pending_)advance(pending_);
    pending_=0;refreshing_=false;
}
}
