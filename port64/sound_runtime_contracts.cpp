#include "sound_runtime.hpp"
#include "main_state.hpp"
#include <algorithm>
#include <iostream>
#include <stdexcept>
using namespace th04::portable;
void require(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
int main(){try {
    const sound::Beeper::Reader reader=[](const std::string& name)->std::optional<sound::Bytes>{
        if(name!="miko.efs")return std::nullopt;
        return sound::Bytes{'4','4','0',' ','0',' '};
    };
    std::vector<std::int16_t> a,b;
    sound::Runtime first(reader,{}, {},[&](const auto& values){a.insert(a.end(),values.begin(),values.end());});
    sound::Runtime second(reader,{}, {},[&](const auto& values){b.insert(b.end(),values.begin(),values.end());});
    for(auto* r:{&first,&second}) {
        r->configure(2,2);require(r->control().bgm==0 && r->control().se==2,"absent FM driver must not fabricate capability");
        r->handle({sound::ActionKind::load,0xb00,"miko"});r->handle({sound::ActionKind::force,1,{}});
    }
    first.advance(1000000000);for(unsigned n=0;n<1000;++n)second.advance(1000000);
    require(a==b && a.size()==48000 && first.beeper().phase==second.beeper().phase,"rational IRQ/PCM refresh partitions");
    require(std::any_of(a.begin(),a.end(),[](auto x){return x!=0;}),"muted backend lost offline PCM");
    sound::Runtime clock(reader);clock.configure(0,2);clock.handle({sound::ActionKind::load,0xb00,"miko"});
    clock.handle({sound::ActionKind::play,1,{}});
    {sound::Refresh refresh(&clock,17730496);require(clock.samples()==0,"refresh begins without advancing time");clock.handle({sound::ActionKind::update});require(clock.samples()==851 && clock.control().playing==255 && clock.beeper().active==1,"SE update follows the refresh wait");}
    {sound::Refresh refresh(&clock,17730496);require(clock.samples()==851,"blocking wait admission");}
    require(clock.samples()==1702 && clock.control().playing==255,"blocked owner advances IRQ without SE update");
    application::State app;app.start_normal(application::Playchar::reimu,application::ShotType::a);
    gameplay::State main(app);std::vector<sound::Action> actions;std::vector<unsigned> counters;
    main.set_sound_sink([&](const auto& e){actions.push_back(e);counters.push_back(main.frames());});
    require(main.add_item({192*16,323*16},item::Type::one_up),"one-up fixture");main.update(0,false);
    require(actions.size()==3 && actions[0].kind==sound::ActionKind::play && actions[0].value==7 &&
        actions[1].kind==sound::ActionKind::play && actions[1].value==11 && actions[2].kind==sound::ActionKind::update && counters[2]==0,
        "item collect/extend/pickup/SE update order");
    main.update(0,false);
    actions.clear();counters.clear();unsigned extends=0;
    for(unsigned frame=0;frame<900;++frame) {
        if(frame<120 && frame%2==0)for(unsigned n=0;n<32;++n)require(main.add_item({192*16,323*16},item::Type::point),"point fixture capacity");
        actions.clear();counters.clear();const auto before=main.frames();main.update(0,false);
        unsigned updates=0;bool updated=false;
        for(unsigned n=0;n<actions.size();++n) {
            if(actions[n].kind==sound::ActionKind::update){++updates;updated=true;require(counters[n]==before,"SE updated after MAIN counter");}
            if(actions[n].kind==sound::ActionKind::play && actions[n].value==7){++extends;require(updated && counters[n]==before+1,"score extend must queue AFTER SE update");}
        }
        require(updates==1,"one sound update per completed MAIN frame");
    }
    require(extends==2,"two real score extends were not routed");
    std::cout<<"MAIN sound order, real item/score extends, absent FM, IRQ wait and PCM partition contracts PASS\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
