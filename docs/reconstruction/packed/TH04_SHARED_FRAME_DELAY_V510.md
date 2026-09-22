# OP/MAINE shared frame-delay acceptance (v510)

The maintained natural C++ source src/shared/hardware/frame_delay.cpp now has
artifact-local decoded acceptance in both OP.EXE and MAINE.EXE. This is a
decoded-function claim only: the DIET-packed files provide no honest direct
file offset for these bodies, and ReC98 remains link scaffolding rather than
accepted TH04 product source.

OP's reviewed authored function is SHARED 0DA1:002B, decoded load
0xDA3B..0xDA4F (21 bytes). MAINE's is SHARED 0CC7:0033, decoded load
0xCCA3..0xCCB7 (21 bytes). Both end at RETF 2 immediately before the reviewed
PI palette owner.

Run:
  python3 scripts/probes/replay_th04_shared_frame_delay.py --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay copies the retained v489 artifact-local scaffold twice, replaces
only th02/frmdely1.cpp with the maintained TH04 source plus checked-in shared
headers, cold-compiles it with the pinned TC86 4.02 profile, validates the
generated OMF producer, relinks with TLINK 6.10, checks the MAP contribution,
compares every ordered MZ relocation, and raw-compares the complete function
body.

Initial receipt:
.analysis/reconstruction/probes/v510-shared-frame-delay-001/receipt.json,
SHA-256 ae9d0c3dd2293e31fed7f8393c023d7bcf871d7f2acf062826fa7c5759b829d0.
Both rounds emit object SHA-256
627ddce0b68d13f499f09f1154145321bdf06fea8fa85eea89cc7e60f3cfae4a.

OP's target/candidate function SHA-256 is
1683f148a8bda60e6dbbe69510b3d79544e84057d6b7721facfaed4820f134aa;
all 804 ordered relocations match and the complete candidate program image is
unchanged from the v489 baseline. MAINE's function SHA-256 is
0d77d41527daea4e009dcbcdbf7fb8fc956243a9cc04dfd9dc2a289468243d2b;
all 559 ordered relocations match and its complete program image is likewise
unchanged. Each function has zero raw differences in both cold rounds.

The full decoded acceptance wrapper also cold-replayed all previously accepted
BGIMAGE and VRAM functions together with frame_delay. OP receipt
v510-decoded-op-001 has SHA-256
edeb12a60a3ed515dcddc3fb94c9ba1c08d7c3e6cc22add57735f300993fbe09;
all five OP slices are raw-zero. MAINE receipt v510-decoded-maine-001 has
SHA-256
130222df56fe201ecbc53ab61e8e9ed574711947d4a0b130a4e9c780065605d5;
all five MAINE slices are raw-zero.

The corresponding units.csv rows remain source-present; their boundary and
decoded-acceptance rows carry the function-level exact state. No MAIN credit,
packed-file exactness, or whole-artifact exactness is inferred. The next
hardware/PI packet is the maintained pi_put.cpp producer
(pi_palette_apply + pi_put_8) and pi_load.cpp, independently replayed in both
artifacts.
