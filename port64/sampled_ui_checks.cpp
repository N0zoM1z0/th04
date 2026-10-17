#include "dialog.hpp"
#include "main_pause.hpp"
#include "gameover.hpp"
#include "host_window.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
namespace p=th04::portable::pc98_input;
namespace d=th04::portable::dialog;
namespace pause_ui=th04::portable::pause;
namespace go=th04::portable::gameover;
namespace hw=th04::portable::host_window;
namespace {
void require(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
p::Sample enter(){p::Sample sample;sample.keys[3]=16;return sample;}
p::Sample shot(){p::Sample sample;sample.keys[5]=2;return sample;}
p::Sample cancel(){p::Sample sample;sample.keys[0]=1;return sample;}
struct Sequence {
    std::vector<std::pair<p::Operation,p::Sample>> samples;
    std::size_t at=0;p::Latch latch;p::Snapshot last_sense;
    p::Snapshot poll(p::Operation op) {
        require(at<samples.size() && samples[at].first==op,"UI sampled operation order");
        const auto sample=samples[at++].second;
        if(op==p::Operation::reset)latch.reset_sense(sample);else latch.sense(sample);
        if(op==p::Operation::sense)last_sense=latch.snapshot();
        return latch.snapshot();
    }
};
void contracts(){
    const auto R=p::Operation::reset,S=p::Operation::sense;
    const std::string bytes="0\x82\xa0\\$\\#";
    d::Script script(d::Bytes(bytes.begin(),bytes.end()));script.begin();
    Sequence sequence{{{R,{}},{R,{}},{R,enter()},{S,{}},{R,{}},{S,{}},{R,{}},{S,enter()}}};
    const p::Poll poll=[&](p::Operation op){return sequence.poll(op);};
    for(unsigned tick=0;tick<6;++tick){
        script.advance_sampled(poll,{});
        if(tick==3)require(script.status()==d::Status::release && sequence.last_sense.actions==0x2000,
                           "pre-wait Enter must survive its release before the post-wait sense");
    }
    require(script.status()==d::Status::stopped && sequence.at==sequence.samples.size() && sequence.latch.actions()==0x2000,
            "sampled dialog completion retains its actual input latch");
    th04::portable::vsync::RasterClock clock;clock.counter().start();
    pause_ui::Scene pause(clock,0x1000);
    Sequence pause_samples{{{R,{}},{R,{}},{S,{}},{R,{}},{S,shot()},{R,{}}}};
    pause.advance_elapsed_sampled(100*hw::period_ns,[&](p::Operation op){return pause_samples.poll(op);});
    require(pause.result()==pause_ui::Result::resume && pause_samples.at==6 && !pause_samples.latch.actions(),
            "pause shares paired samples and its final release with MAIN");
    th04::portable::item::ScoreState resources;th04::portable::score::Snapshot score;
    go::Context context{resources,score};Sequence menu_samples{{{R,{}},{S,{}},{R,{}},{S,cancel()}}};
    const p::Poll menu_poll=[&](p::Operation op){return menu_samples.poll(op);};
    go::Menu menu(context,menu_poll);menu.advance_sampled(menu_poll);menu.advance_sampled(menu_poll);
    require(menu.choice()==go::Choice::quit && menu_samples.at==4 && menu_samples.latch.actions()==0x1000,
            "Game Over menu owns reset before wait and accumulating head sense");
    th04::portable::vsync::RasterClock game_clock;game_clock.counter().start();go::Scene scene(context,0,&game_clock);
    Sequence scene_samples{{{R,{}},{S,{}},{R,{}},{S,shot()},{R,{}},{S,{}},{R,{}},{S,cancel()}}};
    scene.advance_elapsed_sampled(1000*hw::period_ns,[&](p::Operation op){return scene_samples.poll(op);});
    require(scene.finished() && scene.phase()==go::Phase::maine && scene_samples.at==8 && scene_samples.latch.actions()==0x1000,
            "Game Over wait and menu use one shared input latch");
    hw::Keys keys;keys.down_right=true;keys.space=true;keys.shift=true;
    const auto sample=hw::bios_input(keys,true);require(p::keyboard_actions(sample.keys)==0x820 && sample.shift,"host keypad and Space BIOS adapter");
    require(!p::keyboard_actions(hw::bios_input(keys,false).keys) && !hw::bios_input(keys,false).shift,"unfocused BIOS adapter");
}
void trace(const char* script_path,const char* input_path){
    std::ifstream source(script_path,std::ios::binary),input(input_path);require(bool(source)&&bool(input),"sampled dialog fixture missing");
    d::Script script(d::Bytes(std::istreambuf_iterator<char>(source),{}));p::Latch latch;unsigned calls=0;
    const p::Poll poll=[&](p::Operation operation){
        char op;std::string bios;unsigned shift,enabled,pins;
        require(bool(input>>op>>bios>>shift>>enabled>>pins) && bios.size()==20 && shift<=1 && enabled<=1 && pins<=255,"sampled dialog input record");
        require(op==(operation==p::Operation::reset ? 'R' : 'S'),"sampled dialog differs from observed poll order");
        p::Sample sample;sample.shift=shift!=0;sample.joystick_enabled=enabled!=0;sample.joystick_pins=std::uint8_t(pins);
        for(unsigned i=0;i<10;++i)sample.keys[i]=std::uint8_t(std::stoul(bios.substr(i*2,2),nullptr,16));
        if(operation==p::Operation::reset)latch.reset_sense(sample);else latch.sense(sample);
        std::cout<<"P "<<calls++<<' '<<op<<' '<<latch.actions()<<' '<<latch.shift()<<'\n';
        return latch.snapshot();
    };
    for(unsigned scene=0;scene<2;++scene){
        script.begin();unsigned ticks=0;
        while(script.status()!=d::Status::stopped && ++ticks<20000)script.advance_sampled(poll,{});
        require(script.status()==d::Status::stopped,"sampled dialog did not complete");
        std::cout<<"END "<<scene<<' '<<calls<<' '<<ticks<<' '<<script.offset()<<'\n';
    }
    input>>std::ws;require(input.eof(),"unconsumed actual dialog samples");
}
}
int main(int argc,char** argv){
    try{if(argc==4 && std::string(argv[1])=="--dialog-samples")trace(argv[2],argv[3]);else{contracts();std::cout<<"Sampled UI contracts pass\n";}return 0;}
    catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
