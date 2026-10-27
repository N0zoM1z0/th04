#include "pc98_palette.hpp"
#include "registration_render.hpp"
#include "registration_numerals.hpp"
#include "super_kernel.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::registration {
namespace {
void require(bool b,const char* text) {if(!b)throw std::invalid_argument(text);}
int row_top(unsigned place) {return place==0 ? 96 : int(place)*16+112;}
}
TextPlane::TextPlane(const score_file::Bytes& bytes) {
    require(bytes.size()==8000,"incomplete initial text banks");
    for(unsigned at=0;at<2000;++at) {
        codes_[at]=std::uint16_t(bytes[at*2]|unsigned(bytes[at*2+1])<<8);
        attributes_[at]=std::uint16_t(bytes[4000+at*2]|unsigned(bytes[4000+at*2+1])<<8);
    }
}
void TextPlane::put_character(int column,int row,std::uint16_t character,std::uint16_t attribute) {
    const auto segment=std::uint16_t(unsigned(segment_)+unsigned(std::uint16_t(row))*10u);
    auto offset=std::uint16_t(unsigned(std::uint16_t(column))*2u);
    const unsigned high=character>>8;
    if(high) {
        if(high>=0x80) {
            const unsigned trail=character&255u;
            unsigned converted=(unsigned(Byte(high*2u))<<8)|trail,carry=0;
            if(trail<0x9f) {
                converted+=0xfedfu+unsigned(trail<0x80);
                carry=unsigned(converted>65535u);converted&=65535u;
            }
            character=std::uint16_t(converted-0xdffeu-carry)&0x7f7fu;
        }
        character=std::uint16_t((unsigned(Byte(character))<<8)|Byte((character>>8)-0x20u));
        store_word(segment,std::uint16_t(offset+0x2000u),attribute);
        store_word(segment,offset,character);offset=std::uint16_t(offset+2u);
        character|=0x80u;
    }
    store_word(segment,std::uint16_t(offset+0x2000u),attribute);
    store_word(segment,offset,character);
}
void TextPlane::put(int column,int row,Byte glyph,std::uint16_t attribute) {
    const auto segment=std::uint16_t(unsigned(segment_)+unsigned(std::uint16_t(row))*10u);
    auto offset=std::uint16_t(unsigned(std::uint16_t(column))*2u);
    const auto code=std::uint16_t(((unsigned(glyph)&127u)<<8)+0x56u+(unsigned(glyph)>>7));
    store_word(segment,std::uint16_t(offset+0x2000u),attribute);
    store_word(segment,offset,code);offset=std::uint16_t(offset+2u);
    store_word(segment,std::uint16_t(offset+0x2000u),attribute);
    store_word(segment,offset,std::uint16_t(code|0x8000u));
}
void TextPlane::put_string(int column,int row,const std::string& text,std::uint16_t attribute) {
    const auto segment=std::uint16_t(unsigned(segment_)+unsigned(std::uint16_t(row))*10u);
    const auto start=std::uint16_t(unsigned(std::uint16_t(column))*2u);
    auto offset=start;
    for(unsigned char glyph:text) {
        if(!glyph)break;
        const auto code=std::uint16_t(((unsigned(glyph)&127u)<<8)+0x56u+(unsigned(glyph)>>7));
        store_word(segment,offset,code);offset=std::uint16_t(offset+2u);
        store_word(segment,offset,std::uint16_t(code|0x8000u));offset=std::uint16_t(offset+2u);
    }
    const unsigned words=unsigned(std::uint16_t(offset-start))>>1;
    offset=std::uint16_t(start+0x2000u);
    for(unsigned word=0;word<words;++word) {
        store_word(segment,offset,attribute);offset=std::uint16_t(offset+2u);
    }
}
void TextPlane::store_byte(std::uint32_t address,Byte value) {
    auto bank=[&](auto& words,std::uint32_t base) {
        const auto offset=address-base,shift=(offset&1u)*8u;
        auto& word=words[offset/2];
        word=std::uint16_t((word&~(255u<<shift))|(unsigned(value)<<shift));
    };
    if(address>=0xa0000 && address<0xa0000+4000)bank(codes_,0xa0000);
    else if(address>=0xa2000 && address<0xa2000+4000)bank(attributes_,0xa2000);
    else other_pages_[address/256][address%256]=value;
}
void TextPlane::store_word(std::uint16_t segment,std::uint16_t offset,std::uint16_t value) {
    const auto address=std::uint32_t(segment)*16u+offset;
    store_byte(address,Byte(value));store_byte(address+1,Byte(value>>8));
}
void TextPlane::load_memory(std::uint32_t start,const score_file::Bytes& input) {
    require(start<=0x110000 && input.size()<=0x110000-start,"text memory input exceeds real-mode addresses");
    for(std::size_t at=0;at<input.size();) {
        const auto address=start+std::uint32_t(at);
        const auto count=std::min<std::size_t>(256-address%256,input.size()-at);
        std::copy_n(input.begin()+at,count,other_pages_[address/256].begin()+address%256);
        at+=count;
    }
    for(const auto base:{0xa0000u,0xa2000u}) {
        const auto first=std::max(start,base);
        const auto last=std::min<std::size_t>(start+input.size(),base+4000u);
        for(auto address=first;address<last;++address)store_byte(address,input[address-start]);
    }
}
score_file::Bytes TextPlane::physical_bytes(std::uint32_t start,std::size_t length) const {
    require(start<=0x110000 && length<=0x110000-start,"text memory output exceeds real-mode addresses");
    score_file::Bytes result(length);
    for(const auto& [page,bytes]:other_pages_) {
        const auto first=std::max(start,page*256u);
        const auto last=std::min<std::size_t>(start+length,page*256u+256u);
        if(first<last)std::copy_n(bytes.begin()+first-page*256u,last-first,result.begin()+first-start);
    }
    const auto overlay=[&](const auto& words,std::uint32_t base) {
        const auto first=std::max(start,base);
        const auto last=std::min<std::size_t>(start+length,base+4000u);
        for(auto address=first;address<last;++address) {
            const auto offset=address-base;
            result[address-start]=Byte(words[offset/2]>>((offset&1u)*8u));
        }
    };
    overlay(codes_,0xa0000);overlay(attributes_,0xa2000);return result;
}
void TextPlane::put_sjis(int column,int row,const std::string& text,std::uint16_t attribute) {
    const auto segment=std::uint16_t(unsigned(segment_)+unsigned(std::uint16_t(row))*10u);
    const auto start=std::uint16_t(unsigned(std::uint16_t(column))*2u);
    auto offset=start;
    const auto store=[&](std::uint16_t code) {
        store_word(segment,offset,code);offset=std::uint16_t(offset+2u);
    };
    for(std::size_t i=0;i<text.size();) {
        const Byte lead=Byte(text[i++]);if(!lead)break;
        if(lead<=0x80 || (lead>0x9f && lead<=0xdf)) {store(lead);continue;}
        // A dangling lead consumes the terminating zero as its trail.
        const Byte trail=i<text.size() ? Byte(text[i++]) : Byte(0);
        unsigned converted=(unsigned(Byte(unsigned(lead)*2u))<<8)|trail,carry=0;
        if(trail<0x9f) {
            converted+=0xfedfu+unsigned(trail<0x80);
            carry=unsigned(converted>65535u);converted&=65535u;
        }
        converted=(converted&0xff00u)|Byte(converted-0xfeu-carry);
        converted&=0x7f7fu;
        const auto code=std::uint16_t((converted>>8)|((converted&255u)<<8));
        store(code);store(std::uint16_t(code|0x80));
    }
    const unsigned words=unsigned(std::uint16_t(offset-start))>>1;
    offset=std::uint16_t(start+0x2000u);
    for(unsigned word=0;word<words;++word) {
        store_word(segment,offset,attribute);offset=std::uint16_t(offset+2u);
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
namespace {
template<class Paint>
void paint_text(const std::array<std::uint16_t,2000>& codes_,
                const std::array<std::uint16_t,2000>& attributes_,
                const score_file::Bytes& gaiji,const dialog::Font& font,bool blink_visible,Paint paint) {
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
        const bool custom=column==0x56 || column==0x57;
        const unsigned jis_cell=(code>>8)&127u;
        const bool standard=!custom && column>=1 && column<=0x5e && jis_cell>=0x21 && jis_cell<=0x7e;
        const bool kanji=custom || standard;
        if(!kanji)right=false;
        if(right && (code&0x7f7fu)!=(previous&0x7f7fu))right=false;
        const unsigned glyph=custom ? ((code>>8)&127u)+(column-0x56u)*128u : 0;
        for(unsigned y=0;y<16;++y) {
            unsigned mask=0;
            if(attribute&1u) {
                if(custom && (code&0xff00u))mask=gaiji[base+glyph*32+y*2+(right ? 1 : 0)];
                else if(standard) {
                    const unsigned jis_row=column+0x20;
                    const unsigned lead=(jis_row-0x21)/2+(jis_row<0x5f ? 0x81 : 0xc1);
                    const unsigned trail=jis_row&1u ? jis_cell+0x1f+(jis_cell>=0x60 ? 1 : 0) : jis_cell+0x7e;
                    const auto dots=font.row(std::uint16_t((lead<<8)|trail),y);
                    mask=right ? dots&255u : dots>>8;
                }
                else mask=font.ank_row(Byte(code),y);
            }
            if((attribute&2u) && !blink_visible)mask=0;
            if(attribute&4u)mask^=255u; // Blink blanks the font before reverse.
            for(unsigned x=0;x<8;++x)if(mask&(128u>>x)) {
                paint((cell/80*16+y)*640+(cell%80)*8+x,attribute);
            }
        }
        previous=code;right=kanji && (code&0xff00u) && !right;
    }
}
}
void TextPlane::overlay(score_file::Bytes& rgb,const score_file::Bytes& gaiji,const dialog::Font& font,bool blink_visible) const {
    require(rgb.size()==640*400*3,"registration RGB frame is incomplete");
    paint_text(codes_,attributes_,gaiji,font,blink_visible,[&](unsigned at,std::uint16_t attr) {
        rgb[at*3]=(attr&0x40u) ? 255 : 0;
        rgb[at*3+1]=(attr&0x80u) ? 255 : 0;
        rgb[at*3+2]=(attr&0x20u) ? 255 : 0;
    });
}
void TextPlane::overlay(std::vector<std::uint32_t>& argb,const score_file::Bytes& gaiji,const dialog::Font& font,bool blink_visible) const {
    require(argb.size()==640*400,"MAIN ARGB frame is incomplete");
    paint_text(codes_,attributes_,gaiji,font,blink_visible,[&](unsigned at,std::uint16_t attr) {
        argb[at]=0xff000000u|((attr&0x40u) ? 0xff0000u : 0)|
            ((attr&0x80u) ? 0xff00u : 0)|((attr&0x20u) ? 0xffu : 0);
    });
}
void TextPlane::copy_rectangle(const TextPlane& source,unsigned left,unsigned top,unsigned width,unsigned height) {
    require(left<=80 && width<=80-left && top<=25 && height<=25-top,"text copy exceeds banks");
    for(unsigned row=top;row<top+height;++row)for(unsigned col=left;col<left+width;++col) {
        const auto at=row*80+col;codes_[at]=source.codes_[at];attributes_[at]=source.attributes_[at];
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
    const auto scaled=std::uint16_t(std::uint16_t(pattern)*2u);
    const auto owned_pattern=unsigned(scaled/2u);
    require(bool(numerals_) && owned_pattern<numerals_->count(),"unowned registration numeral memory");
    require(owned_pattern<numeral_planes_.size(),"registration planar slot missing");
    const auto& planes=numeral_planes_[owned_pattern];
    auto& page=canvas_.drawing_page();unsigned mode=0,tile=0;std::array<Byte,4> tiles{};
    const auto read=[&](std::uint16_t offset,unsigned count) {
        require(unsigned(offset)+count<=planes.size(),"unowned registration pattern read");
        unsigned value=planes[offset];if(count==2)value|=unsigned(planes[unsigned(offset)+1])<<8;
        return std::uint16_t(value);
    };
    const auto port=[&](unsigned address,Byte value) {
        if(address==0x7c){mode=value;tile=0;}
        else {require(address==0x7e,"unknown registration sprite port");tiles[tile]=value;tile=(tile+1)%4;}
    };
    const auto write=[&](std::uint16_t offset,unsigned count,std::uint16_t value) {
        require((mode&0x80)!=0,"registration sprite outside GRCG mode");
        const unsigned enabled=(~mode)&15u;
        for(unsigned byte=0;byte<count;++byte) {
            const unsigned at=unsigned(offset)+byte;if(at>=32000)continue;
            const unsigned mask=(value>>(byte*8u))&255u;
            for(unsigned bit=0;bit<8;++bit) {
                if((mode&0x40) && !(mask&(128u>>bit)))continue;
                unsigned color=0;for(unsigned plane=0;plane<4;++plane)if(tiles[plane]&(128u>>bit))color|=1u<<plane;
                auto& pixel=page[at*8+bit];pixel=Byte((pixel&~enabled)|(color&enabled));
            }
        }
    };
    sprite::super::put(std::uint16_t(left),std::uint16_t(top),0x0210,read,write,port);

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
    score::Digits digits{};
    std::copy_n(section.begin()+score_file::digits_offset+place*8,8,digits.begin());
    for(const auto& request:numerals::row(digits,place,selected,character))
        put_numeral(request.left,request.top,request.slot.pattern);
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
        numeral_planes_.assign(20,score_file::Bytes(160));
        for(unsigned pattern=0;pattern<20;++pattern)for(unsigned y=0;y<16;++y)for(unsigned x=0;x<16;++x) {
            const auto color=numerals_->pixel(pattern,x,y);const unsigned at=y*2+x/8,bit=128u>>(x&7u);
            if(color){numeral_planes_[pattern][at]|=Byte(bit);for(unsigned plane=0;plane<4;++plane)if(color&(1u<<plane))numeral_planes_[pattern][(plane+1)*32+at]|=Byte(bit);}
        }
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
    case Kind::free_sprites:numerals_.reset();numeral_planes_.clear();break;
    case Kind::clear_text:text_.clear();break;
    default:break; // Timing, sound, file commands and fades are scene-owned.
    }
}
score_file::Bytes Renderer::rgb(unsigned page,int tone) const {
    const auto dac=pc98_palette::show(canvas_.palette(),tone);
    std::array<std::array<Byte,3>,16> colors{};
    for(unsigned color=0;color<16;++color)for(unsigned channel=0;channel<3;++channel)
        colors[color][channel]=pc98_palette::analog_rgb8(dac[color*3+channel]);
    score_file::Bytes rgb(640*400*3);const auto& indices=canvas_.page(page);
    for(unsigned at=0;at<indices.size();++at)for(unsigned channel=0;channel<3;++channel) {
        rgb[at*3+channel]=colors[indices[at]][channel];
    }
    text_.overlay(rgb,assets_->graphics.gaiji,font_);return rgb;
}
} // namespace th04::portable::registration
