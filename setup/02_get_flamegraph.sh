#!/usr/bin/env bash
# Verify the vendored official FlameGraph tools; no download or Git is needed.
set -Eeuo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$REPO_ROOT/config/bench.env"
"$PY_REL" -B - "$FLAMEGRAPH_DIR" <<'PY'
import hashlib, pathlib, sys
root = pathlib.Path(sys.argv[1])
manifest = root / 'SHA256SUMS'
if not manifest.exists():
    raise SystemExit('SHA256SUMS missing; use bundled vendor/FlameGraph or supply a verified toolkit.')
for line in manifest.read_text().splitlines():
    digest, filename = line.split('  ', 1)
    path = root / filename
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit('FlameGraph integrity check failed: ' + filename)
for name in ('stackcollapse-perf.pl', 'flamegraph.pl', 'difffolded.pl'):
    p = root / name
    p.chmod(p.stat().st_mode | 0o111)
print('Official FlameGraph scripts and license verified. Revision: 41fee1f99f9276008b7cd112fca19dc3ea84ac32')
PY
command -v perl >/dev/null || { echo 'Perl is required; install the Ubuntu perl package.' >&2; exit 1; }
for name in stackcollapse-perf.pl flamegraph.pl difffolded.pl; do
  perl -c "$FLAMEGRAPH_DIR/$name"
done
