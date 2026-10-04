#include "verdict.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <iomanip>
#include <stdexcept>
#include <sstream>

using namespace th04::portable;
using Bytes=cutscene::Bytes;
namespace {
void require(bool b,const char* why) { if(!b)throw std::runtime_error(why); }
void event(const verdict::Event& e) {
    std::cout<<verdict::kind_name(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' '<<e.e<<' ';
    if(e.data.empty())std::cout<<'-';
    else for(unsigned char c:e.data)std::cout<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(c);
    std::cout<<std::dec<<'\n';
}
}
void verdict_trace(const char* fixtures,const char* text) {
    std::ifstream f(fixtures),data(text,std::ios::binary);
    require(bool(f) && bool(data),"verdict fixtures/commentary missing");
    const Bytes commentary(std::istreambuf_iterator<char>(data),{});
    std::string line;unsigned index=0;
    while(std::getline(f,line)) {
        std::istringstream row(line);
        std::array<std::uint32_t,29> v{};
        for(auto& n:v)require(bool(row>>n),"verdict fixture field missing");
        std::string extra;require(!(row>>extra),"verdict fixture extra field");
        verdict::Input input;
        auto& r=input.resident;auto& s=r.statistics;
        r.config.rank=std::uint8_t(v[0]);r.stage=std::uint8_t(v[1]);r.end_sequence=application::EndSequence(v[2]);
        r.credit_lives=std::uint8_t(v[3]);r.credit_bombs=std::uint8_t(v[4]);r.config.turbo=bool(v[5]);
        r.graze=std::uint16_t(v[6]);r.random_seed_source=v[7];s.std_frames=std::uint16_t(v[8]);
        s.items_spawned=std::uint16_t(v[9]);s.items_collected=std::uint16_t(v[10]);
        s.point_items_collected=std::uint16_t(v[11]);s.max_valued_point_items_collected=std::uint16_t(v[12]);
        s.enemies_gone=std::uint16_t(v[13]);s.enemies_killed=std::uint16_t(v[14]);
        s.slow_frames=v[15];s.frames=v[16];input.misses=std::uint8_t(v[17]);input.bombs_used=std::uint8_t(v[18]);
        input.initial_skill=v[19];input.subtract_percentages=bool(v[20]);
        for(unsigned i=0;i<8;++i)r.score_digits[i]=std::uint8_t(v[21+i]);
        const verdict::Plan plan(input,commentary);const auto& result=plan.result();
        std::cout<<"CASE "<<index++<<'\n';
        for(const auto& e:plan.requests())event(e);
        std::cout<<"END "<<result.skill<<' '<<result.cap<<' '<<result.random_state<<' '<<result.std_frames<<' '
                 <<unsigned(result.rank)<<' '<<result.commentary_line<<" 0 0 "<<unsigned(input.subtract_percentages)<<" 2\n";
    }
    require(index>0,"verdict fixtures empty");
}
void verdict_clock(const char* commentary_file) {
    std::ifstream data(commentary_file,std::ios::binary);require(bool(data),"verdict commentary missing");
    const Bytes commentary(std::istreambuf_iterator<char>(data),{});
    for(unsigned visible=0;visible<2;++visible)for(unsigned profile=0;profile<5;++profile) {
        verdict::Input input;
        input.resident.credit_lives=3;input.resident.credit_bombs=2;input.resident.stage=5;
        input.resident.end_sequence=application::EndSequence::good;
        input.resident.statistics.frames=1000;input.resident.statistics.slow_frames=visible ? 0 : 500;
        verdict::Script script(verdict::Plan(input,commentary));
        int previous=-1;
        std::cout<<"CLOCK "<<visible<<' '<<profile<<'\n';
        while(script.status()!=verdict::Status::stopped && script.ticks()<1000) {
            const unsigned tick=script.ticks();
            const auto held=[&]() {
                if(profile==0)return tick>=160;
                if(profile==1)return tick<150 || tick>=160;
                if(profile==2)return tick<150 || (tick>=151 && tick<170) || tick>=180;
                if(profile==3)return (tick>=134 && tick<146) || tick>=180;
                return tick==150 || tick>=200;
            };
            script.advance(held() ? 0x20 : 0,[&](const verdict::Event& e) {
                std::cout<<tick<<' ';event(e);
            });
            if(script.tone()!=previous) {
                previous=script.tone();std::cout<<"PALETTE "<<tick<<' '<<previous<<'\n';
            }
        }
        require(script.status()==verdict::Status::stopped,"verdict clock did not finish");
        std::cout<<"STOP "<<script.ticks()-1<<'\n';
    }
}
void verdict_contracts() {
    verdict::Input i;
    i.resident.credit_lives=3;i.resident.credit_bombs=2;i.resident.stage=5;
    i.resident.end_sequence=application::EndSequence::good;i.resident.random_seed_source=0x12345678;
    i.resident.statistics.frames=1000;
    const Bytes text(780,' ');
    const verdict::Plan all(i,text);require(all.result().std_frames==44000,"Good completion not published");
    require(all.result().random_state==0x12345678,"equal item counts must reseed without drawing");
    verdict::Script script(all);
    while(script.status()!=verdict::Status::release && script.ticks()<1000)script.advance(0x20);
    require(script.status()==verdict::Status::release && script.tone()==100,"verdict did not finish fade/read/delay");
    const auto events=script.event_count();
    for(unsigned k=0;k<50;++k)script.advance(0x20);
    require(script.event_count()==events,"held Enter accepted as a fresh verdict press");
    script.advance(0);require(script.status()==verdict::Status::release,"one clear sample accepted as a full release");
    script.advance(0);require(script.status()==verdict::Status::press,"verdict release did not advance");
    for(unsigned k=0;k<50;++k)script.advance(0);
    require(script.event_count()==events,"verdict wait(0) fabricated timeout");
    script.advance(0x20);
    while(script.status()!=verdict::Status::stopped && script.ticks()<1000)script.advance(0x20);
    require(script.status()==verdict::Status::stopped && script.tone()==0 &&
            script.event_count()==all.requests().size(),"verdict final blackout incomplete");
    const auto end_tick=script.ticks();script.advance(0x20);require(script.ticks()==end_tick,"stopped verdict progressed");
    i.resident.statistics.slow_frames=500;
    const verdict::Plan invalid(i,{});
    require(!invalid.result().score_visible && invalid.result().commentary_line==-1,"50 percent slowdown remained assessable");
    for(const auto& e:invalid.requests())require(e.kind!=verdict::Kind::file_open,"unassessable verdict opened commentary");
    bool rejected=false;try { verdict::Plan bad(verdict::Input{},text); }
    catch(const std::invalid_argument&) { rejected=true; }
    require(rejected,"invalid starting lives accepted");
    rejected=false;
    i.resident.statistics.slow_frames=0;
    try { verdict::Plan truncated(i,{}); }catch(const std::invalid_argument&) { rejected=true; }
    require(rejected,"truncated commentary accepted");
    std::cout<<"MAINE verdict arithmetic, input and palette contracts: PASS\n";
}
