#include "src/shared/platform/types.hpp"
#include "src/shared/config/resident.hpp"
#include "src/shared/runtime/api.hpp"

struct cfg_options_t {
	int8_t rank;
	int8_t lives;
	int8_t bombs;
	int8_t bgm_mode;
	int8_t se_mode;
	int8_t turbo_mode;
};

struct cfg_t {
	cfg_options_t opts;
	resident_t __seg *resident_ptr;
	int8_t debug;
	int8_t opts_sum;
};

static char CFG_FN[] = "MIKO.CFG";

static inline resident_t __seg* cfg_load_and_set_resident(
	cfg_t& cfg, const char* fn
)
{
	file_ropen(fn);
	file_read(&cfg, sizeof(cfg));
	file_close();

	resident_t __seg *resident_seg = cfg.resident_ptr;
	resident = resident_seg;
	return resident_seg;
}

#pragma codeseg OP_MAIN_TEXT cfg_load_01
#include "src/op/config/cfg_load.inl"
#pragma codeseg
