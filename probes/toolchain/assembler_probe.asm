; Independent TASM OMF smoke probe; not target-derived code.
.386
.model large
.code

public _assembler_probe
_assembler_probe proc far
	mov ax, 1234h
	xor dx, dx
	ret
_assembler_probe endp

end

