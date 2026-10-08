#include "gameover.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::gameover {
namespace {
void emit(const Sink& sink,Kind kind,int x=0,int y=0,int value=0,int attr=0,std::string text={}) {
    if(sink)sink({kind,x,y,value,attr,std::move(text)});
}
void glyphs(const Sink& sink,int x,int y,const char* text,int attr) {emit(sink,Kind::gaiji,x,y,0,attr,text);}
void fade_cells(std::uint8_t frame,const Sink& sink) {
    if(frame%4 || !frame)return;
    for(int y=1;y<24;++y)for(int x=4;x<52;x+=2)
        emit(sink,Kind::gaiji,x,y,64-frame/4,1);
}
}
bool fade_in(std::uint8_t& frame,const Sink& sink) {
    if(frame>=36) {emit(sink,Kind::wipe);return true;}
    fade_cells(frame,sink);++frame;return false;
}
bool fade_out(std::uint8_t& frame,const Sink& sink) {
    if(!frame) {emit(sink,Kind::black);return true;}
    --frame;fade_cells(frame,sink);return false;
}
Menu::Menu(Context& c,std::uint16_t initial):context_(&c),previous_sample_(initial) {
    const auto credits=std::uint8_t(3-c.scoreboard.digits[0]);
    if(c.stage==6 || !credits) {choice_=Choice::quit;return;}
    glyphs(c.sink,19,10,"\xac\xb8\xb7\xbd\xb2\xb7\xbe\xae\x08",0xe1);
    glyphs(c.sink,24,13,"\xc2\xae\xbc",0x85);
    glyphs(c.sink,25,15,"\xb7\xb8",0xe1);
    glyphs(c.sink,19,22,"\xac\xbb\xae\xad\xb2\xbd",0x81);
    emit(c.sink,Kind::gaiji,33,22,0xa0+credits,0x81);
}
void Menu::advance(std::uint16_t held) {
    if(choice_!=Choice::pending)return;
    auto& c=*context_;const auto keys=std::uint16_t(previous_sample_|held);previous_sample_=held;
    bool confirmed=false;
    if(!previous_input_) {
        previous_input_=keys;
        if(keys&3u) {
            selected_=1-selected_;
            glyphs(c.sink,24,13,"\xc2\xae\xbc",selected_ ? 0xe1 : 0x85);
            glyphs(c.sink,25,15,"\xb7\xb8",selected_ ? 0x85 : 0xe1);
        }
        if(keys&0x1000u) {selected_=1;confirmed=true;}
        else if(keys&(0x2000u|0x20u))confirmed=true;
    } else previous_input_=keys;
    if(!confirmed) {emit(c.sink,Kind::delay,0,0,1);++ticks_;return;}
    if(selected_) {choice_=Choice::quit;return;}
    emit(c.sink,Kind::continue_score);
    if(!c.save_continue)throw std::logic_error("Continue requires score persistence consumer");
    c.save_continue();
    c.resources.power=1;c.resources.dream_items_collected=0;
    c.resources.remaining_bombs=c.credit_bombs;c.resources.remaining_lives=c.credit_lives;
    emit(c.sink,Kind::shot_level);emit(c.sink,Kind::hud_lives);emit(c.sink,Kind::hud_bombs);
    ++c.scoreboard.digits[0];
    std::fill(c.scoreboard.digits.begin()+1,c.scoreboard.digits.end(),0);
    c.scoreboard.delta=c.scoreboard.frame_delta=0;
    c.resources.score_delta=0;
    c.scoreboard.unused=c.scoreboard.extends=c.scoreboard.hiscore_popup_shown=0;
    emit(c.sink,Kind::hud_score);choice_=Choice::continue_run;
}
Scene::Scene(Context& c,std::uint16_t held):context_(&c),previous_sample_(held) {
    if(c.stage==5) {emit(c.sink,Kind::bad_ending);phase_=Phase::bad_ending;return;}
    pump(held);
}
void Scene::pump(std::uint16_t held) {
    auto& c=*context_;
    for(;;) {
        switch(phase_) {
        case Phase::initial_out:case Phase::final_out:
            if(!fade_out(frame_,c.sink)) {delay_=1;emit(c.sink,Kind::delay,0,0,1);return;}
            if(phase_==Phase::initial_out) {tone_=50;emit(c.sink,Kind::tone,0,0,50);phase_=Phase::initial_in;}
            else if(continued_) {tone_=100;emit(c.sink,Kind::tone,0,0,100);phase_=Phase::final_in;}
            else {
                emit(c.sink,Kind::score_sequence);
                emit(c.sink,Kind::song_fade,0,0,4);emit(c.sink,Kind::palette_fade,0,0,4);
                phase_=Phase::blackout;tone_=100;fade_left_=1;return;
            }
            break;
        case Phase::initial_in:case Phase::final_in:
            if(!fade_in(frame_,c.sink)) {delay_=1;emit(c.sink,Kind::delay,0,0,1);return;}
            if(phase_==Phase::final_in) {emit(c.sink,Kind::wipe);phase_=Phase::continue_run;return;}
            phase_=Phase::slide_in;slide_=50;break;
        case Phase::slide_in:case Phase::slide_out:
            if(slide_erase_) {
                emit(c.sink,Kind::ank,slide_,12,0,0xe1,"  ");slide_erase_=false;
                slide_+=phase_==Phase::slide_in ? -2 : 2;
            }
            if(phase_==Phase::slide_in && slide_<=8) {phase_=Phase::slide_out;slide_=8;break;}
            if(phase_==Phase::slide_out && slide_>=20) {
                glyphs(c.sink,20,12,"\xb0\xaa\xb6\xae\xb8\xbf\xae\xbb",0xe1);
                emit(c.sink,Kind::wait);emit(c.sink,Kind::delay,0,0,1);
                phase_=Phase::release;previous_sample_=held;return;
            }
            emit(c.sink,Kind::gaiji,slide_,12,0xb0,0xe1);
            emit(c.sink,Kind::delay,0,0,1);delay_=1;slide_erase_=true;return;
        case Phase::menu:
            if(menu_->choice()==Choice::pending) {
                menu_->advance(held);
                if(menu_->choice()==Choice::pending) {delay_=1;return;}
            }
            continued_=menu_->choice()==Choice::continue_run;
            frame_=32;phase_=Phase::final_out;break;
        default:return;
        }
    }
}
void Scene::advance(std::uint16_t held) {
    if(finished())return;
    ++ticks_;
    if(phase_==Phase::blackout) {
        if(--fade_left_)return;
        if(!blackout_started_) {
            blackout_started_=true;emit(context_->sink,Kind::tone,0,0,tone_);fade_left_=4;return;
        }
        tone_-=6;
        if(tone_>0) {emit(context_->sink,Kind::tone,0,0,tone_);fade_left_=4;return;}
        tone_=0;emit(context_->sink,Kind::tone);emit(context_->sink,Kind::maine);phase_=Phase::maine;return;
    }
    if(phase_==Phase::release || phase_==Phase::press) {
        const auto keys=std::uint16_t(previous_sample_|held);previous_sample_=held;
        if(phase_==Phase::release) {
            if(!keys)phase_=Phase::press;
            emit(context_->sink,Kind::delay,0,0,1);return;
        }
        if(!keys) {emit(context_->sink,Kind::delay,0,0,1);return;}
        emit(context_->sink,Kind::wipe);
        menu_=std::make_unique<Menu>(*context_,held);phase_=Phase::menu;pump(held);return;
    }
    if(delay_ && --delay_)return;
    pump(held);
}
} // namespace th04::portable::gameover
