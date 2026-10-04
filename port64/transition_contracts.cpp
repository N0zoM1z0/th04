#include "stage_transition.hpp"
#include "score.hpp"
#include <iomanip>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
using namespace th04::portable;
namespace {
void overlay(transition::Overlay& s) {
    const auto events=transition::update_overlay(s);
    std::cout<<"O "<<+s.time<<' '<<int(s.callback);
    for(const auto& e:events) std::cout<<'|'<<int(e.kind)<<' '<<e.left<<' '<<e.row<<' '<<e.value<<' '<<e.attribute;
    std::cout<<'\n';
}
void departure(transition::Departure& d,transition::Overlay& o,bool suspend) {
    std::vector<transition::Event> events;
    transition::update_departure(d,o,suspend,[&](const auto& e){events.push_back(e);});
    std::cout<<"D "<<d.frame<<' '<<d.graze<<' '<<d.stage_graze<<' '<<+d.stage<<' '<<+d.stage_ascii<<' '<<+d.quit<<' '<<d.palette_tone<<' '<<+d.palette_changed<<' '<<d.homing.x<<' '<<d.homing.y<<' '<<d.blocked<<' '<<+o.time<<' '<<int(o.callback);
    for(const auto& e:events) std::cout<<'|'<<int(e.kind)<<' '<<e.value;
    std::cout<<'\n';
}

void joint(transition::Departure& d,transition::Overlay& o,score::Snapshot& s) {
    departure(d,o,false);overlay(o);
    const auto events=score::update(s);
    std::cout<<"S "<<s.delta<<' '<<s.frame_delta;
    for(auto n:{s.hiscore_popup_shown,s.unused,s.extends,s.lives,s.bullet_clear,s.performance,s.minimum,s.maximum,s.popup_id}) std::cout<<' '<<+n;
    std::cout<<' '<<s.popup_callback;
    for(const auto* p:{&s.digits,&s.hiscore,&s.temporary,&s.hud}) for(auto n:*p) std::cout<<' '<<+n;
    for(const auto& e:events) {
        std::cout<<'|'<<int(e.kind)<<' '<<e.left<<' '<<e.row<<' '<<e.value<<' ';
        if(e.bytes.empty()) std::cout<<'-';
        else { std::cout<<std::hex<<std::setfill('0');for(unsigned char b:e.bytes) std::cout<<std::setw(2)<<unsigned(b);std::cout<<std::dec; }
    }
    std::cout<<'\n';
}

}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--final-vectors") {
            std::ifstream file(argv[2]);if(!file)throw std::runtime_error("cannot read final-stage vectors");
            int frame,x,y;unsigned graze,stage_graze,tone,changed;
            while(file>>frame>>graze>>stage_graze>>tone>>changed>>x>>y) {
                transition::Departure d;d.frame=motion::wrap(frame);d.graze=graze;d.stage_graze=stage_graze;
                d.palette_tone=motion::wrap(tone);d.palette_changed=changed;d.homing={motion::wrap(x),motion::wrap(y)};
                std::vector<transition::Event> events;
                const bool ending=transition::update_final_departure(d,[&](const auto& e){events.push_back(e);});
                std::cout<<"F "<<d.frame<<' '<<d.graze<<' '<<d.stage_graze<<' '<<d.palette_tone<<' '<<+d.palette_changed<<' '<<d.homing.x<<' '<<d.homing.y<<' '<<ending;
                for(const auto& e:events)std::cout<<'|'<<int(e.kind)<<' '<<e.value;
                std::cout<<'\n';
            }
            if(!file.eof())throw std::runtime_error("invalid final-stage vector");
            return 0;
        }
        if(argc==3 && std::string(argv[1])=="--vectors") {
            std::ifstream file(argv[2]);if(!file) throw std::runtime_error("cannot read transition vectors");
            std::string line;transition::Overlay o;transition::Departure d;score::Snapshot score;
            while(std::getline(file,line)) {
                std::istringstream in(line);char op;in>>op;
                if(op=='J') { unsigned pending;in>>pending;d={};o={72,transition::Callback::none};score={};score.delta=pending;joint(d,o,score); }
                else if(op=='K') joint(d,o,score);
                else if(op=='O') { unsigned time,mode;in>>time>>mode;o.time=time;o.callback=static_cast<transition::Callback>(mode);overlay(o); }
                else if(op=='R') overlay(o);
                else if(op=='D' || op=='P') {
                    int frame;unsigned graze,stage_graze,stage,ascii,quit,tone,changed,time,mode;int x,y;
                    in>>frame>>graze>>stage_graze>>stage>>ascii>>quit>>tone>>changed>>x>>y>>time>>mode;
                    d={};d.frame=frame;d.graze=graze;d.stage_graze=stage_graze;d.stage=stage;d.stage_ascii=ascii;d.quit=quit;d.palette_tone=tone;d.palette_changed=changed;d.homing={static_cast<std::int16_t>(x),static_cast<std::int16_t>(y)};o.time=time;o.callback=static_cast<transition::Callback>(mode);departure(d,o,op=='P');
                } else if(op=='B') departure(d,o,true);
                else if(op=='C' || op=='N') departure(d,o,false);
                else throw std::runtime_error("unknown transition vector");
                if(!in) throw std::runtime_error("truncated transition vector");
            }
            return 0;
        }
        transition::Overlay o;for(unsigned i=0;i<73;++i) transition::update_overlay(o);
        if(o.time!=72 || o.callback!=transition::Callback::titles) throw std::runtime_error("enter union-byte lifetime lost");
        transition::Departure d;d.graze=65535;d.stage_graze=2;
        transition::update_departure(d,o,true);
        if(!d.blocked || d.frame || d.graze!=1) throw std::runtime_error("dialog did not suspend after wrapped graze publication");
        for(unsigned i=0;i<10;++i) transition::update_departure(d,o,true);
        if(d.frame || d.graze!=1) throw std::runtime_error("blocked frame replayed its prefix");
        transition::update_departure(d,o,false);
        if(d.frame!=1 || d.blocked || d.graze!=1) throw std::runtime_error("dialog continuation replayed entry");
        transition::Departure final;final.graze=65535;final.stage_graze=2;final.homing={123,-456};
        unsigned clears=0,endings=0;
        const auto sink=[&](const transition::Event& e) {
            if(e.kind==transition::Kind::all_clear)++clears;
            else if(e.kind==transition::Kind::end_game)++endings;
            else if(e.kind!=transition::Kind::tone)throw std::runtime_error("Final Stage requested dialogue/fade/next stage");
        };
        for(unsigned frame=0;frame<416;++frame)
            if(transition::update_final_departure(final,sink))throw std::runtime_error("Final Stage ended before416");
        if(!transition::update_final_departure(final,sink) || final.frame!=416 || final.graze!=1 || clears!=1 || endings!=1 || final.palette_tone!=60)
            throw std::runtime_error("Final Stage repeated all-clear or advanced the nonreturning Ending call");
        std::cout<<"stage_transition=SHARED_BYTE_72 departure=DIALOG_416_488 pending_score=CARRIES pointer_bits=64\n";
        return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
