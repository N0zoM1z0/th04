bool16 snd_pmd_resident(void)
{
	_AX = 0;
	snd_interrupt_if_midi = PMD;
	snd_midi_possible = _AX;
	snd_bgm_mode = _AX; // SND_BGM_OFF
	snd_se_mode = _AX; // SND_SE_OFF

	_ES = _AX;
