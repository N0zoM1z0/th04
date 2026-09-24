#include "src/shared/platform/x86.hpp"

static const unsigned char SE_NONE = 0xFF;
static const unsigned char SND_SE_OFF = 0;
static const unsigned char SND_SE_BEEP = 2;
static const unsigned char PMD_SE_PLAY = 0x0C;
static const int PMD_INTERRUPT = 0x60;

extern unsigned char snd_se_mode;
extern unsigned char snd_se_playing;
extern unsigned char snd_se_priority_frames[];
extern unsigned char snd_se_frame;

extern "C" int far pascal bgm_sound(int num);

#pragma option -k-
#pragma codeseg SHARED se_update_01
#include "src/op/sound/se_update.inl"
