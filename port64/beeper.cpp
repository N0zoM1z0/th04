#include "beeper.hpp"
#include <stdexcept>

namespace th04::portable::sound {
Beeper::Beeper(bool clock8,BeepSink sink):sink_(std::move(sink)){
    state_.clock8=clock8;state_.timer_divisor=clock8 ? 1996 : 2458;
    state_.divisor=std::uint16_t(state_.timer_divisor/2);
}
void Beeper::out(std::uint16_t port,std::uint8_t value) const {if(sink_)sink_({port,value});}
void Beeper::silence(){
    state_.divisor=state_.clock8 ? 998 : 1229;state_.gate=false;++state_.reloads;
    out(0x3fdb,std::uint8_t(state_.divisor));out(0x3fdb,std::uint8_t(state_.divisor>>8));out(0x37,7);
}
void Beeper::frequency(std::uint16_t hz){
    if(!hz)throw std::logic_error("zero beeper frequency");
    const auto clock=clock_hz();
    state_.divisor=hz<=clock/65536u ? 65535 : std::uint16_t(clock/hz);
    state_.gate=true;++state_.reloads;
    out(0x37,6);out(0x3fdb,std::uint8_t(state_.divisor));out(0x3fdb,std::uint8_t(state_.divisor>>8));
}
int Beeper::read(const std::optional<Bytes>& bytes){
    if(!bytes)return -2;
    // Reject native input/capacity overflow outside the supported DOS segment.
    if(bytes->size()>65534 || state_.count>=16)return -13;
    const auto before=state_.count;state_.effects[state_.count].cursor=0;
    std::size_t position=0;unsigned length=0;
    const auto take=[&](){return position<bytes->size() ? (*bytes)[position++] : std::uint8_t(255);};
    for(;;){
        auto c=take();
        for(;;){
            if(c==';')do{c=take();}while(c!=10 && c!=255);
            if((c>='0' && c<='9') || c==255)break;
            c=take();
        }
        std::uint16_t value=0;
        while(c>='0' && c<='9'){
            value=std::uint16_t(unsigned(value)*10u+unsigned(c-'0'));c=take();
        }
        // The original consumes a separator and does not flush a number at FF.
        if(c==255)break;
        auto& effect=state_.effects[state_.count];
        effect.words[effect.cursor/2]=value;effect.cursor=std::uint16_t(effect.cursor+2);
        if(!value || ++length==256){
            effect.words[effect.cursor/2]=0;length=0;++state_.count;
            if(state_.count==16)break;
            state_.effects[state_.count].cursor=0;
        }
    }
    return state_.count==before ? -11 : 0;
}
int Beeper::play(std::int16_t effect){
    if(effect<1 || unsigned(effect)>state_.count)return -13;
    if(state_.enabled==1){silence();state_.selected=std::uint16_t(effect);state_.effects[unsigned(effect)-1].cursor=0;state_.active=1;}
    return 0;
}
int Beeper::tempo(std::int16_t value){
    if(value<30 || value>240)return -13;
    state_.tempo=std::uint16_t(value);
    const auto base=(state_.clock8 ? 1996u : 2458u)*120u;
    state_.timer_divisor=std::uint16_t(base/unsigned(value));return 0;
}
void Beeper::tick(){
    out(0x71,std::uint8_t(state_.timer_divisor));out(0x71,std::uint8_t(state_.timer_divisor>>8));
    state_.phase=std::uint16_t(state_.phase+1);
    if(state_.phase==20)state_.phase=0;
    else if(!(state_.phase&3) && state_.active==1){
        if(!state_.selected || state_.selected>state_.count)throw std::logic_error("beeper active index");
        auto& effect=state_.effects[state_.selected-1];
        if(effect.cursor/2>=effect.words.size())throw std::logic_error("beeper unterminated effect");
        const auto hz=effect.words[effect.cursor/2];
        if(hz){effect.cursor=std::uint16_t(effect.cursor+2);frequency(hz);}
        else{effect.cursor=0;state_.active=0;silence();}
    }
    out(0,0x20);
}
std::optional<int> Beeper::consume(const Request& q,const Reader& reader){
    if(q.kind==Kind::beep_file){if(!reader)throw std::invalid_argument("beeper resource reader missing");return read(reader(q.name));}
    if(q.kind==Kind::beep)return play(std::int16_t(q.a));
    return std::nullopt;
}
BeepPcm::BeepPcm(Beeper& beeper,std::uint32_t rate):beeper_(&beeper),rate_(rate){
    if(rate<8000 || rate>192000)throw std::invalid_argument("beeper sample rate");
    next_irq_=std::uint64_t(beeper.state().timer_divisor)*rate;
    generation_=beeper.state().reloads;
}
void BeepPcm::observe(std::uint64_t time){
    if(generation_!=beeper_->state().reloads){generation_=beeper_->state().reloads;reload_time_=time;}
}
std::vector<std::int16_t> BeepPcm::render(std::size_t count){
    if(count>192000u*60u)throw std::invalid_argument("beeper render block");
    observe(time_);std::vector<std::int16_t> output;output.reserve(count);
    for(std::size_t i=0;i<count;++i){
        time_+=beeper_->clock_hz();
        while(next_irq_<=time_){beeper_->tick();observe(next_irq_);next_irq_+=std::uint64_t(beeper_->state().timer_divisor)*rate_;}
        const auto& s=beeper_->state();
        if(!s.gate)output.push_back(0);
        else{
            const auto period=std::uint64_t(s.divisor ? s.divisor : 65536u)*rate_;
            const auto high=std::uint64_t((unsigned(s.divisor ? s.divisor : 65536u)+1u)/2u)*rate_;
            output.push_back((time_-reload_time_)%period<high ? 8192 : -8192);
        }
        ++samples_;
    }
    return output;
}
}
