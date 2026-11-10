# Private inputs and disposable output

Keep files because they support current work, contain unique useful knowledge,
or would be expensive to reconstruct. Age, a historical reference, and an old
successful test are not retention reasons.

Keep original programs and required game data, current source and exact-match
ledgers, complete build/comparison scripts, active analyzer projects, and the
locked compiler, headers, libraries and runtime dependencies actually in use.
Keep a special compiler context only when an unresolved problem needs it and
it cannot reasonably be recreated from source and configuration.

Delete superseded builds, duplicate captures, historical archives, temporary
prefixes and cleanup reports. Retain a short conclusion or failed approach
when it will help the next reconstruction task. Remove obsolete recovery
instructions and private-output references from working documentation.
Do not create another archive, permanent inventory or cleanup report.
Historical ledger observations remain provenance; regenerate comparison
outputs when a new exact claim needs them.

## Tools and verification

Prefer matching Factory installations. Share executable tools while keeping
each game's Wine prefix, analyzer project and writable state separate. Moving
the only installation into Factory does not release disk space.

Host and target architectures are separate dependencies. Check current build
configuration and actual receipts before removing components. For uncertain
components, temporarily move them aside, verify the affected compile, link,
runtime or resource path, then delete the temporary copy. Restore on failure;
check whether the original environment fails too before blaming the trim.
Never overwrite canonical objects or existing receipts during these checks.

Use fresh temporary output and run only affected checks. Exact source changes
still require comparison of complete owned extents and relocations, including
consumers of changed shared inputs. No historical full-cohort replay is needed
for deleting obsolete output or editing prose.

## Default CI

`python3 scripts/ci.py` checks the complete current Git tree's machine-readable
syntax, reconstruction ledgers, source paths in build configuration, accidental
private files and whitespace. It needs Python 3.11 and Git, with no original
programs, private tools or reference checkout. CI passes the PR/push base through
`CI_BASE_REF` to check whitespace across the full change; `--base COMMIT` does
the same locally. Comparator and compiler tests are selected for their changes.
