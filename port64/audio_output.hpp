#pragma once
#include "pmd_pcm.hpp"
#include <cstddef>
#include <cstdint>
#include <exception>
#include <functional>
#include <memory>
#include <string>

namespace th04::portable::audio {
constexpr unsigned sample_rate=48000;
constexpr std::size_t queue_limit=sample_rate/5; // Bounded 200 ms host policy.
enum class Push {queued,busy};
class Device {
public:
    virtual ~Device()=default;
    virtual std::size_t queued_frames() const=0;
    virtual Push push(const pmd::StereoSample*,std::size_t)=0;
};
using Factory=std::function<std::unique_ptr<Device>()>;
using Failure=std::function<void(const std::string&)>;
struct Statistics {
    std::uint64_t generated=0,submitted=0,suppressed=0,dropped=0,open_attempts=0;
    bool failed=false;
};
// Host transport only: playback never clocks the game, PMD or beeper.
// The factory is lazy and is never invoked for a muted output.
class Output {
public:
    Output(bool muted,Factory factory,Failure failure={});
    void stereo(const std::vector<pmd::StereoSample>&);
    void mono(const std::vector<std::int16_t>&);
    const Statistics& statistics() const {return stats_;}
    bool muted() const {return muted_;}
    const std::string& error() const {return error_;}
private:
    bool muted_;Factory factory_;Failure failure_;
    std::unique_ptr<Device> device_;Statistics stats_;std::string error_;
    bool admit(std::size_t);
    void send(const pmd::StereoSample*,std::size_t);
    void fail(const std::exception&);
};
} // namespace th04::portable::audio
