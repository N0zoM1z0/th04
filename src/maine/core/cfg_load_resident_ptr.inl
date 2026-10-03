resident_t __seg* near cfg_load_resident_ptr(void)
{
	cfg_t cfg;
	// The file embeds a real-mode segment, not serialized resident contents.
	// ZUN.COM owns that paragraph block; each overlay only installs a far
	// pointer in its own DGROUP.
	file_ropen("MIKO.CFG");
	file_read(&cfg, sizeof(cfg));
	file_close();

	resident_t __seg *resident_segment = cfg.resident;
	resident = resident_segment;
	return resident_segment;
}
