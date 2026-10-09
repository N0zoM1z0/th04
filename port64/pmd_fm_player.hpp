#pragma once
#include "pmd_musical_fm.hpp"
namespace th04::portable::pmd {
// Music and external effects share logical FM registers. No device or clock.
class FmPlayer {
public:
    explicit FmPlayer(Board board=Board::fm26,FmSink sink={},SsgSink ssg={});
    FmPlayer(const FmPlayer&)=delete;FmPlayer& operator=(const FmPlayer&)=delete;
    FmPlayer(FmPlayer&&)=delete;FmPlayer& operator=(FmPlayer&&)=delete;
    void load_music(const Bytes& data) {music_.load(data);}
    void load_effects(const Bytes& data) {effects_.load(data);}
    void start_music() {music_.start();sync_masks();}
    void stop_music() {music_.stop();sync_masks();}
    void fade(std::int8_t speed) {music_.fade(speed);}
    void start_effect(unsigned id);
    void stop_effect() {effects_.stop();sync_masks();}
    void interrupt(std::uint8_t flags);
    void mirror(std::uint8_t bank,std::uint8_t address,std::uint8_t value) {music_.mirror(bank,address,value);effects_.mirror(bank,address,value);}
    const MusicalFm& music() const {return music_;}
    const FmEffects& effects() const {return effects_;}
private:
    FmSink sink_;MusicalFm music_;FmEffects effects_;
    void sync_masks();
};
}
