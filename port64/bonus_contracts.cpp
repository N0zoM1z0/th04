#include "stage_bonus.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <iomanip>
using namespace th04::portable;
namespace {
std::string hex(const std::string& bytes) {
    std::ostringstream out;out<<std::hex<<std::setfill('0');
    for(unsigned char c:bytes) out<<std::setw(2)<<unsigned(c);
    return bytes.empty() ? "-" : out.str();
}
void trace(const bonus::Context& c,bonus::State s,bool all_clear) {
    const auto r=bonus::apply(c,s,all_clear);
    std::cout<<"S "<<s.score_delta<<' '<<+s.bombs<<' '<<+s.performance<<' '<<+s.extends<<' '<<s.palette_tone<<' '<<r.before_modifiers<<' '<<r.awarded;
    for(const auto& e:r.events) std::cout<<"|"<<int(e.kind)<<' '<<e.left<<' '<<e.row<<' '<<e.color<<' '<<e.value<<' '<<hex(e.bytes);
    std::cout<<'\n';
}
}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") {
            std::ifstream file(argv[2]);if(!file) throw std::runtime_error("cannot read bonus vectors");
            std::string line;
            while(std::getline(file,line)) {
                std::istringstream in(line);char mode;unsigned v[19]{};in>>mode;
                for(auto& n:v) if(!(in>>n)) throw std::runtime_error("truncated bonus vector");
                bonus::Context c;c.stage=v[0];c.resource_stage=v[1];c.rank=v[2];c.credit_lives=v[3];c.continues=v[4];
                c.power=v[5];c.point_items=v[6];c.remaining_lives=v[7];c.misses=v[8];c.bombs_used=v[9];c.defeated_in_time=v[10];c.dream=v[11];c.graze=v[12];
                bonus::State s;s.score_delta=v[13];s.bombs=v[14];s.performance=v[15];s.minimum=v[16];s.maximum=v[17];s.extends=v[18];
                if(mode!='C' && mode!='A') throw std::runtime_error("unknown bonus mode");
                trace(c,s,mode=='A');
            }
            return 0;
        }
        bonus::Context c;c.power=3;c.dream=11;c.point_items=1;c.credit_lives=6;c.continues=3;
        bonus::State s;const auto r=bonus::apply(c,s);
        if(r.before_modifiers!=126 || r.awarded!=14 || s.bombs!=1) throw std::runtime_error("stepwise factors or Bomb extend lost");
        c.defeated_in_time=0;s={};const auto timed=bonus::apply(c,s);
        if(timed.awarded || s.bombs!=1) throw std::runtime_error("timeout must zero points but retain Bomb extend");
        c.defeated_in_time=1;c.remaining_lives=0;c.point_items=0;s={};bonus::apply(c,s,true);
        if(s.extends!=10 || s.bombs) throw std::runtime_error("all-clear extend ownership lost");
        std::cout<<"stage_bonus=WORD_COMPONENTS_STEPWISE32 timeout=ZERO_WITH_BOMB allclear=EXTENDS_DISABLED pointer_bits="<<sizeof(void*)*8<<'\n';
        return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
