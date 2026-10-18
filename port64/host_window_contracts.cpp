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
    using K=HostKey;
    Keyboard ordered(0,Keyboard::available_cpu);
    ordered.key(K::keypad_up,true,0);ordered.key(K::up,true,0);
    ordered.advance(2000000);
    require(ordered.device().matrix()[7]==4 && ordered.device().matrix()[8]==8,
        "arrow and keypad must occupy distinct BIOS bits");
    require(ordered.device().keyboard().repeating_key()->make==0x3a,
        "host delivery order must choose repeat owner");
    ordered.key(K::up,true,2000000); // An OS repeat must not restart firmware.
    require(ordered.device().keyboard().wait_ticks()==498,"OS repeat reset firmware timer");
    ordered.key(K::up,false,2000000);ordered.advance(3000000);
    require(!ordered.device().matrix()[7] && ordered.device().matrix()[8]==8 &&
        !ordered.device().keyboard().wait_ticks(),"releasing repeat owner must not transfer to held alias");
    require(input(ordered.keys(),true).held==1,"keypad advice action lost after arrow release");
    Keyboard pulse(0,Keyboard::available_cpu);
    pulse.key(K::shot,true,0);pulse.key(K::shot,false,0);
    pulse.advance(572917);require(pulse.device().matrix()[5]==2,"between-poll make was lost");
    pulse.advance(1145834);require(!pulse.device().matrix()[5],"between-poll break was lost");
    Keyboard returns(0,Keyboard::available_cpu);
    returns.key(K::keypad_enter,true,0);returns.key(K::enter,true,0);
    returns.key(K::keypad_enter,false,0);returns.advance(2000000);
    require(returns.keys().enter && !returns.keys().keypad_enter &&
        !returns.device().matrix()[3] && returns.device().keyboard().wait_ticks()==498,
        "same-scan physical Return keys must preserve independent releases and repeat owner");
    returns.focus(false,2000000);returns.key(K::enter,true,2000000);returns.advance(3000000);
    require(!returns.keys().enter && !returns.device().keyboard().wait_ticks(),"unfocused event acquired repeat ownership");
    returns.focus(true,3000000);returns.advance(4000000);
    require(!returns.keys().enter,"focus gain invented an unobserved make");
    Keyboard shifts(0,Keyboard::available_cpu);
    shifts.key(K::shift,true,0);shifts.key(K::right_shift,true,0);shifts.key(K::shift,false,0);
    shifts.advance(2000000);
    require(shifts.keys().right_shift && !shifts.device().shift() &&
        shifts.device().keyboard().repeating_key()->physical==unsigned(K::right_shift)+1,
        "same-scan Shift keys must not merge physical ownership or BIOS release");
    std::int64_t clock=0;Keyboard timed(0,Keyboard::available_cpu);timed.key(K::shot,true,0);
    const auto elapsed=timed.elapsed_source([&]{clock+=100000;return clock;});
    th04::portable::pc98_input::Latch latch;
    require(latch.poll(th04::portable::pc98_input::Operation::reset,elapsed).keys[5]==0,
        "byte source observed a make before its serial completion");
    require(timed.device().matrix()[5]==2 && clock==900000,"elapsed byte source lost live clock advancement");
    bool installed=false,finish_timer=false;
    Keyboard priority(0,[&](auto& device,auto time) {
        if(!installed) {
            device.set_irq_mask(time,0xfc);device.request_irq(time,0);
            device.accept_irq(time,0,true);device.set_irq_mask(time,0xfd);installed=true;
        }
        if(finish_timer) {device.end_irq(time);finish_timer=false;}
        Keyboard::available_cpu(device,time);
    });
    priority.key(K::shot,true,0);priority.advance(2000000);
    require(priority.device().irq().pending() && !priority.device().irq().eligible(true) &&
        !priority.device().matrix()[5],"IF alone must not bypass a higher in-service interrupt");
    finish_timer=true;priority.advance(2000000);
    require(priority.device().matrix()[5]==2 && !priority.device().pic().state().service,
        "higher EOI must admit keyboard,read BIOS,then finish its own IRQ");
    std::cout<<"Host admission, slowdown/resync, bounded catchup and focused input contracts PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
