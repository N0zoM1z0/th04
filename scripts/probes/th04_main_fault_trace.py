"""Private MAIN gameplay-call and decimal DIV checkpoints to Bochs port E9.

Only modifies the probe's staged source. These observations change layout and
cannot accept uninstrumented gameplay or historical exactness.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

def apply_cpu_fault_overlay(work: Path) -> dict:
    """Arm chained exceptions once, without per-frame or per-bullet output."""
    private = Path(__file__).resolve().parents[2] / ".analysis"
    if not work.resolve().is_relative_to(private):
        raise ValueError("CPU observer requires a private staged source tree")
    path = work / "src/main/core/gameplay_loop.cpp"
    original = path.read_text()
    entry = "void near gameplay_loop(void)"
    loop = "    do {"
    if original.count(entry) != 1 or original.count(loop) != 1:
        raise ValueError("gameplay CPU observer entry changed")
    changed = original.replace(entry,
        'extern "C" void pascal far FAULT_TRACE_SETUP(void);\n' + entry)
    changed = changed.replace(loop, "    FAULT_TRACE_SETUP();\n" + loop)
    digits = work / "src/main/pointnum/digits.asm"
    original_digits = digits.read_text()
    ending = "MAIN_033_TEXT ends\nend"
    if original_digits.count(ending) != 1:
        raise ValueError("CPU observer assembly owner changed")
    handler_source = Path(__file__).with_name("th04_fault_handlers.inc")
    handlers = handler_source.read_text()
    path.write_text(changed)
    digits.write_text(original_digits.replace(ending,
        "MAIN_033_TEXT ends\n" + handlers + "\nend"))
    return {
        "scope": "private chained CPU exceptions only; no gameplay acceptance",
        "mode": "cpu-only",
        "path": str(path),
        "before_sha256": hashlib.sha256(original.encode()).hexdigest(),
        "after_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "decimal_source_before_sha256": hashlib.sha256(original_digits.encode()).hexdigest(),
        "decimal_source_after_sha256": hashlib.sha256(digits.read_bytes()).hexdigest(),
        "calls": [],
        "cpu_handler_source_sha256": hashlib.sha256(handler_source.read_bytes()).hexdigest(),
        "cpu_fault_fields": ["vector", "cs", "ip", "ss", "frame_sp", "ds", "ax",
                             "dx", "bx", "cx", "si", "es", "flags"],
    }

def apply_fault_trace_overlay(work: Path) -> dict:
    private = Path(__file__).resolve().parents[2] / ".analysis"
    if not work.resolve().is_relative_to(private):
        raise ValueError("fault checkpoints require a private staged source tree")
    path = work / "src/main/core/gameplay_loop.cpp"
    original = path.read_text()
    helper = r'''extern "C" void pascal far FAULT_TRACE_SETUP(void);
static void near fault_hex(unsigned int value) {
    for(int shift = 12; shift >= 0; shift -= 4) {
        unsigned char digit = (value >> shift) & 15;
        outportb(0xE9, (digit < 10) ? (digit + '0') : (digit - 10 + 'A'));
    }
}
static void near fault_checkpoint(unsigned int id) {
    outportb(0xE9, 'G'); outportb(0xE9, 'P'); outportb(0xE9, ' ');
    fault_hex(stage_frame); outportb(0xE9, ' '); fault_hex(id);
    outportb(0xE9, ' '); fault_hex(_SS); outportb(0xE9, ':'); fault_hex(_SP);
    outportb(0xE9, ' '); fault_hex(_DS); outportb(0xE9, '\n');
}
'''
    names = [
        'input_sense',
        'fp_23D90',
        'std_update',
        'midboss_activate_if_stage_frame_is_midboss_start_frame',
        'stage_vm',
        'bg_render_not_bombing',
        'bg_render_bombing',
        'pointnums_update',
        'circles_update',
        'sparks_update',
        'player_update',
        'shots_update',
        'bullets_update',
        'enemies_update',
        'midboss_update',
        'boss_update',
        'items_update',
        'gather_update',
        'stage_render',
        'bomb_update_and_render',
        'boss_fg_render',
        'midboss_render',
        'enemies_render',
        'shots_render',
        'player_render',
        'grcg_setmode_rmw',
        'gather_render',
        'sparks_render',
        'items_render',
        'pointnums_render',
        'bullets_render',
        'circles_render',
        'grcg_off',
        'overlay1',
        'overlay2',
        'playfield_shake_update_and_render',
        'input_reset_sense',
        'slowdown_frame_delay',
        'scroll_driver',
        'snd_se_update',
        'score_update_and_render',
    ]
    changed = original
    for i, name in enumerate(names):
        needle = name + "();"
        if needle not in original:
            raise ValueError(f"missing gameplay call checkpoint: {name}")
        changed = re.sub(
            r"\b" + re.escape(needle),
            lambda match: "fault_checkpoint(" + str(i) + "); " + needle,
            changed,
        )
    changed = changed.replace(
        "void near gameplay_loop(void)", helper + "\nvoid near gameplay_loop(void)"
    )
    changed = changed.replace("    do {", "    FAULT_TRACE_SETUP();\n    do {", 1)
    path.write_text(changed)
    digits = work / "src/main/pointnum/digits.asm"
    original_digits = digits.read_text()
    helper=r'''fault_digits proc near
 pushf
 push ax
 push bx
 push cx
 push dx
 push si
 push di
 mov di,ax
 mov al,'P'
 out 0E9h,al
 mov al,'N'
 out 0E9h,al
 mov al,' '
 out 0E9h,al
 mov ax,ds
 call fault_hex_digits
 mov al,':'
 out 0E9h,al
 mov ax,si
 call fault_hex_digits
 mov al,' '
 out 0E9h,al
 mov ax,[si]
 call fault_hex_digits
 mov al,' '
 out 0E9h,al
 mov ax,di
 call fault_hex_digits
 mov al,10
 out 0E9h,al
 pop di
 pop si
 pop dx
 pop cx
 pop bx
 pop ax
 popf
 ret
fault_digits endp
fault_hex_digits proc near
 mov bx,ax
 mov cx,4
fault_hex_loop:
 push cx
 mov cl,4
 rol bx,cl
 pop cx
 mov al,bl
 and al,15
 add al,'0'
 cmp al,'9'
 jbe fault_hex_out
 add al,7
fault_hex_out:
 out 0E9h,al
 loop fault_hex_loop
 ret
fault_hex_digits endp
'''
    division = "div\tword ptr [si]"
    ending = "MAIN_033_TEXT ends\nend"
    if original_digits.count(division) != 1 or original_digits.count(ending) != 1:
        raise ValueError("decimal checkpoint producer changed")
    handler_source = Path(__file__).with_name("th04_fault_handlers.inc")
    handlers = handler_source.read_text()
    digits.write_text(original_digits.replace(
        division, "call fault_digits\n\t" + division
    ).replace(ending, helper + "\nMAIN_033_TEXT ends\n" + handlers + "\nend"))
    bullet_path = work / "src/main/bullet/update_body.inl"
    original_bullets = bullet_path.read_text()
    bullet_helper = r'''static void near fault_bullet_hex(unsigned int value) {
    for(int shift = 12; shift >= 0; shift -= 4) {
        unsigned char digit = (value >> shift) & 15;
        outportb(0xE9, (digit < 10) ? (digit + '0') : (digit - 10 + 'A'));
    }
    outportb(0xE9, ' ');
}
static void near fault_bullet_step(unsigned int step, unsigned int index,
    bullet_t near *bullet) {
    if(stage_frame < 3500) { return; }
    outportb(0xE9, 'B'); outportb(0xE9, 'V'); outportb(0xE9, ' ');
    fault_bullet_hex(stage_frame); fault_bullet_hex(step);
    fault_bullet_hex(index); fault_bullet_hex((unsigned int)bullet);
    fault_bullet_hex(_SS); fault_bullet_hex(_SP); fault_bullet_hex(_DS);
    outportb(0xE9, '\n');
}
'''
    bullet_source = original_bullets.replace("void bullets_update(void)",
                                           bullet_helper + "\nvoid bullets_update(void)")
    loop = "for(i = 0; i < BULLET_COUNT; i++, bullet--) {"
    if bullet_source.count(loop) != 2:
        raise ValueError("bullet iteration producer changed")
    bullet_source = bullet_source.replace(loop, loop + "\n fault_bullet_step(0, i, bullet);")
    bullet_source = bullet_source.replace("bullet->pos.update_seg3();",
        "fault_bullet_step(1, i, bullet); bullet->pos.update_seg3();")
    bullet_source = bullet_source.replace("bullet_update_special(*bullet);",
        "fault_bullet_step(2, i, bullet); bullet_update_special(*bullet); fault_bullet_step(3, i, bullet);")
    for name, before, after in [("sparks_add_random", 4, 5), ("hud_graze_put", 6, 7),
                                ("pointnums_add_white", 8, 9)]:
        pattern = r"\b" + name + r"\([^;]*?\);"
        matches = list(re.finditer(pattern, bullet_source, re.S))
        if len(matches) != 1:
            raise ValueError(f"bullet call checkpoint changed: {name}")
        bullet_source = re.sub(pattern, lambda match:
            f"fault_bullet_step({before}, i, bullet); " + match[0]
            + f" fault_bullet_step({after}, i, bullet);", bullet_source, flags=re.S)
    bullet_path.write_text(bullet_source)
    return {
        "scope": "private gameplay/bullet/DIV checkpoints and chained CPU exceptions; no gameplay acceptance",
        "path": str(path),
        "decimal_source_before_sha256": hashlib.sha256(original_digits.encode()).hexdigest(),
        "decimal_source_after_sha256": hashlib.sha256(digits.read_bytes()).hexdigest(),
        "before_sha256": hashlib.sha256(original.encode()).hexdigest(),
        "after_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "calls": names,
        "cpu_handler_source_sha256": hashlib.sha256(handler_source.read_bytes()).hexdigest(),
        "cpu_fault_fields": ["vector", "cs", "ip", "ss", "frame_sp", "ds", "ax",
                             "dx", "bx", "cx", "si", "es", "flags"],
        "bullet_source_before_sha256": hashlib.sha256(original_bullets.encode()).hexdigest(),
        "bullet_source_after_sha256": hashlib.sha256(bullet_path.read_bytes()).hexdigest(),
    }
