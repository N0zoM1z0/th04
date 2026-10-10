// Every API entry below is fake. This program never initializes or opens a
// real audio backend, including when run on actual Windows.
#include "audio_device_api.hpp"
#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace th04::portable;
using namespace audio;
namespace {
void require(bool b,const char* message){if(!b)throw std::runtime_error(message);}
std::vector<pmd::StereoSample> input(5000,{-32768,32767});
#ifdef _WIN32
struct State {
    unsigned opens=0,prepared=0,writes=0,resets=0,unprepared=0,closed=0;
    unsigned fail_prepare=0;bool fail_open=false,fail_write=false,refuse_cleanup=false;
    DWORD_PTR callback=0,instance=0;
    std::vector<WAVEHDR*> pending;
    std::vector<pmd::StereoSample> copied;
} s;
using Callback=void (CALLBACK*)(HWAVEOUT,UINT,DWORD_PTR,DWORD_PTR,DWORD_PTR);
void done(WAVEHDR* h){reinterpret_cast<Callback>(s.callback)(reinterpret_cast<HWAVEOUT>(1),WOM_DONE,s.instance,reinterpret_cast<DWORD_PTR>(h),0);}
MMRESULT WINAPI open(LPHWAVEOUT h,UINT id,LPCWAVEFORMATEX f,DWORD_PTR cb,DWORD_PTR context,DWORD flags){
    ++s.opens;require(id==WAVE_MAPPER && flags==CALLBACK_FUNCTION && f->wFormatTag==WAVE_FORMAT_PCM &&
        f->nChannels==2 && f->nSamplesPerSec==48000 && f->wBitsPerSample==16 && f->nBlockAlign==4 &&
        f->nAvgBytesPerSec==192000 && f->cbSize==0,"WinMM PCM format");
    if(s.fail_open)return MMSYSERR_ERROR;
    *h=reinterpret_cast<HWAVEOUT>(1);s.callback=cb;s.instance=context;return 0;
}
MMRESULT WINAPI prepare(HWAVEOUT,WAVEHDR* h,UINT size){
    require(size==sizeof(WAVEHDR) && h->lpData && h->dwBufferLength==8192 && h->dwFlags==0,"stable prepared buffer");
    ++s.prepared;if(s.fail_prepare==s.prepared)return MMSYSERR_ERROR;return 0;
}
MMRESULT WINAPI write(HWAVEOUT,WAVEHDR* h,UINT size){
    require(size==sizeof(WAVEHDR) && h->dwBufferLength%4==0 && h->dwBufferLength<=8192,"WinMM frame bytes");
    ++s.writes;if(s.fail_write)return MMSYSERR_ERROR;
    require(std::find(s.pending.begin(),s.pending.end(),h)==s.pending.end(),"reused driver-owned buffer");
    s.pending.push_back(h);auto p=reinterpret_cast<pmd::StereoSample*>(h->lpData);
    s.copied.insert(s.copied.end(),p,p+h->dwBufferLength/4);return 0;
}
MMRESULT WINAPI reset(HWAVEOUT){++s.resets;if(s.refuse_cleanup)return WAVERR_STILLPLAYING;
    for(auto h:s.pending)done(h);s.pending.clear();return 0;}
MMRESULT WINAPI unprepare(HWAVEOUT,WAVEHDR*,UINT){++s.unprepared;return s.refuse_cleanup ? WAVERR_STILLPLAYING : 0;}
MMRESULT WINAPI close(HWAVEOUT){++s.closed;return s.refuse_cleanup ? WAVERR_STILLPLAYING : 0;}
Api fake(){return {&open,&prepare,&write,&reset,&unprepare,&close};}
void tests(){
    {auto d=platform_device(fake());require(s.prepared==8,"WinMM slot count");
     require(d->push(input.data(),input.size())==Push::queued && d->queued_frames()==5000,"WinMM multi-block accounting");
     auto first=s.pending.front();s.pending.erase(s.pending.begin());done(first);
     require(d->queued_frames()==2952,"WinMM completed frames");
     require(d->push(input.data(),7)==Push::queued && s.pending.back()==first,"WinMM completed slot reuse");
     for(unsigned i=0;i<5;++i)require(d->push(input.data(),1)==Push::queued,"WinMM remaining slots");
     const auto before=s.writes;require(d->push(input.data(),1)==Push::busy && s.writes==before,"WinMM busy overwrote slot");
     require(s.copied.size()==5012 && s.copied[0].left==-32768 && s.copied[0].right==32767,"WinMM immutable PCM copy");}
    require(s.resets==1 && s.unprepared==8 && s.closed==1 && s.pending.empty(),"WinMM close ownership");
    s=State{};s.fail_prepare=3;bool failed=false;
    try{platform_device(fake());}catch(const std::runtime_error&){failed=true;}
    require(failed && s.unprepared==2 && s.closed==1,"WinMM partial prepare cleanup");
    s=State{};s.fail_open=true;failed=false;
    try{platform_device(fake());}catch(const std::runtime_error&){failed=true;}
    require(failed && s.prepared==0 && s.closed==0,"WinMM failed open cleanup");
    s=State{};{auto d=platform_device(fake());s.fail_write=true;
     bool failed=false;try{d->push(input.data(),1);}catch(const std::runtime_error&){failed=true;}
     require(failed && d->queued_frames()==0,"WinMM failed write ownership");}
    s=State{};{auto d=platform_device(fake());d->push(input.data(),1);s.refuse_cleanup=true;}
    require(s.pending.size()==1,"WinMM refused cleanup context");
    // The quarantined header and callback context remain alive after d dies.
    done(s.pending.front());s.pending.clear();
    auto incomplete=fake();incomplete.open=nullptr;bool rejected=false;
    try{platform_device(incomplete);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"WinMM incomplete table reached API");
}
#else
struct State {
    unsigned init=0,quit=0,opened=0,closed=0,cleared=0,paused=0,started=0;
    Uint32 queued=0;bool fail_init=false,fail_open=false,bad_format=false,fail_queue=false;
    std::vector<pmd::StereoSample> copied;
} s;
int init(Uint32 f){require(f==SDL_INIT_AUDIO,"SDL init scope");++s.init;return s.fail_init ? -1 : 0;}
void quit(Uint32 f){require(f==SDL_INIT_AUDIO,"SDL quit scope");++s.quit;}
SDL_AudioDeviceID open(const char* name,int capture,const SDL_AudioSpec* want,SDL_AudioSpec* got,int flags){
    ++s.opened;require(!name && capture==0 && flags==0 && want->freq==48000 && want->format==AUDIO_S16SYS &&
        want->channels==2 && want->samples==1024 && !want->callback,"SDL PCM format");
    if(s.fail_open)return 0;*got=*want;if(s.bad_format)got->freq=44100;return 7;
}
void pause(SDL_AudioDeviceID id,int value){require(id==7,"SDL device identity");if(value)++s.paused;else ++s.started;}
int queue(SDL_AudioDeviceID id,const void* data,Uint32 bytes){
    require(id==7 && bytes%4==0,"SDL frame bytes");if(s.fail_queue)return -1;
    auto p=static_cast<const pmd::StereoSample*>(data);s.copied.insert(s.copied.end(),p,p+bytes/4);s.queued+=bytes;return 0;
}
Uint32 queued(SDL_AudioDeviceID id){require(id==7,"SDL queue identity");return s.queued;}
void clear(SDL_AudioDeviceID id){require(id==7,"SDL clear identity");++s.cleared;s.queued=0;}
void close(SDL_AudioDeviceID id){require(id==7 && s.paused==1 && s.cleared==1,"SDL close order");++s.closed;}
const char* error(){return "fake SDL failure";}
Api fake(){return {&init,&quit,&open,&pause,&queue,&queued,&clear,&close,&error};}
void tests(){
    {auto d=platform_device(fake());require(s.started==1,"SDL remains paused");
     require(d->push(input.data(),5000)==Push::queued && d->queued_frames()==5000 && s.queued==20000 &&
             s.copied.size()==5000 && s.copied[0].left==-32768 && s.copied[0].right==32767,"SDL copied frame count");}
    require(s.init==1 && s.quit==1 && s.closed==1 && s.queued==0,"SDL cleanup ownership");
    for(unsigned mode=0;mode<3;++mode){s=State{};s.fail_init=mode==0;s.fail_open=mode==1;s.bad_format=mode==2;
        bool failed=false;try{platform_device(fake());}catch(const std::runtime_error&){failed=true;}
        require(failed && s.quit==(mode==0 ? 0u : 1u) && s.closed==(mode==2 ? 1u : 0u),"SDL failure unwind");}
    s=State{};{auto d=platform_device(fake());s.fail_queue=true;bool failed=false;
        try{d->push(input.data(),1);}catch(const std::runtime_error&){failed=true;}
        require(failed && d->queued_frames()==0,"SDL queue failure");}
    auto incomplete=fake();incomplete.open=nullptr;const auto before=s.init;bool rejected=false;
    try{platform_device(incomplete);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected && s.init==before,"SDL incomplete table reached API");
}
#endif
}
int main(){try{tests();std::cout<<"Production audio backend with exclusively fake APIs:format, copying, ownership, failures PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
