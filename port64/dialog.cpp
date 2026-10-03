#include "dialog.hpp"
#include <stdexcept>
#include <algorithm>

namespace th04::portable::dialog {
namespace {
bool separator(unsigned c) { return c<=32 || c==127; }
bool digit(unsigned c) { return c>='0' && c<='9'; }
void emit(const Sink& sink,const Event& e) { if (sink) sink(e); }
} // namespace
std::uint8_t Script::peek(unsigned ahead) const {
    return ahead<bytes_.size()-std::min(at_,bytes_.size()) ? bytes_[at_+ahead] : 0;
}
std::uint8_t Script::take() {
    if (at_>=bytes_.size()) throw std::invalid_argument("dialog ended without an outer stop command");
    return bytes_[at_++];
}
int Script::number(int fallback) { default_=motion::wrap(fallback);return number(); }
int Script::number() {
    // Original reads three bytes then rewinds one/two/all three. Recover
    // the same consumed extent without reading past a flat native buffer.
    int value=0;unsigned n=0;
    while(n<3 && digit(peek())) { value=value*10+take()-'0';++n; }
    return n ? value : default_;
}
int Script::second() { if (peek()==',') { take();return number(); }return default_; }
std::string Script::filename() {
    std::string name;
    while(name.size()<12) { const auto c=take();if(separator(c)) break;name.push_back(static_cast<char>(c)); }
    return name;
}
void Script::begin() {
    if (status_!=Status::idle && status_!=Status::stopped) throw std::logic_error("dialog scene already running");
    // The buffer base remains owned, while the consumed cursor survives into
    // the post-boss scene. '#' inside a box only exits that box, not the scene.
    status_=Status::running;box_=false;tone_=100;
}
void Script::stop_command(const Sink& sink) {
    if (box_) box_=false;
    else { status_=Status::stopped;emit(sink,{Kind::overlay_wipe}); }
}
void Script::delay(int frames,const Sink& sink,const std::vector<Event>& after) {
    emit(sink,{Kind::delay,frames});ticks_=frames;after_=after;fade_step_=0;
    status_=Status::delay;
}
void Script::op(unsigned c,const Sink& sink) {
    if(c>='A' && c<='Z') c+='a'-'A';
    switch(c) {
    case 'n':cursor_.y=motion::wrap(int(cursor_.y)+16);cursor_.x=side_ ? 48 : 160;break;
    case 't': { const int n=number(100);delay(1,sink,{{Kind::tone,n}});break; }
    case 'f':case 'w': {
        const auto direction=peek();if(direction!='i' && direction!='o') break;
        take();const auto speed=number(1);
        const int from=c=='w' ? (direction=='i' ? 200 : 100) : (direction=='i' ? 0 : 100);
        const int to=direction=='i' ? 100 : (c=='w' ? 200 : 0);
        emit(sink,{Kind::fade,c=='w' ? 1 : 0,direction=='i' ? 1 : 0,speed});
        tone_=from;fade_end_=to;fade_step_=from<to ? 6 : -6;fade_speed_=speed;
        ticks_=1+speed;status_=Status::delay;after_.clear();break;
    }
    case 'g':
        if(peek()=='a') {
            take();const int n=number(0);emit(sink,{Kind::gaiji,cursor_.x,cursor_.y,n,0xe1});cursor_.x=motion::wrap(int(cursor_.x)+16);
        } else {
            const int n=number(8);
            // Shake is a finite ordered scroll/delay sequence, inclusive of n.
            for(int i=0;i<=n;++i) { after_.push_back({Kind::scroll,(i&1) ? 4 : 396});after_.push_back({Kind::delay,1}); }
            after_.push_back({Kind::scroll,0});
        }
        break;
    case 'k':case '$':
        press_budget_=c=='$' ? 0 : number(0);press_elapsed_=0;stop_after_wait_=c=='$';
        emit(sink,{Kind::wait,press_budget_});status_=Status::release;break;
    case '=': {
        const int n=number(1),left=side_ ? 288 : 32,top=side_ ? 112 : 240;
        std::vector<Event> events{{Kind::face_clear,left,top}};
        if(n!=255) events.push_back({Kind::face,left,top,n+(side_ ? 8 : 2)});
        delay(1,sink,events);break;
    }
    case 'b': {
        const int left=number(0),top=second(),pattern=second();delay(1,sink,{{Kind::sprite,left,top,pattern}});break;
    }
    case 'm':
        if(peek()=='$' || peek()=='*') emit(sink,{Kind::bgm_control,take()=='$' ? 256 : 0});
        else if(peek()==',') { take();Event e{Kind::bgm_load,1536};e.name=filename();emit(sink,e);emit(sink,{Kind::bgm_control,0}); }
        break;
    case 'e':emit(sink,{Kind::se_force,number()});break;
    case 'c':emit(sink,{Kind::clean,128,256});break;
    case 'l':
        if(peek()==',') { take();Event e{Kind::sprite_load};e.name=filename();emit(sink,e); }break;
    case 'd':for(int i=1;i<32;++i) emit(sink,{Kind::cdg_free,i});break;
    case '#':stop_command(sink);break;
    default:break;
    }
}
void Script::advance(std::uint16_t held,const Sink& sink) {
    if(status_==Status::idle || status_==Status::stopped) return;
    if(status_==Status::release) {
        // Original release always waits one frame and has no timeout.
        if(!held) { status_=Status::press;if(press_budget_<0) { status_=Status::running;if(stop_after_wait_) stop_command(sink); } }
        return;
    }
    if(status_==Status::press) {
        if(held || (press_budget_ && press_budget_!=9999 && ++press_elapsed_>=press_budget_)) {
            status_=Status::running;if(stop_after_wait_) stop_command(sink);
        }
        return;
    }
    if(status_==Status::delay) {
        if(ticks_>0 && --ticks_>0) return;
        if(fade_step_) {
            if(!fade_speed_) tone_=fade_end_;
            else tone_+=fade_step_;
            if((fade_step_>0 && tone_<fade_end_) || (fade_step_<0 && tone_>fade_end_)) { ticks_=fade_speed_;return; }
            tone_=fade_end_;fade_step_=0;
        }
        status_=Status::running;
    }
    while(status_==Status::running) {
        if(!after_.empty()) {
            const auto e=after_.front();after_.erase(after_.begin());
            emit(sink,e);
            if(e.kind==Kind::tone) tone_=e.a;
            if(e.kind==Kind::delay) { ticks_=e.a;status_=Status::delay;return; }
            continue;
        }
        const auto c=take();if(separator(c)) continue;
        if(c=='\\') { op(take(),sink);continue; }
        if(!box_) {
            if(c!='0' && c!='1') continue;
            side_=static_cast<std::int16_t>(c-'0');cursor_={static_cast<std::int16_t>(side_ ? 48 : 160),static_cast<std::int16_t>(side_ ? 192 : 320)};
            box_=true;emit(sink,{Kind::box,cursor_.x,cursor_.y,side_});continue;
        }
        const auto glyph=(unsigned(c)<<8)|take();emit(sink,{Kind::text,cursor_.x,cursor_.y,static_cast<int>(glyph),0xe1});
        cursor_.x=motion::wrap(int(cursor_.x)+16);
        // speedup_cycle is initialized to zero and never incremented by TH04.
        // Any held input removes text delays; it does not dismiss a wait.
        if(!held) delay(2,sink);
    }
}

Font::Font(const Bytes& bitmap):bytes_(bitmap) {
    if(bytes_.empty()) return;
    const auto word=[&](unsigned at) { return unsigned(bytes_.at(at))|(unsigned(bytes_.at(at+1))<<8); };
    const auto dword=[&](unsigned at) { return word(at)|(word(at+2)<<16); };
    if(bytes_.size()<62 || word(0)!=0x4d42 || dword(14)!=40 || dword(18)!=2048 || dword(22)!=2048 || word(26)!=1 || word(28)!=1 || dword(30)!=0)
        throw std::invalid_argument("PC-98 font requires a 2048x2048 uncompressed monochrome BMP");
    offset_=dword(10);if(offset_>bytes_.size() || bytes_.size()-offset_<524288) throw std::invalid_argument("truncated PC-98 font bitmap");
}
bool Font::pixel(std::uint16_t sjis,unsigned x,unsigned y) const {
    if(bytes_.empty() || x>=16 || y>=16) return false;
    const unsigned lead=sjis>>8,trail=sjis&255;
    if(!((lead>=0x81 && lead<=0x9f) || (lead>=0xe0 && lead<=0xef)) || trail<0x40 || trail==0x7f || trail>0xfc) return false;
    unsigned row=(lead-(lead<0xa0 ? 0x81 : 0xc1))*2+0x21;
    const unsigned cell=trail>=0x9f ? (++row,trail-0x7e) : trail-(trail>0x7e ? 0x20 : 0x1f);
    // Anex86 rows are JIS cell, columns are the PC-98 row minus20h.
    const unsigned px=(row-0x20)*16+x,py=cell*16+y;
    const auto byte=bytes_[offset_+(2047-py)*256+px/8];
    return (byte&(0x80u>>(px&7)))==0; // Font BMP uses white for blank pixels.
}
} // namespace th04::portable::dialog
