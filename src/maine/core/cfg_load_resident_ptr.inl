resident_t __seg* near cfg_load_resident_ptr(void)
{
	cfg_t cfg;
	file_ropen("MIKO.CFG");
	file_read(&cfg, sizeof(cfg));
	file_close();

	resident_t __seg *resident_seg = cfg.resident;
	resident = resident_seg;
	return resident_seg;
}
