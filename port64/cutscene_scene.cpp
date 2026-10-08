#include "cutscene_scene.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::cutscene {
namespace {
constexpr unsigned width=640,height=400;
// Observed MAINE DATA0E53:060C/062C. These words are hardware mask data,
// not instruction bytes. EGC words are little endian, with MSB-first dots
// within each byte; interpreting bit15 as the first dot swaps both bytes.
constexpr std::uint16_t picture_masks[4][4]={
    {0x0000,0x1111,0x0000,0x4444}, {0x8888,0x1111,0x2222,0x4444},
    {0xAAAA,0x5555,0xAAAA,0x5555}, {0xEEEE,0x7777,0xBBBB,0xDDDD}
};
constexpr std::uint16_t box_masks[5][4]={
    {0x8888,0x0000,0x2222,0x0000}, {0x8888,0x4444,0x2222,0x1111},
    {0xAAAA,0x4444,0xAAAA,0x1111}, {0xAAAA,0x4444,0xAAAA,0x5555},
    {0xFFFF,0xFFFF,0xFFFF,0xFFFF}
};
bool selected(unsigned mask,unsigned x) {
    return (mask & ((0x80u>>(x&7u))<<((x&8u) ? 8 : 0)))!=0;
}
std::string uppercase(std::string name) {
    for(auto& c:name) if(c>='a' && c<='z') c=static_cast<char>(c-32);
    return name;
}
std::uint16_t bold(std::uint16_t row) {
    const auto expanded=static_cast<std::uint16_t>(row|(row<<1));
    const auto added=static_cast<std::uint16_t>((row^expanded)<<1);
    return static_cast<std::uint16_t>(expanded&~added);
}
}

