#include "registration.hpp"
#include <utility>

namespace th04::portable::registration {
// Target keyboard order: letters/punctuation, special symbols, digits and
// commands. These are TH04 gaiji indices, not ASCII or host Unicode text.
const std::array<Byte,51> alphabet={
    0xaa,0xab,0xac,0xad,0xae,0xaf,0xb0,0xb1,0xb2,0xb3,0xb4,0xb5,0xb6,0xb7,0xb8,0xb9,0xba,
    0xbb,0xbc,0xbd,0xbe,0xbf,0xc0,0xc1,0xc2,0xc3,0xc4,0xc5,0x03,0x06,0x07,0x08,0x0c,0x0f,
    0xa0,0xa1,0xa2,0xa3,0xa4,0xa5,0xa6,0xa7,0xa8,0xa9,0xe6,0xe7,0xe8,back,forward,space,enter
};
void Menu::event(Kind kind,int a,int b,int c,int d,std::string text) {
    events_.push_back({kind,a,b,c,d,{},std::move(text),{}});
}
void Menu::flush_io() {
    const auto& operations=file_->operations();
    while(io_at_<operations.size()) {
        Event e{Kind::file};e.io=operations[io_at_++];events_.push_back(std::move(e));
    }
}
void Menu::table(Byte character) {
    Event e{Kind::table,int(character)};e.bytes.assign(section_.begin(),section_.end());
    events_.push_back(std::move(e));
}
void Menu::alphabet_cursor(int color) {
    event(Kind::gaiji,23+column_*2,18+row_,alphabet[row_*17+column_],color);
}
void Menu::redraw_name() {
    Event e{Kind::name,int(place_),int(character_),cursor_};
    e.bytes.assign(section_.begin(),section_.end());events_.push_back(std::move(e));
}
Menu::Menu(Run run,score_file::File& file,const score_file::Random& random,std::uint16_t initial_keys)
    :file_(&file),random_(random),io_at_(file.operations().size()),previous_keys_(initial_keys) {
    event(Kind::tone,0);event(Kind::access,1);
    event(Kind::pi_load,0,0,0,0,"HI01.PI");event(Kind::pi_palette,0);
    event(Kind::pi_put,0,0,0);event(Kind::pi_free,0);event(Kind::copy,0);
    event(Kind::bfnt,0,0,0,0,"SCNUM2.BFT");
    rank_=run.stage==6 ? 4 : run.rank;
    character_=run.character_ascii=='1' ? 1 : 0;
    // Render the other character while its decoded section occupies HI, then
    // replace that same work buffer with the selected character's section.
    score_file::load_for(section_,file,Byte(1-character_),rank_,random_);flush_io();table(Byte(1-character_));
    score_file::load_for(section_,file,character_,rank_,random_);flush_io();
    if(run.turbo || rank_==4)place_=score_file::insert(section_,run.digits,run.stage,run.end_sequence);
    table(character_);
    if(!run.turbo && rank_!=4) {
        // The actual Shift-JIS message is a separately attested graphics input;
        // these two requests retain its shadow/foreground placement and owner.
        event(Kind::text,124,196,9,0,"non_turbo_shadow");
        event(Kind::text,120,192,2,0,"non_turbo_foreground");
    }
    if(run.end_sequence==0xff || run.end_sequence==0xfd || rank_==0) {
        auto& cleared=section_[score_file::cleared_offset];
        const Byte bit=run.shot_type==0 ? 1 : 2;
        cleared=cleared>=4 ? bit : Byte(cleared|bit);
    }
    event(Kind::sound,0x100);event(Kind::song,0x600,0,0,0,"NAME");event(Kind::sound,0);
    event(Kind::fade,1,2);
    if(!editable()) { finish(true);return; }
    for(int row=0;row<3;++row)for(int col=0;col<17;++col)
        event(Kind::gaiji,23+col*2,18+row,alphabet[row*17+col],0xe1);
    alphabet_cursor(0x85);
    // Original reset_sense stores one sample; sense ORs a later sample into it.
    // Lock starts at1 even with no key held. The first released iteration
    // clears it, preventing an inherited confirmation from immediately typing.
}
void Menu::erase_and_back() {
    section_[score_file::names_offset+place_*score_file::name_stride+cursor_]=empty;
    if(cursor_>0)--cursor_;
    redraw_name();
}
void Menu::finish(bool acknowledgement) {
    score_file::save(section_,*file_,character_,rank_,random_);flush_io();
    // section_ is now encoded section9. All editable rendering requests retain
    // their pre-save snapshots; never read name glyphs from this buffer again.
    if(acknowledgement)event(Kind::wait,0);
    event(Kind::free_sprites);event(Kind::clear_text);event(Kind::fade,0,1);finished_=true;
}
void Menu::advance(std::uint16_t held) {
    if(finished_)return;
    const auto keys=std::uint16_t(previous_keys_|held);
    if(!lock_) {
        if(keys&15) {
            alphabet_cursor(0xe1);
            if(keys&up)--row_;
            if(keys&down)++row_;
            if(keys&left)--column_;
            if(keys&right)++column_;
            if(row_<0)row_=2;else if(row_>2)row_=0;
            if(column_<0)column_=16;else if(column_>16)column_=0;
            alphabet_cursor(0x85);
        }
        if(keys&(shot|ok)) {
            const auto glyph=alphabet[row_*17+column_];
            if(glyph==enter) {finish(false);return;}
            if(glyph==back)erase_and_back();
            else if(glyph==forward) {if(cursor_<7)++cursor_;redraw_name();}
            else {
                section_[score_file::names_offset+place_*score_file::name_stride+cursor_]=glyph==space ? empty : glyph;
                if(cursor_==7) {
                    alphabet_cursor(0xe1);column_=16;row_=2;alphabet_cursor(0x85);
                }
                if(cursor_<7)++cursor_;
                redraw_name();
            }
        }
        // Commands are independent and ordered. A combined Shot/Bomb can
        // type, advance and erase the following cell in the SAME iteration.
        if(keys&bomb)erase_and_back();
        if(keys&cancel) {finish(false);return;} // Esc saves the partial name.
        lock_=keys;
    } else if(keys==lock_) {
        repeat_=Byte(repeat_+1);
        // This BYTE is not reset on an accepted repeated action. Preserve its
        // wrap and the original every-second held iteration after delay30.
        if(repeat_>30 && !(repeat_&1))lock_=0;
    } else {
        // A different NONZERO chord leaves the old lock unchanged. A complete
        // release clears it; changing this to lock_=keys invents new repeats.
        if(!keys)lock_=0;
        repeat_=0;
    }
    previous_keys_=held;++ticks_;
}
} // namespace th04::portable::registration
