; MAIN-owned score/config storage.
;
; The pointer and score-section owners are data/BSS surfaces of MAIN, not
; compiler-generated stand-ins.  Their widths follow the maintained C++
; declarations in score.hpp, scoredat.hpp, and resident.hpp; the target
; combination sources corroborate the ten-entry TH04 score-section layout.

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_DATA segment word public 'DATA' use16
public _CFG_FN
_CFG_FN db 'MIKO.CFG', 0

public _SCOREDAT_FN, _SCOREDAT_FN_0, _SCOREDAT_FN_1, _SCOREDAT_FN_2
_SCOREDAT_FN   db 'GENSOU.SCR', 0
_SCOREDAT_FN_0 db 'GENSOU.SCR', 0
_SCOREDAT_FN_1 db 'GENSOU.SCR', 0
_SCOREDAT_FN_2 db 'GENSOU.SCR', 0

public _gCONTINUE_
_gCONTINUE_ db 0ACh, 0B8h, 0B7h, 0BDh, 0B2h, 0B7h, 0BEh, 0AEh

public _extends_gained, _hiscore_popup_shown
_extends_gained      db 0
_hiscore_popup_shown db 0

public _hud_gaiji_row, _temp_lebcd
_hud_gaiji_row db 9 dup(0)
_temp_lebcd    db 8 dup(0)
_DATA ends

_BSS segment word public 'BSS' use16
public _resident
_resident dd ?

public _continues_used, _score, _hiscore, _score_unused
; Continue count is the first byte of score_lebcd_t, not separate storage.
; Original MAIN0AAF:3CDA increments the score base at DGROUP4349.
_continues_used label byte
_score          db 8 dup(?)
_hiscore        db 8 dup(?)
_score_unused   db ?

public _score_delta, _score_delta_frame
_score_delta       dd ?
_score_delta_frame dd ?

public _rank, _stage_id, _entered_place
_rank           db ?
_stage_id       db ?
_entered_place  db ?

; scoredat_section_t is 4 bytes of framing followed by a 0xC0-byte TH04
; scoredat_t (10 names, 10 BCD scores, clear flag, stage bytes, and padding).
public _hi, _hi2
_hi  db 0C4h dup(?)
_hi2 db 0C4h dup(?)
_BSS ends

DGROUP group _DATA, _BSS
end
