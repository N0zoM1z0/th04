#include "audio_device_api.hpp"
#include <algorithm>
#include <array>
#include <atomic>
#include <cstring>
#include <stdexcept>

namespace th04::portable::audio {
static_assert(sizeof(pmd::StereoSample)==4,"host PCM requires two signed16 channels");
#ifdef _WIN32
namespace {
class WaveDevice final:public Device {
    static constexpr std::size_t block_frames=2048,block_count=8;
    struct Block {
        WAVEHDR header{};std::array<pmd::StereoSample,block_frames> samples{};
        std::atomic<bool> available{true};std::size_t frames=0;bool prepared=false;
    };
    struct Storage {
        std::array<Block,block_count> blocks;
        std::atomic<std::size_t> queued{0};
    };
    Api api_;HWAVEOUT handle_=nullptr;std::unique_ptr<Storage> storage_=std::make_unique<Storage>();
    static void CALLBACK callback(HWAVEOUT,UINT message,DWORD_PTR instance,DWORD_PTR first,DWORD_PTR) {
        if(message!=WOM_DONE)return;
        auto& self=*reinterpret_cast<Storage*>(instance);
        auto* header=reinterpret_cast<WAVEHDR*>(first);
        auto& block=self.blocks[header->dwUser];
        self.queued.fetch_sub(block.frames,std::memory_order_relaxed);
        block.available.store(true,std::memory_order_release);
    }
    static void check(MMRESULT result,const char* operation) {
        if(result!=MMSYSERR_NOERROR)
            throw std::runtime_error(std::string(operation)+" failed (WinMM "+std::to_string(result)+")");
    }
    void close() noexcept {
        if(!handle_)return;
        bool released=api_.reset(handle_)==MMSYSERR_NOERROR;
        for(auto& block:storage_->blocks)if(block.prepared)
            released=(api_.unprepare(handle_,&block.header,sizeof(WAVEHDR))==MMSYSERR_NOERROR) && released;
        released=(api_.close(handle_)==MMSYSERR_NOERROR) && released;handle_=nullptr;
        // A refusing driver may still own these headers and callback context.
        // Quarantine this bounded allocation until process exit in that case.
        if(!released)storage_.release();
    }
public:
    explicit WaveDevice(Api api):api_(api) {
        if(!api.open || !api.prepare || !api.write || !api.reset || !api.unprepare || !api.close)
            throw std::invalid_argument("incomplete WinMM audio API");
        WAVEFORMATEX format{};format.wFormatTag=WAVE_FORMAT_PCM;format.nChannels=2;
        format.nSamplesPerSec=sample_rate;format.wBitsPerSample=16;
        format.nBlockAlign=4;format.nAvgBytesPerSec=sample_rate*4;
        check(api_.open(&handle_,WAVE_MAPPER,&format,reinterpret_cast<DWORD_PTR>(&callback),
                        reinterpret_cast<DWORD_PTR>(storage_.get()),CALLBACK_FUNCTION),"waveOutOpen");
        try {
            for(std::size_t i=0;i<storage_->blocks.size();++i) {
                auto& block=storage_->blocks[i];block.header.lpData=reinterpret_cast<char*>(block.samples.data());
                block.header.dwBufferLength=DWORD(sizeof(block.samples));block.header.dwUser=i;
                check(api_.prepare(handle_,&block.header,sizeof(WAVEHDR)),"waveOutPrepareHeader");
                block.prepared=true;
            }
        } catch(...) {close();throw;}
    }
    ~WaveDevice() override {close();}
    std::size_t queued_frames() const override {return storage_->queued.load(std::memory_order_relaxed);}
    Push push(const pmd::StereoSample* samples,std::size_t frames) override {
        const auto needed=(frames+block_frames-1)/block_frames;
        std::size_t free=0;
        for(const auto& block:storage_->blocks)free+=block.available.load(std::memory_order_acquire);
        if(free<needed)return Push::busy;
        for(auto& block:storage_->blocks) {
            if(!frames)break;
            if(!block.available.load(std::memory_order_acquire))continue;
            block.frames=std::min(frames,block_frames);
            std::copy_n(samples,block.frames,block.samples.begin());
            block.header.dwBufferLength=DWORD(block.frames*sizeof(pmd::StereoSample));
            block.available.store(false,std::memory_order_relaxed);
            storage_->queued.fetch_add(block.frames,std::memory_order_relaxed);
            const auto result=api_.write(handle_,&block.header,sizeof(WAVEHDR));
            if(result!=MMSYSERR_NOERROR) {
                storage_->queued.fetch_sub(block.frames,std::memory_order_relaxed);
                block.available.store(true,std::memory_order_release);
                check(result,"waveOutWrite");
            }
            samples+=block.frames;frames-=block.frames;
        }
        return Push::queued;
    }
};
}
std::unique_ptr<Device> platform_device(const Api& api) {return std::make_unique<WaveDevice>(api);}
std::unique_ptr<Device> platform_device() {
    return platform_device({&waveOutOpen,&waveOutPrepareHeader,&waveOutWrite,&waveOutReset,
                            &waveOutUnprepareHeader,&waveOutClose});
}
#else
namespace {
class SdlDevice final:public Device {
    Api api_;SDL_AudioDeviceID device_=0;bool initialized_=false;
    void close() noexcept {
        if(device_) {api_.pause(device_,1);api_.clear(device_);api_.close(device_);device_=0;}
        if(initialized_) {api_.quit(SDL_INIT_AUDIO);initialized_=false;}
    }
public:
    explicit SdlDevice(Api api):api_(api) {
        if(!api.init || !api.quit || !api.open || !api.pause || !api.queue || !api.queued ||
           !api.clear || !api.close || !api.error)throw std::invalid_argument("incomplete SDL audio API");
        if(api_.init(SDL_INIT_AUDIO)!=0)throw std::runtime_error(api_.error());
        initialized_=true;
        try {
            SDL_AudioSpec desired{},obtained{};
            desired.freq=sample_rate;desired.format=AUDIO_S16SYS;desired.channels=2;desired.samples=1024;
            device_=api_.open(nullptr,0,&desired,&obtained,0);
            if(!device_)throw std::runtime_error(api_.error());
            if(obtained.freq!=int(sample_rate) || obtained.format!=AUDIO_S16SYS || obtained.channels!=2)
                throw std::runtime_error("audio device did not retain 48kHz signed16 stereo");
            api_.pause(device_,0);
        } catch(...) {close();throw;}
    }
    ~SdlDevice() override {close();}
    std::size_t queued_frames() const override {return api_.queued(device_)/sizeof(pmd::StereoSample);}
    Push push(const pmd::StereoSample* samples,std::size_t frames) override {
        if(frames>queue_limit)throw std::length_error("oversized SDL audio block");
        if(api_.queue(device_,samples,Uint32(frames*sizeof(pmd::StereoSample)))!=0)
            throw std::runtime_error(api_.error());
        return Push::queued;
    }
};
}
std::unique_ptr<Device> platform_device(const Api& api) {return std::make_unique<SdlDevice>(api);}
std::unique_ptr<Device> platform_device() {
    return platform_device({&SDL_InitSubSystem,&SDL_QuitSubSystem,&SDL_OpenAudioDevice,&SDL_PauseAudioDevice,
                            &SDL_QueueAudio,&SDL_GetQueuedAudioSize,&SDL_ClearQueuedAudio,&SDL_CloseAudioDevice,&SDL_GetError});
}
#endif
} // namespace th04::portable::audio
