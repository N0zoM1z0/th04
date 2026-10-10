#pragma once
#include "audio_output.hpp"

namespace th04::portable::audio {
// Calling this factory opts into the platform device. Merely creating a
// muted Output does not initialize an audio subsystem or open a device.
std::unique_ptr<Device> platform_device();
} // namespace th04::portable::audio
