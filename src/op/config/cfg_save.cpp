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

	int8_t sum(void) const {
		return (rank + lives + bombs + bgm_mode + se_mode + turbo_mode);
	}
};

static char CFG_FN[] = "MIKO.CFG";

inline void cfg_options_update_from_resident(cfg_options_t &opts)
{
	opts.rank = resident->rank;
	opts.lives = resident->cfg_lives;
	opts.bombs = resident->cfg_bombs;
	opts.bgm_mode = resident->bgm_mode;
	opts.se_mode = resident->se_mode;
	opts.turbo_mode = resident->turbo_mode;
}

#pragma codeseg OP_MAIN_TEXT cfg_save_01
#include "src/op/config/cfg_save.inl"
#pragma codeseg
