# OP/MAINE packed input partition (v231)

## Controlled question

The [v228 round trip](TH04_DIET145F_ROUNDTRIP_V228.md) identifies DIET 1.45f
and a target-restored MZ view that repacks raw equal to each packed target.
`scripts/probes/partition_diet_mz_residual.py` compares that view with the
v214 cold ReC98-overlay candidate MZ. It checks that `-RA` restores our own
candidate packed files **byte-for-byte** to their prepack MZs, then builds
eight private diagnostic hybrids. This supports DIET invertibility for these
candidate inputs; it still does not prove that a restored target view is the
historical TLINK output.

The entire candidate-versus-restored-target MZ difference is covered by three
surfaces:

| Surface | OP.EXE | MAINE.EXE |
| --- | ---: | ---: |
| `P`: program-image bytes | 7 differing bytes | 5 differing bytes |
| `R`: ordered relocation table | 657 differing table bytes; first entry mismatch 146 | 769 differing table bytes; first entry mismatch 48 |
| `T`: coupled MZ file length, minimum allocation, trailing zero bytes | 3,228 zero bytes; minimum allocation 612→410 paragraphs | 3,220 zero bytes; minimum allocation 817→615 paragraphs |

The candidate and restored target have the same header paragraph count,
relocation count, and relocation-site multiset. All other header bytes match.
`T` is kept coupled because applying the smaller minimum allocation alone
makes the candidate MZ invalid: its initial `SS:SP` would exceed the minimum
allocated memory. The seven OP load-module offsets are `0x2D59`, `0x34AF`,
`0xBFB7`, `0xBFB9`, `0xDE8B`, `0xDE8C`, `0xFB97`; the five MAINE offsets are
`0x0CBD`, `0x2D11`, `0xD1D3`, `0xD1D4`, `0xE933`. These are physical MZ
program-image offsets, not standalone source function identities.

## Eight-way pack result

Each diagnostic MZ is valid and packed through the same pinned DIET 1.45f
and DOSBox-X profile. `P`, `R`, and `T` denote replacing only the named
candidate surface with bytes from the **target-restored** view. Empty means
the untouched candidate.

| Surfaces | OP packed bytes | MAINE packed bytes | Raw target equality |
| --- | ---: | ---: | --- |
| none | 42,251 | 37,985 | neither |
| P | 42,257 | 37,991 | neither |
| R | 42,239 | 37,932 | neither |
| PR | 42,243 | 37,936 | neither |
| T | 42,298 | 38,084 | neither |
| PT | 42,304 | 38,088 | neither |
| RT | 42,284 | 38,029 | neither |
| PRT | **42,290** | **38,035** | both raw equal |

The `PRT` hybrid equals the full target-restored MZ byte-for-byte. Only that
combination packed raw equal in this bounded factorial test; lengths are
nonadditive because compression depends on the whole stream. The OP and MAINE
v231 receipt SHA-256 values are
`4ab66c108ad73a4c5d2cf8cb48650c183021c5486f2a6bc23c558cedad5fe394`
and `1aaa9174653ed0dd084d57d874e1210e6998f59a3f3c862e98dc9ffa4e16df38`.
The private receipts and all hybrid inputs are under
`.analysis/reconstruction/diet-replay/v231-{op,maine}-mz-partition/`.
Superseded v229/v230 scratch copies were removed after the v231 inverse
controls and receipts passed.

This is a **diagnostic localization**. The hybrids copy target-derived bytes
and are forbidden as product source or exact-match evidence. Next resolve
the seven/five natural payload bytes and recover the compiler/linker cause of
relocation order and `T` topology. The original pre-DIET target MZ remains
unobserved; alternate preimages of the packed target are not excluded.

## v430 historical BGM BSS check

The v228 target-derived restored views have a striking `T` boundary that was
not localized in v231. Relative to the current v427/v425 topology candidates,
OP gains `0xC9C` file-backed zero bytes and MAINE gains `0xC94`; in both cases
minimum allocation falls by 202 paragraphs. The restored program-image EOF is:

| Artifact | Restored EOF | Current MAP public at EOF | `timerorg` | Span |
| --- | ---: | --- | ---: | ---: |
| OP | `0x11A40` | `_snd_load_fn` | `0x1197A` | `0xC6` |
| MAINE | `0x10062` | `_snd_load_fn` | `0x0FF9C` | `0xC6` |

That `0xC6` span is exactly the maintained `libs/master.lib/bgm[bss].asm`
layout: `timerorg`, `part`, then `esound`; `_snd_load_fn` begins immediately
after it. This initially makes the v228 zero tail look like a plausible BGM-BSS
materialization boundary.

