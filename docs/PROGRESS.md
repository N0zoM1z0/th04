# TH04 reconstruction progress

This is a conservative snapshot derived from `config/units.csv`. The reviewed
authored denominator is provisional and grows only as target boundaries and
ownership are verified.

| Measure | Count |
| --- | ---: |
| Required target artifacts | 4 |
| Required target bytes | 244,337 |
| Reviewed authored units | 1 |
| Reviewed authored bytes | 26 |
| Source-present authored units | 1 / 1 |
| Source-present authored bytes | 26 / 26 |
| Accepted exact units | 0 |
| Accepted exact target bytes | 0 / 244,337 (0.00%) |

`slowdown_frame_delay` currently has maintained source and a locally compiled
26-byte candidate slice that matches its target extent. It remains
`source-present`, not `exact`, because the complete required unit-bound Oracle
set and checked-in cold replay have not been recorded.

Only units whose ledger state is `exact` fill the exact bar. Source presence,
an upstream implementation, a matching slice from an untrusted aggregate
candidate, and the SVG itself never promote a unit.
