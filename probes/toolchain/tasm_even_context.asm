; TASM 5.0 EVEN fill control: preceding source kind versus segment class.
.386

DATA_IN_CODE segment word public 'CODE' use16
    db 1
    even
DATA_IN_CODE ends

DATA_IN_DATA segment word public 'DATA' use16
    db 1
    even
DATA_IN_DATA ends

INSTR_IN_DATA segment word public 'DATA' use16
    nop
    even
INSTR_IN_DATA ends

INSTR_IN_CODE segment word public 'CODE' use16
    nop
    even
INSTR_IN_CODE ends

end
