; Large-model assembly ABI used by migrated PC-98 graphics providers.
; Derived from ReC98 master.lib's func.inc; only the TH04 large-model path.
.386
.model use16 large SHARED
locals
RETSIZE equ 2
DATASIZE equ 2
JMOV macro reg,lab
    mov reg,1234h
    org $-2
lab dw ?
endm
_push macro reg
    push reg
endm
_pop macro reg
    pop reg
endm
_lds macro reg,mem
    lds reg,mem
endm
_les macro reg,mem
    les reg,mem
endm
; Explicit inter-provider far call: do not relax through another code group.
_call macro dest
    db 09Ah
    dw offset dest
    dw seg dest
endm
