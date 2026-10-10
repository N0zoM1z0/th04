#include "host_window.hpp"
#include <iostream>
#include <stdexcept>
using namespace th04::portable::host_window;
void require(bool b,const char* s){if(!b)throw std::runtime_error(s);}
int main(){try{
    Schedule s(100);s.wake();require(!s.due(100+period_ns-1) && s.due(100+period_ns),"early/late admission");
    s.completed(2);require(s.next()==100+3*period_ns && !s.due(100+2*period_ns),"slowdown deadline");
    s.completed(1);s.completed(1);s.completed(2);
    const auto late=100+20*period_ns;require(!s.due(late),"unbounded catchup");
    require(s.resync(late,2)>0 && s.next()==late+2*period_ns,"resync lost slowdown");
    s.wake();require(!s.due(late+period_ns) && s.due(late+2*period_ns),"resync cadence");
    require(!s.resync(late+100*period_ns,1) && s.total()==4,"resync without four steps");
    bool rejected=false;try{s.completed(0);}catch(const std::logic_error&){rejected=true;}require(rejected,"zero slowdown");
    Keys all{true,true,true,true,true,true,true,true,true,true};
    require(input(all,true).held==0x782f && input(all,true).shift,"complete held map");
    require(input(all,false).held==0 && !input(all,false).shift,"unfocused input leaked");
    Keys enter;enter.enter=true;require(input(enter,true).held==0x1000,"Enter action");
    std::cout<<"Host admission, slowdown/resync, bounded catchup and focused input contracts PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
