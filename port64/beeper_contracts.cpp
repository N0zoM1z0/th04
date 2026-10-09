#include "beeper.hpp"
#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
using namespace th04::portable::sound;
Bytes bytes(const std::string& s){if(s=="-")return {};if(s.size()%2)throw std::runtime_error("beeper fixture hex");Bytes b;for(unsigned i=0;i<s.size();i+=2)b.push_back(std::uint8_t(std::stoul(s.substr(i,2),nullptr,16)));return b;}
void dump(const BeepState& s){std::cout<<"DATA ";std::ios old(nullptr);old.copyfmt(std::cout);std::cout<<std::hex<<std::setfill('0');for(const auto& e:s.effects)for(auto w:e.words)std::cout<<std::setw(2)<<unsigned(w&255)<<std::setw(2)<<unsigned(w>>8);std::cout<<'\n';std::cout.copyfmt(old);}
void state(const BeepState& s,int result){std::cout<<"STATE "<<result<<' '<<s.count<<' '<<s.selected<<' '<<s.active<<' '<<s.phase<<' '<<s.tempo<<' '<<s.timer_divisor<<' '<<s.enabled<<' '<<s.gate<<' '<<s.divisor<<' '<<s.reloads;for(const auto& e:s.effects)std::cout<<' '<<e.cursor;std::cout<<'\n';}
Bytes file(const char* p){std::ifstream in(p,std::ios::binary);if(!in)throw std::runtime_error("beeper input file");return Bytes(std::istreambuf_iterator<char>(in),{});}
int main(int argc,char** argv){try{
 if(argc==3 && std::string(argv[1])=="--replay"){
  std::ifstream in(argv[2]);std::string line;unsigned number=0;if(!in)throw std::runtime_error("beeper fixtures missing");
  while(std::getline(in,line)){
   std::istringstream f(line);unsigned clock8,enabled,phase,count;f>>clock8>>enabled>>phase>>count;
   BeepState initial;initial.clock8=clock8!=0;initial.enabled=std::uint16_t(enabled);initial.phase=std::uint16_t(phase);initial.timer_divisor=clock8?1996:2458;initial.divisor=clock8?998:1229;
   std::cout<<"CASE "<<number++<<'\n';Beeper beep(initial,[](BeepPort p){std::cout<<"OUT "<<p.port<<' '<<unsigned(p.value)<<'\n';});
   for(unsigned i=0;i<count;++i){unsigned op,value;std::string data;f>>op>>value>>data;if(!f)throw std::runtime_error("beeper action fixture");int result=0;
    switch(op){case 0:result=beep.read(data=="!" ? std::nullopt : std::optional<Bytes>(bytes(data)));dump(beep.state());break;case 1:result=beep.play(std::int16_t(value));break;case 2:for(unsigned n=0;n<value;++n){beep.tick();state(beep.state(),0);}break;case 3:result=beep.tempo(std::int16_t(value));break;case 4:beep.enable(std::uint16_t(value));break;default:throw std::runtime_error("beeper operation");}
    if(op!=2)state(beep.state(),result);
   }
  }
  return 0;
 }
 if(argc==8 && std::string(argv[1])=="--pcm"){
#ifdef _WIN32
  _setmode(_fileno(stdout),_O_BINARY);
#endif
  Beeper beep(std::stoul(argv[2])!=0);if(beep.read(file(argv[5]))!=0)throw std::runtime_error("beeper PCM resource");beep.play(std::int16_t(std::stoul(argv[6])));
  BeepPcm pcm(beep,unsigned(std::stoul(argv[3])));unsigned left=unsigned(std::stoul(argv[4])),block=unsigned(std::stoul(argv[7]));if(!block)throw std::runtime_error("beeper PCM block");
  while(left){const auto n=std::min(left,block);const auto samples=pcm.render(n);for(auto v:samples){char raw[2]{char(std::uint16_t(v)&255),char(std::uint16_t(v)>>8)};std::cout.write(raw,2);}left-=n;}return 0;
 }
 Beeper beep;std::vector<BeepPort> ports;Beeper joined(false,[&](BeepPort p){ports.push_back(p);});int loads=0;
 Control control({2,2,0,96,255,0,{}},[&](const Request& q){const auto result=joined.consume(q,[&](const std::string& name)->std::optional<Bytes>{++loads;if(name!="MIKO.efs")throw std::runtime_error("beeper resource route");return Bytes{'4','4','0',' ','0',' '};});if(!result)throw std::runtime_error("unexpected FM request in beeper fixture");});
 std::array<std::uint8_t,13> name{{'M','I','K','O'}};control.load(name,0xb00);control.play(1);control.update();if(loads!=1 || !joined.state().active)throw std::runtime_error("sound control/beeper join");
 BeepPcm pcm(joined);const auto samples=pcm.render(2000);if(std::find_if(samples.begin(),samples.end(),[](auto v){return v!=0;})==samples.end() || ports.empty())throw std::runtime_error("offline beeper samples absent");
 if(beep.tempo(29)!=-13 || beep.read(std::nullopt)!=-2 || beep.play(0)!=-13)throw std::runtime_error("beeper admission");
 std::cout<<"beeper control/resource/offline PCM contracts PASS\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
