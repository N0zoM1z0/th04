#include "registration_render.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::registration {
namespace {
void require(bool b,const char* text) {if(!b)throw std::invalid_argument(text);}
int row_top(unsigned place) {return place==0 ? 96 : int(place)*16+112;}
}
void TextPlane::put(int column,int row,Byte glyph,std::uint16_t attribute) {
    require(column>=0 && column<80 && row>=0 && row<25,"invalid registration text cell");
    const unsigned at=unsigned(row*80+column);
    require(at+1<codes_.size(),"registration gaiji exceeds text bank");
    const auto code=std::uint16_t(((unsigned(glyph)&127u)<<8)+0x56u+(unsigned(glyph)>>7));
    codes_[at]=code;codes_[at+1]=std::uint16_t(code|0x8000u);
    attributes_[at]=attribute;attributes_[at+1]=attribute;
}
void TextPlane::put_string(int column,int row,const std::string& text,std::uint16_t attribute) {
    for(unsigned char glyph:text) {
        if(!glyph)break;
        put(column,row,glyph,attribute);column+=2;
        // The target uses a linear WORD bank: a pair at column79 spills into
        // the next row. Keep that defined bank behavior for subsequent pairs.
        while(column>=80) {column-=80;++row;}
    }
}
void TextPlane::clear() {codes_.fill(0);attributes_.fill(0);}
score_file::Bytes TextPlane::bytes() const {
    score_file::Bytes result;result.reserve(8000);
    for(const auto& bank:{codes_,attributes_})for(auto word:bank) {
        result.push_back(Byte(word));result.push_back(Byte(word>>8));
    }
    return result;
}
void TextPlane::overlay(score_file::Bytes& rgb,const score_file::Bytes& gaiji,const dialog::Font& font) const {
    require(rgb.size()==640*400*3,"registration RGB frame is incomplete");
    require(gaiji.size()>=32,"registration gaiji header is incomplete");
    const unsigned base=32u+unsigned(gaiji[28])+(unsigned(gaiji[29])<<8);
    require(base<=gaiji.size() && gaiji.size()-base>=256*32,"registration gaiji bank is incomplete");
    // Registration writes both halves explicitly in the custom 56/57 bank.
    // As observed in the pinned PC-98 video consumer, a mismatching second
    // code starts a new left half. Each half uses its OWN attribute word.
    bool right=false;std::uint16_t previous=0;
    for(unsigned cell=0;cell<codes_.size();++cell) {
        if(cell%80==0)right=false;
        const auto code=codes_[cell],attribute=attributes_[cell];
        const unsigned column=code&127u;
        if(column!=0x56 && column!=0x57) {right=false;continue;}
        if(right && (code&0x7f7fu)!=(previous&0x7f7fu))right=false;
        const unsigned glyph=((code>>8)&127u)+(column-0x56u)*128u;
        for(unsigned y=0;y<16;++y) {
            unsigned mask=0;
            if(attribute&1u) {
                if(code&0xff00u)mask=gaiji[base+glyph*32+y*2+(right ? 1 : 0)];
                else for(unsigned x=0;x<8;++x)if(font.ank_pixel(Byte(code),x,y))mask|=128u>>x;
            }
            if(attribute&4u)mask^=255u; // Reverse MASK; holes still expose graphics.
            for(unsigned x=0;x<8;++x)if(mask&(128u>>x)) {
                const unsigned at=((cell/80*16+y)*640+(cell%80)*8+x)*3;
                rgb[at]=(attribute&0x40u) ? 255 : 0;
                rgb[at+1]=(attribute&0x80u) ? 255 : 0;
                rgb[at+2]=(attribute&0x20u) ? 255 : 0;
            }
        }
        previous=code;right=(code&0xff00u) && !right;
    }
}
Renderer::Renderer(const GraphicsAssets& assets,Byte character,Byte place,
                   std::array<score_file::Bytes,2> pages,unsigned shown)
    :assets_(&assets),canvas_(assets.graphics,std::move(pages),shown),
     font_(assets.graphics.font_bitmap),selected_character_(character),entered_place_(place) {
    require(character<2,"invalid selected registration character");
    require(place<10 || place==score_file::no_entry,"invalid registration placement");
}
std::string Renderer::name(const score_file::Bytes& section,unsigned place) const {
    require(section.size()==score_file::section_size && place<10,"invalid registration row");
    const auto begin=section.begin()+score_file::names_offset+place*score_file::name_stride;
    // The original consumes a NUL-terminated string. The ninth byte belongs
    // to its row; do not silently invent a terminator after the eight letters.
    const auto end=std::find(begin,section.end(),Byte(0));
    require(end!=section.end(),"registration name lacks a bounded terminator");
    return std::string(begin,end);
}
void Renderer::put_numeral(int left,int top,unsigned pattern) {
    require(bool(numerals_) && pattern<numerals_->count(),"undefined registration numeral pattern");
    auto& page=canvas_.drawing_page();
    for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16;++x) {
        const auto color=numerals_->pixel(pattern,x,y);
        const int px=left+int(x),py=top+int(y);
        if(color && px>=0 && px<640 && py>=0 && py<400)page[unsigned(py)*640+unsigned(px)]=color;
    }
}
void Renderer::restore_name_background(int left,int top,unsigned width,unsigned height) {
    require(left>=0,"negative registration background column");
    // MAINE 0A05:2BA3 shifts X by3 and copies width/16 WORDs. Its caller
    // passes X+2: copying from the unrounded dot would leave wrong shadows.
    canvas_.copy_rectangle(1,0,(left/8)*8,top,(width/16)*16,height);
    canvas_.apply({cutscene::Kind::access,0});
}
void Renderer::row(const score_file::Bytes& section,unsigned place,Byte character) {
    require(character<2,"invalid rendered registration character");
    const bool selected=place==entered_place_ && character==selected_character_;
    const int x=character==0 ? 16 : 320,y=row_top(place);
    const auto letters=name(section,place);
    canvas_.put_gaiji(x+2,y+2,letters,16,14);
    if(selected)text_.put_string(x/8,y/16,letters,0x41);
    else canvas_.put_gaiji(x,y,letters,16,12);
    // The highest score byte can hold two decimal digits (dream score).
    // Remaining bytes select a sprite directly; invalid indices are original
    // undefined pattern-table reads, not a license to manufacture pixels.
    int digit_x=character==0 ? 172 : 480;
    const unsigned bank=selected ? 10 : 0;
    const int high=int(section[score_file::digits_offset+place*8+7])-0xa0;
    if(high>=10)put_numeral(digit_x-32,y,unsigned(high/10)+bank);
    require(high>=0,"undefined negative registration numeral");
    put_numeral(digit_x-16,y,unsigned(high%10)+bank);
    for(int digit=6;digit>=0;--digit,digit_x+=16) {
        const int value=int(section[score_file::digits_offset+place*8+unsigned(digit)])-0xa0;
        require(value>=0,"undefined negative registration numeral");
        put_numeral(digit_x,y,unsigned(value)+bank);
    }
    const auto stage=std::string(1,char(section[score_file::stages_offset+place]));
    const int stage_x=character==0 ? 292 : 600;
    // putc draws glyph0 as well; Canvas string helpers stop at NUL.
    canvas_.apply({cutscene::Kind::gaiji,stage_x+2,y+2,Byte(stage[0]),14});
    canvas_.apply({cutscene::Kind::gaiji,stage_x,y,Byte(stage[0]),selected ? 7 : 12});
}
void Renderer::apply(const Event& e) {
    using C=cutscene::Kind;
    switch(e.kind) {
    case Kind::access:canvas_.apply({C::access,e.a});break;
    case Kind::pi_load: {cutscene::Event load{C::pi_load};load.name=e.text;canvas_.apply(load);break;}
    case Kind::pi_palette:canvas_.apply({C::pi_palette});break;
    case Kind::pi_put:canvas_.apply({C::pi_put,e.b,e.c});break;
    case Kind::pi_free:canvas_.apply({C::pi_free});break;
    case Kind::copy:canvas_.apply({C::copy_page,e.a});break;
    case Kind::bfnt:
        numerals_=std::make_unique<sprite::Sheet>(assets_->numerals);
        require(numerals_->width()==16 && numerals_->height()==16 && numerals_->count()==20,"SCNUM2 geometry differs");
        // Both private assets have the same RGB palette. Preserve the BFNT
        // palette load as a checked invariant instead of silently ignoring it.
        require(!numerals_->has_palette() || numerals_->palette()==canvas_.palette(),"registration PI/BFNT palettes differ");
        break;
    case Kind::table:for(unsigned place=0;place<10;++place)row(e.bytes,place,Byte(e.a));break;
    case Kind::name: {
        require(e.a>=0 && e.a<10 && e.b>=0 && e.b<2 && e.c>=0 && e.c<8,"invalid registration name cursor");
        const int x=e.b==0 ? 2 : 40,y=e.a==0 ? 6 : e.a+7;
        const auto letters=name(e.bytes,unsigned(e.a));
        restore_name_background(x*8+2,y*16+2,128,16);
        canvas_.put_gaiji(x*8+2,y*16+2,letters,16,14);
        text_.put_string(x,y,letters,0x41);
        text_.put(x+e.c*2,y,e.bytes[score_file::names_offset+unsigned(e.a)*9+unsigned(e.c)],0x45);
        break;
    }
    case Kind::gaiji:text_.put(e.a,e.b,Byte(e.c),std::uint16_t(e.d));break;
    case Kind::text:
        require(!assets_->non_turbo_message.empty(),"registration non-Turbo message is absent");
        canvas_.put_text(e.a,e.b,assets_->non_turbo_message,unsigned(e.c),assets_->text_weight);break;
    case Kind::free_sprites:numerals_.reset();break;
    case Kind::clear_text:text_.clear();break;
    default:break; // Timing, sound, file commands and fades are scene-owned.
    }
}
score_file::Bytes Renderer::rgb(unsigned page,int tone) const {
    require(tone>=0 && tone<=100,"registration tone outside fade range");
    score_file::Bytes rgb(640*400*3);const auto& indices=canvas_.page(page);
    for(unsigned at=0;at<indices.size();++at)for(unsigned channel=0;channel<3;++channel) {
        const unsigned component=canvas_.palette()[unsigned(indices[at])*3+channel]>>4;
        rgb[at*3+channel]=Byte((component*unsigned(tone)/100)*17);
    }
    text_.overlay(rgb,assets_->graphics.gaiji,font_);return rgb;
}
} // namespace th04::portable::registration
