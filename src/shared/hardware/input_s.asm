	.386
	.model use16 large SHARED
	locals

; TH04 PC-98 BIOS key bitmap addresses and input flags used by this unit.
; The complete linked module is independently compared in MAIN, OP, MAINE.
KEYGROUP_0 = 52Ah
KEYGROUP_2 = 52Ch
KEYGROUP_3 = 52Dh
KEYGROUP_5 = 52Fh
KEYGROUP_6 = 530h
KEYGROUP_7 = 531h
KEYGROUP_8 = 532h
KEYGROUP_9 = 533h

K0_ESC = 01h
K2_Q = 01h
K3_RETURN = 10h
K5_Z = 02h
K5_X = 04h
K6_SPACE = 10h
K7_ARROW_UP = 04h
K7_ARROW_LEFT = 08h
K7_ARROW_RIGHT = 10h
K7_ARROW_DOWN = 20h
K8_NUM_7 = 04h
K8_NUM_8 = 08h
K8_NUM_9 = 10h
K8_NUM_4 = 40h
K9_NUM_6 = 01h
K9_NUM_1 = 04h
K9_NUM_2 = 08h
K9_NUM_3 = 10h

INPUT_UP = 1
INPUT_DOWN = 2
INPUT_LEFT = 4
INPUT_RIGHT = 8
INPUT_BOMB = 10h
INPUT_SHOT = 20h
INPUT_UP_LEFT = 100h
INPUT_UP_RIGHT = 200h
INPUT_DOWN_LEFT = 400h
INPUT_DOWN_RIGHT = 800h
INPUT_CANCEL = 1000h
INPUT_OK = 2000h
INPUT_Q = 4000h

	extrn _key_det:word
	extrn _shiftkey:byte
	extrn js_stat:word
	extrn js_bexist:word

	extrn JS_SENSE:proc

	.code SHARED

; TH05 insists on only updating the affected byte, so...
if GAME eq 4
	OR_INPUT_LOW macro value
		or	_key_det, value
	endm
	OR_INPUT_HIGH macro value
		or	_key_det, value
	endm
else
	OR_INPUT_LOW macro value
		or	_key_det.lo, low value
	endm
	OR_INPUT_HIGH macro value
		or	_key_det.hi, high value
	endm
endif

public @input_reset_sense$qv
@input_reset_sense$qv label proc
	xor	ax, ax
	mov	_key_det, ax
	mov	js_stat, ax

public @input_sense$qv
@input_sense$qv proc far
	xor	ax, ax
	mov	es, ax
	mov	ah, byte ptr es:[KEYGROUP_7]
	test	ah, K7_ARROW_UP
	jz	short @@down?
	OR_INPUT_LOW	INPUT_UP

@@down?:
	test	ah, K7_ARROW_DOWN
	jz	short @@left?
	OR_INPUT_LOW	INPUT_DOWN

@@left?:
	test	ah, K7_ARROW_LEFT
	jz	short @@right?
	OR_INPUT_LOW	INPUT_LEFT

@@right?:
	test	ah, K7_ARROW_RIGHT
	jz	short @@num6?
	OR_INPUT_LOW	INPUT_RIGHT

@@num6?:
	mov	ah, byte ptr es:[KEYGROUP_9]
	test	ah, K9_NUM_6
	jz	short @@num1?
	OR_INPUT_LOW	INPUT_RIGHT

@@num1?:
	test	ah, K9_NUM_1
	jz	short @@num2?
	OR_INPUT_HIGH	INPUT_DOWN_LEFT

@@num2?:
	test	ah, K9_NUM_2
	jz	short @@num3?
	OR_INPUT_LOW	INPUT_DOWN

@@num3?:
	test	ah, K9_NUM_3
	jz	short @@num4?
	OR_INPUT_HIGH	INPUT_DOWN_RIGHT

@@num4?:
	mov	ah, byte ptr es:[KEYGROUP_8]
	test	ah, K8_NUM_4
	jz	short @@num7?
	OR_INPUT_LOW	INPUT_LEFT

@@num7?:
	test	ah, K8_NUM_7
	jz	short @@num8?
	OR_INPUT_HIGH	INPUT_UP_LEFT

@@num8?:
	test	ah, K8_NUM_8
	jz	short @@num9?
	OR_INPUT_LOW	INPUT_UP

@@num9?:
	test	ah, K8_NUM_9
	jz	short @@z?
	OR_INPUT_HIGH	INPUT_UP_RIGHT

@@z?:
	mov	ah, byte ptr es:[KEYGROUP_5]
	test	ah, K5_Z
	jz	short @@x?
	OR_INPUT_LOW	INPUT_SHOT

@@x?:
	test	ah, K5_X
	jz	short @@q?
	OR_INPUT_LOW	INPUT_BOMB

@@q?:
	mov	ah, byte ptr es:[KEYGROUP_2]
	test	ah, K2_Q
	jz	short @@esc?
	OR_INPUT_HIGH	INPUT_Q

@@esc?:
	mov	ah, byte ptr es:[KEYGROUP_0]
	test	ah, K0_ESC
	jz	short @@return?
	OR_INPUT_HIGH	INPUT_CANCEL

@@return?:
	mov	ah, byte ptr es:[KEYGROUP_3]
	test	ah, K3_RETURN
	jz	short @@space?
	OR_INPUT_HIGH	INPUT_OK

@@space?:
	mov	ah, byte ptr es:[KEYGROUP_6]
	test	ah, K6_SPACE
	jz	short @@shift?
	OR_INPUT_LOW	INPUT_SHOT

@@shift?:
	mov	ah, 2
	int	18h
	and	al, 1
	mov	_shiftkey, al
	cmp	js_bexist, 0
	jz	short @@ret
	call	js_sense
	or	_key_det, ax

@@ret:
if GAME eq 5
	mov	ax, _key_det
endif
	retf
@input_sense$qv endp
	even

	end
