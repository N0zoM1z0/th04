#include "pmd_ssg_effects.hpp"
#include <stdexcept>

namespace th04::portable::pmd {
const std::array<Effect,40>& SsgEffects::bank() {
    // The supplied PMD/PMD86/PMDB2 built-in instruments share these recovered
    // semantic parameters. Each row is a timed tone/noise/envelope segment,
    // with signed pitch/noise increments, rather than executable bytecode.
    static const std::array<Effect,40> effects{{
        // Instrument 0; priority 1.
        {1, {
            {1, 1500, 31, true, true, 15, 0, 0, 127, 0, 0},
            {8, 1700, 0, true, false, 16, 1200, 0, 127, 0, 0},
        }},
        // Instrument 1; priority 1.
        {1, {
            {14, 400, 7, true, true, 16, 3000, 0, 93, -1, 2},
        }},
        // Instrument 2; priority 1.
        {1, {
            {2, 700, 0, true, true, 15, 0, 0, 100, 0, 0},
            {14, 900, 0, true, true, 16, 2500, 0, 100, 0, 0},
        }},
        // Instrument 3; priority 1.
        {1, {
            {2, 500, 5, true, true, 15, 0, 0, 60, 0, 0},
            {14, 620, 0, true, true, 16, 2500, 0, 60, 0, 0},
        }},
        // Instrument 4; priority 1.
        {1, {
            {2, 300, 0, true, true, 15, 0, 0, 50, 0, 0},
            {14, 400, 0, true, true, 16, 2500, 0, 50, 0, 0},
        }},
        // Instrument 5; priority 1.
        {1, {
            {2, 55, 0, true, false, 16, 300, 0, 100, 0, 0},
        }},
        // Instrument 6; priority 1.
        {1, {
            {16, 0, 15, false, true, 16, 3000, 0, 0, -1, 1},
        }},
        // Instrument 7; priority 1.
        {1, {
            {6, 39, 0, true, true, 16, 500, 0, 0, 0, 0},
        }},
        // Instrument 8; priority 1.
        {1, {
            {32, 39, 0, true, true, 16, 5000, 0, 0, 0, 0},
        }},
        // Instrument 9; priority 1.
        {1, {
            {31, 40, 31, true, true, 16, 5000, 0, 0, -1, 1},
        }},
        // Instrument 10; priority 1.
        {1, {
            {31, 30, 0, true, true, 16, 5000, 0, 0, 0, 0},
        }},
        // Instrument 11; priority 2.
        {2, {
            {3, 477, 15, false, true, 16, 1000, 0, 0, 7, 1},
            {2, 477, 0, false, true, 16, 1000, 0, 0, 0, 0},
        }},
        // Instrument 12; priority 2.
        {2, {
            {1, 300, 0, true, false, 16, 300, 13, 0, 0, 0},
            {6, 300, 0, true, false, 16, 10000, 0, 80, 0, 0},
        }},
        // Instrument 13; priority 2.
        {2, {
            {4, 477, 0, false, true, 14, 10000, 0, 0, 5, 1},
            {4, 477, 10, false, true, 16, 2000, 0, 0, -1, 1},
        }},
        // Instrument 14; priority 2.
        {2, {
            {3, 477, 0, false, true, 16, 500, 13, 0, 0, 0},
            {8, 477, 15, false, true, 16, 2000, 0, 0, 0, 0},
        }},
        // Instrument 15; priority 2.
        {2, {
            {3, 477, 10, false, true, 16, 100, 13, 0, 0, 0},
            {16, 477, 5, false, true, 16, 10000, 0, 0, 0, 0},
        }},
        // Instrument 16; priority 2.
        {2, {
            {2, 400, 0, true, false, 16, 500, 0, 0, 0, 0},
        }},
        // Instrument 17; priority 2.
        {2, {
            {4, 477, 15, false, true, 16, 1000, 0, 0, 0, 0},
        }},
        // Instrument 18; priority 2.
        {2, {
            {2, 477, 31, false, true, 15, 10000, 0, 0, 0, 0},
            {12, 477, 0, false, true, 16, 5000, 0, 0, 1, 1},
        }},
        // Instrument 19; priority 2.
        {2, {
            {2, 400, 0, true, false, 16, 1000, 0, 0, 0, 0},
            {2, 200, 0, true, false, 16, 1000, 0, 0, 0, 0},
        }},
        // Instrument 20; priority 2.
        {2, {
            {4, 400, 0, true, false, 16, 2000, 0, 0, 0, 0},
            {8, 200, 0, true, false, 16, 3000, 0, 0, 0, 0},
        }},
        // Instrument 21; priority 2.
        {2, {
            {3, 400, 0, true, false, 16, 2000, 0, 0, 0, 0},
            {3, 100, 0, true, false, 16, 2000, 0, 0, 0, 0},
            {3, 200, 0, true, false, 16, 2000, 0, 0, 0, 0},
            {3, 400, 0, true, false, 16, 2000, 0, 0, 0, 0},
            {8, 100, 0, true, false, 16, 3000, 0, 0, 0, 0},
        }},
        // Instrument 22; priority 2.
        {2, {
            {16, 2000, 0, true, false, 15, 10000, 0, 0, 0, 0},
        }},
        // Instrument 23; priority 2.
        {2, {
            {4, 477, 31, false, true, 16, 5000, 0, 0, 0, 0},
            {8, 477, 31, true, true, 16, 3000, 0, 127, -1, 1},
        }},
        // Instrument 24; priority 2.
        {2, {
            {4, 477, 25, false, true, 16, 2000, 0, 0, 0, 0},
            {32, 477, 20, false, true, 16, 6000, 0, 0, 1, 3},
        }},
        // Instrument 25; priority 2.
        {2, {
            {6, 200, 0, true, true, 16, 5000, 0, 20, 0, 0},
        }},
        // Instrument 26; priority 2.
        {2, {
            {4, 40, 20, true, true, 16, 10000, 0, 20, 0, 0},
            {16, 20, 5, true, true, 16, 5000, 0, 0, 0, 0},
        }},
        // Instrument 27; priority 2.
        {2, {
            {6, 600, 0, true, false, 16, 1000, 0, 0, 0, 0},
        }},
        // Instrument 28; priority 2.
        {2, {
            {4, 1000, 0, true, false, 16, 10000, 0, 127, 0, 0},
            {16, 477, 0, true, true, 16, 10000, 0, 64, 0, 0},
        }},
        // Instrument 29; priority 2.
        {2, {
            {4, 1000, 31, true, true, 15, 10000, 0, 0, 0, 0},
        }},
        // Instrument 30; priority 2.
        {2, {
            {4, 4095, 31, true, true, 15, 10000, 0, 0, 0, 0},
        }},
        // Instrument 31; priority 2.
        {2, {
            {4, 477, 0, true, false, 16, 1000, 0, -50, 0, 0},
            {16, 242, 0, true, false, 16, 6000, 0, -8, 0, 0},
        }},
        // Instrument 32; priority 2.
        {2, {
            {4, 100, 0, true, false, 16, 500, 0, 0, 0, 0},
            {4, 10, 0, true, true, 16, 1000, 0, 0, 0, 0},
        }},
        // Instrument 33; priority 2.
        {2, {
            {8, 477, 5, false, true, 16, 500, 13, 0, 0, 0},
            {24, 30, 0, true, true, 16, 10000, 0, 0, 0, 0},
        }},
        // Instrument 34; priority 2.
        {2, {
            {4, 300, 0, true, false, 16, 5000, 0, 0, 0, 0},
            {4, 180, 0, true, false, 16, 5000, 0, 0, 0, 0},
            {4, 200, 0, true, false, 16, 5000, 0, 0, 0, 0},
            {24, 150, 0, true, false, 16, 5000, 0, 0, 0, 0},
        }},
        // Instrument 35; priority 2.
        {2, {
            {3, 238, 0, true, false, 14, 2000, 0, 0, 0, 0},
        }},
        // Instrument 36; priority 2.
        {2, {
            {4, 200, 0, true, false, 16, 5000, 0, 0, 0, 0},
            {16, 100, 0, true, false, 16, 5000, 0, 0, 0, 0},
        }},
        // Instrument 37; priority 2.
        {2, {
            {16, 0, 0, true, true, 16, 500, 13, 1, 1, 1},
            {16, 16, 16, true, true, 16, 5500, 0, 1, 1, 1},
        }},
        // Instrument 38; priority 2.
        {2, {
            {1, 200, 0, true, false, 14, 1000, 0, 0, 0, 0},
        }},
        // Instrument 39; priority 2.
        {2, {
            {2, 200, 0, true, false, 16, 800, 0, 0, 0, 0},
            {2, 100, 0, true, false, 16, 800, 0, 0, 0, 0},
            {2, 50, 0, true, false, 16, 800, 0, 0, 0, 0},
            {2, 25, 0, true, false, 16, 800, 0, 0, 0, 0},
        }},
    }};
    return effects;
}
void SsgEffects::mirror(std::uint8_t address,std::uint8_t value) {
    if(address>=registers_.size())throw std::out_of_range("SSG mirror register");
    registers_[address]=value;
}
void SsgEffects::write(std::uint8_t address,std::uint8_t value) {
    mirror(address,value);if(sink_)sink_({address,value});
}
bool SsgEffects::start(unsigned effect) {
    if(effect>=bank().size())throw std::out_of_range("PMD built-in SSG effect");
    // A refused lower-priority request still updates the published effect ID.
    state_.effect=std::uint8_t(effect);
    const auto& instrument=bank()[effect];
    if(state_.priority>instrument.priority)return false;
    state_.resource=int(effect);state_.next_frame=0;
    frame();state_.priority=instrument.priority;return true;
}
void SsgEffects::stop() {
    write(10,0);write(7,std::uint8_t((registers_[7]&0xdb)|0x24));
    state_.priority=0;state_.effect=255;
}
void SsgEffects::frame() {
    const auto& frames=bank().at(unsigned(state_.resource)).frames;
    if(state_.next_frame==frames.size()){stop();return;}
    const auto& f=frames.at(state_.next_frame++);
    state_.ticks=f.ticks;state_.tone=f.tone;state_.tone_step=f.tone_step;
    state_.noise=f.noise;state_.noise_step=f.noise_step;
    state_.noise_interval=state_.noise_counter=f.noise_interval;
    write(4,std::uint8_t(f.tone));write(5,std::uint8_t(f.tone>>8));write(6,f.noise);
    const auto disabled=(f.tone_enabled ? 0 : 4)|(f.noise_enabled ? 0 : 32);
    write(7,std::uint8_t((registers_[7]&0xdb)|disabled));
    write(10,f.volume);write(11,std::uint8_t(f.envelope));
    write(12,std::uint8_t(f.envelope>>8));write(13,f.shape);
}
void SsgEffects::timer_a() {
    if(!state_.priority)return;
    --state_.ticks;
    if(!state_.ticks){frame();return;}
    state_.tone=std::uint16_t(int(state_.tone)+state_.tone_step);
    write(4,std::uint8_t(state_.tone));write(5,std::uint8_t(state_.tone>>8));
    // The original rewrites its observed mixer on every sweep tick.
    write(7,registers_[7]);
    if(state_.noise_step || state_.noise_interval) {
        --state_.noise_counter;
        if(!state_.noise_counter) {
            state_.noise_counter=state_.noise_interval;
            state_.noise=std::uint8_t(int(state_.noise)+state_.noise_step);
            write(6,state_.noise);
        }
    }
}
}