v430 checks that interpretation against the independent historical
`_reference/ReC98/bin/masters.lib`, rather than changing source to fit the
restored image. Pinned TLIB extracts `b_data.OBJ` SHA-256
`e85c6d60229b3137b3c9c32228e3744577c74fd28e36f53712018a2d9007e688`.
Its OMF has:

- `_DATA` length `0x11C`, with one LEDATA record;
- `_BSS` length **`0xC6`**;
- `_BSS` publics `timerorg=0`, `part/_bgm_part=4`,
  `esound/_bgm_esound=0x46`;
- **zero `_BSS` LEDATA and zero `_BSS` LIDATA records**.

So the historical library object independently confirms the same BGM BSS shape
while also confirming that this state was genuinely uninitialized in OMF. It
does **not** support rewriting that BSS as initialized zero data just because
DIET `-RA` emits a repackable target-derived view whose EOF lands there.

Private receipt SHA-256:
`23ac23e2ddf3111a510eeb048c25978b6b35ebeeda4610da24b7e9873d4db1e3`.

This strengthens the existing v231 limit: the restored `T` surface is useful
for understanding one DIET preimage, but at v430 neither its file length nor
`minalloc` had an independent packed-container interpretation. v446 below later
attests the **unpacked file length** directly from target DIET metadata; it still
does not turn the zero tail into authored initialized BSS or establish the
historical TLINK `minalloc`.

## v436 current packed frontier and TLINK `/i`

The v231 factorial table predates the v397-v427 object-topology work. v436
replays the **current** v427 OP and v425 MAINE preimages through the same pinned
DIET 1.45f toolchain and then repeats the useful target-derived controls. No
product source, object bytes, or relocation-table bytes are edited for the
natural baseline.

| Input surface | OP packed bytes | MAINE packed bytes | Raw target equality |
| --- | ---: | ---: | --- |
| current natural candidate | 42,256 | 37,989 | neither |
| current + target-derived `R+T` | **42,289** | **38,034** | neither; each 1 byte short |
| current + target-derived `P+R+T` | **42,290** | **38,035** | both raw exact |

At this frontier, `P` is no longer the old seven/five-byte surface. All prior
payload residuals are closed except the shared `snd_load` handle copy
(`89 C3` target versus natural TC4J `8B D8`), two decoded bytes in each
artifact. Under the private `R+T` control, those two input bytes account for one
remaining packed byte in each file. This is a localization result only: `R`,
`T`, and `PRT` still copy target-derived bytes and are not acceptable product
inputs.

v430 made the target-restored zero tail look linker-related, so v436 also tests
the active Borland linker mechanism directly. The pinned TLINK 6.10 binary
(SHA-256 `e54f5177...`) contains its own help text:
`/i   Initialize all segments`. Adding **only** `/i` to the otherwise unchanged
current response files gives:

| Artifact | Natural MZ | TLINK `/i` MZ | `/i` minalloc | `/i` packed | Target |
| --- | ---: | ---: | ---: | ---: | ---: |
| OP | 73,636 | 83,424 | 0 | 42,383 | 42,290 |
| MAINE | 65,998 | 79,056 | 0 | 38,202 | 38,035 |

The `/i` images preserve the target-equal relocation-site multisets and merely
extend the image with zero-backed uninitialized storage, but they materialize
**all** trailing storage rather than the v228 target-derived partial tail.
Their packed outputs overshoot target by 93 and 167 bytes.

One final private control tests whether DIET might nevertheless treat the full
`/i` tail as an equivalent `T` preimage: keep `/i`'s own file extent and
`minalloc=0`, but substitute target-derived payload and ordered relocation
bytes. It still packs to **42,369** OP and **38,154** MAINE, respectively 79
and 119 bytes over target. Therefore active TLINK 6.10 `/i` is a **closed
negative** for the missing `T` mechanism, not an alternate exact preimage.

v436 private receipt SHA-256:
`c21073e17762709d0be818bcc888fd6a2db142dbb72361927745ae80826f594d`.

The remaining packed problem is thus still provenance/topology: natural source
payload is down to `snd_load`, while historical/legitimate causes for the `R`
and `T` surfaces remain unobserved. Do not retry active TLINK 6.10 `/i` unless
new evidence changes the linker identity or invocation semantics.

## v446 DIET 1.45f internal metadata

