#include "stage_program.hpp"
#include <stdexcept>

namespace th04::portable::stage {
namespace {
unsigned word(const Program::Bytes& bytes,unsigned at) {
    if (at>=bytes.size() || bytes.size()-at<2) throw std::invalid_argument("short STD word");
    return unsigned(bytes[at]) | (unsigned(bytes[at+1])<<8);
}
} // namespace
Program::Program(const Bytes& input) {
    const auto extent=word(input,0)+2;
    if (extent>input.size() || extent<5) throw std::invalid_argument("short STD extent");
    const Bytes bytes(input.begin(),input.begin()+extent);
    unsigned at=3+bytes[2];
    if (at>=extent) throw std::invalid_argument("STD order exceeds extent");
    at+=1+bytes[at];
    if (at>=extent) throw std::invalid_argument("STD speeds exceed extent");
    script_count_=bytes[at++];
    if (!script_count_ || script_count_>scripts_.size()) throw std::invalid_argument("STD script count exceeds capacity");
    for (unsigned id=0;id<script_count_;++id) {
        if (at>=extent) throw std::invalid_argument("short STD script header");
        const auto length=bytes[at++];
        if (!length || length>extent-at) throw std::invalid_argument("short STD script");
        script_offsets_[id]=at-3;
        scripts_[id].assign(bytes.begin()+at,bytes.begin()+at+length);
        at+=length;
    }
    // The intervening byte is opaque: attested stages use 00, FF and AA.
    // std_load skips it unconditionally, so it is not a fixed magic value.
    if (at>=extent) throw std::invalid_argument("missing STD wave marker");
    ++at;
    while (true) {
        const auto frame=word(bytes,at);
        if (!frame) { terminator_=at-3;break; }
        Wave wave;wave.frame=static_cast<std::uint16_t>(frame);wave.offset=at-3;at+=2;
        if (at>=extent) throw std::invalid_argument("short STD spawn count");
        const auto count=bytes[at++];
        // Zero enters a 256-iteration underflow loop in DOS. Reject that
        // malformed path rather than reading beyond a native resource.
        if (!count || unsigned(count)*8>extent-at) throw std::invalid_argument("invalid STD spawn extent");
        for (unsigned i=0;i<count;++i,at+=8) {
            if (bytes[at]>=script_count_) throw std::invalid_argument("STD spawn references missing script");
            wave.spawns.push_back({bytes[at],{motion::wrap(word(bytes,at+1)),motion::wrap(word(bytes,at+3))},bytes[at+5]});
        }
        waves_.push_back(std::move(wave));
    }
    // Empty schedules never dispatch their zero frame sentinel as a wave.
    stopped_=waves_.empty();
}
const Program::Bytes& Program::script(unsigned id) const {
    if (id>=script_count_) throw std::out_of_range("STD script ID");
    return scripts_[id];
}
unsigned Program::original_script_offset(unsigned id) const {
    script(id);return script_offsets_[id];
}
unsigned Program::original_cursor() const {
    return cursor_<waves_.size() ? waves_[cursor_].offset : terminator_;
}
std::vector<Spawn> Program::run(std::uint16_t frame,bool midboss_active) {
    // Exactly one wave per call, equality rather than catch-up. Skipped
    // midboss spawns still consume the wave and can stop the stage VM.
    if (stopped_ || waves_[cursor_].frame!=frame) return {};
    const auto& wave=waves_[cursor_++];
    if (cursor_==waves_.size()) stopped_=true;
    return midboss_active ? std::vector<Spawn>{} : wave.spawns;
}
} // namespace th04::portable::stage
