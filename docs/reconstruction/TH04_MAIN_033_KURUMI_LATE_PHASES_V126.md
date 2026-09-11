# TH04 `MAIN_033_TEXT` Kurumi late phase-handler packet (v126)

## Scope and target identity

This packet continues the exact `MAIN_033_TEXT` producer split immediately after
the v125 Kurumi spawn-ray phase handlers. It recovers four adjacent target
functions as one maintained natural-C++ translation unit:

| Function | Load extent | Ghidra linear extent | File extent | Size |
| --- | --- | --- | --- | ---: |
| `kurumi_turning_bullets_phase()` | `0x18DB6..0x18E42` | `0x28DB6..0x28E42` | `0x1A5B6..0x1A642` | `0x8D` |
| `kurumi_spawnray_pattern_left()` | `0x18E43..0x18EE6` | `0x28E43..0x28EE6` | `0x1A643..0x1A6E6` | `0xA4` |
| `kurumi_spawnray_pattern_right()` | `0x18EE7..0x18F8A` | `0x28EE7..0x28F8A` | `0x1A6E7..0x1A78A` | `0xA4` |
| `kurumi_spawnray_pattern_dual()` | `0x18F8B..0x19059` | `0x28F8B..0x29059` | `0x1A78B..0x1A859` | `0xCF` |

The aggregate target extent is `0x18DB6..0x19059`, map
`13A9:5326..55C9`, file `0x1A5B6..0x1A859`, size `0x2A4` / 676 bytes,
with SHA-256
`82bfe35c2faf87d7f879fec7e89f1d63dd2db00c74be40da0484122d964b00a7`.
The tested target remains the same private `candidate-local-attested` Japanese
`MAIN.EXE`, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.

Fresh `th04-ghidra` target-bound metadata reports all four entries as
`__cdecl16near`. The final three bodies are contiguous and complete at 164,
164, and 207 body addresses. The first entry has the correct physical min/max
span but only 114 body addresses for a 141-byte function, so it requires the
manual sparse-body boundary gate described below. Ghidra observations remain
provisional routing evidence and receive no exactness credit by themselves.

## Sparse boundary correction at `0x28DB6`

Pinned TASM, target bytes, and the next physical PROC prove that
`kurumi_turning_bullets_phase()` occupies all `0x8D` bytes through the `RET` at
`0x28E42`. Ghidra omits exactly `0x28E26..0x28E40` from its function body even
though the bytes are ordinary reachable code inside the PROC.

That omitted 27-byte block:

- adds `0x80` to the selected special-turn angle;
- lowers the bullet-template speed;
- obtains a fresh random angle;
- emits the second special bullet;
- increments the persistent Kurumi turn toggle; and
- rejoins the terminal `RET`.

The function reviewer therefore does not treat the sparse Ghidra body as a
closed extent. `[[reviewed_exact]]` forces a gap-free raw decode of the full
141-byte configured span. The accepted decode contains 43 instructions and
ends exclusively at `0x28E43` with terminal `RET`, exactly where the next TLINK
public begins. The formal boundary ledger deliberately preserves
`ghidra_contiguous=false` and `ghidra_range_count=2` while recording the full
reviewed/exact physical size.

The other three functions use the ordinary contiguous-Ghidra/TLINK/exact-owner
path. All four have zero direct Ghidra callers because the surrounding Kurumi
boss update dispatches them through phase/mode jump-table control flow rather
than ordinary target-recognized direct call ownership.

## Natural-source compiler result

The maintained source is:

`src/main/boss/kurumi_late_phases.cpp`

Source SHA-256:

`ad9e1b7b70c676824f80413d6c5963839efb42ab20ce211a844c86f5c64d19a3`

It contains ordinary maintainable C++ using the existing TH04 boss, bullet,
frame, circle, sound, sprite, and randring interfaces. It contains no inline
assembly, target-derived byte arrays, `#pragma codestring`, fake returns, inert
padding, target patching, or copied target bytes.

