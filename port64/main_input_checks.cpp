#include "main_state.hpp"
#include <iostream>
#include <stdexcept>
#include <string>

namespace input=th04::portable::pc98_input;
namespace app=th04::portable::application;
namespace main_game=th04::portable::gameplay;
namespace {
void require(bool yes,const char* reason) {
    if(!yes)throw std::runtime_error(reason);
}
struct Game {
    app::State application;
    main_game::State state;
    static app::State started() {
        app::State application;
        application.start_normal(app::Playchar::reimu,app::ShotType::a);
        return application;
    }
    Game():application(started()),state(application) {}
};
void contracts() {
    const unsigned groups[]={8,8,9,9};
    const unsigned masks[]={4,16,4,16};
    const unsigned actions[]={0x100,0x200,0x400,0x800};
    const int vx[]={-48,48,-48,48},vy[]={-48,-48,48,48};
    for(unsigned i=0;i<4;++i) {
        input::Latch latch;input::Sample sample;sample.keys[groups[i]]=std::uint8_t(masks[i]);
        latch.reset_sense(sample);Game game;game.state.update(latch.snapshot());
        const auto& position=game.state.player().position();
        require(game.state.consumed_input()==actions[i] && game.state.player_input()==actions[i],
                "sampled keypad action was translated as a host key");
        require(position.velocity.x==vx[i] && position.velocity.y==vy[i],"sampled keypad movement");
    }
    input::Latch latch;input::Sample enter;enter.keys[3]=16;
    latch.reset_sense(enter);latch.sense({});const auto sampled=latch.snapshot();
    input::Sample shot;shot.keys[5]=2;latch.reset_sense(shot);
    Game game;game.state.update(sampled);
    require(game.state.player_input()==0x2000 && game.state.consumed_input()==0x2000,
            "MAIN must consume the value sampled before later BIOS/latch changes");
    Game bomb;input::Sample bomb_key;bomb_key.keys[5]=4;latch.reset_sense(bomb_key);
    bomb.state.update(latch.snapshot());
    require(bomb.state.player_input()==0x10 && bomb.state.life().bombing && bomb.state.score().remaining_bombs==1,
            "sampled BOMB bit must reach the real lifecycle");
    input::Sample shift;shift.keys[8]=4;shift.shift=true;latch.reset_sense(shift);
    Game shifted;shifted.state.update(latch.snapshot());
    require(shifted.state.player().position().velocity.x==-24 && shifted.state.player().position().velocity.y==-24,
            "sampled Shift must reach player movement");
    input::Sample all;all.keys.fill(255);latch.reset_sense(all);
    Game complete;complete.state.update(latch.snapshot());
    require(complete.state.consumed_input()==0x7f3f && complete.state.player_input()==0x7f3f,
            "MAIN must retain the complete sampled action word");
    for(auto host:{0x800u,0x1000u,0x2000u}) {
        Game adapter;adapter.state.update(std::uint16_t(host),false);
        const auto expected=host==0x800 ? 0x10u : host==0x1000 ? 0x2000u : 0x1000u;
        require(adapter.state.player_input()==expected,"existing host adapter domain");
    }
    app::State demo_app;demo_app.start_next_demo();main_game::State demo(demo_app);
    demo.set_demo_replay(std::vector<std::uint8_t>(8000));
    input::Sample q;q.keys[2]=1;latch.reset_sense(q);demo.update(latch.snapshot());
    require(demo.demo_exit_requested() && demo.frames()==0,"sampled Q must exit the demo before player update");
}
void movement_samples(bool live_bytes=false) {
    char operation;std::string bios;unsigned shift,enabled,pins;input::Latch latch;
    while(std::cin>>operation>>bios>>shift>>enabled>>pins) {
        if((operation!='R' && operation!='S') || bios.size()!=20 || shift>1 || enabled>1 || pins>255)
            throw std::invalid_argument("invalid sampled movement record");
        input::Sample sample;sample.shift=shift!=0;sample.joystick_enabled=enabled!=0;sample.joystick_pins=std::uint8_t(pins);
        for(unsigned i=0;i<10;++i)sample.keys[i]=std::uint8_t(std::stoul(bios.substr(2*i,2),nullptr,16));
        if(live_bytes) {
            input::ByteSource source{{},[&](unsigned group){return sample.keys.at(group);},
                [&]{return sample.shift;},[&]{return sample.joystick_enabled;},[&]{return sample.joystick_pins;}};
            latch.poll(operation=='R'?input::Operation::reset:input::Operation::sense,source);
        } else if(operation=='R')latch.reset_sense(sample);else latch.sense(sample);
        Game game;game.state.update(latch.snapshot());const auto& position=game.state.player().position();
        std::cout<<latch.actions()<<' '<<game.state.consumed_input()<<' '<<game.state.player_input()<<' '
                 <<position.current.x<<' '<<position.current.y<<' '<<position.velocity.x<<' '<<position.velocity.y<<'\n';
    }
    if(!std::cin.eof())throw std::invalid_argument("truncated sampled movement record");
}
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--movement-samples")movement_samples();
        else if(argc==2 && std::string(argv[1])=="--byte-movement-samples")movement_samples(true);
        else {contracts();std::cout<<"MAIN sampled input contracts pass\n";}
        return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
