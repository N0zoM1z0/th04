#!/usr/bin/env python3
"""List script purposes by task; maintain a complete, checked catalog without running probes."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = {
    'setup': 'Pinned targets, tools and environment attestation',
    'tracking': 'Status, ledgers, CI and maintenance',
    'build': 'Standalone DOS products and Windows packaging',
    'matching': 'Historical raw/OMF/layout matching and compiler probes',
    'boundaries': 'Physical boundaries and disassembler databases',
    'runtime': 'Emulator scenarios, images, checkpoints and fault observers',
    'hardware': 'PC-98 ABI, vectors, planar video, timing and sound controls',
    'formats': 'Archives, images, fonts, memory and score-file services',
    'source-review': 'Source ownership, dependencies and provenance review',
    'support': 'Imported libraries, fixtures and tool-side support',
}
EXTENSIONS = {'.py', '.sh', '.ps1', '.cmd', '.bat', '.java', '.asm', '.gdb'}
OVERRIDES = {
    'build.py': ('build', 'Build/publish local-source DOS products after all requested build and link audits.'),
    'build_zun_composite.py': ('build', 'Build the local-source ZUN container and embedded resident components.'),
    'export_windows_play.py': ('build', 'Package verified DOS products and launchers while retaining nonproduct image files.'),
    'play_invincible.py': ('build', 'Build/package the separately staged invincible MAIN variant for testing.'),
    'prepare_product_hdi.py': ('runtime', 'Prepare a disposable original-data image with verified source or original products.'),
    'build_th04_demo_emulator.py': ('runtime', 'Build a resource-limited pinned read-only normal-core demo observer.'),
    'capture_th04_dos_demos.py': ('runtime', 'Capture ordinary bundled DOS demos after replay input and at the terminal decision.'),
    'compare_th04_dos_demos.py': ('runtime', 'Reject incomplete/reset-mismatched demo traces and report the first logical divergence.'),
    'inspect_th04_demo_snapshots.py': ('runtime', 'Read back DGROUP snapshots against complete ordinary demos and diagnose actor differences.'),
    'check_th04_midboss4_initial_state.py': ('runtime', 'Check the Stage4 midboss toggle initializer and DATA ownership against pinned MAIN.'),
    'th04_demo_snapshot.gdb': ('runtime', 'Observe stage-frame writes in host RAM and take read-only DGROUP diagnostic snapshots.'),
    'th04_demo_dgroup_stream.gdb': ('runtime', 'Read every demo DGROUP at frame-counter writes through natural termination.'),
    'th04_demo_dgroup.py': ('runtime', 'Decode complete compressed DGROUP streams with order, address and stage validation.'),
    'th04_demo_host_ram.py': ('runtime', 'Read conventional emulator host RAM with an independent read-only VM86 page walk.'),
    'compare_th04_demo_dgroup.py': ('runtime', 'Attest nine pool extents and compare every raw actor/effect byte against complete ordinary controls.'),
    'prune_analysis.py': ('tracking', 'Review private retention; default dry run, explicit apply after archive verification.'),
    'product_input_fingerprint.py': ('build', 'Compute validated product/cache input identities.'),
    'check_default_repair_omf.py': ('matching', 'Compare complete default-branch OMF across native repair revisions.'),
    'index.py': ('tracking', 'Browse or check this catalog; no target/probe is executed.'),
    'bootstrap_analysis_toolchain.sh': ('setup', 'Download/install the pinned Ghidra/JDK pair into ignored private tools.'),
    'bootstrap_toolchain.sh': ('setup', 'Acquire/install calibrated Borland candidate tools below ignored private state.'),
    'ExportFunctionInventory.java': ('support', 'Export a read-only Ghidra function inventory for physical boundary review.'),
    'ExportMzAttestation.java': ('support', 'Export loaded MZ bytes/mappings for independent database attestation.'),
    'SeedCodeEntries.java': ('support', 'Seed the DOS entry before headless auto-analysis; this is an analysis aid.'),
    'th04_cpu_fault_fixture.asm': ('runtime', 'Private real-mode DIV-zero observer calibration; never install in game media.'),
    'th04_primary_cpu_fault.gdb': ('runtime', 'Run the primary-emulator fault observer with configured symbols/event inputs.'),
    'good_ending.asm': ('runtime', 'Private resident seed for real MAINE Ending tests; bypasses OP/gameplay initialization.'),
    'tool-env.sh': ('setup', 'Source pinned Ghidra/JDK environment paths into the current shell.'),
    'Build-TH04.ps1': ('build', 'English Windows-to-WSL DOS build progress, validated fast reuse, normal/cold/launch options.'),
    'build-th04.cmd': ('build', 'Forward command-line arguments and exit status to Build-TH04.ps1.'),
}


def category(path: Path) -> str:
    """Routing labels only: neither evidence confidence nor acceptance state."""
    n = path.name.lower()
    if n in OVERRIDES:
        return OVERRIDES[n][0]
    if path.parts[1] == 'windows':
        return 'build'
    if path.parts[1] in {'lib', 'ghidra', 'runtime'} or n == '__init__.py':
        return 'support'
    if 'boundary' in str(path) or any(t in n for t in ('ghidra', 'diet', 'analysis_bundle')):
        return 'boundaries'
    if any(t in n for t in ('bootstrap', 'attest', 'verify_targets', 'import_targets', 'environment', 'tool-env')):
        return 'setup'
    if n in {'ci.py', 'preflight.py', 'status.py', 'progress.py', 'validate_tracking.py'}:
        return 'tracking'
    if any(t in n for t in ('compile_tc', 'probe_tc', 'cold_build', 'compare_', 'replay_th04_main_exact', 'inspect_omf', 'fixup', 'relocation', 'codegen')):
        return 'matching'
    if any(t in n for t in ('irq', 'vsync', 'egc', 'grcg', 'gaiji', 'graph_', 'cdg_cs', 'cs_operand', 'call_abi', 'far_', 'bullet_switch', 'planar', 'bullet_load', 'clear_dwords', 'scroll_and_slowdown', 'bgm', 'kaja', 'pmd', 'mmd', 'vector_math', 'polar')):
        return 'hardware'
    if any(t in n for t in ('prepare_', 'run_', 'inspect_th04', 'calibrate_', 'runtime', 'hdi', 'cpu_fault', 'fault_fixture', 'startup', 'smoke_')):
        return 'runtime'
    if any(t in n for t in ('native_source', 'native_main_', 'native_maine_link', 'native_op_link', 'manifest', 'source_compile', 'zun_parts')):
        return 'build'
    if any(t in n for t in ('score', 'regist', 'heap', 'pack', '_pi_', 'pf_', 'bfnt', 'super_', 'font', 'file_', 'dos_', 'bgimage')):
        return 'formats'
    return 'source-review'


def inventory(root: Path = ROOT) -> list[dict[str, str]]:
    entries = []
    for file in sorted((root / 'scripts').rglob('*')):
        rel = file.relative_to(root)
        if not file.is_file() or file.suffix not in EXTENSIONS or '__pycache__' in rel.parts:
            continue
        text = file.read_text(encoding='utf-8', errors='replace')
        summary = ''
        cli = file.suffix in {'.sh', '.ps1', '.cmd', '.bat'}
        if file.suffix == '.py':
            tree = ast.parse(text, filename=str(rel))
            summary = (ast.get_docstring(tree) or '').strip().split('\n')[0]
            cli = any(isinstance(node, ast.If) and '__name__' in ast.unparse(node.test) for node in tree.body)
        if file.name in OVERRIDES:
            summary = OVERRIDES[file.name][1]
        origin = 'maintained-description' if file.name in OVERRIDES else ('source-docstring' if summary else 'filename-routing')
        if not summary:
            summary = file.stem.replace('_', ' ').replace('-', ' ') + ' (filename-derived; inspect source before use).'
        role = 'command' if cli and file.name != 'tool-env.sh' else 'support'
        if file.suffix in {'.asm', '.gdb', '.java'}:
            role = 'fixture' if file.suffix != '.java' else 'tool-script'
        entries.append({'path': rel.as_posix(), 'category': category(rel), 'role': role,
                        'purpose': summary, 'purpose_source': origin})
    return entries


def artifacts(entries: list[dict[str, str]]) -> dict[str, str]:
    outputs = {'scripts/catalog/catalog.json': json.dumps(entries, indent=2, ensure_ascii=False) + '\n'}
    for name, title in CATEGORIES.items():
        lines = [f'# {title}', '', 'Generated by `python3 scripts/catalog/index.py --write`. See [usage](../README.md).', '',
                 'Categories route work; they do not claim current acceptance or successful replay.',
                 'Historical paths are retained. Read the source/subject note and use fresh outputs before executing.', '',
                 '| Path | Kind | Purpose |', '| --- | --- | --- |']
        for row in entries:
            if row['category'] == name:
                relative = Path(row['path']).relative_to('scripts').as_posix()
                purpose = row['purpose'].replace('|', '\\|').replace('\r', ' ').replace('\n', ' ')
                lines.append(f"| [{relative}](../{relative}) | {row['role']} | {purpose} |")
        outputs[f'scripts/catalog/{name}.md'] = '\n'.join(lines) + '\n'
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--write', action='store_true', help='Regenerate deterministic catalog and category indexes.')
    modes.add_argument('--check', action='store_true', help='Reject stale/missing catalog entries or indexes.')
    subs = parser.add_subparsers(dest='action')
    ls = subs.add_parser('list', help='List commands and support files by purpose.')
    ls.add_argument('--category', choices=CATEGORIES)
    ls.add_argument('--query', default='', help='Case-insensitive path/purpose filter.')
    ls.add_argument('--json', action='store_true')
    show = subs.add_parser('show', help='Show one path or unambiguous filename; never execute it.')
    show.add_argument('path')
    args = parser.parse_args()
    if (args.write or args.check) and args.action:
        parser.error('Choose catalog maintenance or browsing, not both.')
    entries = inventory()
    if args.write or args.check:
        stale = []
        for rel, text in artifacts(entries).items():
            path = ROOT / rel
            if args.write:
                path.write_text(text, encoding='utf-8')
            elif not path.is_file() or path.read_text(encoding='utf-8') != text:
                stale.append(rel)
        if stale:
            print('Stale catalog: ' + ', '.join(stale), file=sys.stderr)
            return 1
        print(f'Script catalog: {len(entries)} paths, {len(CATEGORIES)} categories; ' + ('written' if args.write else 'PASS'))
        return 0
    if args.action == 'show':
        candidates = [e for e in entries if e['path'] == args.path or Path(e['path']).name == args.path]
        if len(candidates) != 1:
            parser.error('Expected one catalog path; found ' + str(len(candidates)))
        print(json.dumps(candidates[0], indent=2))
    elif args.action == 'list':
        query = args.query.lower()
        selected = [e for e in entries if (not args.category or e['category'] == args.category)
                    and query in (e['path'] + ' ' + e['purpose']).lower()]
        if args.json:
            print(json.dumps(selected, indent=2))
        else:
            for e in selected:
                print(f"[{e['category']}/{e['role']}] {e['path']}\n  {e['purpose']}")
    else:
        parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
