"""Private real-PC-98 full-pool timing fixture; never part of product source."""
import hashlib
from pathlib import Path
import subprocess

FIELDS = ["phase", "active_bullets", "frame_start_tick", "update_start_tick",
          "update_end_tick", "render_start_tick", "render_end_tick",
          "work_end_tick", "delay_end_tick", "slowdown_factor", "pellets_rendered",
          "rank", "turbo", "work_count1"]


def apply(work: Path, root: Path, baseline_revision: str | None = None) -> dict:
    """Seed bounded stationary loads and buffer IRQ-counter samples in RAM.

    The fixture uses actual loaded sprites, scrolling background and the normal
    update/render/frame-wait calls. Collision suppression, reseeding and forced
    rank/Turbo are diagnostic only. No per-frame disk or debug-port output.
    """
    path = work / "src/main/core/gameplay_loop.cpp"
    entry = work / "src/main/core/main.cpp"
    session = work / "src/main/core/gameplay_session_init.cpp"
    originals = {path: path.read_text(), entry: entry.read_text(), session: session.read_text()}
    helper = r'''
// Private Lunatic/full-pool diagnostic; never compiled into a playable product.
static void native_load_begin(void)
{
    unsigned phase = native_load_frame / 32;
    unsigned count = phase == 0 ? 0 : phase == 1 ? 120 : phase == 2 ? 340 : 440;
    native_load_samples[native_load_frame][0] = phase;
    native_load_samples[native_load_frame][1] = count;
    native_load_samples[native_load_frame][2] = vsync_Count2;
    rank = RANK_LUNATIC;
    turbo_mode = true;
    player_invincibility_time = 100;
    player_is_hit = false;
    bullet_zap.active = false;
    bullet_clear_time = phase == 5 ? 20 : 0;
    pellets_render_count = 0;
    for(unsigned i = 0; i < BULLET_COUNT; i++) {
        bullet_t near &b = bullets[i];
        b.flag = i < count ? F_ALIVE : F_FREE;
        b.age = 1;
        b.pos.cur.x.v = TO_SP(32 + ((i * 13) % 300));
        b.pos.cur.y.v = TO_SP(32 + ((i * 7) % 240));
        b.pos.prev = b.pos.cur;
        b.pos.velocity.x.v = b.pos.velocity.y.v = 0;
        b.spawn_flag = (phase == 4 && i >= PELLET_COUNT) ? BSF_CLOUD_FORWARDS : BSF_GRAZED;
        b.move_flag = BMF_REGULAR;
        b.patnum = PAT_BULLET16_N_OUTLINED_BALL_BLUE;
    }
}
static void native_load_end(void)
{
    native_load_samples[native_load_frame][8] = vsync_Count2;
    native_load_samples[native_load_frame][10] = pellets_render_count;
    native_load_samples[native_load_frame][11] = rank;
    native_load_samples[native_load_frame][12] = turbo_mode;
    native_load_frame++;
    if(native_load_frame != 192) return;
    int handle;
    unsigned written;
    if(!_dos_creat("BLOAD.BIN", 0, &handle)) {
        _dos_write(handle, native_load_samples, sizeof(native_load_samples), &written);
        _dos_close(handle);
    }
    quit = Q_QUIT_TO_OP;
}
'''
    original = originals[path]
    # Keep the fused producer's existing header order: loading bullet.hpp
    # early can change the CS frame for its near callback fixups. Implement
    # these helpers after the session initializer has declared that header.
    declarations = ('static unsigned native_load_samples[192][14];\n'
                    'static unsigned native_load_frame;\n'
                    'static void native_load_begin(void);\n'
                    'static void native_load_end(void);\n')
    pairs = [
        ('void near gameplay_loop(void)\n{\n', declarations + '\nvoid near gameplay_loop(void)\n{\n'),
        ('        bullets_update();\n', '        native_load_begin();\n'
         '        native_load_samples[native_load_frame][3] = vsync_Count2;\n'
         '        bullets_update();\n'
         '        native_load_samples[native_load_frame][4] = vsync_Count2;\n'),
        ('        bullets_render();\n',
         '        native_load_samples[native_load_frame][5] = vsync_Count2;\n'
         '        bullets_render();\n'
         '        native_load_samples[native_load_frame][6] = vsync_Count2;\n'),
        ('        total_slow_frames += (vsync_Count1 >= slowdown_factor);\n',
         '        native_load_samples[native_load_frame][7] = vsync_Count2;\n'
         '        native_load_samples[native_load_frame][9] = slowdown_factor;\n'
         '        native_load_samples[native_load_frame][13] = vsync_Count1;\n'
         '        total_slow_frames += (vsync_Count1 >= slowdown_factor);\n'),
        ('        score_update_and_render();\n', '        score_update_and_render();\n        native_load_end();\n'),
    ]
    for old, new in pairs:
        if original.count(old) != 1:
            raise ValueError(f"bullet-load overlay anchor is not unique: {old!r}")
        original = original.replace(old, new, 1)
    path.write_text(original)
    session.write_text(originals[session] + '\n#include "src/main/bullet/pellet_r.hpp"\n'
                       '#include "src/main/bullet/clearzap.hpp"\n' + helper)
    anchor = '#include "platform.h"\n'
    if originals[entry].count(anchor) != 1:
        raise ValueError("bullet-load DOS include anchor is not unique")
    entry.write_text(originals[entry].replace(anchor, '#include <dos.h>\n' + anchor, 1))
    baseline = {}
    if baseline_revision:
        revision = subprocess.check_output(
            ["git", "rev-parse", "--verify", baseline_revision + "^{commit}"], cwd=root, text=True).strip()
        for relative in ("src/main/bullet/pellet_render.asm", "src/main/formats/z_super_roll_put_tiny.asm"):
            data = subprocess.check_output(["git", "show", revision + ":" + relative], cwd=root)
            (work / relative).write_bytes(data)
            baseline[relative] = hashlib.sha256(data).hexdigest()
        baseline = dict(revision=revision, sources=baseline)
    digest = lambda data: hashlib.sha256(data).hexdigest()
    return dict(scope=__doc__,fields=FIELDS,record_words=14,records=192,
                source_sha256={p.relative_to(work).as_posix():digest(s.encode()) for p,s in originals.items()},
                overlay_sha256={p.relative_to(work).as_posix():digest(p.read_bytes()) for p in originals},
                baseline_renderer_sources=baseline,
                limitation="Stationary synthetic full-pool load, forced Lunatic/Turbo and suppressed collision; reseed cost affects frame totals. Actual sprite data and PC-98 IRQ/GRCG are exercised, not a complete natural Lunatic route.")
