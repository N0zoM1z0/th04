#include "stage_transition.hpp"

namespace th04::portable::transition {
std::vector<Text> update_overlay(Overlay& s) {
    std::vector<Text> out;
    const auto fill=[&](unsigned attribute) {
        for(unsigned row=1;row<24;++row) for(unsigned left=4;left<52;++left)
            out.push_back({TextKind::character,left,row,32,attribute});
    };
    const auto fade=[&] {
        if(s.time%8 || !s.time) return;
        // Keep byte conversion: injected times above72 select wrapped gaiji.
        const auto glyph=static_cast<std::uint8_t>(64-s.time/8);
        for(unsigned row=1;row<24;++row) for(unsigned left=4;left<52;left+=2)
            out.push_back({TextKind::gaiji,left,row,glyph,1});
    };
    if(s.callback==Callback::enter) {
        if(s.time>=72) { fill(0xe1);s.callback=Callback::titles; }
        else { fade();++s.time; }
    } else if(s.callback==Callback::leave) {
        if(!s.time) { fill(5);s.callback=Callback::none; }
        else { --s.time;fade(); }
    }
    return out;
}
void update_departure(Departure& s,Overlay& overlay,bool suspend_dialog,const Sink& sink) {
    const auto emit=[&](Kind kind,unsigned value=0) { if(sink) sink({kind,value}); };
    if(s.blocked) {
        if(suspend_dialog) return;
        // The already entered frame resumes at stage_clear_bonus(), AFTER
        // the blocking dialog. Pending score is never forcibly committed.
        s.blocked=false;emit(Kind::bonus);
    } else {
        s.palette_tone=60;s.palette_changed=1;emit(Kind::tone,60);
        if(s.frame==0) {
            s.graze=static_cast<std::uint16_t>(s.graze+s.stage_graze);
            emit(Kind::dialog);
            if(suspend_dialog) { s.blocked=true;return; }
            emit(Kind::bonus);
        } else if(s.frame==416) {
            overlay.callback=Callback::leave;emit(Kind::fade,10);
        } else if(s.frame==488) {
            ++s.stage;++s.stage_ascii;s.quit=2;
            emit(Kind::next_stage);emit(Kind::delay,1);
        }
    }
    s.frame=motion::wrap(int(s.frame)+1);s.homing={-15984,-15984};
}
bool update_final_departure(Departure& s,const Sink& sink) {
    const auto emit=[&](Kind kind,unsigned value=0) { if(sink) sink({kind,value}); };
    s.palette_tone=60;s.palette_changed=1;emit(Kind::tone,60);
    if(s.frame==0) {
        s.graze=static_cast<std::uint16_t>(s.graze+s.stage_graze);
        emit(Kind::all_clear);
    } else if(s.frame==416) {
        emit(Kind::end_game);return true;
    }
    s.frame=motion::wrap(int(s.frame)+1);s.homing={-15984,-15984};return false;
}
} // namespace th04::portable::transition