Canvas::Canvas(const Assets& assets,std::array<Bytes,2> pages,unsigned shown)
    :assets_(&assets),font_(assets.font_bitmap),pages_(std::move(pages)),shown_(shown&1u) {
    if(!font_.present()) throw std::invalid_argument("MAINE requires a supplied PC-98 font bitmap");
    for(auto& page:pages_) {
        if(page.empty())page.resize(width*height);
        if(page.size()!=width*height)throw std::invalid_argument("MAINE graphics page is incomplete");
    }
}
Scene::Scene(const Assets& assets,const std::string& name)
    :Canvas(assets),script_(assets.scripts.at(uppercase(name))) {
    script_.begin();
}
void Scene::advance(std::uint16_t held,const Sink& observer) {
    script_.advance(held,[&](const Event& event) { apply(event);if(observer) observer(event); });
}
void Canvas::rect_copy(unsigned source,unsigned dest,int left,int top,unsigned w,unsigned h,unsigned mask) {
    if(source>1 || dest>1) throw std::invalid_argument("invalid MAINE page copy");
    for(unsigned y=0;y<h;++y) for(unsigned x=0;x<w;++x) {
        const int px=left+int(x),py=top+int(y);
        if(px<0 || px>=int(width) || py<0 || py>=int(height)) continue;
        if(selected(mask,x)) pages_[dest][unsigned(py)*width+unsigned(px)]=pages_[source][unsigned(py)*width+unsigned(px)];
    }
}
void Canvas::draw_picture(int left,int top,int quarter,unsigned mask,bool full) {
    if(!loaded_) throw std::logic_error("MAINE picture slot is empty");
    if(loaded_->pixels.size()!=std::size_t(loaded_->width)*loaded_->height/2)
        throw std::invalid_argument("invalid MAINE packed picture");
    if(!full && (loaded_->width!=640 || loaded_->height!=400))
        throw std::invalid_argument("MAINE quarters require a 640x400 PI image");
    const unsigned w=full ? loaded_->width : 320,h=full ? loaded_->height : 200;
    // The original quarter pointer only applies offsets for 1,2,3. Other
    // values use quarter0; the immediate script command separately clears >=4.
    const unsigned sx=!full && (quarter==1 || quarter==3) ? 320 : 0;
    const unsigned sy=!full && (quarter==2 || quarter==3) ? 200 : 0;
    left=(left/8)*8;
    for(unsigned y=0;y<h;++y) for(unsigned x=0;x<w;++x) {
        const int px=left+int(x),py=((top+int(y))%int(height)+int(height))%int(height);
        if(px<0 || px>=int(width) || !selected(mask,x)) continue;
        const auto packed=loaded_->pixels[(sy+y)*(loaded_->width/2)+(sx+x)/2];
        pages_[accessed_][unsigned(py)*width+unsigned(px)]=static_cast<std::uint8_t>((x&1) ? packed&15 : packed>>4);
    }
}
void Canvas::glyph(const Event& e,bool gaiji) {
    if(!gaiji && e.e>3) throw std::invalid_argument("unsupported MAINE glyph effect");
    if(!gaiji)text_weight_=unsigned(e.e);
    unsigned base=0;
    if(gaiji) {
        if(e.c<0 || e.c>=256 || assets_->gaiji.size()<32) throw std::invalid_argument("invalid MAINE gaiji");
        base=32u+unsigned(assets_->gaiji[28])+(unsigned(assets_->gaiji[29])<<8)+unsigned(e.c)*32;
        if(base>assets_->gaiji.size() || assets_->gaiji.size()-base<32) throw std::invalid_argument("truncated MAINE gaiji");
    }
    const auto weight=[&](std::uint16_t row) {
        // MAINE's heavy/bold/black kernels operate on a 16-bit register,
        // even for an eight-dot ANK row. Preserve truncation at each step.
        if(e.e==1 || e.e==3) row=static_cast<std::uint16_t>(row|(row<<1));
        if(e.e==2 || e.e==3) row=bold(row);
        return row;
    };
    const auto put=[&](int px,int py) {
        if(px>=0 && px<int(width) && py>=0 && py<int(height))
            pages_[accessed_][unsigned(py)*width+unsigned(px)]=static_cast<std::uint8_t>(e.d&15);
    };
    if(gaiji) {
        for(unsigned y=0;y<16;++y) for(unsigned x=0;x<16;++x)
            if(assets_->gaiji[base+y*2+x/8]&(0x80u>>(x&7))) put(e.a+int(x),e.b+int(y));
        return;
    }
    // script_op passes a two-byte NUL-terminated string, rather than a
    // guaranteed Shift-JIS character. The real _ED000 script also supplies
    // ",4". Decode each character as the observed graph_putsa_fx does.
    const unsigned chars[3]={unsigned(e.c>>8)&255u,unsigned(e.c)&255u,0};
    unsigned at=0;int left=e.a;
    while(at<2 && chars[at]) {
        const unsigned first=chars[at++],high=first&0xE0u;
        const bool full=high==0x80u || high==0xE0u;
        const auto sjis=static_cast<std::uint16_t>((first<<8)|chars[at]);
        if(full) ++at;
        for(unsigned y=0;y<16;++y) {
            std::uint16_t row=0;
            const unsigned dots=full ? 16 : 8;
            for(unsigned x=0;x<dots;++x) {
                const bool set=full ? font_.pixel(sjis,x,y) : font_.ank_pixel(static_cast<std::uint8_t>(first),x,y);
                if(set) row|=static_cast<std::uint16_t>(1u<<(dots-1-x));
            }
            row=weight(row);
            if(full) {
                for(unsigned x=0;x<16;++x) if(row&(0x8000u>>x)) put(left+int(x),e.b+int(y));
            } else if(first!=' ') {
                // The target stores ANK in AL, applies the same WORD effect,
                // then RORs and writes little-endian. For aligned x, weight
                // dots in AH appear eight dots to the right; do not repair
                // this original graphics-font quirk in the native port.
                const unsigned shift=unsigned(left)&7u;
                if(shift) row=static_cast<std::uint16_t>((row>>shift)|(row<<(16-shift)));
                for(unsigned x=0;x<16;++x)
                    if(row&(1u<<((x/8)*8+7-(x&7)))) put((left&~7)+int(x),e.b+int(y));
            }
        }
        left+=full ? 16 : 8;
    }
}
void Canvas::put_text(int left,int top,const std::string& text,unsigned color,unsigned weight) {
    if(weight>3)throw std::invalid_argument("unsupported MAINE text effect");
    text_weight_=weight;
    for(std::size_t at=0;at<text.size() && text[at];) {
        const unsigned first=static_cast<unsigned char>(text[at++]);
        const bool full=(first&0xe0u)==0x80u || (first&0xe0u)==0xe0u;
        unsigned second=0;
        if(full) {
            if(at>=text.size() || !text[at])throw std::invalid_argument("MAINE text has a truncated Shift-JIS character");
            second=static_cast<unsigned char>(text[at++]);
        }
        glyph({Kind::text,left,top,int((first<<8)|second),int(color),int(weight)},false);
        left+=full ? 16 : 8;
    }
}
void Canvas::put_gaiji(int left,int top,const std::string& text,int step,unsigned color) {
    for(unsigned char c:text) {
        if(!c)break;
        glyph({Kind::gaiji,left,top,c,int(color)},true);left+=step;
    }
}
void Canvas::apply(const Event& e) {
    ++event_count_;
    switch(e.kind) {
    case Kind::show:shown_=unsigned(e.a)&1u;break;
    case Kind::access:accessed_=unsigned(e.a)&1u;break;
    case Kind::snap:
        box_background_.resize(480*64);
        for(unsigned y=0;y<64;++y) std::copy_n(pages_[accessed_].begin()+(320+y)*width+80,480,box_background_.begin()+y*480);
        break;
    case Kind::restore:
        if(box_background_.size()!=480*64) throw std::logic_error("MAINE text-box background is absent");
        for(unsigned y=0;y<64;++y) std::copy_n(box_background_.begin()+y*480,480,pages_[accessed_].begin()+(320+y)*width+80);
        break;
    case Kind::bg_free:box_background_.clear();break;
    case Kind::clear:std::fill(pages_[accessed_].begin(),pages_[accessed_].end(),0);break;
    case Kind::copy_page:
        // graph_copy_page selects the destination and copies its opposite
        // page. It does not copy whichever page happened to be accessed.
        accessed_=unsigned(e.a)&1u;pages_[accessed_]=pages_[1-accessed_];break;
    case Kind::text:glyph(e,false);break;
    case Kind::gaiji:glyph(e,true);break;
    case Kind::box_mask:
        if(e.a<0 || e.a>4) throw std::invalid_argument("invalid MAINE box mask");
        for(unsigned y=320;y<384;++y) rect_copy(1,0,80,int(y),480,1,box_masks[e.a][y&3]);
        accessed_=0;break;
    case Kind::pi_free:loaded_=nullptr;break;
    case Kind::pi_load:loaded_=&assets_->pictures.at(uppercase(e.name));break;
    case Kind::pi_palette:
        if(!loaded_) throw std::logic_error("MAINE palette slot is empty");
        palette_=loaded_->palette;break;
    case Kind::pi_put:draw_picture(e.a,e.b,0,0xFFFF,true);break;
    case Kind::quarter:draw_picture(e.a,e.b,e.c,0xFFFF);break;
    case Kind::pic_mask:
        if(e.d<0 || e.d>3) throw std::invalid_argument("invalid MAINE picture mask");
        if(!loaded_) throw std::logic_error("MAINE masked picture slot is empty");
        shown_=1;accessed_=0;
        for(unsigned y=0;y<200;++y) {
            // Draw each selected row directly. The original packs it into
            // offscreen row400, then EGC copies it into the shown rectangle.
            const auto& image=*loaded_;
            if(image.width!=640 || image.height!=400) throw std::invalid_argument("invalid masked PI dimensions");
            const unsigned sx=(e.c==1 || e.c==3) ? 320 : 0,sy=(e.c==2 || e.c==3) ? 200 : 0;
            const unsigned mask=picture_masks[e.d][y&3];
            for(unsigned x=0;x<320;++x) if(selected(mask,x)) {
                const int px=e.a+int(x),py=e.b+int(y);
                if(px<0 || px>=int(width) || py<0 || py>=int(height)) continue;
                const auto packed=image.pixels[(sy+y)*320+(sx+x)/2];
                pages_[0][unsigned(py)*width+unsigned(px)]=static_cast<std::uint8_t>((x&1) ? packed&15 : packed>>4);
            }
        }
        shown_=0;rect_copy(0,1,e.a,e.b,320,200,0xFFFF);accessed_=1;break;
    case Kind::pic_copy:rect_copy(0,1,e.a,e.b,320,200,0xFFFF);accessed_=1;break;
    case Kind::clear_rect:
        for(int y=0;y<e.d;++y) for(int x=0;x<e.c;++x) {
            const int px=e.a+x,py=e.b+y;
            if(px>=0 && px<int(width) && py>=0 && py<int(height)) pages_[accessed_][unsigned(py)*width+unsigned(px)]=0;
        }
        break;
    case Kind::scroll:scroll_=e.a;break;
    case Kind::bgm_control:case Kind::bgm_load:case Kind::se_begin:case Kind::se:case Kind::se_end:case Kind::measure:
        sound_requests_.push_back(e);break;
    default:break; // Waits, palette tone and fades belong to Script's clock.
    }
}
} // namespace th04::portable::cutscene
