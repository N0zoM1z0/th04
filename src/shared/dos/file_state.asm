; MASTER single-file global state used by the TH04 ZUN resident support.
; The physical archive member owns four initialized DATA bytes and 0x14 BSS
; bytes. BSS is uninitialized layout ownership and has no bytes in the COM file.

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_DATA segment word public 'DATA' use16
public _file_BufferSize, file_BufferSize
public _file_Handle, file_Handle

_file_BufferSize label word
file_BufferSize dw 0

_file_Handle label word
file_Handle dw -1
_DATA ends

_BSS segment word public 'BSS' use16
public _file_Pointer, file_Pointer
public _file_Buffer, file_Buffer
public _file_BufferPos, file_BufferPos
public _file_BufPtr, file_BufPtr
public _file_InReadBuf, file_InReadBuf
public _file_Eof, file_Eof
public _file_ErrorStat, file_ErrorStat

_file_Pointer label dword
file_Pointer dd ?

_file_Buffer label dword
file_Buffer dd ?

_file_BufferPos label dword
file_BufferPos dd ?

_file_BufPtr label word
file_BufPtr dw ?

_file_InReadBuf label word
file_InReadBuf dw ?

_file_Eof label word
file_Eof dw ?

_file_ErrorStat label word
file_ErrorStat dw ?
_BSS ends

DGROUP group _TEXT, _DATA, _BSS
end
