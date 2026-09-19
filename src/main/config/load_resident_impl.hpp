#ifndef TH04_MAIN_CONFIG_LOAD_RESIDENT_IMPL_HPP
#define TH04_MAIN_CONFIG_LOAD_RESIDENT_IMPL_HPP

#include "src/shared/runtime/api.hpp"

#if (GAME == 4)
#include "src/shared/config/cfg.hpp"

#elif (GAME == 3)

// The maintained cfg_lres source is also compiled as the TH03 calibration
// producer. Preserve only the GAME3 file layout consumed by this helper.
struct resident_t;
extern resident_t far *resident;

struct cfg_options_t {
	uint8_t bgm_mode;
	uint8_t key_mode;
	uint8_t rank;
	int16_t unused;
};

struct cfg_t {
	cfg_options_t opts;
	resident_t __seg *resident;
	int8_t debug;
};

typedef char th03_cfg_options_size_check[
	(sizeof(cfg_options_t) == 5) ? 1 : -1
];
typedef char th03_cfg_size_check[(sizeof(cfg_t) == 8) ? 1 : -1];

#else
#error cfg_load_resident_ptr source is only shared by GAME3 and GAME4
#endif

static inline resident_t __seg* cfg_load_and_set_resident(
	cfg_t& cfg, const char* fn
) {
	file_ropen(fn);
	file_read(&cfg, sizeof(cfg));
	file_close();

	resident_t __seg *resident_seg = cfg.resident;
	resident = resident_seg;
	return resident_seg;
}

#endif
