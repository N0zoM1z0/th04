; MASTER.LIB PC-98 graphics state used by the TH04 ZUN resident link.
; The physical archive member owns 0x0B DATA bytes. The following word-alignment
; zero is linker padding, not part of this TU's DATA owner.

.8086

; The historical GRP object deliberately declares this external without a
; FIXUPP so TLINK pulls the VERSION member from MASTER.LIB.
extrn _Master_Version:byte

_TEXT segment word public 'CODE' use16
_TEXT ends

_DATA segment word public 'DATA' use16
public _graph_VramSeg, graph_VramSeg
public _graph_VramWords, graph_VramWords
public _graph_VramLines, graph_VramLines
public _graph_VramWidth, graph_VramWidth
public _graph_VramZoom, graph_VramZoom
public _graph_MeshByte, graph_MeshByte

graph_VramSeg label word
_graph_VramSeg dw 0A800h

graph_VramWords label word
_graph_VramWords dw 16000

graph_VramLines label word
_graph_VramLines dw 400

graph_VramWidth label word
_graph_VramWidth dw 80

graph_VramZoom label word
_graph_VramZoom dw 0

graph_MeshByte label byte
_graph_MeshByte db 55h
_DATA ends

DGROUP group _TEXT, _DATA
end
