#include "pmd_ssg_effects.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>

using namespace th04::portable::pmd;
namespace {
void require(bool value,const char* text){if(!value)throw std::runtime_error(text);}
void record(std::ostream& out,const SsgEffects& player,const std::vector<SsgWrite>& writes) {
    const auto& s=player.state();
    out<<s.resource<<' '<<s.next_frame<<' '<<s.tone<<' '<<s.tone_step<<' '
       <<unsigned(s.ticks)<<' '<<unsigned(s.noise)<<' '<<int(s.noise_step)<<' '
       <<unsigned(s.noise_interval)<<' '<<unsigned(s.noise_counter)<<' '
       <<unsigned(s.priority)<<' '<<unsigned(s.effect);
    for(unsigned address:{4,5,6,7,10,11,12,13})out<<' '<<unsigned(player.registers()[address]);
    out<<' '<<writes.size();
    for(auto w:writes)out<<' '<<unsigned(w.address)<<' '<<unsigned(w.value);
    out<<'\n';
}
void contracts() {
    std::vector<SsgWrite> writes;
    SsgEffects p([&](SsgWrite w){writes.push_back(w);});p.mirror(7,0xbf);
    p.start(1);require(p.state().tone==400 && p.state().noise==7,"SSG instrument load");
    p.timer_a();require(p.state().tone==493 && p.state().noise==7,"SSG signed sweep interval");
    p.timer_a();require(p.state().tone==586 && p.state().noise==6,"SSG noise sweep");
    p.start(31);require(p.state().priority==2,"SSG priority admission");
    p.timer_a();require(p.state().tone==427,"SSG negative tone sweep");
    const auto before=p.state().resource;writes.clear();
    require(!p.start(0) && p.state().resource==before && writes.empty(),"SSG lower priority steals channel");
    require(p.state().effect==0,"refused request must publish ID");
    require(p.start(12),"SSG equal priority restart");
    p.stop();require(p.state().effect==255 && p.state().priority==0 && p.registers()[10]==0,"SSG stop");
    const auto count=writes.size();p.timer_a();require(count==writes.size(),"SSG stopped sweep writes");
    bool rejected=false;try{p.start(40);}catch(const std::out_of_range&){rejected=true;}
    require(rejected,"SSG unknown instrument accepted");
    std::cout<<"PMD SSG effect pitch/noise sweeps, admission, restart and stop PASS\n";
}
}
int main(int argc,char** argv) {
    try {
        if(argc==1){contracts();return 0;}
        require(argc==3,"SSG trace: operations output");
        std::ifstream input(argv[1]);std::ofstream output(argv[2]);
        require(bool(input)&&bool(output),"SSG trace file admission");
        std::vector<SsgWrite> writes;
        SsgEffects p([&](SsgWrite w){writes.push_back(w);});p.mirror(7,0xbf);
        char operation;int value;
        while(input>>operation>>value) {
            writes.clear();
            if(operation=='P'){require(value>=0 && value<40,"SSG effect index");p.start(unsigned(value));}
            else if(operation=='T'){require(value>=0 && value<=3,"SSG timer status");if(value&1)p.timer_a();}
            else if(operation=='S')p.stop();
            else if(operation=='M'){require(value>=0 && value<=255,"SSG mixer");p.mirror(7,std::uint8_t(value));}
            else throw std::invalid_argument("SSG operation");
            record(output,p,writes);
        }
        require(input.eof(),"SSG trace parse");output.close();require(bool(output),"SSG trace write");
        return 0;
    }catch(const std::exception& e){std::cerr<<"PMD SSG: "<<e.what()<<'\n';return 1;}
}
