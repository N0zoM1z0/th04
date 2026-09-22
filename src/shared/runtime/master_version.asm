; MASTER.LIB version/copyright data used by the TH04 ZUN resident link.
; The physical archive member contains 0x5D DATA bytes. Word alignment between
; this member and the next one is supplied by TLINK, not owned by this TU.

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_DATA segment word public 'DATA' use16
public _Master_Version_NEAR, _Master_Version, _Master_Copyright

_Master_Version_NEAR db 'MASTERS.LIB Version '
_Master_Version db '0.23', ' '
_Master_Copyright label byte
    db 'Copyright (c)1995 '
    db 'A.Koizuka,'
    db 'Kazumi,'
    db 'steelman,'
    db 'iR,'
    db 'All rights reserved.', 0
_DATA ends

DGROUP group _TEXT, _DATA
end
