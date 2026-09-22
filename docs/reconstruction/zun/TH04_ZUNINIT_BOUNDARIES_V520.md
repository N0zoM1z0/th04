# ZUNINIT physical boundary review (v520)

This packet closes the physical code/data boundaries of the complete ZUNINIT
component in the decoded TH04 ZUN.COM payload. It does **not** establish that
the target-derived candidate assembly is original source, and it grants no
authored exactness.

## Target component

The attested decoded ZUN payload contains ZUNINIT at payload
`0x6F3..0xB67`, size `0x475 / 1141` bytes, SHA-256
`692b1e056d907a9649bd1effa6e83239f71039d17de3569464067d0b42b7aa5e`.

The complete component is partitioned without gaps or overlaps into eight code
extents and two data islands:

| Entry | Payload extent | Size | Terminal |
| --- | --- | ---: | --- |
| `start` | `0x6F3..0x6F5` | `0x03` | near `JMP` |
| `sub_103` | `0x6F6..0x707` | `0x12` | `IRET` |
| `sub_115` | `0x708..0x719` | `0x12` | `IRET` |
| `sub_127` | `0x71A..0x7AF` | `0x96` | `RET` |
| `sub_1BD` | `0x7B0..0x7C1` | `0x12` | `RET` |
| `sub_1CF` | `0x7C2..0x7FC` | `0x3B` | `RET` |
| data | `0x7FD..0x8FE` | `0x102` | non-code |
| `sub_30C` | `0x8FF..0x925` | `0x27` | `RET` |
| `start_0` | `0x926..0x9FF` | `0xDA` | DOS `INT 21h/AH=4Ch` exit |
| data | `0xA00..0xB67` | `0x168` | non-code |

`start_0` therefore ends at runtime COM offset `0x40D`; the following `0x168`
bytes are data. Ghidra's previous sparse extra ranges are not part of this
function.

## Independent boundary evidence

Run:

    python3 scripts/probes/probe_th04_zuninit_boundaries.py \
      --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The probe first attests the target and toolchain. It then checks the retained
candidate assembly, MAP, and linked ZUNINIT component identities. A fresh TASM32
5.0 expanded listing must expose exactly the eight expected PROC entries.

Those PROC entries are only corroboration. Each function extent is independently
decoded from the hash-attested target bytes with `ndisasm`; its full branch edge
vector and terminal instruction are checked, and no control-flow edge may enter
either configured data island. The union of all reviewed code extents and the
two data islands must tile the entire component exactly.

The candidate linked ZUNINIT component happens to be raw-equal to the target
component. That equality is not used as source authority and does not convert
the target-derived candidate assembly into accepted original ASM.

The durable v520 receipt is
`.analysis/reconstruction/probes/v520-zuninit-boundaries-001/receipt.json`,
SHA-256
`39433b3b834143b7dd7e3a5daca42127171e42e702e7c0b61a4889c41d76bab7`.

A fresh replay after wiring the ledger override support produced
`.analysis/reconstruction/probes/v520-zuninit-boundaries-002/receipt.json`,
SHA-256
`a4046ed18aa262c5ea753541f26346ad2802d050547ccd6670e4a5732d64985e`,
with the same partition and target component identity.

## Ledger effect

All eight ZUNINIT function-like entries are now `boundary_state=reviewed`.
This removes the remaining six provisional ZUN authored boundaries and upgrades
the previously corroborated `sub_30C` entry to reviewed. The source form remains
`target-derived-asm` for every ZUNINIT entry.

No `units.csv` source owner is added, no function becomes exact, and the eleven
ZUN `target-derived-asm` source/origin questions remain open. The next ZUN work
is provenance/ownership for ZUNINIT and MEMCHK plus replacement of external
component/link inputs, while `_main` and `cfg_init` stay blocked as documented
by v518/v519.