The first bounded TC4J probe was already structurally decisive. It emitted all
four publics, and the final three functions had their exact target sizes
(164/164/207 bytes), but the first function was three bytes too long: candidate
public offsets were `0x000 / 0x090 / 0x134 / 0x1D8` rather than target
`0x000 / 0x08D / 0x131 / 0x1D5`.

The mismatch was localized to the special-turn sign selection. Direct source
assignments to the memory field made TC4J emit one memory-immediate store in
each branch. The target instead selects `+0x40` or `-0x40` in `AL` and performs
one common memory store after the branch. Expressing only this live-byte value
through Borland's ordinary `_AL` pseudo-register source form reproduces that
compiler shape without emitting bytes manually.

The second isolated TC4J probe then emits exactly 676 `MAIN_033_TEXT` bytes and
four PUBDEF offsets:

- `0x000`
- `0x08D`
- `0x131`
- `0x1D5`

These exactly tile the target 141/164/164/207-byte function boundaries. The
probe object is valid TC86 Borland C++ 4.02 OMF. The formal cold replay later
produces dependency-normalized natural-object SHA-256
`59783e841d9dc7b352bed937a0052790180372363faa66db1ea92c466090c0e8`.

## Physical producer split and storage ownership

Before v126, the replay-only `m33kseam.asm` residual started at target load
`0x18DB6`. v126 peels the 676-byte natural producer from that residual and links
it in the exact physical position:

```text
v124/v125 residual prefix   0x18B68..0x18BE5
v125 kphase.cpp             0x18BE6..0x18DB5
v126 kphase2.cpp            0x18DB6..0x19059
replay-only residual suffix 0x1905A..MAIN_033_TEXT end
```

The residual assembler is still hash-bound cold-replay plumbing and receives
zero reconstruction, source, byte-owner, or function-owner credit.

Two semantic aliases are needed without moving any target storage or code:

1. `kurumi_orbit_step_reverse()` labels the unchanged residual near helper
   formerly named `kurumi_18BA7` in the replay-only prefix object.
2. `kurumi_special_turn_toggle` labels the unchanged BSS byte `byte_259F0` in
   its real `th04_main.asm` storage owner.

An initial scratch transform incorrectly assumed `byte_259F0` was owned by the
suffix object. The fail-closed assertion exposed that mistake before any formal
replay; the accepted transform publishes the alias only in the true BSS owner.

The hash-bound transforms are:

- `th04_main.asm` scaffold
  `a71fcc828a6e1e6113cd768acb30a03ebf32f8feb563fae734f8accc0d56c0ec`
  -> patched
  `3a3e9009e41fe8cfbc94698d15d4947d3337195c1e27258f293ea820d18e0c64`;
- `m33kpre.asm` scaffold
  `d763c687b53509a44503baef38b38bbb324e4a823672210b0848e99ab90bd6b3`
  -> patched
  `3a30cf25d4bd52c0ff11d9757f7a4d2d54b93b35330ac70002ba732b3d0fb03f`;
- `m33kseam.asm` scaffold
  `b7e278aaecd81f8f22b71a7f8245294d5ee4cdaa72a4162368768c316b351edd`
  -> patched
  `5d60d84d16ef9eb7fac753f825fefdebe5be80387bc0e8ec46339a5f1f36de23`.

The removed pinned-TASM source-text span is 7,468 bytes with SHA-256
`b468d572074d46b31cd54a12231f243c1ae38a3f54e1597557954ebd72327afc`;
it corresponds to the four 676-byte target function bodies. Dispatcher call
sites in the residual are rebound to the four generated C++ publics. The next
residual PROC remains at target load `0x1905A`.

## Focused and aggregate replay

Focused replay actually run:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-kurumi-late-phases-v126 \
  --run-id gptweb-v126-kurumi-late-phases-focused-001
