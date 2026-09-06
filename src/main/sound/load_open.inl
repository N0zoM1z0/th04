	// DOS file open
	reinterpret_cast<char near *>(_DX) = snd_load_fn;
	_AX = 0x3D00;
	geninterrupt(0x21);
