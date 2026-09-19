#ifndef TH04_SND_SND_H
#define TH04_SND_SND_H

#include "src/shared/platform/types.hpp"

typedef enum {
	KAJA_SONG_PLAY = 0x00,
	KAJA_SONG_STOP = 0x01,
	KAJA_SONG_FADE = 0x02,
	KAJA_GET_SONG_MEASURE = 0x05,
	KAJA_GET_SONG_ADDRESS = 0x06,
	KAJA_GET_VOLUME = 0x08,
	PMD_GET_DRIVER_TYPE_AND_VERSION = 0x09,
	PMD_GET_SE_ADDRESS = 0x0B,
	PMD_SE_PLAY = 0x0C,
	PMD_GET_WORKAREA_ADDRESS = 0x10,
	PMD_GET_BUFFER_SIZES = 0x22,
} kaja_func_t;

#define PMD 0x60
#define MMD 0x61

typedef struct {
	uint8_t jmp[2];
	uint8_t magic[3];
} kaja_isr_t;

#define kaja_isr_magic_matches(isr, magic1, magic2, magic3) ( \
	((kaja_isr_t *)(isr))->magic[0] == magic1 && \
	((kaja_isr_t *)(isr))->magic[1] == magic2 && \
	((kaja_isr_t *)(isr))->magic[2] == magic3 \
)

#ifdef __cplusplus
extern "C" {
#endif

extern char snd_interrupt_if_midi;
extern bool snd_midi_possible;

bool16 snd_pmd_resident(void);
bool16 snd_mmd_resident(void);
int16_t pascal snd_kaja_interrupt(int16_t ax);
void snd_delay_until_volume(uint8_t volume);
void pascal snd_delay_until_measure(int measure, unsigned int frames_if_no_bgm);

#ifdef __cplusplus
}
#endif

typedef enum {
	SND_BGM_OFF = 0,
	SND_BGM_FM26 = 1,
	SND_BGM_FM86 = 2,
	SND_BGM_MODE_COUNT = 3,
	SND_BGM_MIDI = 3,

	_snd_bgm_mode_t_FORCE_UINT8 = 0xFF
} snd_bgm_mode_t;

typedef enum {
	SND_SE_OFF = 0,
	SND_SE_FM = 1,
	SND_SE_BEEP = 2,
	SND_SE_MODE_COUNT = 3,

	_snd_se_mode_t_FORCE_INT16 = 0x7FFF
} snd_se_mode_t;

extern unsigned char snd_se_mode;
extern snd_bgm_mode_t snd_bgm_mode;

#ifdef __cplusplus
static inline bool snd_bgm_active() {
	return snd_bgm_mode;
}

static inline bool16 snd_se_active() {
	return (snd_se_mode != SND_SE_OFF);
}
#endif

#define snd_bgm_is_fm() (snd_bgm_mode != SND_BGM_MIDI)

#define snd_kaja_func(func, param) ( \
	snd_kaja_interrupt(((func) << 8) | static_cast<uint8_t>(param)) \
)

typedef enum {
	SND_LOAD_SONG = (KAJA_GET_SONG_ADDRESS << 8),
	SND_LOAD_SE = (PMD_GET_SE_ADDRESS << 8),
} snd_load_func_t;

#ifdef __cplusplus
extern "C" {
#endif

int pascal snd_determine_modes(int req_bgm_mode, int req_se_mode);
void pascal snd_load(const char fn[13], snd_load_func_t func);
void snd_se_reset(void);
void pascal snd_se_play(int new_se);
void snd_se_update(void);

#ifdef __cplusplus
}
#endif

#define snd_se_play_force(new_se) { \
	snd_se_reset(); \
	snd_se_play(new_se); \
	snd_se_update(); \
}

#endif
