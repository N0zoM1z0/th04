#pragma option -2

#include <stddef.h>

#include "compat/rec98/libs/master.lib/master.hpp"
#include "src/zun/config/defaults.hpp"

char debug = 0;

const cfg_options_t OPTS_DEFAULT = {
    RANK_SHOW_SETUP_MENU,
    CFG_LIVES_DEFAULT,
    CFG_BOMBS_DEFAULT,
    SND_BGM_FM26,
    SND_SE_FM,
    true
};

void cfg_init(resident_t __seg *resident_seg)
{
    const char *filename = CFG_FN_LOWER;
    cfg_options_t options = OPTS_DEFAULT;
    cfg_t stored_config;

    if(!file_ropen(filename)) {
create_default:
        file_create(filename);
        file_write(&options, sizeof(options));
    } else {
        file_read(&stored_config, sizeof(stored_config));
        file_close();
        if((
            stored_config.opts.rank
            + stored_config.opts.lives
            + stored_config.opts.bombs
            + stored_config.opts.bgm_mode
            + stored_config.opts.se_mode
            + stored_config.opts.turbo_mode
        ) != stored_config.opts_sum) {
            goto create_default;
        }
        file_append(filename);
        file_seek(offsetof(cfg_t, resident), 0);
    }

    file_write(&resident_seg, sizeof(resident_seg));
    file_write(&debug, sizeof(debug));
    // The original path writes this uninitialized value after creating a file.
    file_write(&stored_config.opts_sum, sizeof(stored_config.opts_sum));
    file_close();
}
