# Non-MAIN replay facilities and acceptance boundary (v507)

2026-09-22, locally attested Japanese TH04 targets. This packet checks
whether OP, MAINE, and ZUN work can resume from retained inputs. It changes
no source/byte acceptance state. OP and MAINE decoded-image observations use
the v228 target-derived DIET restores; their packed target bytes and restored
views must not be conflated. ZUN decoded offsets below use the attested
13,422-byte target-stub payload (`baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`).

## OP/MAINE aggregate controls

Run the current v489 source snapshot from the protected retained tree:

```bash
python3 scripts/probes/probe_th04_bgimage_hybrid_v489.py --current-snapshot \
  --op-source-dir .analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source \
  --maine-source-dir .analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source \
  --op-target-restored .analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin \
  --maine-target-restored .analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin
```

Without `--output-dir` the script allocates a new private replay directory.
The v507 two-cold-build result has receipt SHA-256
`38894c47024315f857991bda6e5d3d6b0f2852ef66499a82a996cdd5a4322c2f`.
Its private receipt is
`.analysis/gpt-web/v507-bgimage-current-replay-001/receipt.json`.
OP's 804/804 and MAINE's 559/559 ordered relocation entries match the
target-restored MZs. Each decoded program has only its shared `snd_load`
two-byte mismatch. BGIMAGE remains decoded/link-exact in both artifacts;
there is no packed-file function offset or whole-file exact claim. Historical
v489 documentation names now-compacted v487/v488 input snapshots; the six
BGIMAGE unit commands use this current-snapshot path instead.

The independent Reduction #172 BGM-BSS control is:

```bash
python3 scripts/probes/probe_th04_bgm_bss_reduction172_v494.py \
  --op-source-dir .analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source \
  --maine-source-dir .analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source \
  --op-target-restored .analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin \
  --maine-target-restored .analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin \
  --output-dir .analysis/gpt-web/NEW_UNIQUE_V494_REPLAY
```

The v507 result has receipt SHA-256
`a42ef0dd043eca9fed8022c3416b3cc10262851ba715c6dc8dab47492c8d12ae`.
Its private receipt is
`.analysis/gpt-web/v507-op-maine-handoff-smoke-001/receipt.json`.
Two isolated rounds agree; OP and MAINE preserve exact ordered relocation
tables, target `T`/minalloc and program prefix. Decoded residual offsets are
OP `0xDE8B..0xDE8C` and MAINE `0xD1D3..0xD1D4` (program offsets). The
historical blob is a binary-preserving representation, not proof that ZUN's
original BGM source initialized this BSS. Both probes overlay retained source
into the ReC98 scaffold; neither proves standalone checked-in product builds.

## ZUN source-only control and gap

```bash
python3 scripts/probes/replay_th04_zun_source_only.py \
  --output-dir .analysis/reconstruction/probes/NEW_UNIQUE_ZUN_SOURCE_REPLAY
```

The driver now recursively materializes and hashes repository-local quoted
headers, including `src/shared/config/score.hpp`. Two cold TC4J compilations
of checked-in source agree: `cfg_init` at decoded `_TEXT` `0xDCF..0xE66`
produces 152 CODE bytes (SHA-256
`4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4`);
resident `_main` at `0xE67..0xF62` produces 246 CODE bytes (SHA-256
`24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea`)
versus the 252-byte target. Receipt SHA-256 is
`8ef05ac37787385ce79a74dc0ccb4a9d305b0359a5cef8ea92e02a68a231eadd`.
Compilation alone cannot accept `cfg_init` exact: the checked-in product
link/DIET replay, other components, and physical acceptance evidence are
missing. The older `replay_th04_zun_cfg_init.py` depends on pruned v214
source snapshots and needs rebasing before it can serve as a live driver.

## Next infrastructure unit

Build a common artifact-local decoded-function acceptance contract for
OP/MAINE/ZUN, bound to reviewed physical extent and cold source/build inputs.
Keep the separate raw packed-file ledger exact gate. Start with the ten
reviewed `src/shared/` owners in OP/MAINE, 633 decoded bytes per artifact;
do not inherit MAIN acceptance. For ZUN, rebase the component link on
maintained source and explicit library inputs before any exact promotion.
