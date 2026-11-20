# DOS position independence

The maintained DOS `MAIN.EXE`, `OP.EXE`, and `MAINE.EXE` passed two
relinks that moved code and data within their frames. The unchanged-object
control reproduced the complete executable and MAP for each artifact.
The cold baseline used the product sources at `75ff6d2` and the pinned
Borland toolchain. ZUN supplied the same startup program in both runs.
[ReC98 scope](../../REFERENCE_ANALYSIS.md#th04-position-independence).

## Link and source evidence

The replay inserts public-segment contributions after an existing
definition. It preserves the order and hashes of the original objects.
The two runs insert 16/32/48 and 32/16/64 bytes of CODE/DATA/BSS respectively.
Each real contribution retains its extent. The check maps MZ relocation
sites back to those contributions and follows immediate far CALL/JMP
targets to their code owners. The 2,666 relocation sites retain their
order within the matched owners in both runs.

| DOS artifact | CODE / DATA / BSS contributions moved within frame | MZ relocation sites | Far transfers with matching destinations |
| --- | ---: | ---: | ---: |
| MAIN | 343 / 87 / 61 | 1,183 | 957 |
| OP | 195 / 73 / 27 | 819 | 569 |
| MAINE | 174 / 56 / 23 | 664 | 511 |

Both layouts pass the existing IRQ-vector and self-modifying operand checks
for all three executables, and both MAIN bullet switch checks. MAINE's SHARED
paragraph frame is an alias within its larger link group. The far calls
from the PAR and BGM interrupt owners still land at the same offsets in
their respective destination owners. The MAINE negative controls kept
the original layout, dropped a relocation, or restored a moved far call's
old offset. The checker rejected all three.

Capstone 5.0.6 screened 10,841 direct 16-bit CS/DS displacements that could
name a mapped owner. Of 75 candidates flagged for review, 22 belong to
maintained sources. In MAIN they fall in compiler switch keys and jump
tables. In MAINE three fall in jump tables and one starts inside the
displacement of a real instruction in `sub_bb81()`. OP has no maintained
source candidates from this screen. The other 53 are in Borland runtime
members. A separate source review covered direct numeric memory operands,
absolute pointer construction, and emitted asm opcodes. The observed
fixed addresses belong to PC-98 hardware, BIOS, and DOS interfaces.

OP's resident counter follows its resident pointer from `0FF2:2626`
to `1012:2676` in the alternate layout. MAINE's entry operand follows
`CONG00.pi` from `0F3B:0111` to `0F61:0121`. The latter is the reference
that ReC98 resolved to reach its TH04 PI milestone.
[OP counter check](../../../scripts/probes/th04_product_surface.py),
[ReC98 change](https://github.com/nmlgc/ReC98/commit/97f0c3b4f53a60caed48ffba1a7fa0817fd1dd0e).

This screen sees direct displacements. Register-carried or computed
addresses and unexercised paths still need review for a whole-product PI
claim. Treat the score pair and the random ring plus cursor as contiguous
owners when moving them. The earlier score experiment demonstrates why
splitting those owners can change behavior.
[Source review and score control](../../REFERENCE_ANALYSIS.md#th04-position-independence).

## Runtime evidence

Muted DOSBox-X runs booted each build through GAME.BAT and OP into bundled
Demo 1 in Stage 4. The observer verified the complete relocated MAIN image
on entry against each build's own file. The 3,996 gameplay rows and terminal
row match on consumed input, score, RNG state and call order, player state,
and the recorded resident fields. The other demos and full ending/registration
routes are outside this runtime sample.

Independent 16-bit CPU replays of both builds' MAINE use the pinned
`SFF1B.CDG` and `SFF1.CDG` resources at load segments `2000h` and `6000h`.
Both far calls return, the four self-modifying operands stay in their own
renderers, and the aligned plane output matches the source image bytes.
[Component scope](TH04_NATIVE_ENDING_CDG_CS_V1230.md).

## Replay

```sh
python3 scripts/build.py --output-dir .analysis/build/pi-dos-baseline
python3 scripts/audit_th04_dos_pi.py --baseline .analysis/build/pi-dos-baseline \
  --output-dir .analysis/build/pi-dos-audit-final
python3 scripts/audit_th04_dos_pi.py --baseline .analysis/build/pi-dos-baseline \
  --output-dir .analysis/build/pi-dos-audit-alt --padding 32 16 64
```

Use each build's own MAIN MAP with `capture_th04_dos_demos.py --demos 1`.
Compare the two runs with `compare_th04_dos_demos.py --baseline` and
`--candidate`. Run `probe_th04_native_cdg_cs.py` against both builds.
The `ev-th04-*-dos-pi-*` evidence rows identify the receipts and input
digests. These results describe the standalone DOS product; the historical
exact-match ledger has a separate scope.
