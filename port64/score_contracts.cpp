#include "score.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <stdexcept>
using namespace th04::portable;
namespace {
std::string hex(const std::string& bytes) {
    if(bytes.empty()) return "-";
    std::ostringstream out;out<<std::hex<<std::setfill('0');for(unsigned char b:bytes) out<<std::setw(2)<<unsigned(b);return out.str();
}
void trace(char op,score::Snapshot& s) {
    const auto events=op=='U' ? score::update(s) : op=='E' ? score::extend(s) : score::render(s);
    std::cout<<"S "<<s.delta<<' '<<s.frame_delta;
    for(auto n:{s.hiscore_popup_shown,s.unused,s.extends,s.lives,s.bullet_clear,s.performance,s.minimum,s.maximum,s.popup_id}) std::cout<<' '<<+n;
    std::cout<<' '<<s.popup_callback;
    for(const auto* p:{&s.digits,&s.hiscore,&s.temporary,&s.hud}) for(auto n:*p) std::cout<<' '<<+n;
    for(const auto& e:events) std::cout<<'|'<<int(e.kind)<<' '<<e.left<<' '<<e.row<<' '<<e.value<<' '<<hex(e.bytes);
    std::cout<<'\n';
}
}
int main(int argc,char** argv) {
    try {
        if(argc==3 && std::string(argv[1])=="--vectors") {
            std::ifstream file(argv[2]);if(!file) throw std::runtime_error("cannot read score vectors");
            std::string line;score::Snapshot s;
            while(std::getline(file,line)) {
                std::istringstream in(line);char op;unsigned v[44]{};in>>op;
                if(op=='R') { unsigned award=0;if(!(in>>award)) throw std::runtime_error("missing retained-state award");s.delta+=award;trace('U',s);continue; }
                for(auto& n:v) if(!(in>>n)) throw std::runtime_error("truncated score vector");
                if(op!='U' && op!='E' && op!='H') throw std::runtime_error("unknown score operation");
                s={};s.delta=v[0];s.frame_delta=v[1];s.hiscore_popup_shown=v[2];s.unused=v[3];s.extends=v[4];s.lives=v[5];s.bullet_clear=v[6];s.performance=v[7];s.minimum=v[8];s.maximum=v[9];s.popup_id=v[10];s.popup_callback=v[11]!=0;
                unsigned at=12;for(auto* p:{&s.digits,&s.hiscore,&s.temporary,&s.hud}) for(auto& n:*p) n=static_cast<std::uint8_t>(v[at++]);trace(op,s);
            }
            return 0;
        }
        score::Snapshot s;s.digits[0]=7;s.delta=200000;unsigned calls=0;
        while(s.delta && calls++<1000) score::update(s);
        if(s.delta || s.digits[0]!=7 || score::numeric_units(s.digits)!=200000) throw std::runtime_error("score drain or continues preservation failed");
        s={};s.digits[7]=2;s.extends=2;
        if(!score::extend(s).empty()) throw std::runtime_error("original digit-wise extend predicate replaced by total comparison");
        s.digits[6]=5;s.lives=99;score::extend(s);
        if(s.lives!=100 || s.bullet_clear!=20 || s.extends!=3) throw std::runtime_error("extend cap/order lost");
        std::cout<<"score=DECIMAL_BYTES_LOW_WORD_DRAIN extend=DIGIT_PREDICATES high_digit=UNNORMALIZED pointer_bits="<<sizeof(void*)*8<<'\n';return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}
