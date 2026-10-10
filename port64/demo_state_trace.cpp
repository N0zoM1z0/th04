// Headless MAIN state trace. External assets and ordinary actor updates only.
#include "main_state.hpp"
#include "configuration.hpp"
#include "demo_pool_wire.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable;
namespace {
void require(bool ok,const char* reason) {if(!ok)throw std::runtime_error(reason);}
std::vector<std::uint8_t> read(const std::filesystem::path& path) {
    std::ifstream input(path,std::ios::binary);require(bool(input),"missing demo input");
    return {std::istreambuf_iterator<char>(input),{}};
}
template<class T> void hex(const T& bytes) {
    constexpr char digits[]="0123456789abcdef";
    for(auto value:bytes)std::cout<<digits[unsigned(value)>>4]<<digits[unsigned(value)&15];
}
}
int main(int argc,char** argv) {
    try {
        require(argc==2 || argc==3,"usage: th04-port64-demo-state-trace INPUT_DIRECTORY [POOL_STREAM]");
        const std::filesystem::path directory(argv[1]);
        std::ofstream pools;
        if(argc==3) {
            require(!std::filesystem::exists(argv[2]),"pool output already exists");
            pools.open(argv[2],std::ios::binary);require(bool(pools),"cannot open pool output");
            pools.write("TH04NP2\n",8);
        }
        for(unsigned number=1;number<=4;++number) {
            application::State application;
            const auto config=read(directory/"MIKO.CFG");
            application.apply_options(configuration::decode(configuration::load(config).options));
            for(unsigned n=1;n<=number;++n) {
                application.start_next_demo();if(n<number)application.return_from_main({});
            }
            score_file::HostStore storage(directory/"save");
            const auto old_scores=storage.file().bytes();
            gameplay::State state(application,gameplay::Mode::ordinary,{},&storage);
            const auto replay_bytes=read(directory/demo::Replay::filename(number));
            demo::Replay replay(replay_bytes);
            const auto stage=application.resident().resource_stage;
            const auto stem="ST0"+std::to_string(stage);
            const auto standard=read(directory/(stem+".STD"));
            stage::Background background(read(directory/(stem+".MAP")),standard);
            state.load_stage(standard);state.set_demo_replay(replay_bytes);
            const stage::Program script_owner(standard);
            if(argc==3)state.set_actor_observer([&](const gameplay::State& checkpoint) {
                demo_wire::pools(pools,number,checkpoint,script_owner);
            });
            const auto base_draws=application.process_random_draws();
            const auto base_samples=state.random_samples();
            for(unsigned frame=0;frame<=3996;++frame) {
                require(state.frames()==frame,"demo frame missing or blocked");
                const auto sample=replay.sample(std::uint16_t(frame),0,0);
                const auto& life=state.life();const auto& player=state.player().position().current;
                const auto& score=state.scoreboard();const auto& resident=application.resident();
                std::cout<<number<<' '<<frame<<' '<<(sample.finished?'T':'I')<<' '
                    <<sample.input<<' '<<+sample.shift<<' '<<+resident.stage<<' ';
                hex(score.digits);
                std::cout<<' '<<state.score().score_delta<<' '<<score.frame_delta<<' '
                    <<application.process_random_state()<<' ';hex(state.random_ring_bytes());
                std::cout<<' '<<state.random_cursor()<<' '<<player.x<<' '<<player.y<<' '
                    <<+state.score().power<<' '<<+life.hit<<' '<<+life.invincibility<<' '<<+life.respawn_time<<' '
                    <<+state.score().remaining_lives<<' '<<+state.score().remaining_bombs<<' '
                    <<+resident.miss_count<<' '<<+resident.bombs_used<<' '
                    <<application.process_random_draws()-base_draws<<' '<<state.random_samples()-base_samples<<'\n';
                state.update(0,false,false,background.last_delta(),&background);
                const auto actual=state.demo_sample();
                require(actual.input==sample.input && actual.shift==sample.shift && actual.replaced &&
                    actual.finished==sample.finished,"MAIN consumed a different replay sample");
                if(frame<3996) {
                    require(!state.demo_exit_requested() && state.frames()==frame+1,"demo update or early terminal");
                    for(const auto& event:state.life_events())if(event.kind==player::LifeKind::scroll)
                        background.set_display_line(unsigned(event.value));
                    background.update(state.life().scroll_active!=0);
                } else require(state.demo_exit_requested() && state.frames()==frame,"demo terminal advanced actors");
            }
            require(storage.file().bytes()==old_scores && storage.commits()==0,"valid demo scores changed");
        }
        return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
