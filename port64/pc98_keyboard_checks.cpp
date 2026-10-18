#include "pc98_keyboard.hpp"
#include "pc98_input.hpp"
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <vector>
using namespace th04::portable::pc98_keyboard;
namespace {
void require(bool condition,const char* text) {
    if(!condition)throw std::runtime_error(text);
}
void repeat_and_latch() {
    Typematic keyboard;Receiver uart;
    th04::portable::pc98_input::Sample sample;
    th04::portable::pc98_input::Latch latch;
    Time now=0;std::vector<unsigned> codes;
    const auto send=[&](std::uint8_t byte) {
        codes.push_back(byte);require(uart.enqueue(byte,now),"unexpected queue overflow");
    };
    keyboard.key({30,0x29},true,send);
    now=*uart.next_event();require(uart.complete(now)==Receiver::Completion::ready,"first make");
    require(!sample.keys[5],"receive completion must not update BIOS");
    require(update_matrix(sample.keys,uart.read_data(now)),"ordinary scan matrix");
    latch.reset_sense(sample);require(latch.actions()==32,"initial Shot latch");
    for(unsigned i=0;i<499;++i)keyboard.tick(send);
    require(codes.size()==1 && keyboard.wait_ticks()==1,"repeat pause boundary");
    now=500*quanta_per_ms;keyboard.tick(send);
    require(codes==std::vector<unsigned>({0x29,0xa9,0x29}),"real repeat break/make order");
    now=*uart.next_event();uart.complete(now);update_matrix(sample.keys,uart.read_data(now));
    require(!(sample.keys[5]&2),"held key has a BIOS break interval");
    latch.sense(sample);require(latch.actions()==32,"sense retains previous Shot");
    latch.reset_sense(sample);require(latch.actions()==0,"reset during break sees zero");
    const auto break_time=now;now=*uart.next_event();uart.complete(now);
    require(now-break_time==character_time,"serialized repeat gap");
    update_matrix(sample.keys,uart.read_data(now));latch.sense(sample);
    require(latch.actions()==32,"later make restores sampled Shot");
    for(unsigned i=0;i<32;++i)keyboard.tick(send);
    require(codes.size()==3,"repeat rate boundary");
    now=533*quanta_per_ms;keyboard.tick(send);require(codes.size()==5,"second repeat");
}
void key_ownership() {
    Typematic keyboard;std::vector<unsigned> codes;
    const auto send=[&](std::uint8_t v){codes.push_back(v);};
    keyboard.key({1,0x29},true,send);keyboard.key({2,0x1c},true,send);
    keyboard.key({1,0x29},false,send);
    require(keyboard.wait_ticks()==500 && keyboard.repeating_key()->physical==2,
            "releasing another key preserves the repeat owner");
    for(unsigned i=0;i<500;++i)keyboard.tick(send,false);
    require(keyboard.wait_ticks()==500,"disabled scanning freezes repeat countdown");
    keyboard.key({2,0x1c},false,send);
    for(unsigned i=0;i<1000;++i)keyboard.tick(send);
    require(codes==std::vector<unsigned>({0x29,0x1c,0xa9,0x9c}),"release stops repeat");
}
void blocked_receiver() {
    Receiver uart;require(uart.enqueue(0x29,0) && uart.enqueue(0xa9,0),"queued bytes");
    uart.complete(character_time);const auto next=*uart.next_event();
    require(uart.data()==0x29 && uart.ready() && uart.queued()==1,"first byte waits for CPU");
    require(uart.complete(next)==Receiver::Completion::overrun,"unread data blocks next receive");
    require(!uart.busy() && uart.ready() && uart.queued()==1 && !uart.next_event(),"overrun retains queued byte");
    const auto read_time=4*character_time;
    require(uart.read_data(read_time)==0x29,"late CPU read returns first byte");
    require(uart.next_event()==read_time+character_time,"CPU read restarts stalled transfer");
    uart.complete(*uart.next_event());require(uart.read_data(read_time+character_time)==0xa9,"queued break survives");
    uart.reset();require(!uart.ready() && !uart.busy() && !uart.queued() && uart.data()==0xa9,"reset leaves data byte");
}
void queue_and_deadline() {
    Receiver uart;
    for(unsigned i=0;i<31;++i)require(uart.enqueue(std::uint8_t(i),0),"ring capacity");
    require(!uart.enqueue(99,0) && uart.queued()==31,"overflow drops newest byte");
    for(unsigned i=0;i<31;++i) {
        const auto due=*uart.next_event();const auto callback=due+16;
        require(uart.complete(callback)==Receiver::Completion::ready,"delayed callback");
        require(uart.read_data(callback)==i,"ring order");
        if(i<30)require(uart.next_event()==due+character_time,"chain uses service deadline");
    }
    require(!uart.next_event() && !uart.queued(),"queue drained");
    require(uart.enqueue(0x1c,40*character_time),"ring wraps after draining");
    const auto due=*uart.next_event();uart.complete(due);
    require(uart.read_data(due)==0x1c,"wrapped ring byte");
    std::array<std::uint8_t,10> matrix{};
    require(!update_matrix(matrix,0x70),"modifier bytes require their separate owner");
}
void trace() {
    Typematic keyboard;Receiver receiver;std::array<std::uint8_t,10> matrix{};
    Time now=0;std::vector<unsigned> emitted;unsigned operation=0;char kind;
    const auto send=[&](std::uint8_t code){emitted.push_back(code);receiver.enqueue(code,now);};
    while(std::cin>>kind>>now) {
        if(kind=='K') {
            unsigned id=0,scan=0,down=0;std::cin>>id>>scan>>down;
            if(!std::cin)throw std::runtime_error("malformed key stimulus");
            if(id>65535 || scan>127 || down>1)throw std::runtime_error("invalid key stimulus");
            keyboard.key({std::uint16_t(id),std::uint8_t(scan)},down!=0,send);
        } else if(kind=='T') {
            unsigned enabled=0;std::cin>>enabled;
            if(!std::cin || enabled>1)throw std::runtime_error("invalid tick stimulus");
            keyboard.tick(send,enabled!=0);
        }
        else if(kind=='R')receiver.complete(now);
        else if(kind=='B')require(update_matrix(matrix,receiver.read_data(now)),"unsupported trace modifier");
        else throw std::runtime_error("unknown keyboard stimulus");
        if(!std::cin)throw std::runtime_error("malformed keyboard stimulus");
        std::cout<<operation++<<' '<<keyboard.wait_ticks()<<' '
            <<(keyboard.repeating_key() ? keyboard.repeating_key()->physical : 0)<<' '
            <<unsigned(receiver.input_index())<<' '<<unsigned(receiver.output_index())<<' '
            <<receiver.busy()<<' '<<receiver.ready()<<' '<<unsigned(receiver.data())<<' '
            <<receiver.queued()<<' ';
        for(auto byte:matrix)std::cout<<std::hex<<std::setfill('0')<<std::setw(2)<<unsigned(byte);
        std::cout<<std::dec<<' '<<emitted.size();
        for(auto byte:emitted)std::cout<<' '<<byte;
        std::cout<<'\n';
    }
}
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--trace") {trace();return 0;}
        if(argc!=1)throw std::runtime_error("expected no arguments or --trace");
        repeat_and_latch();key_ownership();blocked_receiver();queue_and_deadline();
        std::cout<<"PC-98 keyboard repeat/transport/BIOS contracts pass\n";return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
