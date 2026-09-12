.386
.model use16 large _TEXT
include ReC98.inc
include th04/th04.inc

PELLET_H = 8
extrn _sPELLET:byte

B4M_UPDATE_TEXT segment word public 'CODE' use16
B4M_UPDATE_TEXT ends
main_03 group B4M_UPDATE_TEXT
assume cs:main_03

B4M_UPDATE_TEXT segment word public 'CODE' use16
include th04/main/gather_point_render.asm
B4M_UPDATE_TEXT ends
end
