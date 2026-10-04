#include "yuuka6_foreground.hpp"
#include "yuuka5.hpp"
#include <stdexcept>

namespace th04::portable::yuuka6 {
void raster_sprite(const sprite::Sheet& sheet,unsigned image,int left,int top,DrawKind kind,
                   const std::function<std::uint8_t(int,int)>& read,
                   const std::function<void(int,int,std::uint8_t)>& write) {
    if(kind==DrawKind::red_sprite) {
        // MAIN0000:2838 writes the alpha mask with tileFF and modeCD.
        // In PC-98 plane order B/R/G/I, only red (bit1) is enabled. The
        // other three destination bits survive: this is an additive tint,
        // not replacement by indexed color2. Reuse the attested mask and
        // WORD-offset walk of the white variant, changing only plane merge.
        yuuka5::raster_sprite(sheet,image,left,top,yuuka5::DrawKind::white_sprite,read,
            [&](int x,int y,std::uint8_t) { write(x,y,static_cast<std::uint8_t>(read(x,y)|2)); });
        return;
    }
    if(kind!=DrawKind::sprite && kind!=DrawKind::white_sprite && kind!=DrawKind::zoom_sprite)
        throw std::invalid_argument("unsupported Yuuka6 sprite raster kind");
    // Normal/white masks and phase254 factor3 already have independent
    // original controls. Keep one implementation; death uses MIKO32 4..11,
    // rather than the48x96 boss sheet used by ordinary body halves.
    yuuka5::raster_sprite(sheet,image,left,top,static_cast<yuuka5::DrawKind>(kind),read,write);
}
} // namespace th04::portable::yuuka6
