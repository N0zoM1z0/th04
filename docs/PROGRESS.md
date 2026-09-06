# TH04 reconstruction progress

This is a conservative snapshot derived from `config/units.csv`. The reviewed
authored denominator is provisional and grows only as target boundaries and
ownership are verified. It is intentionally not the size of the four complete
executables.

| Measure | Count |
| --- | ---: |
| Screened source-module contributions | 58 / 17,412 bytes |
| Raw-aligned module candidates | 54 / 14,123 bytes |
| Ghidra function entries in screened modules | 151 |
| Reviewed authored units | 16 |
| Currently confirmed authored bytes | 1,446 |
| Source-present authored units | 1 / 16 (6.25%) |
| Source-present authored bytes | 26 / 1,446 (1.80%) |
| Accepted exact units | 0 |
| Exact / currently confirmed authored bytes | 0 / 1,446 (0.00%) |

`slowdown_frame_delay` currently has maintained source and a locally compiled
26-byte candidate slice that matches its target extent. It remains
`source-present`, not `exact`, because the complete required unit-bound Oracle
set and checked-in cold replay have not been recorded.

The other 15 reviewed units have complete target boundaries but no maintained
source yet. Another 42 module-level candidates remain provisional and do not
enter the authored denominator. See
`docs/reconstruction/TH04_MAIN_AUTHORED_SCREEN.md` for the screening method and
next-work routing.

Only units whose ledger state is `exact` fill the exact bar. Source presence,
an upstream implementation, a matching slice from an untrusted aggregate
candidate, and the SVG itself never promote a unit.
