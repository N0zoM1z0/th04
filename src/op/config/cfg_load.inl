void near cfg_load(void)
{
	cfg_t cfg;

	cfg_load_and_set_resident(cfg, CFG_FN);

	resident->rank = cfg.opts.rank;
	resident->cfg_lives = cfg.opts.lives;
	resident->cfg_bombs = cfg.opts.bombs;
	resident->bgm_mode = cfg.opts.bgm_mode;
	resident->se_mode = cfg.opts.se_mode;
	resident->turbo_mode = cfg.opts.turbo_mode;

	if((resident->cfg_lives > 6) || (resident->cfg_lives == 0)) {
		resident->cfg_lives = 3;
	}
	if(resident->cfg_bombs > 2) {
		resident->cfg_bombs = 2;
	}
	if(resident->bgm_mode >= 3) {
		resident->bgm_mode = 0;
	}
	if(resident->se_mode >= 3) {
		resident->se_mode = 0;
	}
}
