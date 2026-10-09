#include "sound_control.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
using namespace th04::portable;
std::array<std::uint8_t,13> decode(const std::string& s){if(s.size()!=26)throw std::runtime_error("sound fixture filename");std::array<std::uint8_t,13> v{};for(unsigned i=0;i<13;++i)v[i]=std::uint8_t(std::stoul(s.substr(i*2,2),nullptr,16));return v;}
std::string hex(const std::array<std::uint8_t,13>& v){std::ostringstream o;o<<std::hex<<std::setfill('0');for(auto x:v)o<<std::setw(2)<<unsigned(x);return o.str();}
int main(int argc,char** argv){try{
 if(argc==3 && std::string(argv[1])=="--replay"){
  std::ifstream input(argv[2]);if(!input)throw std::runtime_error("sound fixtures missing");std::string line;unsigned number=0;
  while(std::getline(input,line)){
   std::istringstream in(line);unsigned bgm,se,midi,irq,playing,frame,count;std::string fn;in>>bgm>>se>>midi>>irq>>playing>>frame>>fn>>count;
   sound::State state{std::uint8_t(bgm),std::uint8_t(se),std::uint8_t(midi),std::uint8_t(irq),std::uint8_t(playing),std::uint8_t(frame),decode(fn)};
   std::cout<<"CASE "<<number++<<'\n';sound::Control control(state,[](const sound::Request& q){std::cout<<sound::kind_name(q.kind)<<' '<<q.a<<' '<<q.b<<' '<<(q.name.empty()?"-":q.name)<<'\n';});
   for(unsigned i=0;i<count;++i){unsigned op,a,b,c,d,e;std::string name;in>>op>>a>>b>>c>>d>>e>>name;if(!in)throw std::runtime_error("sound action fixture");
    unsigned result=0;
    switch(op){case 0:result=control.determine(a,b,{c!=0,d!=0,std::uint16_t(e)});break;case 1:result=control.command(a,b,c);break;case 2:control.reset();break;case 3:control.play(a);break;case 4:for(unsigned n=0;n<a;++n)control.update();break;case 5:control.load(decode(name),a);break;default:throw std::runtime_error("sound fixture operation");}
    const auto& s=control.state();std::cout<<"STATE "<<result<<' '<<unsigned(s.bgm)<<' '<<unsigned(s.se)<<' '<<unsigned(s.midi_possible)<<' '<<unsigned(s.interrupt_if_midi)<<' '<<unsigned(s.playing)<<' '<<unsigned(s.frame)<<' '<<hex(s.filename)<<'\n';
   }
  }
  return 0;
 }
 sound::Control c({2,1,0,96,255,0,{}});c.play(7);c.update();c.play(1);if(c.state().playing!=7)throw std::runtime_error("priority arbitration");for(unsigned i=0;i<48;++i)c.update();if(c.state().playing!=255)throw std::runtime_error("duration release");
 c.determine(0,1,{true,false,1});if(c.state().bgm!=0 || c.state().se!=1)throw std::runtime_error("BGM off silenced FM SE");
 bool rejected=false;try{c.play(256);}catch(const std::out_of_range&){rejected=true;}if(!rejected)throw std::runtime_error("unsafe SE accepted");
 std::cout<<"sound control contracts PASS\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
