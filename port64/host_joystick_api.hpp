#pragma once
#include "host_joystick.hpp"
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

namespace th04::portable::host_joystick {
// An injected table is complete; tests never fall through to host devices.
#ifdef _WIN32
struct Api {
    decltype(&joyGetNumDevs) count;
    decltype(&joyGetDevCapsA) caps;
    decltype(&joyGetPosEx) position;
};
#else
struct Api {
    decltype(&SDL_InitSubSystem) init;
    decltype(&SDL_QuitSubSystem) quit;
    decltype(&SDL_NumJoysticks) count;
    decltype(&SDL_JoystickOpen) open;
    decltype(&SDL_JoystickClose) close;
    decltype(&SDL_JoystickUpdate) update;
    decltype(&SDL_JoystickGetAttached) attached;
    decltype(&SDL_JoystickInstanceID) identity;
    decltype(&SDL_JoystickNumAxes) axes;
    decltype(&SDL_JoystickNumHats) hats;
    decltype(&SDL_JoystickNumButtons) buttons;
    decltype(&SDL_JoystickGetAxis) axis;
    decltype(&SDL_JoystickGetHat) hat;
    decltype(&SDL_JoystickGetButton) button;
};
#endif
std::unique_ptr<Device> platform_device(const Api&);
} // namespace th04::portable::host_joystick
