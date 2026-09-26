; DOS '$'-terminated messages printed by ZUNINIT.COM.
; UTF-8 literals are converted to CP932 before pinned TASM runs.

.8086

_TEXT segment byte public 'CODE' use16
assume cs:_TEXT

CR equ 0Dh
LF equ 0Ah

public ZUNINIT_BANNER
public ZUNINIT_MSG_RESIDENT_SIZE
public ZUNINIT_MSG_INSTALLED
public ZUNINIT_MSG_UNINSTALLED
public ZUNINIT_MSG_NOT_INSTALLED
public ZUNINIT_MSG_BAD_OPTION
public ZUNINIT_MSG_FREE_ERROR
public ZUNINIT_MSG_MEMORY_HINT

ZUNINIT_BANNER db CR, LF, CR, LF
    db 'INTvector set program  zuninit.com Version1.01              (c)zun 1998', CR, LF, '$'
ZUNINIT_MSG_RESIDENT_SIZE db 'ちょこっとメモリかりるね', CR, LF, CR, LF, '$'
ZUNINIT_MSG_INSTALLED db 'すでに常駐してるの', CR, LF, CR, LF, '$'
ZUNINIT_MSG_UNINSTALLED db 'メモリから消えてなくなっちゃったけど、きっとまたあえるよ、ねっ', CR, LF, CR, LF, '$'
ZUNINIT_MSG_NOT_INSTALLED db 'まだ、常駐してないわぁ', CR, LF, CR, LF, '$'
ZUNINIT_MSG_BAD_OPTION db '意味不明なオプションよぉ（オプションは -Rのみ）', CR, LF, '$'
ZUNINIT_MSG_FREE_ERROR db 'メモリ解放エラーです。 : zuninit.com', CR, LF, '$'
ZUNINIT_MSG_MEMORY_HINT db 'メインメモリは５６０Ｋ以上空けといて下さいね', CR, LF, '$'

_TEXT ends
end
