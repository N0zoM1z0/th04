void near cfg_save_exit(void)
{
	cfg_t cfg = { 0 };

	file_append(CFG_FN);
	file_seek(0, SEEK_SET);

	cfg_options_update_from_resident(cfg.opts);
	cfg.opts_sum = cfg.opts.sum();
	file_write(&cfg, sizeof(cfg));
	file_close();
}
