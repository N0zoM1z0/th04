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
    Keys shot;shot.shot=true;
    Keyboard keyboard(0,Keyboard::available_cpu);keyboard.observe({shot,true,0});
    keyboard.advance(572916);require(!keyboard.device().matrix()[5],"host make bypassed serial receive");
    keyboard.advance(572917);require(keyboard.device().matrix()[5]==2,"host make failed BIOS service");
    keyboard.advance(500572916);require(keyboard.device().matrix()[5]==2,"early typematic break");
    keyboard.advance(500572917);require(!keyboard.device().matrix()[5],"held host key must retain serialized break interval");
    keyboard.advance(501145834);require(keyboard.device().matrix()[5]==2,"serialized repeat make");
    Keyboard split(0,Keyboard::available_cpu);split.observe({shot,true,0});
    for(std::int64_t t=7;t<533000000;t+=125137)split.advance(t);
    split.advance(533000000);keyboard.advance(533000000);
    require(split.device().matrix()==keyboard.device().matrix() &&
        split.device().keyboard().wait_ticks()==keyboard.device().keyboard().wait_ticks() &&
        split.device().receiver().next_event()==keyboard.device().receiver().next_event(),"elapsed partition changed repeat or UART phase");
    keyboard.observe({shot,false,533000001});keyboard.advance(536000000);
    require(!keyboard.device().matrix()[5] && !keyboard.device().keyboard().wait_ticks(),"focus loss must serialize releases and stop repeat");
    bool available=false;
    Keyboard blocked(0,[&](auto& device,auto time){if(available)Keyboard::available_cpu(device,time);});
    blocked.observe({shot,true,0});blocked.advance(2000000);
    require(blocked.device().irq().pending() && blocked.device().receiver().ready() && !blocked.device().matrix()[5],"elapsed time must not imply CPU admission");
    available=true;blocked.advance(2000000);
    require(!blocked.device().irq().pending() && blocked.device().matrix()[5]==2,"explicit available-CPU service");
    bool backward=false;try{blocked.advance(1999999);}catch(const std::logic_error&){backward=true;}
    require(backward,"backward elapsed clock accepted");
    Keyboard modifier(0,Keyboard::available_cpu);Keys shift;shift.shift=true;
    modifier.observe({shift,true,0});modifier.advance(572917);
    require(modifier.device().shift(),"Shift must pass through serial BIOS service");
    modifier.observe({shift,false,600000});modifier.advance(1200000);
    require(!modifier.device().shift(),"Shift focus release");
    std::cout<<"Host admission, slowdown/resync, bounded catchup and focused input contracts PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
