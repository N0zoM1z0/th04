# TH04 native PC-98 scroll and GRCG rectangle owners

2026-09-27 product-build investigation. The local historical library supplies
bounded semantic reference behavior; it is not evidence that these TH04
implementations reproduce target bytes or real hardware timing.

`src/shared/hardware/graph_scrollup.asm` owns the far Pascal
`GRAPH_SCROLLUP(line)` entry. It clamps the requested line count to the
current `graph_VramLines`, applies `graph_VramZoom`, waits for the graphics
GDC parameter FIFO, and sends the two start-address/line-count runs through
PC-98 ports `0xA2` and `0xA0`. Its near helper writes a 16-bit parameter
with the inter-byte delay used by the bounded reference.

`src/shared/hardware/grcg_byteboxfill_x.asm` owns the far Pascal
`GRCG_BYTEBOXFILL_X(left, top, right, bottom)` entry. It clips vertical
coordinates against the TH04-owned `ClipYT` and `ClipYH`, rejects reversed
X or Y ranges, then writes `0xFF` to each byte in the inclusive rectangle.
It advances ES by five paragraphs per row, equal to 80 VRAM bytes. The
caller owns GRCG mode and tile state; this routine does not silently change
it. Horizontal clipping is absent, as in the bounded reference.

Both additions are semantic product candidates. TC4J/TASM32 emitted valid
OMF and two cold 114-TU no-archive MAINE links each leave 28 unresolved
names with zero warnings, down exactly two from the prior graphics-start
checkpoint. Their link-relevant and timestamp-normalized objects agree;
BGIMAGE has only the known raw dependency timestamp drift. Cold receipt
SHA-256: `5f4fceb14aa7e50ce465408c6725fb4bd92dbb11901c7ad6369714cb123097da`
and `7b44e3af3fb3e7d7b218e183e63a33a4d8b5db107b5e8e3b79ad7b7c17bf9f15`.

The historical-library calibration link exits 0 with its existing archive
dictionary warning (receipt
`888c8234cd377d7baa2ca87bd9d1a5f9fd10540ec2c3ea4bb684bd1d16eab746`).
The resulting MZ has 594 unique in-image relocation sites; its entry, stack,
and two DOS load checks pass (receipt
`8985974013985b08718dff408cd9ff93bfb0b22719545886cec91b52eabba63d`).
The call ABI audit checks 14 local entry returns, 51 relocated direct far
calls, and one same-CS `push cs; call rel16` (receipt
`63e84693b5be4e38a9d989ab269b9b8742b6ba39bbca628246bff3f7a9aa4bf5`).

These static checks cannot establish GDC timing, GRCG write effects, or a
runnable TH04-only product. The original MAINE entry still needs a valid
OP→MAIN→MAINE scenario; the no-archive link still needs 28 local support
names. For TH05, keep graphics state ownership, far ABI, GDC FIFO timing,
and VRAM write semantics as separately testable surfaces.

## MAIN integration: top stripe and explicit slowdown

The 2026-10-03 user reports show a top stripe during Marisa/Normal versus
Reimu, the corresponding Reimu versus Marisa background, and late Yuuka's
checkerboard background. Marisa's bomb removes it in both tested fights.
These are user observations; the screenshots do not establish an original
behavior or a confirmed cause. The bomb path explicitly calls
`graph_scrollup(0)` at frame 48, restores `graph_scrollup(scroll_line)` at
frame 177, and changes background rendering during that interval. A display
origin mismatch and incomplete redraw remain distinguishable hypotheses.

A separate defect is confirmed in the current product. Three initialization
names and driver names own different native storage, although the target
uses one field for each pair:

| State | Target DS offset | Native driver symbol at DGROUP | Native initialization symbol at DGROUP |
| --- | --- | --- | --- |
| Previous row-copy request | 3DBE | `_byte_250FE`, 227F:C767 | `_scroll_row_advance_previous`, 227F:B56D |
| Current row advance | 3DC4 | `_byte_25104`, 227F:C768 | `_scroll_row_advance_current`, 227F:B56E |
| Previous tile-ring row | 3DC0 | `_word_25100`, 227F:C769 | `_tile_ring_scroll_row_prev`, 227F:B56F |

The native addresses belong to build `product-20261003-040353-7d7e1b7e` and
must be rediscovered from a later MAP. The original target initialization
slice at load B1D6..B207 clears all three driver fields. Native initialization
at MAIN 0708:03BA..03EB clears only the separate semantic fields. A Unicorn
CPU control seeds the fields with A5/A5/CAFE and reproduces original zeros
versus retained native A5/A5/CAFE. The historical source-transform aliases
`alias-scroll-row-{prev,current,previous}-v166` already describe single-field
ownership. Their historical acceptance is not transferred to this native link.
This proves an initialization/ownership defect; it does not yet prove the
reported stripe's visual cause. Source repair and Windows replacement are
postponed while the user tests. Unify the product owners and then replay
stage transitions, both pages and the original/native display-scroll state.

The Reimu/Marisa backdrop body at original load BEDA..BF14 and native MAIN
0708:1490..14CA has identical 59-byte code. An ordinary-RAM write-address
control observes 9,472 written bytes, including every playfield byte in rows
16..31. This rejects a simple missing-top-row loop hypothesis for that producer.
It does not emulate GRCG tile colors, page selection, or GDC display origins.

The late Yuuka cross-pattern report also needs timing separation. In the
attested original MAIN target, load 1CB04..1CB40 implements the existing
bullet-count slowdown: when Turbo is off, threshold = 24 + playperf + rank*8;
on even stage frames at/above that threshold, `slowdown_factor` becomes 2.
`slowdown_frame_delay()` waits for that many vertical-sync ticks. Normal's
threshold is 32 + playperf. A bounded original/native CPU replay checks 96
combinations of Turbo, rank, performance value, threshold boundaries and frame
parity; all results agree. The cross-spawn phase has no separate explicit
slowdown assignment in its source. These controls prove the preserved policy,
not the user's active Turbo/count state or adequate Windows frame pacing.

```text
python3 scripts/probes/probe_th04_native_scroll_and_slowdown.py --build-dir .analysis/build/semantic-heap-readable --output-dir .analysis/reconstruction/probes/NEW-render-policy
```

Attested replay receipt:
`.analysis/reconstruction/probes/render-policy-v1229-clean/receipt.json`.
The probe verifies full MZ identities/integrity, MAP identity and the Unicorn
engine digest. It copies unrelocated modules at load segment 2000 and executes
only prefixes/branches without used relocation operands, with synthetic DS=8000
and SS=7000. No PC-98 launch, actual in-game state, or full visual acceptance
is claimed; all target/unit acceptance states remain unchanged.
