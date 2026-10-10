#include "audio_output.hpp"
#include "sound_runtime.hpp"
#include <algorithm>
#include <iostream>
#include <stdexcept>
using namespace th04::portable;
using namespace audio;
namespace {
void require(bool b,const char* message){if(!b)throw std::runtime_error(message);}
struct State {unsigned opens=0,closes=0;std::size_t queued=0;bool busy=false,fail=false;
    std::vector<pmd::StereoSample> values;};
class Capture final:public Device {
    State& state;
public:
    explicit Capture(State& s):state(s){++state.opens;}
    ~Capture(){++state.closes;}
    std::size_t queued_frames()const override{return state.queued;}
    Push push(const pmd::StereoSample* p,std::size_t n)override{
        if(state.fail)throw std::runtime_error("write failed");
        if(state.busy)return Push::busy;
        state.values.insert(state.values.end(),p,p+n);return Push::queued;
    }
};
void balance(const Output& o){const auto& s=o.statistics();require(s.generated==s.submitted+s.suppressed+s.dropped,"frame accounting");}
}
int main(){try{
    State s;unsigned reports=0;
    auto factory=[&]{return std::make_unique<Capture>(s);};
    const std::vector<pmd::StereoSample> block={{-32768,32767},{123,-456}};
    {Output mute(true,factory);mute.stereo(block);mute.mono({-32768,0,32767});
     require(!s.opens && !mute.statistics().open_attempts && mute.statistics().suppressed==5,"mute invoked factory");balance(mute);}
    {Output output(false,factory,[&](const auto&){++reports;});output.stereo({});
     require(!s.opens,"empty block opened audio");output.stereo(block);output.mono({-32768,0,32767});
     require(s.opens==1 && s.values.size()==5 && s.values[0].left==-32768 && s.values[0].right==32767 &&
             s.values[1].left==123 && s.values[1].right==-456 && s.values[2].left==-32768 &&
             s.values[2].right==-32768 && s.values[4].left==32767 && s.values[4].right==32767,"PCM identity/mono channels");
     s.queued=queue_limit-2;output.stereo(block);s.queued=queue_limit-1;output.stereo(block);
     s.queued=0;s.busy=true;output.stereo(block);s.busy=false;
     output.stereo(std::vector<pmd::StereoSample>(queue_limit+1));balance(output);
     require(output.statistics().submitted==7 && output.statistics().dropped==queue_limit+5,"bounded queue/drop policy");
     s.fail=true;output.stereo(block);output.stereo(block);balance(output);
     require(output.statistics().failed && output.statistics().suppressed==4 && reports==1 &&
             s.opens==1 && s.closes==1 && output.error()=="write failed","failure cleanup/retry");}
    unsigned attempts=0;
    Output failed(false,[&]()->std::unique_ptr<Device>{++attempts;throw std::runtime_error("open failed");});
    failed.mono({1});failed.mono({2});balance(failed);
    require(attempts==1 && failed.statistics().suppressed==2,"open failure retried");
    Output nofactory(false,{});nofactory.stereo(block);balance(nofactory);
    require(nofactory.statistics().failed,"missing factory was accepted");
    Output reporter(false,{},[](const auto&){throw std::runtime_error("reporter failed");});
    reporter.stereo(block);balance(reporter);require(reporter.statistics().failed,"failed reporter stopped transport isolation");
    State beeper;Output mono(false,[&]{return std::make_unique<Capture>(beeper);});
    std::vector<std::int16_t> original;
    sound::Runtime runtime([](const auto& name)->std::optional<sound::Bytes>{
        if(name=="miko.efs")return sound::Bytes{'4','4','0',' ','0',' '};return std::nullopt;
    },{},{},[&](const auto& v){original=v;mono.mono(v);});
    runtime.configure(0,2);runtime.handle({sound::ActionKind::load,0xb00,"miko"});
    runtime.handle({sound::ActionKind::force,1,{}});runtime.advance(17730496);
    require(original.size()==851 && beeper.values.size()==851 && std::any_of(original.begin(),original.end(),[](auto v){return v!=0;}),"real beeper PCM transport");
    for(std::size_t i=0;i<original.size();++i)require(beeper.values[i].left==original[i] && beeper.values[i].right==original[i],"beeper transport altered PCM");
    std::cout<<"Audio transport mute, lazy open, PCM identity, bounds and failure contracts PASS\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
