; MAIN-owned HUD glyph rows and color tables.
;
; The glyph IDs and color attributes are the maintained TH04 gaiji contract;
; the target HUD data fragments establish their element widths and ordering.

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_DATA segment word public 'DATA' use16
public _hud_bar_max
_hud_bar_max db 030h, 031h, 032h, 033h, 034h, 035h, 036h, 037h, 0

public _gHUD_HP_BLANK
_gHUD_HP_BLANK db 8 dup(2), 0

public _HUD_HP_COLORS, _HUD_POWER_COLORS
_HUD_HP_COLORS    db 041h, 061h, 0A1h, 0C1h, 0E1h
_HUD_POWER_COLORS db 041h, 041h, 041h, 061h, 061h
                   db 021h, 081h, 0A1h, 0C1h, 0E1h

public _gsSCORE, _gsHISCORE, _gsREIGEKI, _gsREIMU
public _gsREIRYOKU, _gsBOMB, _gsPLAYER, _gsPOWER, _gsENEMY
_gsSCORE   db 0D7h, 0D8h, 0D9h, 0, 0
_gsHISCORE db 0D6h, 0D7h, 0D8h, 0D9h, 0
_gsREIGEKI db 0DAh, 0DBh, 0, 0, 0
_gsREIMU   db 0DCh, 0DDh, 0, 0, 0
_gsREIRYOKU db 0DEh, 0DFh, 0, 0, 0
_gsBOMB    db 0E0h, 0E1h, 0, 0, 0
_gsPLAYER  db 0E2h, 0E3h, 0, 0, 0
_gsPOWER   db 0E4h, 0E5h, 0, 0, 0
_gsENEMY   db 0EAh, 0EBh, 0ECh, 0, 0

public _glEASY
_glEASY db 0AEh, 0AAh, 0BCh, 0C2h, 2, 2, 2, 0
; hud_put indexes four eight-byte rank rows. Bold capitals follow digits
; in the maintained gaiji alphabet, beginning at A=AAh.
HUD_ALPHA_A equ 0AAh
db HUD_ALPHA_A + ('N'-'A'), HUD_ALPHA_A + ('O'-'A')
db HUD_ALPHA_A + ('R'-'A'), HUD_ALPHA_A + ('M'-'A')
db HUD_ALPHA_A + ('A'-'A'), HUD_ALPHA_A + ('L'-'A'), 2, 0
db HUD_ALPHA_A + ('H'-'A'), HUD_ALPHA_A + ('A'-'A')
db HUD_ALPHA_A + ('R'-'A'), HUD_ALPHA_A + ('D'-'A'), 2, 2, 2, 0
db HUD_ALPHA_A + ('L'-'A'), HUD_ALPHA_A + ('U'-'A')
db HUD_ALPHA_A + ('N'-'A'), HUD_ALPHA_A + ('A'-'A')
db HUD_ALPHA_A + ('T'-'A'), HUD_ALPHA_A + ('I'-'A')
db HUD_ALPHA_A + ('C'-'A'), 0

; High-count HUD labels (Shift-JIS gaiji sequence, five two-byte glyphs).
public _hud_lives_extra, _hud_bombs_extra
_hud_lives_extra db 081h, 040h, 081h, 040h, 081h, 07Eh, 081h, 040h, 081h, 040h, 0
_hud_bombs_extra db 081h, 040h, 081h, 040h, 081h, 07Eh, 081h, 040h, 081h, 040h, 0
_DATA ends

DGROUP group _DATA
end
