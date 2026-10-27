#pragma once

#ifdef _WIN32
#include <windows.h>
#include <cstdlib>
#include <string>
#include "host_window.hpp"

namespace th04::portable::host_window {
// One deadline per displayed refresh. SetTimer's 10 ms minimum and coarse
// wakeups otherwise alternate short and double-length presentation intervals.
// No process-wide timeBeginPeriod request or spin wait is needed.
class FrameTimer {
public:
    FrameTimer() {
        const auto legacy=std::getenv("TH04_LEGACY_WINDOW_TIMER");
        if(legacy && std::string(legacy)=="1")return;
        constexpr DWORD high_resolution=0x00000002;
        timer_=CreateWaitableTimerExW(nullptr,nullptr,high_resolution,
                                     TIMER_MODIFY_STATE|SYNCHRONIZE);
    }
    ~FrameTimer() {
        if(timer_) {CancelWaitableTimer(timer_);CloseHandle(timer_);}
    }
    FrameTimer(const FrameTimer&)=delete;
    FrameTimer& operator=(const FrameTimer&)=delete;
    HANDLE handle()const{return timer_;}
    bool arm(std::int64_t deadline) {
        if(!timer_)return false;
        const auto remaining=deadline-now_ns();
        LARGE_INTEGER due{};
        due.QuadPart=-(remaining>0 ? (remaining+99)/100 : 1);
        return SetWaitableTimer(timer_,&due,0,nullptr,nullptr,FALSE)!=FALSE;
    }
private:
    HANDLE timer_=nullptr;
};
}
#endif
