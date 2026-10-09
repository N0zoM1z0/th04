#pragma once
#include "pmd_clock.hpp"
#include <memory>

namespace th04::portable::pmd {
struct StereoSample {std::int16_t left=0,right=0;};
struct ChipLevels {std::int32_t left=0,right=0,ssg=0;};
using PcmSink=std::function<void(StereoSample)>;
// CPU-only OPN/OPNA synthesis and 48 kHz stereo conversion. No device API.
// The external OPNA rhythm ROM must be supplied by the runtime resource owner.
class OpnPcm {
public:
    OpnPcm(Board board,std::uint32_t master_hz,Bytes rhythm_rom,PcmSink sink={});
    ~OpnPcm();
    OpnPcm(const OpnPcm&)=delete;OpnPcm& operator=(const OpnPcm&)=delete;
    void write(std::uint64_t cycle,FmWrite value);
    void advance_to(std::uint64_t cycle);
    std::uint64_t cycles() const;
    std::uint64_t samples() const;
    ChipLevels levels() const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};

// Live parser -> timed register writes -> chip -> PCM. The installed timer
// epoch matches ClockedPlayer; source mirrors remain distinct from chip I/O.
class PcmPlayer {
public:
    PcmPlayer(Board board,std::uint32_t hz,Bytes rhythm_rom,PcmSink sink={});
    void load_music(const Bytes& b) {player_->load_music(b);}
    void load_effects(const Bytes& b) {player_->load_effects(b);}
    void start_music() {player_->start_music();}
    void stop_music() {player_->stop_music();}
    void fade(std::int8_t v) {player_->fade(v);}
    void start_effect(unsigned v) {player_->start_effect(v);}
    void stop_effect() {player_->stop_effect();}
    void start_ssg_effect(unsigned v) {player_->start_ssg_effect(v);}
    void stop_ssg_effect() {player_->stop_ssg_effect();}
    void mirror(std::uint8_t bank,std::uint8_t a,std::uint8_t v) {player_->mirror(bank,a,v);}
    void initialize(FmWrite value); // actual installation writes, at epoch zero
    void advance_cycles(std::uint64_t cycles);
    void advance_ns(std::uint64_t ns);
    const ClockedPlayer& player() const {return *player_;}
    const OpnPcm& pcm() const {return pcm_;}
private:
    OpnPcm pcm_;std::unique_ptr<ClockedPlayer> player_;
};
}
