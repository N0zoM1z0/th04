; ZUNINIT resident marker, vector slots, reentry guard, and modal UI text.
; UTF-8 literals are converted to CP932 before pinned TASM runs.

.8086

_TEXT segment byte public 'CODE' use16
assume cs:_TEXT

public ZUNINIT_SIGNATURE
public ZUNINIT_VECTOR_SLOT_1
public ZUNINIT_VECTOR_SLOT_2
public ZUNINIT_BUSY
public ZUNINIT_STOP_LINE1
public ZUNINIT_STOP_LINE2
public ZUNINIT_STOP_LINE3
public ZUNINIT_CLEAR_LINE
public ZUNINIT_COPY_LINE1
public ZUNINIT_COPY_LINE2
public ZUNINIT_COPY_LINE3

ZUNINIT_SIGNATURE dw 'ZU', 'NP'
ZUNINIT_VECTOR_SLOT_1 dd 0
ZUNINIT_VECTOR_SLOT_2 dd 0
ZUNINIT_BUSY db 0

ZUNINIT_STOP_LINE1 db 'むやみにＳＴＯＰキー押したりしない$'
ZUNINIT_STOP_LINE2 db '方がいいと思うの。（ゲーム中はね）$'
ZUNINIT_STOP_LINE3 db '（ＳＴＯＰキーで戻れるよ、ねっ）　$'
ZUNINIT_CLEAR_LINE db '　　　　　　　　　　　　　　　　　$'
ZUNINIT_COPY_LINE1 db 'なんでＣＯＰＹキー押したりしてるの$'
ZUNINIT_COPY_LINE2 db 'かな～。ふしぎ～。　　（もう一度、$'
ZUNINIT_COPY_LINE3 db 'ＣＯＰＹキー押せば戻れるよ、ねっ）$'

_TEXT ends
end