```

Result: PASS, `failures=[]`, 98 dependency-closure owners, two isolated cold
materializations. Both A/B builds report:

- raw exact: true;
- map exact: true;
- ordered relocations exact: true;
- natural object valid: true;
- map contribution
  `13A9:5326 02A4 C=CODE S=MAIN_033_TEXT G=MAIN_03 M=th04/kphase2.cpp ACBP=28`;
- natural normalized OMF SHA-256
  `59783e841d9dc7b352bed937a0052790180372363faa66db1ea92c466090c0e8`;
- focused candidate MAIN SHA-256
  `7aa8c37e63990386c434fddf1120d919004378c0d1ff7fa71d26b68f9e539d8f`.

The target/candidate ordered relocation overlap is identical at load addresses:

`0x18FD3, 0x18FC7, 0x18FB4, 0x18F1C, 0x18F10, 0x18E78, 0x18E6C`.

The auxiliary replay-only prefix/suffix objects are valid and deterministic at
normalized SHA-256
`744ec1d796d3c35639b62d86be14064b9ae536ecdf7b738483de8023598c322a`
and
`31a802cd111ddde5d74d384923a9663668f6108ab9baf6df8fd686327a972c95`.
They are physical-link evidence only.

Mandatory aggregate replay actually run:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v126-kurumi-late-phases-aggregate-001
```

Result: PASS, `failures=[]`, all 162 default owners, two isolated cold
materializations. The new owner retains the same exact map, raw bytes, seven
ordered relocations, and OMF identity, no previous owner regresses, and A/B
candidate MAIN SHA-256 is
`ffbf3b6c13670b338e53af3fb6020ff1d62bea2c0c903479fc45ba5975a23918`.

## Function review and progress

The v126 function review uses the aggregate map, fresh target-bound Ghidra
metadata, the private target, and the explicit manual sparse-body gate. It
reports:

- 285 / 287 reviewed authored functions exact = 99.303136%;
- 141 automatic exact acceptances;
- 144 manual exact acceptances;
- zero strict rejections;
- two reviewed nonexact functions.

Report SHA-256:

`47f9b15e4ba1ef2e3c52e6f5e69656297caee33e4e9231b9ff16f4bbeebddfab`

The reviewed authored-byte plane is now 43,709 / 43,740 exact = 99.929127%.
The reviewed-function plane remains below the 99.5% campaign pressure target,
so this packet is not a completion claim.

## Independent verification planes and continuation

This packet establishes exact source ownership only for the bounded 676-byte
v126 unit under the configured TH04 exact-unit Oracle. It does not establish a
standalone TH04 production compile/link closure, runtime-storage identity,
deterministic runtime scenario validation, whole-image exactness, or project
completion. No Factory Truth-Kernel replay was submitted for v126, so Factory
acceptance is not claimed.

`sub_11DE6` remains an unresolved semantic/code-generation seam. Fresh review
still shows the same 44-byte FAR target shape with the nine-threshold DS scan,
`CX=9` plus `LOOP`, `shot_level` store, callback selection, same-segment
`NOP; PUSH CS; CALL near`, and `RETF`. No new natural TC4J hypothesis was found,
so the previously negative ordinary-loop matrix was not repeated.

The first concrete continuation is the immediately following
`kurumi_1905A`:

- `MAIN_033_TEXT` load `0x1905A..0x1915C`;
- Ghidra linear `0x2905A..0x2915C`;
- file `0x1A85A..0x1A95C`;
- `0x103` / 259 bytes;
- target SHA-256
  `85d2e8324f93bb6c3e7dbc88bc3c0915881bf9ea34647132d0120d75a0f1b2d3`;
- one MZ relocation at load `0x190DC`;
- fresh Ghidra contiguous `__cdecl16near` body with 259 body addresses;
- pinned TASM terminates at `RET` immediately before FAR `kurumi_update()` at
  load `0x1915D`;
- the Kurumi dispatcher calls it from the phase/mode path at `loc_194BE`.

The v126 aggregate residual now begins exactly at map `13A9:55CA`, while
`kurumi_update()` begins at `13A9:56CD`; the difference is exactly `0x103`.
This makes `kurumi_1905A` the next evidence-connected producer-split candidate.
Its source/origin/exactness remain unreviewed and receive no credit from this
packet.
