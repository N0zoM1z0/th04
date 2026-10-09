#include "sound_scenes.hpp"
#include <algorithm>
#include <iostream>
#include <stdexcept>
using namespace th04::portable;
namespace {
void require(bool value,const char* reason) {if(!value)throw std::runtime_error(reason);}
}
int main() {try {
    unsigned reads=0;std::vector<sound::SceneEvent> events;
    std::vector<std::pair<application::Program,std::uint32_t>> samples;
    sound::Timeline timeline([&](const std::string& name)->std::optional<sound::Bytes> {
        require(name=="miko.efs","unexpected effect file");++reads;
        return sound::Bytes{'4','4','0',' ','0',' '};
    },[&](const auto& e){events.push_back(e);},
      [&](auto program,auto generation,const auto&){samples.emplace_back(program,generation);});
    menu::Options options;options.se_mode=2;
    timeline.enter(application::Program::op,1,options);timeline.op_title(false);
    require(reads==1 && timeline.runtime()->beeper().count==1 &&
        timeline.runtime()->control().se==2 && timeline.runtime()->control().bgm==0,
        "OP effects and absent resident music");
    options.se_mode=0;
    require(timeline.runtime()->control().se==2,"SE option remains deferred");
    timeline.op_restart(options);
    require(reads==1 && timeline.runtime()->control().se==0 &&
        timeline.runtime()->beeper().count==1,"BGM restart determines modes without EFS reload");
    options.se_mode=2;
    timeline.enter(application::Program::main,2,options);
    auto main=timeline.runtime();
    {sound::Refresh refresh(main.get(),17730496);
        timeline.handle({sound::ActionKind::reset});
        timeline.handle({sound::ActionKind::play,1});
        timeline.handle({sound::ActionKind::immediate_update});
        require(main->samples()==0 && main->beeper().active==1,
            "forced cutscene SE must not consume the refresh wait");
        timeline.enter(application::Program::maine,3,options);
        require(timeline.runtime()!=main && timeline.runtime()->beeper().count==0 &&
            reads==2,"fresh MAINE must not borrow MAIN effects");
    }
    require(main->samples()==851 && samples.back()==std::make_pair(application::Program::main,2u),
        "retained refresh must publish under its original generation");
    timeline.handle({sound::ActionKind::force,1});
    require(timeline.runtime()->beeper().active==0,"empty MAINE EFS must not invent an effect");
    registration::Event song{registration::Kind::song};song.a=0x600;song.text="name";
    timeline.registration(song);
    registration::Event stop{registration::Kind::sound};stop.a=0x100;timeline.registration(stop);
    require(timeline.runtime()->control().filename[0]=='n',"registration song routing");
    cutscene::Event measure{cutscene::Kind::measure,3,64};timeline.cutscene(measure);
    require(events.back().kind==sound::SceneKind::measure && events.back().goal==3 &&
        events.back().fallback==64 && timeline.runtime()->control().bgm==0,
        "measure request records an absent driver without fabricating progress");
    timeline.enter(application::Program::op,4,options);timeline.op_title(true);
    require(reads==3 && timeline.runtime()->beeper().count==1 &&
        events.back().action.kind==sound::ActionKind::load && events.back().action.value==0xb00,
        "demo-return OP must not restart title music");
    timeline.leave();require(!timeline.runtime(),"process exit releases local sound");
    std::cout<<"Sound process lifetimes, forced SE wait ordering and absent measures PASS\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
