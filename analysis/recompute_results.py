#!/usr/bin/env python3
"""Recompute headline timing/counters/flame attribution from retained results.

Run from any directory: python3 analysis/recompute_results.py
Only standard-library modules are used. Results are printed as JSON; no source
or measurement artifact is changed. Historical full data are not recomputed
because only their extracted evidence, not superseded run directories, is kept.
"""
from pathlib import Path
import csv
import json
import re
import statistics
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
RUNS = {
    'raytrace': ('raytrace_baseline_20260929-193534_678',
                 'raytrace_optimized_20260929-195030_678', 4),
    'nbody': ('nbody_baseline_20260920-080806_16940',
              'nbody_optimized_20260920-081744_16940', 16),
}

def read_run(directory, variant, loops):
    folder = ROOT / 'results' / directory
    with (folder / 'timing' / f'clean_{variant}.csv').open() as handle:
        samples = [float(r['total_sec']) / loops for r in csv.DictReader(handle)]
    counters = {}
    text = (folder / 'perf' / f'stat_{variant}.txt').read_text()
    for line in text.splitlines():
        match = re.match(r'^\s*([\d,.]+)\s+(?:msec\s+)?([A-Za-z][A-Za-z0-9-]+)\s*(?:#|$)', line)
        if match:
            counters[match[2]] = float(match[1].replace(',', '')) / loops
    leaf = Counter()
    for line in (folder / 'flame' / f'{variant}.folded').read_text().splitlines():
        stack, count = line.rsplit(' ', 1)
        symbol = re.sub(r'\.lto_priv\.\d+', '', stack.split(';')[-1])
        leaf[symbol] += int(count)
    return {
        'run_directory': directory, 'loops': loops, 'n': len(samples),
        'median_ms': statistics.median(samples) * 1000,
        'stdev_ms': statistics.stdev(samples) * 1000,
        'counter_source': f'results/{directory}/perf/stat_{variant}.txt',
        'counters_per_unit': counters,
        'ipc': counters['instructions'] / counters['cycles'],
        'debug_samples': sum(leaf.values()),
        'debug_eval_self_samples': leaf['_PyEval_EvalFrameDefault'],
    }

out = {}
for benchmark, (baseline, optimized, loops) in RUNS.items():
    b = read_run(baseline, 'baseline', loops)
    o = read_run(optimized, 'optimized', loops)
    out[benchmark] = {
        'baseline': b, 'optimized': o,
        'runtime_reduction_percent': 100 * (1 - o['median_ms'] / b['median_ms']),
        'speedup': b['median_ms'] / o['median_ms'],
        'instructions_reduction_percent': 100 * (1 - o['counters_per_unit']['instructions'] / b['counters_per_unit']['instructions']),
        'cycles_reduction_percent': 100 * (1 - o['counters_per_unit']['cycles'] / b['counters_per_unit']['cycles']),
    }
print(json.dumps(out, indent=2))
