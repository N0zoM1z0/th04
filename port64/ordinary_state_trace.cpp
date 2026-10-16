// Bounded ordinary MAIN component trace. External recorded input and assets.
#include "main_state.hpp"
#include "configuration.hpp"
#include "demo_pool_wire.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
using namespace th04::portable;
namespace {
void require(bool ok,const char* reason){if(!ok)throw std::runtime_error(reason);}
std::vector<std::uint8_t> read(const std::filesystem::path& p){std::ifstream s(p,std::ios::binary);require(bool(s),"missing ordinary input");return {std::istreambuf_iterator<char>(s),{}};}
template<class T>void hex(const T& values){constexpr char digits[]="0123456789abcdef";for(auto v:values)std::cout<<digits[unsigned(v)>>4]<<digits[unsigned(v)&15];}
}
int main(int argc,char** argv){try{
 require(argc==3,"usage: th04-port64-ordinary-state-trace INPUT_DIRECTORY POOL_STREAM");
 const std::filesystem::path directory(argv[1]);
 std::ifstream input(directory/"inputs.txt");std::uint32_t seed;unsigned updates,character,shot;
 require(bool(input>>seed>>updates>>character>>shot) && seed<=65535 && updates>0 && updates<=65535 && character<2 && shot<2,"ordinary plan header");
 require(!std::filesystem::exists(argv[2]),"pool output already exists");std::ofstream pools(argv[2],std::ios::binary);require(bool(pools),"cannot open ordinary pools");pools.write("TH04OP1\n",8);
 application::State application;application.apply_options(configuration::decode(configuration::load(read(directory/"MIKO.CFG")).options));
 for(std::uint32_t i=0;i<seed;++i)application.advance_op_menu_frame();
 application.start_normal(application::Playchar(character),application::ShotType(shot));
 score_file::HostStore storage(directory/"save");const auto old_scores=storage.file().bytes();
 gameplay::State state(application,gameplay::Mode::ordinary,{},&storage);
 const auto standard=read(directory/"ST00.STD");stage::Background background(read(directory/"ST00.MAP"),standard);stage::Program program(standard);state.load_stage(standard);
 state.set_actor_observer([&](const gameplay::State& s){demo_wire::pools(pools,0,s,program);});
 const auto base_draws=application.process_random_draws(),base_samples=state.random_samples();
 std::cout<<"TH04_ORDINARY_STATE 1 "<<updates<<'\n';
 for(unsigned frame=0;frame<=updates;++frame){
  unsigned number,keys,shift;require(bool(input>>number>>keys>>shift) && number==frame && keys<=65535 && shift<=1,"ordinary input frame/order/width");require(state.frames()==frame,"ordinary update blocked or skipped");
  const auto& life=state.life();const auto& player=state.player().position().current;const auto& score=state.scoreboard();const auto& resident=application.resident();
  std::cout<<frame<<' '<<(frame==updates ? 'P':'I')<<' '<<keys<<' '<<shift<<' '<<+resident.stage<<' ';hex(score.digits);
  std::cout<<' '<<state.score().score_delta<<' '<<score.frame_delta<<' '<<application.process_random_state()<<' ';hex(state.random_ring_bytes());
  std::cout<<' '<<state.random_cursor()<<' '<<player.x<<' '<<player.y<<' '<<+state.score().power<<' '<<+life.hit<<' '<<+life.invincibility<<' '<<+life.respawn_time<<' '<<+state.score().remaining_lives<<' '<<+state.score().remaining_bombs<<' '<<+resident.miss_count<<' '<<+resident.bombs_used<<' '<<application.process_random_draws()-base_draws<<' '<<state.random_samples()-base_samples<<'\n';
  if(frame==updates)break;
  require(!(keys&~0x3fu),"ordinary gameplay input has unowned high bits");
  const auto held=std::uint16_t((keys&0x2fu)|(keys&0x10u ? 0x800u : 0));
  require(player::input_from_host_actions(held)==keys,"ordinary host input translation");
  state.update(held,shift!=0,false,background.last_delta(),&background);
  require(state.frames()==frame+1 && !state.game_over(),"ordinary prefix crossed an unconfigured blocking boundary");
  for(const auto& event:state.life_events())if(event.kind==player::LifeKind::scroll)background.set_display_line(unsigned(event.value));
  background.update(state.life().scroll_active!=0);
 }
 input>>std::ws;require(input.peek()==std::char_traits<char>::eof(),"trailing ordinary input");require(storage.file().bytes()==old_scores && storage.commits()==0,"ordinary prefix changed saved scores");return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
