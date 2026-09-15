	.8086
	.model use16 large _TEXT

include th03/arg_bx.inc
include libs/master.lib/macros.inc
include th04/math/motion.inc

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01
MOTION_UPDATE_DEF 1
CIRCLE_TEXT ends

	end
