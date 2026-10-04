#include "cutscene.hpp"
#include "motion.hpp"
#include <algorithm>
#include <stdexcept>
#include <utility>

namespace th04::portable::cutscene {
namespace {
bool separator(unsigned c) { return c<=32 || c==127; }
bool digit(unsigned c) { return c>='0' && c<='9'; }
unsigned lower(unsigned c) { return c>='A' && c<='Z' ? c+32 : c; }
}

Script::Script(Bytes bytes):bytes_(std::move(bytes)) {
    if(bytes_.size()>8192) throw std::invalid_argument("MAINE script exceeds its 8192-byte buffer");
}
unsigned Script::peek() const { return at_<bytes_.size() ? bytes_[at_] : 0; }
unsigned Script::take() {
    if(at_>=bytes_.size()) throw std::invalid_argument("MAINE script ended without its stop command");
    return bytes_[at_++];
}
int Script::number(int fallback) { default_=motion::wrap(fallback);return number(); }
int Script::number() {
    // Original reads three bytes, then rewinds unused bytes. A native bounded
    // read consumes the same one/two/three digits and retains the shared default.
    int n=0;unsigned count=0;
    while(count<3 && digit(peek())) { n=n*10+int(take())-'0';++count; }
    return count ? n : default_;
}
int Script::second() { if(peek()==',') { take();return number(); }return default_; }
std::string Script::filename() {
    std::string result;
    while(result.size()<12) { const auto c=take();if(separator(c)) break;result.push_back(static_cast<char>(c)); }
    return result;
}
void Script::begin() {
    if(status_!=Status::idle) throw std::logic_error("MAINE script already started");
    x_=80;y_=320;interval_=1;color_=15;weight_=2;fast_forward_=false;
    // TH04 snapshots the initially black box too. '@' later clears the pages
    // but deliberately keeps this saved background until a 'p='/'p@' replaces it.
    queue({Kind::snap});status_=Status::running;
}
void Script::box_animate() {
    queue({Kind::egc_begin});
    if(!fast_forward_) for(int mask=0;mask<4;++mask) {
        queue({Kind::box_mask,mask});queue({Kind::delay,interval_});
    }
    queue({Kind::box_mask,4});queue({Kind::egc_end});
}
void Script::box_restore() {
    queue({Kind::access,1});queue({Kind::restore});
    queue({Kind::access,0});queue({Kind::restore});
}
void Script::cursor_advance() {
    x_=motion::wrap(int(x_)+16);
    if(x_<560) return;
    y_=motion::wrap(int(y_)+16);x_=144;
    if(y_<384) return;
    box_animate();if(!fast_forward_) queue({Kind::wait,0});
    x_=80;y_=320;box_restore();
}
void Script::op(unsigned command) {
    switch(lower(command)) {
    case 'n':
        y_=motion::wrap(int(y_)+16);x_=80;
        if(y_<384) break;
        [[fallthrough]];
    case 's': {
        const bool minus=peek()=='-';box_animate();
        if(minus) take();
        else { const int frames=number(0);if(!fast_forward_) queue({Kind::wait,frames}); }
        x_=80;y_=320;box_restore();break;
    }
    case 'c':color_=static_cast<std::uint8_t>(number(15));break;
    case 'b':weight_=static_cast<std::uint16_t>(number(2));break;
    case 'v':
        if(peek()=='p') { take();queue({Kind::show,number(0)&255}); }
        else interval_=motion::wrap(number(1));
        break;
    case 't': {
        const int value=number(100);
        if(!fast_forward_) queue({Kind::delay,1});
        queue({Kind::tone,value});break;
    }
    case 'f':case 'w': {
        const auto c=command=='w' || command=='W' ? lower(peek()) : peek();
        if(c=='i' || c=='o') {
            take();queue({Kind::fade,lower(command)=='w' ? 1 : 0,c=='i' ? 1 : 0,number(1)});break;
        }
        if(lower(command)=='f') {
            if(c=='m') {
                take();const int speed=number(1);
                // Original adds the complete WORD to AX=0200h. 256 selects
                // a different KAJA function; preserve this overflow explicitly.
                queue({Kind::bgm_control,(0x200+speed)&65535});
            }
            break;
        }
        box_animate();default_=64;
        if(c!='m') {
            if(c=='k') take();
            const int frames=number();if(!fast_forward_) queue({Kind::delay,frames});
        } else {
            take();if(peek()=='k') take();
            const int measure=number(), frames=second();
            if(!fast_forward_) queue({Kind::measure,measure,frames});
        }
        break;
    }
    case 'g':
        if(peek()=='a') {
            take();const int glyph=number(0);
            queue({Kind::access,1});queue({Kind::gaiji,x_,y_,glyph,color_});cursor_advance();
        } else {
            const int duration=number(8);
            for(int i=0;i<=duration;++i) {
                queue({Kind::scroll,(i&1) ? 4 : 396});
                if(!fast_forward_) queue({Kind::delay,1});
            }
            queue({Kind::scroll,0});
        }
        break;
    case 'k': {
        // TH04 intentionally does not publish the text box here. A mid-box
        // wait remains invisible unless the script already showed page1.
        const int frames=number(0);if(!fast_forward_) queue({Kind::wait,frames});break;
    }
    case '@':
        queue({Kind::access,1});queue({Kind::clear});
        queue({Kind::access,0});queue({Kind::clear});break;
    case 'p': {
        const auto sub=take();
        if(sub=='=' || sub=='@') {
            queue({Kind::access,1});if(sub=='=') queue({Kind::pi_palette});
            queue({Kind::pi_put,0,0});queue({Kind::copy_page,0});
            queue({Kind::access,0});queue({Kind::snap});
        } else if(sub=='-') queue({Kind::pi_free});
        else if(sub=='p') queue({Kind::pi_palette});
        else if(sub==',') {
            Event event{Kind::pi_load};event.name=filename();
            queue({Kind::pi_free});queue(std::move(event));
        } else --at_;
        break;
    }
    case '=': {
        default_=4;
        if(peek()!='=') {
            const int quarter=number();
            queue({Kind::show,1});queue({Kind::access,0});
            if(quarter<4) queue({Kind::quarter,160,64,quarter});
            else queue({Kind::clear_rect,160,64,320,200});
        } else {
            take();const int quarter=number();default_=1;const int speed=second();
            for(int mask=0;mask<4;++mask) {
                queue({Kind::pic_mask,160,64,quarter,mask});
                if(!fast_forward_) queue({Kind::delay,speed});
            }
            queue({Kind::show,1});queue({Kind::access,0});
            queue({Kind::quarter,160,64,quarter});
        }
        queue({Kind::show,0});queue({Kind::pic_copy,160,64});break;
    }
    case 'm':
        if(peek()=='$' || peek()=='*') queue({Kind::bgm_control,take()=='$' ? 0x100 : 0});
        else if(peek()==',') {
            take();Event event{Kind::bgm_load,0x600};event.name=filename();
            queue({Kind::bgm_control,0x100});queue(std::move(event));queue({Kind::bgm_control,0});
        }
        break;
    case 'e':
        queue({Kind::se_begin});queue({Kind::se,number()});queue({Kind::se_end});break;
    case '$':
        queue({Kind::restore});queue({Kind::bg_free});ending_=true;break;
    default:break;
    }
}

void Script::complete_measure_wait() {
    if(status_!=Status::measure) throw std::logic_error("MAINE is not waiting for a song measure");
    status_=Status::running;
}
void Script::advance(std::uint16_t held,const Sink& sink) {
    if(status_==Status::idle || status_==Status::stopped || status_==Status::measure) return;
    if(status_==Status::release) {
        if(!held) status_=press_budget_<0 ? Status::running : Status::press;
        return;
    }
    if(status_==Status::press) {
        if(held || (press_budget_ && press_budget_!=9999 && ++press_elapsed_>=press_budget_)) status_=Status::running;
        return;
    }
    if(status_==Status::delay) {
        if(ticks_>0 && --ticks_>0) return;
        if(fade_step_) {
            do {
                tone_+=fade_step_;
                if((fade_step_>0 && tone_>=fade_end_) || (fade_step_<0 && tone_<=fade_end_)) {
                    tone_=fade_end_;fade_step_=0;break;
                }
            } while(!fade_speed_);
            if(fade_step_) { ticks_=fade_speed_;return; }
        }
        status_=Status::running;
    }
    while(status_==Status::running) {
        if(!requests_.empty()) {
            const auto event=std::move(requests_.front());requests_.pop_front();
            if(sink) sink(event);
            switch(event.kind) {
            case Kind::delay:
                ticks_=std::max(1,event.a);fade_step_=0;status_=Status::delay;return;
            case Kind::wait:
                press_budget_=event.a;press_elapsed_=0;status_=Status::release;return;
            case Kind::measure:status_=Status::measure;return;
            case Kind::tone:tone_=event.a;break;
            case Kind::fade:
                tone_=event.a ? (event.b ? 200 : 100) : (event.b ? 0 : 100);
                fade_end_=event.b ? 100 : (event.a ? 200 : 0);
                fade_step_=tone_<fade_end_ ? 6 : -6;fade_speed_=event.c;
                // One initial VSync, then a wait at each displayed six-tone
                // step. Even held Escape does not skip a palette fade.
                ticks_=1+fade_speed_;status_=Status::delay;return;
            default:break;
            }
            continue;
        }
        if(ending_) { status_=Status::stopped;return; }
        // Escape is sampled only at a new outer iteration. Releasing it while
        // a command is blocked cannot change that command's queued mask loop.
        fast_forward_=(held&input_cancel)!=0;
        const auto c=take();if(separator(c)) continue;
        if(c=='\\') { op(take());continue; }
        const auto glyph=(c<<8)|take();
        queue({Kind::show,0});queue({Kind::access,1});
        queue({Kind::text,x_,y_,static_cast<int>(glyph),color_,weight_});cursor_advance();
    }
}

std::string script_name(unsigned character,unsigned shot,bool bad) {
    if(character>1 || shot>1) throw std::invalid_argument("invalid MAINE character/shot route");
    std::string name="_ED000.TXT";
    name[3]=static_cast<char>('0'+character);name[4]=static_cast<char>('0'+shot);name[5]=bad ? '1' : '0';
    return name;
}
const char* kind_name(Kind kind) {
    static const char* names[]={"snap","restore","bg_free","show","access","clear","copy_page",
        "text","gaiji","egc_begin","box_mask","egc_end","pic_mask","pic_copy","pi_free","pi_load",
        "pi_palette","pi_put","quarter","clear_rect","delay","wait","measure","tone","fade","scroll",
        "bgm_control","bgm_load","se_begin","se","se_end"};
    return names[static_cast<unsigned>(kind)];
}
} // namespace th04::portable::cutscene
