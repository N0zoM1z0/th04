#include "sound_runtime.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::sound {
Runtime::Runtime(Beeper::Reader reader,ActionSink actions,Sink requests,Samples samples,bool clock8)
    :reader_(std::move(reader)),actions_(std::move(actions)),requests_(std::move(requests)),samples_(std::move(samples)),
     beeper_(clock8),pcm_(beeper_),control_({},[this](const Request& q){consume(q);}) {}
void Runtime::consume(const Request& q) {
    if(requests_)requests_(q);
    const auto result=beeper_.consume(q,reader_);
    if(result)resource_result_=*result;else ++unsupported_;
}
void Runtime::configure(std::uint16_t bgm,std::uint16_t se,Drivers drivers) {
    control_.determine(bgm,se,drivers);
}
void Runtime::handle(const Action& a) {
    if(actions_)actions_(a);
    switch(a.kind) {
    case ActionKind::play:control_.play(a.value);break;
    case ActionKind::update:
        // Original MAIN waits and switches pages before snd_se_update. Extend
        // requests emitted by its later score drain remain queued next frame.
        if(refreshing_ && pending_){advance(pending_);pending_=0;}
        control_.update();break;
    case ActionKind::reset:control_.reset();break;
    case ActionKind::immediate_update:control_.update();break;
    case ActionKind::force:control_.reset();control_.play(a.value);control_.update();break;
    case ActionKind::command:control_.command(a.value,0,0);break;
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
