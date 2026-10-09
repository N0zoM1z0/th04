#include "super_wave.hpp"
#include "motion.hpp"
#include <array>
#include <stdexcept>
namespace th04::portable::wave {
namespace {
// Independently generated: min(127, trunc(128*sin(a*pi/128))) for a=0..64.
// Quarter-wave symmetry supplies the remaining angles without host libm.
constexpr std::array<int,65> quarter{{
    0,3,6,9,12,15,18,21,24,28,31,34,37,40,43,46,
    48,51,54,57,60,63,65,68,71,73,76,78,81,83,85,88,
    90,92,94,96,98,100,102,104,106,108,109,111,112,114,115,117,
    118,119,120,121,122,123,124,124,125,126,126,127,127,127,127,127,127
}};
int sine_value(unsigned angle) {
    angle&=255;const auto n=angle&127;
    const auto value=quarter[n<=64 ? n : 128-n];
    return angle<128 ? value : -value;
}
int signed_byte(unsigned value) {value&=255;return value<128 ? int(value) : int(value)-256;}
int floor_div(int value,int divisor) {return value>=0 ? value/divisor : -((-value+divisor-1)/divisor);}
}
int sine(std::uint8_t angle) {return sine_value(angle);}
void raster(const sprite::Sheet& sheet,unsigned image,std::int16_t left,std::int16_t top,
            std::int16_t length,std::uint16_t amplitude,std::uint16_t phase,
            const std::function<void(int,int,std::uint8_t)>& write) {
    // The original uses 96 WORD row-table slots and FS word loads. The
    // Gengetsu body has 48x96 patterns; odd-byte rows require a separate owner.
    if(sheet.height()>96 || !sheet.height() || sheet.width()%16 || !sheet.width())
        throw std::invalid_argument("unsupported wave pattern dimensions");
    if(image>=sheet.count())throw std::out_of_range("wave pattern index");
    if(!length)throw std::domain_error("wave length division by zero");
    // The target stores the original length's AH and tests it as a byte.
    // Positive lengths>=256 therefore alternate too; sign only chooses DIV.
    const bool alternate=(static_cast<std::uint16_t>(length)>>8)!=0;
    const unsigned divisor=length<0 ? unsigned(-int(length)) : unsigned(length);
    int amp=signed_byte(amplitude);
    for(unsigned y=0;y<sheet.height();++y) {
        const unsigned angle=((y*256)/divisor+phase)&255;
        const auto x=motion::wrap(int(left)+floor_div(amp*sine_value(angle),128));
        // SUPER_WAVE aligns X to a signed 16-pixel boundary, then adds
        // Y*80 in a WORD. Preserve visible flat address aliases on both axes.
        const unsigned shift=static_cast<std::uint16_t>(x)&15;
        const auto row=static_cast<std::uint16_t>(floor_div(x,16)*2+(int(top)+int(y))*80);
        for(unsigned column=0;column<sheet.width();++column) {
            const auto color=sheet.pixel(image,column,y);if(!color)continue;
            const auto byte=static_cast<std::uint16_t>(row+(shift+column)/8);
            if(byte>=32000)continue;
            const unsigned position=unsigned(byte)*8+(shift+column)%8;
            write(int(position%640),int(position/640),color);
        }
        if(alternate)amp=signed_byte(unsigned(-amp));
    }
}
}
