; MAIN-owned playfield scrolling state. The initialized stage setup assigns
; semantic values before the first gameplay use; these are BSS owners.

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_BSS segment word public 'BSS' use16
public _scroll_subpixel_line, _scroll_speed
public _scroll_line, _scroll_last_delta, _scroll_active
public _byte_250FE, _byte_25104, _word_25100
_scroll_subpixel_line db ?
_scroll_speed         db ?
_scroll_line          dw ?
_scroll_last_delta    dw ?
_scroll_active        db ?
; The driver and tile-ring source retain these address-derived publics as the
; historical OMF ABI, but use readable preprocessor aliases in expressions.
; Native initialization uses the readable labels below. Both naming surfaces
; therefore refer to one physical three-field request state.
ifdef TH04_LARGE_PRODUCT
public _scroll_row_advance_previous, _scroll_row_advance_current
public _tile_ring_scroll_row_prev
_scroll_row_advance_previous label byte
endif
_byte_250FE           db ?
ifdef TH04_LARGE_PRODUCT
_scroll_row_advance_current label byte
endif
_byte_25104           db ?
ifdef TH04_LARGE_PRODUCT
_tile_ring_scroll_row_prev label word
endif
_word_25100           dw ?
evendata
_BSS ends

DGROUP group _BSS
end
