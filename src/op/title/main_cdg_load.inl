void near main_cdg_load(void)
{
	cdg_load_all(0, "sft1.cd2");
	cdg_load_all(10, "sft2.cd2");
	cdg_load_all(35, "car.cd2");
	cdg_load_all_noalpha(40, "sl.cd2");
}
