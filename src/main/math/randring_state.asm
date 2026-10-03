; MAIN-owned random-number ring and shared cursor.
;
; Keep these symbols adjacent and in this order. All randring1_* and
; randring2_* accessors read an overlapping word from _randring[BX] and advance
; only the low byte of _randring_p. Consequently, the BX=255 sample reads
; _randring[255] as its low byte and the pre-increment cursor value 0FFh as its
; high byte. This storage layout is observable RNG behavior.

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_BSS segment word public 'BSS' use16
public _randring, _randring_p
_randring   db 256 dup(?)
_randring_p dw ?
_BSS ends

DGROUP group _BSS
end
