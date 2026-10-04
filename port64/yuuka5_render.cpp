#include "yuuka5.hpp"
#include <algorithm>
#include <stdexcept>
namespace th04::portable::yuuka5 {
namespace {
int pixels(motion::Subpixel value) { return value>=0 ? value/16 : -((-int(value)+15)/16); }
}
Backdrop backdrop(std::uint8_t phase,std::int16_t clock) {
    if(phase==0) return {clock<=2 ? BackdropKind::all_tiles : BackdropKind::dirty_tiles,0};
    if(phase==1) {
        // IDIV4 truncates toward zero, then AL alone is tested as unsigned.
        // A negative clock must not become a signed "cel <8" shortcut.
        const auto cel=static_cast<std::uint8_t>(clock/4);
        return {cel<8 ? BackdropKind::tiles_and_mask : BackdropKind::picture_and_mask,cel};
    }
    if(phase<254) return {BackdropKind::picture,0};
    return {phase==254 || clock<=2 ? BackdropKind::all_tiles : BackdropKind::dirty_tiles,0};
}
std::vector<BackgroundDraw> backdrop_requests(std::uint8_t phase,std::int16_t clock) {
    const auto b=backdrop(phase,clock);std::vector<BackgroundDraw> result;
    if(b.kind==BackdropKind::all_tiles || b.kind==BackdropKind::tiles_and_mask) result.push_back({0,0,0,0});
    else if(b.kind==BackdropKind::dirty_tiles) result.push_back({1,0,0,0});
    else {
        // Phase1 clears the uncovered region before CDG. The common picture
        // path puts CDG first, then calls the retained filler. Keep that call
        // order even though the ordinary two pixel regions are disjoint.
        if(b.kind==BackdropKind::picture_and_mask) result.push_back({4,0,0,0});
        result.push_back({2,128,128,16});
        if(b.kind==BackdropKind::picture) result.push_back({4,0,0,0});
    }
    if(b.kind==BackdropKind::tiles_and_mask || b.kind==BackdropKind::picture_and_mask) result.push_back({3,b.cel,0,0});
    return result;
}
void System::prepare_render(std::uint16_t frame,const laser::System& lasers) {
    draws_.clear();auto& s=state_.boss;
    const auto sprite=[&](unsigned kind,int x,int y,unsigned pattern,unsigned zoom=0) {
        draws_.push_back({static_cast<DrawKind>(kind),motion::wrap(x),motion::wrap(y),static_cast<std::uint16_t>(pattern),0,0,0,static_cast<std::uint16_t>(zoom)});
    };
    const auto disc=[&](int x,int y,int radius) {
        draws_.push_back({DrawKind::disc,motion::wrap(x),motion::wrap(y),static_cast<std::uint16_t>(radius),15});
    };
    const int x=pixels(s.position.current.x),y=pixels(s.position.current.y);
    if(s.phase==254) sprite(10,x-16,y-32,s.sprite,3);
    else if(s.phase<=1) {
        sprite(s.damage ? 1 : 0,x,y-16,128);
        if(s.damage) s.damage=0;
    } else if(s.phase<254) {
        switch(state_.move_state) {
        case 0: {
            const unsigned pattern=129+((frame%16)/4)*2;
            sprite(s.damage ? 1 : 0,x-16,y-32,pattern);
            sprite(s.damage ? 1 : 0,x+32,y-32,pattern+1);
            if(s.damage) s.damage=0;
            break;
        }
        case 1:
            disc(x+32,y+16,motion::wrap(80-int(s.phase_frame)*2));sprite(0,x,y-16,128);break;
        case 2:disc(x+32,y+16,16);break;
        case 3:
            disc(x+32,y+16,motion::wrap(int(s.phase_frame)*8+16));sprite(0,x,y-16,128);break;
        default:break; // Unknown movement states retain the hit byte.
        }
    }
    // These shared owners mutate explosion age/flash exactly once, after the
    // body. Repaints consume this cached list and never advance their clocks.
    std::vector<orange::Draw> explosions;orange::prepare_explosions(s,explosions);
    for(const auto& d:explosions) {
        draws_.push_back({static_cast<DrawKind>(d.kind),d.left,d.top,d.pattern_or_radius,d.color});
    }
    if(s.phase>=255) return;
    std::uint16_t color=0;
    for(const auto& d:lasers.draws()) {
        if(d.kind==laser::DrawKind::color) { color=d.color;draws_.push_back({DrawKind::color,0,0,0,d.color,0,0,d.mode}); }
        else if(d.kind==laser::DrawKind::line) draws_.push_back({DrawKind::vertical_line,d.x,d.y,0,color,0,d.end_y});
        else if(d.kind==laser::DrawKind::disc) draws_.push_back({DrawKind::disc,d.x,d.y,static_cast<std::uint16_t>(d.radius),color});
        else if(d.kind==laser::DrawKind::rectangle) draws_.push_back({DrawKind::rectangle,d.x,d.y,0,color,d.end_x,d.end_y});
        else draws_.push_back({DrawKind::disable});
    }
}
std::vector<motion::Point> disc_pixels(motion::Point center,std::uint16_t radius) {
    std::vector<motion::Point> result;
    // This is MAIN0000:114C's midpoint *filled* circle, with its clipped
    // horizontal spans. It is not a Euclidean distance test or an outline.
    // The pixel Oracle covers small ordinary radii. Negative WORD values
    // remain draw requests; this raster does not guess their loop behavior.
    if(radius>512) throw std::domain_error("disc radius outside attested portable raster range");
    const auto pixel=[&](int x,int y) { if(x>=32 && x<=415 && y>=16 && y<=383) result.push_back({static_cast<std::int16_t>(x),static_cast<std::int16_t>(y)}); };
    if(!radius) { pixel(center.x,center.y);return result; }
    const auto span=[&](int half,int offset) {
        const int left=motion::wrap(int(center.x)-half),right=motion::wrap(int(center.x)+half),y=motion::wrap(int(center.y)+offset);
        if(y<16 || y>383) return;
        for(int x=std::max(32,left);x<=std::min(415,right);++x) pixel(x,y);
    };
    int x=radius,y=0,error=radius;
    do {
        span(x,-y);span(x,y);error=motion::wrap(error-(2*y+1));
        if(error<0) { span(y,-x);span(y,x);--x;error=motion::wrap(error+2*x); }
        ++y;
    } while(static_cast<unsigned>(x)>=static_cast<unsigned>(y));
    return result;
}
namespace {
// Rectangle107C and vertical-line1774 sort signed endpoints, then subtract
// the clip origin in a WORD. That subtraction may wrap even for an offscreen
// endpoint. An ordinary host min/max clamp changes the extreme WORD cases.
bool clipped_range(std::int16_t first,std::int16_t last,int origin,int length,int& start,int& end) {
    if(first>last) std::swap(first,last);
    int lower=motion::wrap(int(first)-origin),upper=motion::wrap(int(last)-origin);
    if(upper<0) return false;
    if(lower<0) lower=0;
    upper=std::min(length,upper);
    if(motion::wrap(upper-lower)<0) return false;
    start=lower+origin;end=upper+origin;return true;
}
}
std::vector<motion::Point> rectangle_pixels(motion::Point first,motion::Point last) {
    std::vector<motion::Point> result;int left,right,top,bottom;
    if(!clipped_range(first.x,last.x,32,383,left,right) || !clipped_range(first.y,last.y,16,367,top,bottom)) return result;
    for(int y=top;y<=bottom;++y) for(int x=left;x<=right;++x) result.push_back({static_cast<std::int16_t>(x),static_cast<std::int16_t>(y)});
    return result;
}
std::vector<motion::Point> vertical_line_pixels(std::int16_t x,std::int16_t first,std::int16_t last) {
    std::vector<motion::Point> result;int top,bottom;
    if(x<32 || x>415 || !clipped_range(first,last,16,367,top,bottom)) return result;
    for(int y=top;y<=bottom;++y) result.push_back({x,static_cast<std::int16_t>(y)});
    return result;
}
std::vector<motion::Point> filler_pixels() {
    // MAIN0AAF:1508 writes the left96 pixels below Y128;7578 writes the
    // full384-pixel top region. ST04BK.CDG occupies the remaining288x256.
    auto result=rectangle_pixels({32,128},{127,383});
    const auto top=rectangle_pixels({32,16},{415,127});result.insert(result.end(),top.begin(),top.end());return result;
}
void raster_sprite(const sprite::Sheet& sheet,unsigned image,int left,int top,DrawKind kind,
                   const std::function<std::uint8_t(int,int)>& read,
                   const std::function<void(int,int,std::uint8_t)>& write) {
    if(kind==DrawKind::sprite || kind==DrawKind::white_sprite) {
        (void)read;
        // SUPER2F54/2838 convert X with unsigned SHR3, add Y*80 in a WORD,
        // then advance the row address in WORDs. Preserve that flat visible
        // VRAM addressing: negative X can paint a different visible row.
        // Host screen-coordinate clipping would discard those stores.
        const auto x_word=static_cast<std::uint16_t>(left);
        const unsigned shift=x_word&7;
        const auto start=static_cast<std::uint16_t>(top*80+(x_word>>3));
        for(unsigned y=0;y<sheet.height();++y) {
            const auto row=static_cast<std::uint16_t>(start+y*80);
            for(unsigned x=0;x<sheet.width();++x) {
                auto color=sheet.pixel(image,x,y);if(!color) continue;
                const auto byte=static_cast<std::uint16_t>(row+(shift+x)/8);
                if(byte>=32000) continue;
                const unsigned position=unsigned(byte)*8+(shift+x)%8;
                if(kind==DrawKind::white_sprite) color=15;
                write(int(position%640),int(position/640),color);
            }
        }
        return;
    }
    if(kind!=DrawKind::zoom_sprite) throw std::invalid_argument("unsupported Yuuka sprite raster kind");
    // Yuuka's phase254 requests SUPER_ZOOM_PUT with factor3. It reads four
    // color planes (not the alpha plane), skips color0 and paints an inclusive
    // clipped3x3 rectangle for each source pixel. Idle sheets are48x96, while
    // the entrance/zoom sheet is64x64; never infer either size from the ID.
    for(unsigned y=0;y<sheet.height();++y) for(unsigned x=0;x<sheet.width();++x) {
        const auto color=sheet.pixel(image,x,y);if(!color) continue;
        const motion::Point at{motion::wrap(left+int(x)*3),motion::wrap(top+int(y)*3)};
        for(auto p:rectangle_pixels(at,{motion::wrap(int(at.x)+2),motion::wrap(int(at.y)+2)})) write(p.x,p.y,color);
    }
}
} // namespace th04::portable::yuuka5
