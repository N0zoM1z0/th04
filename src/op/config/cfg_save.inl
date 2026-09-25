void near cfg_save(void)
{
	union {
		int8_t sum;
		int16_t space;
	} u1;
	cfg_options_t opts;

	file_append(CFG_FN);
	file_seek(0, SEEK_SET);

	cfg_options_update_from_resident(opts);
	file_write(&opts, sizeof(cfg_options_t));

	file_seek(9, SEEK_SET);

	u1.sum = opts.sum();
	file_write(&u1.sum, sizeof(u1.sum));
	file_close();
}
