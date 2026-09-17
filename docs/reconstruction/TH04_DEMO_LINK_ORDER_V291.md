# MAIN DEMO link-input order control, v291

The pinned MAIN target's stage-session owner is `DEMO_TEXT` 0AAF:03E0,
load 0xAED0..0xB3ED, file 0xC6D0..0xCBED, size 0x51E. The v214 maintained
source links byte-identically and has all 52 relocation sites, but the
ordered table differs. Target owner entries occupy global MZ indices
22..62 and 89..99; the v214 candidate puts all 52 at 506..557.

`python3 scripts/probes/probe_th04_demo_link_order.py --output-dir
.analysis/reconstruction/probes/v291-demo-link-order-replay` attests the
target, v214 cold snapshot objects/response, and pinned toolchain. It copies
that snapshot into temporary private trees and changes only the TLINK
response's object order. Both trials produce valid MZ files:

| Link input change | Session MAP start | Session's global MZ indices | Owner raw difference | Owner site set |
| --- | ---: | ---: | ---: | --- |
| Move `sess.obj` just after `coanch.obj` | 0xAB0C | 4..55 | 1,275 bytes | differs |
| Move `main.obj`, then `sess.obj`, after `coanch.obj` | 0xAED0 | 357..408 | 61 bytes | same |

Neither trial matches ordered relocations. The first moves the session code
away from its target address. The second retains the session MAP start and
all 52 sites, but changes 61 linked bytes. Object order does influence MZ
table position; a plain response reorder cannot satisfy byte, layout, and
relocation gates together. The original target OMF and link response remain
unknown. A subsequent producer hypothesis must explain why the target
places the DEMO prefix, session, EMS, and DEMO tail fixups in early runs
while preserving their linked values and code positions.

Private receipt SHA-256:
`a62f143c5040e309ced67b37472541db33e4953bdae9c0af84a049b35895a9c9`.
No exact promotion.
