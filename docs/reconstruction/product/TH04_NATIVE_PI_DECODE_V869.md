# TH04-local packed PI decoder

2026-09-28 native product-build batch. `src/shared/formats/pi_decode.cpp`
owns `GRAPH_PI_LOAD_PACK` for TH04. It parses the PI header, reads the
adaptive color/position stream, allocates a paragraph-backed image block,
and returns a far pointer after two reference rows. Its output indexing uses
explicit segment-plus-offset arithmetic, so the 640×400 resources cross the
64 KiB boundary without wrapping into unrelated memory. `graph_pi_free()`
releases the base segment from that returned pointer. The source is a semantic
implementation; no target-byte exactness is claimed.

The pinned OP/ending PAR archive contains `CONG10.PI` (stored PAR payload)
and `CONG14.PI` (RLE PAR payload), each declaring a 640×400 16-color image.
The checked-in `scripts/probes/probe_th04_native_pi_decode_runtime.py` first
compiles a separate *small-model* DOS oracle against the pinned historical
`masters.lib`, then compiles a TH04-only *large-model* MZ. The local MZ reads
both real images through the TH04 PAR hook and as loose DOS files, checks all
128,000 displayed pixel bytes by FNV-1a, frees and reloads the image block,
and checks invalid/missing files and hook shutdown. The historical and local
pixel digests agree:

| Member | FNV-1a over displayed bytes |
| --- | --- |
| `CONG10.PI` | `232AE649` |
| `CONG14.PI` | `EDFA0534` |

The first complete probe passed with 247 unique, nonoverlapping test-MZ
relocations audited at DOS load segments `0x2000` and `0x6000`; receipt
SHA-256 is
`d42db167f7b8282a5648c73aa08ab4f2258ed1929429bb9a3b2e3866b9778cbb`.
This is an isolated DOS service/runtime result, not a MAINE PC-98 launch.
The probe keeps original archives, decoded assets, and the historical binary
under private `.analysis/`; none belongs in Git.

## Historical reference hazards

The readable ReC98 `graph_pi_load_pack.asm` contains three initial
`_read_color` calls before filling the two reference rows. The pinned
`masters.lib` binary has only two at calibration code `0000:0624` and
`0000:062E`, followed by `OR AL,DL` at `0000:0631`; it fills the rows with
`FB` for these resources. A host decoder following the readable file's three
calls diverged from the first pixel. Using the binary-observed two-call
sequence made all 128,000 `CONG10.PI` bytes identical to the independently
executed historical decoder. These are historical calibration addresses and
cannot be called target MAINE offsets. The result is a concrete reason to
check archived object behavior instead of assuming neighboring reference
source matches it.

The historical PI archive member is near/small-model code. A large-model
test harness linked it without a useful ABI rejection, then repeatedly
re-entered `main` and terminated abnormally. Recompiling only that oracle
harness as small-model made its `PiHeader` size 72 and output stable. The
TH04 product decoder remains far Pascal under the MAINE `-ml` profile and
does not link the historical library. TH05 should attest procedure distance
and return instructions before treating any mixed-library MZ as runnable.

Replay the full differential with a fresh private output directory:

```text
python3 scripts/probes/probe_th04_native_pi_decode_runtime.py --output-dir .analysis/reconstruction/probes/NEW-pi
```

Two cold MAINE no-support builds compile all 126 TH04-owned translation units
(81 C/C++, 45 ASM) with zero warnings. The seven unresolved names are
`SUPER_PUT`, `SUPER_FREE`, `SUPER_ENTRY_BFNT`, `BGM_FINISH`, `BGM_INIT`,
`BGM_READ_SDATA`, and `BGM_SOUND`. All 126 link-relevant and
timestamp-normalized OMF objects agree across the builds; only BGIMAGE has
raw timestamp drift. The first no-support receipt SHA-256 is
`ac41d5077a7bc144d0c7aff208d29cbb704cded0444a8abafe9c43b4421c7cae`.
A diagnostic link with the pinned historical library resolves those seven
names, with its known extended-dictionary warning. The MAP places the local
`GRAPH_PI_LOAD_PACK` at `0825:3323`; this is a candidate link address, not a
target MAINE address. The MZ audit checks all 637 relocation sites at DOS load
segments `0x2000` and `0x6000`. The call audit checks 33 far returns, 134
relocated direct far calls, and one same-CS far call. The calibration, MZ, and
call-audit receipt SHA-256 values are respectively
`7256b4c8b32ef09a9cb55fd365559d81c137aebbed3d6358c88b7dcd80e95768`,
`62fb4f91f6fb075b3122e93915e453bf1a9e335c91a3bbcd03a43c6d887a68ec`,
and `99deca903272d344be6d4e99b8d5b7e96e9cb01a9a27c15d7e05cb5bf1e81dd9`.
This mixed-support MZ is a diagnostic, not a standalone TH04 product. At v869,
native MAINE still needed the sprite and BGM providers; the
[v870 sprite batch](TH04_NATIVE_SUPER_SPRITE_V870.md) later closed the sprite
names. Larger or odd-width PI
resources and an actual PC-98 display scenario remain separate runtime
coverage.

## DOS semantic readability batch

The `semantic/readable` branch renames private decoder helpers, input state
and locals by their meaning, introduces named copy selectors and storage
constants, and explains the existing packing, adaptive history, overlapping
copy runs, error checks and ownership transfer. The translation unit,
external far/Pascal entry, field order, integer widths and evaluation order
are preserved. These explanations describe the maintained implementation;
they do not establish additional original-target semantics.

For even-width images, selectors 1 and 2 copy from one and two rows back.
Selectors 3 and 4 sample the preceding row one pixel ahead or behind,
joining adjacent bytes' nibbles. The comments explicitly restrict this
geometric interpretation to even widths; the original odd-width arithmetic
is retained. Other port hazards are the sticky input-error flag, signed
16-bit return from the header-word reader, and the image pointer's
nonzero offset into a paragraph-owned allocation. Palette bytes pass
through unchanged; PC-98 application uses the components' high nibbles.

Two fresh executions of the existing DOS probe compile source snapshots
before and after the readability edit. Both pass the independent historical
image hashes, PAR/loose file paths, invalid/missing file controls and repeated
slot load/free checks. The complete linked service test is byte-identical:
38,050 bytes, SHA-256
`9cc4e7adcd287c590f78373042352137f18d0145be13039cd9f3e19c087ef9fa`,
254 relocations, zero raw differences, equal MZ fields and ordered
relocations. Its `GRAPH_PI_LOAD_PACK` is at candidate `SHARED 0629:05A7`
(relative load-module address); this is not a target MAINE address.

Replay the existing runtime probe from `8d20492` and from this branch with
separate fresh output directories, then compare the two generated
`product/bin/pitest.exe` files:

```sh
python3 scripts/probes/probe_th04_native_pi_decode_runtime.py \
  --output-dir .analysis/reconstruction/probes/NEW-semantic-pi
python3 scripts/compare_artifacts.py BEFORE/product/bin/pitest.exe \
  AFTER/product/bin/pitest.exe
```

The current receipts are
`.analysis/reconstruction/probes/semantic-pi-{baseline,readable}-20261003/receipt.json`.
This is compiler-observed source-regression equality plus bounded DOS
runtime coverage. No historical exact ledger is promoted, and the user's
complete Good Ending-to-registration visual regression remains open.
