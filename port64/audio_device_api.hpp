#pragma once
#include "audio_device.hpp"
#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <mmsystem.h>
#else
#include <SDL.h>
#endif

namespace th04::portable::audio {
// Tests supply every function explicitly, so no missing test entry silently
// falls through to a real audio API. Production supplies the native table.
#ifdef _WIN32
struct Api {
    decltype(&waveOutOpen) open;
    decltype(&waveOutPrepareHeader) prepare;
    decltype(&waveOutWrite) write;
    decltype(&waveOutReset) reset;
    decltype(&waveOutUnprepareHeader) unprepare;
    decltype(&waveOutClose) close;
};
#else
struct Api {
    decltype(&SDL_InitSubSystem) init;
    decltype(&SDL_QuitSubSystem) quit;
    decltype(&SDL_OpenAudioDevice) open;
    decltype(&SDL_PauseAudioDevice) pause;
    decltype(&SDL_QueueAudio) queue;
    decltype(&SDL_GetQueuedAudioSize) queued;
    decltype(&SDL_ClearQueuedAudio) clear;
    decltype(&SDL_CloseAudioDevice) close;
    decltype(&SDL_GetError) error;
};
#endif
std::unique_ptr<Device> platform_device(const Api&);
} // namespace th04::portable::audio
