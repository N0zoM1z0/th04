; MAIN-owned midboss state and dispatch pointers.
; motion_t is three SPPoint values in the 16-bit target ABI (12 bytes).

.8086

_TEXT segment word public 'CODE' use16
_TEXT ends

_DATA segment word public 'DATA' use16
public _midboss4_aim_toggle
; Observed MAIN DGROUP:185E starts at 1. Pattern-stack increments this byte
; before testing its parity: the first stack uses fixed angles, the next aims.
; BSS zero initialization reverses that order (Demo1 first score/RNG miss3343).
_midboss4_aim_toggle db 1
_DATA ends

_BSS segment word public 'BSS' use16
public _midboss, _midboss_pos, _midboss_frames_until, _midboss_hp
public _midboss_sprite, _midboss_phase, _midboss_phase_frame
public _midboss_damage_this_frame, _midboss_angle
_midboss label byte
_midboss_pos db 12 dup(?)
_midboss_frames_until dw ?
_midboss_hp dw ?
_midboss_sprite db ?
_midboss_phase db ?
_midboss_phase_frame dw ?
_midboss_damage_this_frame db ?
_midboss_angle db ?

public _midboss_active, _midboss_invalidate, _midboss_update
public _midboss_update_func, _midboss_render, _midboss_render_func
_midboss_active db ?
                db ?
_midboss_invalidate dw ?
_midboss_update dd ?
_midboss_render dw ?
_midboss_update_func dd ?
_midboss_render_func dw ?

; Per-midboss pattern state declared by the maintained update/render units.
; These are inferred ABI-width owners; the original target offsets are still
; a separate layout question.
public _midboss_defeat_angle
_midboss_defeat_angle db ?

public _midboss1_vram_y, _midboss1_angle
_midboss1_vram_y dw ?
_midboss1_angle db ?

public _midboss2_patterns_done, _midboss2_direction, _midboss2_pattern
_midboss2_patterns_done db ?
_midboss2_direction      db ?
_midboss2_pattern        db ?

public _midboss3_mirror, _midboss3_pattern
_midboss3_mirror  db ?
_midboss3_pattern db ?

public _midboss4_pattern, _midboss4_patterns_done
public _midboss4_unknown_state
_midboss4_pattern        db ?
_midboss4_patterns_done  db ?
_midboss4_unknown_state   db ?
_BSS ends

DGROUP group _DATA, _BSS
end
