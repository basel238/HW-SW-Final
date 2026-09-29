#!/usr/bin/env bash
# Verify the supplied, pinned pyperformance workload without modifying it.
set -Eeuo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/../lib/common.sh"
"$PY_REL" -B - "$REPO_ROOT" <<'PY'
import hashlib, pathlib, sys
root = pathlib.Path(sys.argv[1]).resolve()
expected = {
    'nbody': 'd1385e816d7cfea361b7915e2cf70138cd6b84f40df8bd5152638851f7bcac2b',
    'raytrace': '88ef4d9060d8e8f6ce40f376477aaf89cc808fa44813225a3071a05a1467f017',
}
for benchmark, digest in expected.items():
    path = root / 'upstream' / ('bm_' + benchmark + '_upstream.py')
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit('FAIL: ' + benchmark + ' differs from pinned pyperformance 1.14.0')
    print(benchmark + ': SHA-256 matches pyperformance 1.14.0 wheel source')
sys.path.insert(0, str(root / 'bench'))
import bm_raytrace_upstream as raytrace
import bm_nbody_upstream as nbody
r, n = raytrace.load_upstream(), nbody.load_upstream()
functions = [r.Vector.__add__, r.Vector.dot, r.Sphere.intersectionTime,
             r.Scene.rayColour, r.Scene.render, r.SimpleSurface.colourAt,
             r.bench_raytrace, n.advance, n.report_energy, n.offset_momentum,
             n.bench_nbody]
for fn in functions:
    if pathlib.Path(fn.__code__.co_filename).resolve().parent != root / 'upstream':
        raise SystemExit('FAIL: baseline function was not loaded from upstream: ' + fn.__name__)
print('All 11 baseline functions execute directly from the verified upstream source.')
print('Workload verified; upstream source was not modified.')
PY
