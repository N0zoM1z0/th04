#include "pmd_pcm.hpp"
#include "vendor/ymfm/src/ymfm_opn.h"
#include <algorithm>
#include <limits>
#include <stdexcept>

namespace th04::portable::pmd {
struct OpnPcm::Impl:ymfm::ymfm_interface {
    Board board;std::uint32_t hz,step,quantum;
    Bytes rom;PcmSink sink;
    std::unique_ptr<ymfm::ym2203> opn;std::unique_ptr<ymfm::ym2608> opna;
    std::uint64_t now=0,next_chip,next_pcm=0,pcm_floor=0,count=0,last_pcm=0;
    std::uint32_t pcm_fraction=0;
    std::array<std::uint64_t,2> timers{};
    ChipLevels raw{},averaged{};
    std::array<std::int64_t,3> area{};
    std::array<std::int64_t,2> previous{},filtered{};
    Impl(Board b,std::uint32_t frequency,Bytes data,PcmSink action)
        :board(b),hz(frequency),step(b==Board::fm26 ? 4 : 8),quantum(18*step),rom(std::move(data)),sink(std::move(action)),next_chip(quantum) {
        if(b!=Board::fm26 && b!=Board::fm86 && b!=Board::speakboard)throw std::invalid_argument("PCM board");
        if(hz<48000 || hz>1000000000)throw std::invalid_argument("PCM master frequency");
        if((b!=Board::fm26 && rom.size()!=8192) || (!rom.empty() && rom.size()!=8192))throw std::invalid_argument("OPNA rhythm ROM size");
        if(b==Board::fm26) {opn=std::make_unique<ymfm::ym2203>(*this);opn->reset();}
        else {opna=std::make_unique<ymfm::ym2608>(*this);opna->reset();}
        schedule_pcm();
    }
    void ymfm_set_timer(std::uint32_t t,std::int32_t clocks) override {timers.at(t)=clocks<0 ? 0 : now+std::uint32_t(clocks);}
    std::uint8_t ymfm_external_read(ymfm::access_class type,std::uint32_t address) override {
        if(type==ymfm::ACCESS_ADPCM_A && !rom.empty())return rom[address&8191];
        // PMD external ADPCM memory ownership is not joined to this renderer.
        if(type==ymfm::ACCESS_ADPCM_B)throw std::runtime_error("external ADPCM memory not installed");
        return 0;
    }
    void schedule_pcm() {
        const auto numerator=std::uint64_t(pcm_fraction)+hz;
        pcm_floor+=numerator/48000;pcm_fraction=std::uint32_t(numerator%48000);
        next_pcm=pcm_floor+(pcm_fraction!=0);
    }
    void generate() {
        if(opn) {ymfm::ym2203::output_data value;opn->generate(&value);raw={value.data[0],value.data[0],value.data[1]+value.data[2]+value.data[3]};}
        else {ymfm::ym2608::output_data value;opna->generate(&value);raw={value.data[0],value.data[1],value.data[2]};}
    }
    std::int16_t mix(unsigned channel,std::int64_t value) {
        // Explicit portable output adapter: half gain, then a fixed 48 kHz
        // DC blocker. This is not a measured PC-98 analogue transfer function.
        value/=2;
        const auto result=value-previous[channel]+filtered[channel]*32700/32768;
        previous[channel]=value;filtered[channel]=result;
        return std::int16_t(std::max<std::int64_t>(-32768,std::min<std::int64_t>(32767,result)));
    }
    void emit() {
        const auto width=now-last_pcm;
        averaged={std::int32_t(area[0]/std::int64_t(width)),std::int32_t(area[1]/std::int64_t(width)),std::int32_t(area[2]/std::int64_t(width))};
        StereoSample value{mix(0,std::int64_t(averaged.left)+averaged.ssg),mix(1,std::int64_t(averaged.right)+averaged.ssg)};
        area={};last_pcm=now;++count;schedule_pcm();if(sink)sink(value);
    }
    void advance(std::uint64_t end) {
        constexpr auto headroom=std::uint64_t(4096)*144;
        if(end<now || end-now>1000000000 || end>std::numeric_limits<std::uint64_t>::max()-headroom)throw std::invalid_argument("PCM cycle step");
        while(now<end) {
            auto next=std::min(end,std::min(next_chip,next_pcm));
            for(auto t:timers)if(t)next=std::min(next,t);
            const auto duration=next-now;
            area[0]+=std::int64_t(duration)*raw.left;area[1]+=std::int64_t(duration)*raw.right;area[2]+=std::int64_t(duration)*raw.ssg;
            now=next;
            // Advance the real FM counter before coincident timer expirations,
            // preserving the clock epoch used by the independent timer Oracle.
            if(now==next_chip) {generate();next_chip+=step;}
            const std::array<bool,2> due{{timers[0] && timers[0]==now,timers[1] && timers[1]==now}};
            for(unsigned t=0;t<2;++t)if(due[t])m_engine->engine_timer_expired(t);
            if(now==next_pcm)emit();
        }
    }
    void write(FmWrite value) {
        if(value.bank>1)throw std::invalid_argument("PCM register bank");
        // PMD's universal installation touches the absent OPNA bank even on
        // a 26K profile. Those physical writes have no YM2203 destination.
        if(opn && value.bank)return;
        if(!value.bank && value.address>=0x2d && value.address<=0x2f)throw std::invalid_argument("PCM prescaler not default");
        if(opn) {opn->write_address(value.address);opn->write_data(value.value);}
        else {opna->write(value.bank*2,value.address);opna->write(value.bank*2+1,value.value);}
    }
};
OpnPcm::OpnPcm(Board board,std::uint32_t hz,Bytes rom,PcmSink sink):impl_(std::make_unique<Impl>(board,hz,std::move(rom),std::move(sink))) {}
OpnPcm::~OpnPcm()=default;
void OpnPcm::write(std::uint64_t cycle,FmWrite value) {impl_->advance(cycle);impl_->write(value);}
void OpnPcm::advance_to(std::uint64_t cycle) {impl_->advance(cycle);}
std::uint64_t OpnPcm::cycles() const {return impl_->now;}
std::uint64_t OpnPcm::samples() const {return impl_->count;}
ChipLevels OpnPcm::levels() const {return impl_->averaged;}
PcmPlayer::PcmPlayer(Board board,std::uint32_t hz,Bytes rom,PcmSink sink):pcm_(board,hz,std::move(rom),std::move(sink)) {
    player_=std::make_unique<ClockedPlayer>(board,hz,[this](FmWrite value){
        if(!player_)throw std::logic_error("PCM write before resident clock construction");
        pcm_.write(player_->timers().cycles(),value);
    },[this](SsgWrite value){
        if(!player_)throw std::logic_error("SSG write before resident clock construction");
        pcm_.write(player_->timers().cycles(),{0,value.address,value.value});
    });
    for(auto value:std::vector<FmWrite>{{0,0x29,0x83},{0,0x24,0},{0,0x25,0},{0,0x26,200},{0,0x27,0x3f}})pcm_.write(0,value);
}
void PcmPlayer::initialize(FmWrite value) {
    if(player_->timers().cycles())throw std::logic_error("PCM initialization after epoch zero");
    pcm_.write(0,value);
}
void PcmPlayer::advance_cycles(std::uint64_t value) {player_->advance_cycles(value);pcm_.advance_to(player_->timers().cycles());}
void PcmPlayer::advance_ns(std::uint64_t value) {player_->advance_ns(value);pcm_.advance_to(player_->timers().cycles());}
}
