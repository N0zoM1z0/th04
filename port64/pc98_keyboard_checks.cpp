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
void masked_interrupt() {
    Receiver receiver;InterruptRequest irq;
    std::array<std::uint8_t,10> matrix{};
    receiver.enqueue(0x29,0);receiver.enqueue(0xa9,0);
    require(receiver.complete(character_time)==Receiver::Completion::ready,"masked receive");
    irq.request();irq.request();
    require(irq.pending() && !irq.eligible(false),"masked request is retained");
    bool rejected=false;
    try {irq.accept(false);} catch(const std::logic_error&) {rejected=true;}
    require(rejected && irq.pending(),"masked acceptance must fail without losing request");
    require(receiver.complete(2*character_time)==Receiver::Completion::overrun,"masked overrun");
    require(irq.pending() && receiver.ready() && !matrix[5],"overrun preserves request without BIOS write");
    require(irq.eligible(true) && irq.pending(),"restoring IF only makes request eligible");
    irq.accept(true);
    require(!irq.pending() && receiver.ready() && !matrix[5],"CPU acceptance is separate from data read");
    rejected=false;
    try {irq.accept(true);} catch(const std::logic_error&) {rejected=true;}
    require(rejected,"duplicate acceptance must fail");
    update_matrix(matrix,receiver.read_data(3*character_time));
    require(matrix[5]==2 && receiver.next_event()==4*character_time,"actual data read restarts stalled receiver");
    require(receiver.complete(4*character_time)==Receiver::Completion::ready,"queued break arrives");
    irq.request();irq.accept(true);
    require(matrix[5]==2,"accepting break interrupt leaves BIOS make until data read");
    update_matrix(matrix,receiver.read_data(4*character_time));
    require(!matrix[5] && !irq.pending(),"CPU read finally applies break");
}
void primary_pic() {
    FixedPriorityPic pic({0,0,0});pic.request(1);pic.request(0);
    require(pic.eligible(true)==0 && !pic.eligible(false),"primary priority and CPU IF");
    bool rejected=false;try{pic.accept(1,true);}catch(const std::logic_error&){rejected=true;}
    require(rejected && pic.state().requests==3,"out-of-priority acceptance lost request");
    pic.accept(0,true);pic.set_mask(0xfd);
    require(pic.pending(1) && !pic.eligible(true),"masking IRQ0 does not end its service");
    pic.eoi();require(pic.eligible(true)==1,"nonspecific EOI restores lower priority eligibility");
    pic.accept(1,true);pic.request(1);pic.set_mask(0xff);
    require(pic.pending(1) && !pic.eligible(true),"masking does not erase a re-request");
    pic.eoi(1);pic.set_mask(0xfd);require(pic.eligible(true)==1,"specific EOI retains queued request");
    pic.accept(1,true);pic.set_mask(0xfc);pic.request(0);pic.accept(0,true);
    require(pic.state().service==3 && pic.active()==0,"higher-priority interrupt nests");
    pic.eoi(1);require(pic.state().service==1,"specific EOI must not clear another active line");
    pic.eoi();pic.eoi();require(!pic.state().service,"EOI with no service is inert");
    Device device;device.set_irq_mask(0,0xfc);device.request_irq(0,0);
    device.accept_irq(0,0,true);device.set_irq_mask(0,0xfd);device.key({1,0x29},true,0);
    device.receive(character_time);
    require(device.irq().pending() && !device.irq().eligible(true),"device must retain PIC-blocked keyboard request");
    device.end_irq(character_time);device.accept(character_time,true);device.read_bios(character_time);
    require(device.matrix()[5]==2 && device.pic().state().service==2,
        "BIOS read must leave keyboard in service until its separate EOI");
    device.key({1,0x29},false,character_time);device.receive(2*character_time);
    require(device.irq().pending() && !device.irq().eligible(true),"same line cannot re-enter before EOI");
    device.end_irq(2*character_time);device.accept(2*character_time,true);device.read_bios(2*character_time);
    device.end_irq(2*character_time);
    require(!device.matrix()[5] && !device.pic().state().service,"separate break service completes");
}
void device_trace() {
    Device device;Time now=0;unsigned operation=0;char kind;
    while(std::cin>>kind>>now) {
        unsigned enabled_if=0;std::cin>>enabled_if;
        if(!std::cin || enabled_if>1)throw std::runtime_error("invalid CPU IF stimulus");
        if(kind=='K') {
            unsigned id=0,scan=0,down=0;std::cin>>id>>scan>>down;
            if(!std::cin || id>65535 || scan>127 || down>1)throw std::runtime_error("invalid key stimulus");
            device.key({std::uint16_t(id),std::uint8_t(scan)},down!=0,now);
        } else if(kind=='T') {
            unsigned enabled=0;std::cin>>enabled;
            if(!std::cin || enabled>1)throw std::runtime_error("invalid tick stimulus");
            device.tick(now,enabled!=0);
        } else if(kind=='R')device.receive(now);
        else if(kind=='A')device.accept(now,enabled_if!=0);
        // This legacy projection collapses the callback read and its EOI.
        // Separate PIC/BIOS/EOI boundaries are exercised by the PIC controls.
        else if(kind=='B'){device.read_bios(now);device.end_irq(now);}
        else throw std::runtime_error("unknown keyboard stimulus");
        const auto& keyboard=device.keyboard();const auto& receiver=device.receiver();
        std::cout<<operation++<<' '<<keyboard.wait_ticks()<<' '
            <<(keyboard.repeating_key() ? keyboard.repeating_key()->physical : 0)<<' '
            <<unsigned(receiver.input_index())<<' '<<unsigned(receiver.output_index())<<' '
            <<receiver.busy()<<' '<<receiver.ready()<<' '<<unsigned(receiver.data())<<' '<<receiver.queued()<<' ';
        for(auto byte:device.matrix())std::cout<<std::hex<<std::setfill('0')<<std::setw(2)<<unsigned(byte);
        std::cout<<std::dec<<' '<<device.irq().pending()<<' '<<device.irq().eligible(enabled_if!=0)<<' '<<device.admitted()<<'\n';
    }
}
void trace(bool irq_mode=false) {
    Typematic keyboard;Receiver receiver;std::array<std::uint8_t,10> matrix{};
    InterruptRequest irq;bool admitted=false;
    Time now=0;std::vector<unsigned> emitted;unsigned operation=0;char kind;
    const auto send=[&](std::uint8_t code){emitted.push_back(code);receiver.enqueue(code,now);};
    while(std::cin>>kind>>now) {
        unsigned enabled_if=0;
        if(irq_mode) {
            std::cin>>enabled_if;
            if(!std::cin || enabled_if>1)throw std::runtime_error("invalid CPU IF stimulus");
        }
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
        else if(kind=='R') {
            const auto result=receiver.complete(now);
            if(irq_mode && result==Receiver::Completion::ready)irq.request();
        }
        else if(kind=='A' && irq_mode) {
            require(!admitted,"keyboard ISR already owns an unread byte");
            irq.accept(enabled_if!=0);admitted=true;
        }
        else if(kind=='B') {
            if(irq_mode)require(admitted && receiver.ready(),"BIOS read without CPU acceptance");
            require(update_matrix(matrix,receiver.read_data(now)),"unsupported trace modifier");
            admitted=false;
        }
        else throw std::runtime_error("unknown keyboard stimulus");
        if(!std::cin)throw std::runtime_error("malformed keyboard stimulus");
        std::cout<<operation++<<' '<<keyboard.wait_ticks()<<' '
            <<(keyboard.repeating_key() ? keyboard.repeating_key()->physical : 0)<<' '
            <<unsigned(receiver.input_index())<<' '<<unsigned(receiver.output_index())<<' '
            <<receiver.busy()<<' '<<receiver.ready()<<' '<<unsigned(receiver.data())<<' '
            <<receiver.queued()<<' ';
        for(auto byte:matrix)std::cout<<std::hex<<std::setfill('0')<<std::setw(2)<<unsigned(byte);
        std::cout<<std::dec<<' ';
        if(irq_mode)std::cout<<irq.pending()<<' '<<irq.eligible(enabled_if!=0)<<' '<<admitted<<' ';
        std::cout<<emitted.size();
        for(auto byte:emitted)std::cout<<' '<<byte;
        std::cout<<'\n';
    }
}
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--trace") {trace();return 0;}
        if(argc==2 && std::string(argv[1])=="--irq-trace") {trace(true);return 0;}
        if(argc==2 && std::string(argv[1])=="--device-irq-trace") {device_trace();return 0;}
        if(argc!=1)throw std::runtime_error("expected no arguments, --trace, --irq-trace or --device-irq-trace");
        repeat_and_latch();key_ownership();blocked_receiver();queue_and_deadline();masked_interrupt();primary_pic();
        std::cout<<"PC-98 keyboard repeat/transport/BIOS contracts pass\n";return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}
