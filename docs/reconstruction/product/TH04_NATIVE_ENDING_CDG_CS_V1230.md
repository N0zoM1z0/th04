# Native Ending CDG instruction ownership

The user's Reimu/Lunatic Good Ending stopped before score registration,
with image remnants and continuing sound. The prior PI slot lifetime repair
was insufficient. This note separates a confirmed native code corruption
from the remaining full-route and emulator questions.

## Defect and source repair

The deployed MAINE SHA-256 `0a2d3ce89e7663265b4c498a66b78225e14ea75af9a59a40066928ea6d18afba`
has the following compiler-observed ownership mismatch:

| Renderer | Native extent | Intended writable immediates | Actual CS-relative destinations |
| --- | --- | --- | --- |
| `CDG_PUT_PLANE` | 0703:5C3C + 009A | 5CA1, 5CA8, 5CB5 | 30C1, 30C8, 30D5 |
| `CDG_PUT_8` | 0703:5E3C + 009E | 5EB4 | 32D4 |

Direct far calls use CS frame 0703. All four actual destinations lie in
the shared PI decoder contribution, 0703:2D63 + 08E4. TASM's segment-relative
labels disagree with the group-relative far-call frame by 2BE0h. Private
CPU replay of the unchanged, relocated deployed code at load segments 2000h
and 6000h reproduces the writes into the PI decoder and leaves the renderer
immediates unchanged. This is native-product evidence, not packed target
byte equality or an original-game behavior claim.

With `TH04_LARGE_PRODUCT`, the shared color renderer now owns
`TH04_CDG_PUT_TEXT`, and MAINE's plane renderer owns `TH04_CDG_PLANE_TEXT`.
Both are independent code frames. The build auditor includes both owners,
their CS-relative operands and actual direct far callers. The previous
auditor omitted these CDG owners.

The first repaired normal MAINE, SHA-256 `56a023af4fa69b60391337ca5872de4c42d718d5430c850894fb443b7fe21f2c`,
has plane entry 0D82:000E and color entry 0D8C:0008. The plane writes its own
0073 width byte and 007A/0087 mask words; the color entry writes its own
0080 segment word. Rediscover all addresses from subsequent MAPs.

## Bounded verification

```text
python3 scripts/probes/probe_th04_native_cdg_cs.py --build-dir .analysis/build/native-ending-scroll-fix --output-dir .analysis/reconstruction/probes/native-cdg-cs-fixed-20261003
python3 scripts/probes/probe_th04_native_scroll_and_slowdown.py --build-dir .analysis/build/native-ending-scroll-fix --output-dir .analysis/reconstruction/probes/render-policy-fixed-20261003
```

The CDG CPU replay uses real pinned `SFF1B.CDG` and `SFF1.CDG` assets. At
both load segments, complete far calls return, all four patches stay in their
own renderer, and the aligned plane pixels match their real source rows.
The old semantic-heap MAINE fails the same complete-call control. Ordinary
RAM replaces VRAM in this check: GRCG color compositing and full Ending
behavior require the separate emulator replay.

Four cold before/after TASM builds without `TH04_LARGE_PRODUCT` preserve
all link-relevant OMF records after normalizing only source timestamps:
shared CDG color renderer, MAINE CDG plane renderer, MAIN scroll state and
MAIN stage-resource state. Receipt:
`.analysis/reconstruction/probes/ending-scroll-default-omf-replay-20261003/receipt.json`.
The raw objects differ in source timestamps. This source-to-source control
does not promote original-target exactness.

## Runtime scenario

`scripts/probes/prepare_th04_good_ending.py` creates a private diagnostic
image from a pinned original HDI and verified source products. An openly
labeled NASM COM fixture seeds the resident block and executes real MAINE;
it bypasses gameplay and OP initialization. The resident sound mode is zero,
so Staff Roll uses frame-based waits. The fixture must never enter a user
package. The runner records optional built-in DOS, fixed CPU cycle and
bitmap-font controls without changing the pinned baseline configuration.

The preliminary Reimu/Lunatic built-in-DOS replay displays the cutscene,
Staff Roll and the registration score table at 240 seconds. The score file
has not yet changed at that checkpoint. OP-first diagnostics remain at a
pink rectangle and do not establish MAINE execution; the initial held-key
run also ends before its requested final checkpoint. These are unaccepted
negative controls.

The cleared-text Reimu/Lunatic and Marisa/Normal runs display registration and
accept six name characters before Esc completes entry. Both persist the
fixture score 12,345,678: only sections 3 and 6 change respectively. All ten
section checksums pass, every changed-section score digit is valid, and the
other nine sections stay byte-identical. The starting user-derived disk has
an unchanged blank Reimu Easy section; do not misreport that existing blank
as a newly corrupted score. Receipts:
`.analysis/runtime/candidates/ending-cdg-fixed-20261003/{reimu-lunatic,marisa-normal}/run-clear/{receipt,score-save-control}.json`.
Both final frames at 340 seconds are black, so they do not accept return to
OP. The user independently confirms death registration/save in the new
normal Windows package; that scenario skips the Ending/Staff Roll path.

None of these seeded scenarios establish full ordinary gameplay, Windows
frame pacing or cross-emulator agreement. The user's next Windows playtest
must cover the actual gameplay-to-Ending handoff.
