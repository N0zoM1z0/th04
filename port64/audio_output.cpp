#include "audio_output.hpp"
#include <stdexcept>

namespace th04::portable::audio {
Output::Output(bool muted,Factory factory,Failure failure)
    :muted_(muted),factory_(std::move(factory)),failure_(std::move(failure)) {}
void Output::fail(const std::exception& e) {
    stats_.failed=true;error_=e.what();device_.reset();
    stats_.suppressed=stats_.generated-stats_.submitted-stats_.dropped;
    if(failure_)try{failure_(error_);}catch(...){} // Reporting cannot stop gameplay.
}
bool Output::admit(std::size_t frames) {
    stats_.generated+=frames;
    if(!frames)return false;
    if(muted_ || stats_.failed) {stats_.suppressed+=frames;return false;}
    if(frames>queue_limit) {stats_.dropped+=frames;return false;}
    if(!device_) {
        ++stats_.open_attempts;
        if(!factory_)throw std::runtime_error("audio output has no device factory");
        device_=factory_();
        if(!device_)throw std::runtime_error("audio device factory returned no device");
    }
    const auto queued=device_->queued_frames();
    if(queued>queue_limit-frames) {stats_.dropped+=frames;return false;}
    return true;
}
void Output::send(const pmd::StereoSample* data,std::size_t frames) {
    if(device_->push(data,frames)==Push::busy)stats_.dropped+=frames;
    else stats_.submitted+=frames;
}
void Output::stereo(const std::vector<pmd::StereoSample>& values) {
    try {if(admit(values.size()))send(values.data(),values.size());}
    catch(const std::exception& e) {fail(e);}
}
void Output::mono(const std::vector<std::int16_t>& values) {
    try {
        if(!admit(values.size()))return;
        std::vector<pmd::StereoSample> stereo;stereo.reserve(values.size());
        for(auto v:values)stereo.push_back({v,v});
        send(stereo.data(),stereo.size());
    } catch(const std::exception& e) {fail(e);}
}
} // namespace th04::portable::audio
