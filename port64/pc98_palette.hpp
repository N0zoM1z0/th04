#pragma once
#include <algorithm>
#include <array>
#include <cstdint>

namespace th04::portable::pc98_palette {
using Palette=std::array<std::uint8_t,48>;

// PALETTE_SHOW reads signed PaletteTone from a WORD and clamps its local
// value. Neither the raw palette nor the stored tone is changed.
constexpr int clamped_tone(int value) {
    const auto word=std::uint16_t(value);
    return std::clamp(word<0x8000 ? int(word) : int(word)-0x10000,0,200);
}
constexpr std::uint8_t component(std::uint8_t raw,int tone) {
    const unsigned invert=tone>100 ? 15 : 0;
    const unsigned scale=unsigned(tone>100 ? 200-tone : tone);
    return std::uint8_t(((((raw>>4)^invert)*scale)/100)^invert);
}
constexpr std::uint8_t lcd_component(unsigned value,int tone) {
    const unsigned invert=tone>100 ? 15 : 0;
    const unsigned scale=unsigned(tone>100 ? 200-tone : tone);
    return std::uint8_t(((value^invert)*scale/100)^invert);
}
constexpr unsigned lcd_level(std::uint8_t red,std::uint8_t green,
                             std::uint8_t blue,int tone) {
    const unsigned mask=tone>100 ? 15 : 0;
    const unsigned r=lcd_component((red>>4)&mask,tone);
    const unsigned g=lcd_component(green>>4,tone);
    const unsigned b=lcd_component(blue&mask,tone);
    const unsigned weighted=2*r+4*g+b+std::max({r,g,b});
    const int level=int(((weighted*3/20)+1)/2)-2;
    return unsigned(std::max(level,0));
}

// Complete analog/LCD port sequence from MAIN0000:1F04, OP0000:1DE0 and
// MAINE0000:19EC. Read/write callbacks represent hardware I/O; the return
// value is the RGB DAC register image consumed by the native renderers.
template<class Read,class Write>
Palette show(const Palette& raw,int value,std::uint16_t note,Read read,Write write) {
    const int tone=clamped_tone(value);
    unsigned polarity=0;
    if(note) {
        write(0xf6,0xa0);
        auto selector=std::uint8_t(read(0x871e));
        if(selector==0xff)selector=std::uint8_t(read(0xae8e))>>2;
        polarity=(selector&1) ? 0 : 0xff;
    }
    Palette dac{};
    for(unsigned color=0;color<16;++color) {
        const unsigned at=color*3;
        write(0xa8,color);
        if(note) {
            const auto level=lcd_level(raw[at],raw[at+1],raw[at+2],tone)^polarity;
            dac[at]=std::uint8_t((level&2) ? 15 : 0);
            dac[at+1]=std::uint8_t((level&4) ? 15 : 0);
            dac[at+2]=std::uint8_t((level&1) ? 15 : 0);
            write(0xae,dac[at+2]);write(0xac,dac[at]);write(0xaa,dac[at+1]);
        } else {
            for(unsigned channel=0;channel<3;++channel)dac[at+channel]=component(raw[at+channel],tone);
            write(0xac,dac[at]);write(0xaa,dac[at+1]);write(0xae,dac[at+2]);
        }
    }
    return dac;
}
inline Palette show(const Palette& raw,int tone) {
    return show(raw,tone,0,[](unsigned){return 0;},[](unsigned,unsigned){});
}
// PI consumers retain an eight-bit palette carrier, with DAC values in its
// high nibbles. Tone is still applied once in the four-bit output domain.
inline Palette shown_palette(const Palette& raw,int tone) {
    auto output=show(raw,tone);
    for(auto& channel:output)channel=std::uint8_t(channel<<4);
    return output;
}

// Match the recorded DOSBox-X PC-98 analog DAC scanout path: expand the
// four-bit port value to six bits, then expand those six bits to RGB8.
// Apply palette tone in the four-bit domain before calling this function.
// Physical PC-98 output and other emulator DAC paths remain separate claims.
constexpr std::uint8_t analog_rgb8(unsigned nibble) {
    const unsigned four = nibble & 15u;
    const unsigned six = (four << 2) | (four >> 2);
    return std::uint8_t((six << 2) | (six >> 4));
}
// Indexed graphics use one DAC conversion for each of the sixteen colors.
inline std::array<std::uint32_t,16> argb(const Palette& raw,int tone) {
    const auto dac=show(raw,tone);std::array<std::uint32_t,16> colors{};
    for(unsigned color=0;color<16;++color) {
        const unsigned at=color*3;
        colors[color]=0xff000000u|(std::uint32_t(analog_rgb8(dac[at]))<<16)|
            (std::uint32_t(analog_rgb8(dac[at+1]))<<8)|analog_rgb8(dac[at+2]);
    }
    return colors;
}
} // namespace th04::portable::pc98_palette
