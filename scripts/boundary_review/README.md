# TH04 boundary-review tools

These scripts inventory function-like boundaries and classify their ownership;
they do not reconstruct source or promote exactness.

The DIET target-stub Oracle pins its Python execution engine. Install it into
the active Python environment if absent:

```bash
python3 -m pip install 'unicorn==1.0.2'
```

Run them in this order for a full private refresh:

1. `unpack_diet.py` — execute each packed target's own DIET stub at two load
   segments and recover a load-invariant unrelocated payload.
2. `prepare_analysis_images.py` — compare those payloads with a cold candidate
   and create private Ghidra analysis images.
3. `export_ghidra_inventory.py` — import/check a headless Ghidra project and
   emit a nonce-bound function inventory.
4. `export_tasm_function_boundaries.py` — use the attested TASM32 5.0 to expose
   local `PROC` entries omitted by MAP files and sometimes by Ghidra.
5. `build_function_boundary_ledger.py` — merge target Ghidra observations,
   candidate MAP ownership, TASM `PROC` entries, configured COM regions, and
   accepted MAIN decisions into `config/th04_function_boundaries.csv`.
6. `validate_function_boundary_ledger.py` — fail closed on malformed routing,
   accidental runtime/library promotion, or divergence from the accepted MAIN
   function ledger.
7. `report_function_boundaries.py` — regenerate `docs/BOUNDARY_REVIEW.md`.

The exact commands and evidence limitations are in
`docs/BOUNDARY_REVIEW.md`. Generated executables, payloads, listings, projects,
and exports stay below ignored `.analysis/` or `ghidra-project/` paths.