The bundled public 1.45f release contains an unusually useful self-diagnostic.
Its `UPDATE.DOC` says the 1.45d→1.45f test revision added `-^` to reveal
information during DIETing/unDIETing. The checked-in
`scripts/probes/probe_diet145f_internal_metadata.py` verifies that documentation
inside the same pinned archive, runs `DIET -^` under the already-attested
DOSBox-X profile, and parses the packed-file metadata without modifying inputs.

The real packed targets report:

| Artifact | `dlzflag` | compressed `packsize` | CRC | `unpacksize` | SFX/header overhead |
| --- | ---: | ---: | ---: | ---: | ---: |
| OP | `0x30` | `0xA342` (41,794) | `0xE124` | **`0x12C40` (76,864)** | 496 |
| MAINE | `0x30` | `0x92A3` (37,539) | `0x97CF` | **`0x10E62` (69,218)** | 496 |

Those two `unpacksize` values are exactly the v228 `-RA` restored file sizes.
Therefore the `T` **file-length** surface is not merely an arbitrary choice made
by the restore command: the packed target itself carries the same logical
unpacked length. This is narrower than proving a lost historical TLINK file.
The packed metadata still does not reveal whether that EOF came from TLINK,
an intermediate post-link transform, or another equivalent preimage, and it
does not recover historical `minalloc` provenance or historical relocation-table
order.

The current v432 factorial gives two further constraints. In both artifacts,
private target-derived `R+T` produces compressed data exactly **one byte shorter**
than target, while `P+R+T` matches target `packsize` and CRC. `P` at this frontier
is only the shared two-byte `snd_load` `89 C3` versus natural `8B D8` residual.

MAINE additionally exposes a format-mode threshold entirely controlled by `T`:

| MAINE factorial cells | `dlzflag` | overhead | `unpacksize` |
| --- | ---: | ---: | ---: |
| base, `P`, `R`, `PR` | `0x20` | 444 | 65,998 |
| `T`, `PT`, `RT`, `PRT` | **`0x30`** | **496** | **69,218** |

Thus neither payload bytes nor relocation order cause the MAINE target's larger
SFX form; changing the `T` extent alone does. OP is already `0x30` / 496 in all
eight cells.

Private receipt SHA-256:
`e40613031d86a0c5646845f6d3af415cdf1ca8d3990e84b1ac6c98942871aa41`.

All non-target factorial cells are private target-derived diagnostics and grant
no reconstruction credit. The practical routing change is only this: preserve
the target-attested logical unpacked lengths as a real packed-file constraint,
while continuing to treat v228 relocation order and the source of the zero-backed
extent/minalloc as unresolved reconstruction questions.

## v490 minalloc is derived from the T extent

Earlier packets conservatively kept the target-restored `e_minalloc` values as
an independent historical-header provenance question. v490 separates that field
from the still-open `T` file extent.

For a DOS MZ whose initial stack lies beyond the file-backed load image, the
observed Borland outputs in this corpus satisfy:

```text
e_minalloc = ceil(max(0, e_ss * 16 + e_sp - load_image_bytes) / 16)
```

The checked probe applies this formula to eight identity-bound cases:

- current v489 OP and MAINE natural candidates;
- v228 target-restored OP and MAINE views;
- retained v436 target-derived `RT` controls;
- retained v436 full `/i` controls.

Every case matches its MZ header exactly. In particular:

| Artifact | Natural load bytes | Restored load bytes | SS:SP | Natural minalloc | Restored minalloc |
| --- | ---: | ---: | ---: | ---: | ---: |
| OP | 69,028 | 72,256 | `4918:0080` | 612 | 410 |
| MAINE | 62,414 | 65,634 | `4709:0080` | 817 | 615 |

The initial stack endpoint is unchanged. The restored `T` surface adds 3,228 OP
bytes and 3,220 MAINE bytes; both increases round up to **202 paragraphs**,
exactly the observed minalloc drop. The v436 `/i` controls file-back storage all
the way to the stack endpoint and correspondingly have `e_minalloc=0`, again
matching the same formula.

Therefore `minalloc` is **not an independent reconstruction degree of freedom**
for the remaining packed frontier. Once the target-attested file extent and
unchanged `SS:SP` are fixed, the header field follows mechanically.

This does **not** explain what historical linker or post-link step produced the
target-attested `T` extent. v446 already proves that packed DIET metadata carries
that larger logical unpacked length, and v436 proves that active TLINK 6.10 `/i`
is not the mechanism. The remaining packed-header problem is the provenance of
`T` itself, not a separate search for `minalloc`.

Private receipt SHA-256:
`a76b89c99b6f008f7e6f5986a785d45af66fe5048875a64f738d804696a3fec9`.
