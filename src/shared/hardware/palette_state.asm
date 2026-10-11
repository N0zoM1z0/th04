; TH04-local 16-color palette storage. Both C and historical Pascal spelling
; refer to the same words/bytes in DGROUP.

    .8086
    .model use16 large SHARED
    .data

public _PaletteTone, PaletteTone, _Palettes, Palettes
public _PalettesInit, PalettesInit
public _PaletteNote, PaletteNote

PaletteTone label word
_PaletteTone dw 100

Palettes label byte
_Palettes db 48 dup (0) ; 16 RGB triplets, 8 bits per component

PalettesInit label byte
_PalettesInit db 000h,000h,000h, 000h,000h,0FFh
              db 0FFh,000h,000h, 0FFh,000h,0FFh
              db 000h,0FFh,000h, 000h,0FFh,0FFh
              db 0FFh,0FFh,000h, 0FFh,0FFh,0FFh
              db 077h,077h,077h, 000h,000h,0AAh
              db 0AAh,000h,000h, 0AAh,000h,0AAh
              db 000h,0AAh,000h, 000h,0AAh,0AAh
              db 0AAh,0AAh,000h, 0AAh,0AAh,0AAh

PaletteNote label word
_PaletteNote dw 0 ; zero selects analog RGB; nonzero selects LCD eight shades

end
