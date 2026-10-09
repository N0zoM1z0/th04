#include "pmd_clock.hpp"
#include <limits>
#include <stdexcept>

namespace th04::portable::pmd {
OpnTimers::OpnTimers(Board board):quantum_(board==Board::fm26 ? 72 : 144),opna_(board!=Board::fm26) {
    if(board!=Board::fm26 && board!=Board::fm86 && board!=Board::speakboard)throw std::invalid_argument("OPN board");
    if(opna_)irq_mask_=0;
}
std::uint64_t OpnTimers::period(unsigned timer,bool initial) const {
    const unsigned ticks=timer ? 16*(256-unsigned(registers_[2]))-(initial ? unsigned((cycles_/quantum_)&15) : 0)
        : 1024-((unsigned(registers_[0])<<2)|(registers_[1]&3));
    return std::uint64_t(ticks)*quantum_;
}
void OpnTimers::write(std::uint8_t address,std::uint8_t value) {
    if(address==0x29 && opna_) {irq_mask_=value&3;return;}
    if(address<0x24 || address>0x27)return;
    registers_[address-0x24]=value;
    if(address!=0x27)return;
    status_&=std::uint8_t(~((value>>4)&3));
    for(unsigned t=0;t<2;++t) {
        if(!(value&(1u<<t)))deadlines_[t]=0;
        else if(!deadlines_[t]) {
            const auto p=period(t,true);
            if(cycles_>std::numeric_limits<std::uint64_t>::max()-p)throw std::overflow_error("OPN deadline");
            deadlines_[t]=cycles_+p;
        }
    }
}
void OpnTimers::advance(std::uint64_t count,const std::function<void(std::uint8_t)>& irq) {
    // Bound host work and all additions, including the next reload beyond end.
    constexpr auto headroom=std::uint64_t(4096)*144;
    if(count>1000000000 || cycles_>std::numeric_limits<std::uint64_t>::max()-headroom-count)
        throw std::invalid_argument("OPN cycle step");
    const auto end=cycles_+count;
    while(true) {
        auto next=end;
        bool due=false;
        for(auto d:deadlines_)if(d && d<=next) {next=d;due=true;}
        if(!due)break;
        cycles_=next;
        for(unsigned t=0;t<2;++t)if(deadlines_[t]==next) {
            deadlines_[t]=next+period(t,false);
            if(registers_[3]&(4u<<t))status_|=std::uint8_t(1u<<t);
        }
        if((status_&irq_mask_) && irq)irq(status_);
    }
    cycles_=end;
}
ClockedPlayer::ClockedPlayer(Board board,std::uint32_t hz,FmSink sink,SsgSink ssg)
    :timers_(board),master_hz_(hz),player_(board,[this,sink](FmWrite w){
        if(!w.bank)timers_.write(w.address,w.value);
        if(sink)sink(w);
    },std::move(ssg)) {
    if(!hz || hz>1000000000)throw std::invalid_argument("OPN master frequency");
    // Installation is a separate epoch from the first music start. Mirrors
    // supplied by the original observer do not reset these live deadlines.
    timers_.write(0x29,0x83);timers_.write(0x26,200);timers_.write(0x27,0x3f);
}
void ClockedPlayer::advance_cycles(std::uint64_t count) {
    timers_.advance(count,[this](std::uint8_t status){
        player_.interrupt(status);++interrupts_;
        if(interrupt_)interrupt_(timers_.cycles(),status);
    });
}
void ClockedPlayer::advance_ns(std::uint64_t ns) {
    if(ns>1000000000)throw std::invalid_argument("OPN nanosecond step");
    const auto scaled=ns*master_hz_+fraction_;
    advance_cycles(scaled/1000000000);
    fraction_=std::uint32_t(scaled%1000000000);
}
}
