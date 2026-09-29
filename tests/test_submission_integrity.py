"""Portable submission provenance and truthful flame-graph sampling labels."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SubmissionIntegrityTests(unittest.TestCase):
    def test_upstream_verification_rejects_modified_kernel_without_repairing_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ('lib', 'config', 'tools', 'bench', 'upstream'):
                shutil.copytree(ROOT / directory, root / directory)
            source = root / 'upstream/bm_nbody_upstream.py'
            source.write_bytes(source.read_bytes() + b'\n# changed by the test\n')
            before = source.read_bytes()
            p = subprocess.run(['bash', str(root / 'tools/verify_upstream.sh')],
                               env=dict(os.environ, PY_REL=sys.executable),
                               capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('differs from pinned pyperformance', p.stderr)
            self.assertEqual(before, source.read_bytes())

    def test_bundled_flamegraph_matches_official_download_hashes(self):
        root = ROOT / 'vendor/FlameGraph'
        for line in (root / 'SHA256SUMS').read_text().splitlines():
            expected, name = line.split('  ', 1)
            self.assertEqual(expected, hashlib.sha256((root / name).read_bytes()).hexdigest(), name)
        self.assertTrue((root / 'docs/cddl1.txt').is_file())

    @unittest.skipUnless(shutil.which('perl'), 'Perl is required for actual SVG generation')
    def test_flamegraph_labels_actual_sampling_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / 'perf').mkdir(); (run / 'flame').mkdir()
            (run / 'perf/baseline_script.txt').write_text(
                'python3 123 [000] 1.000000: cycles:\n'
                '        1234 _PyEval_EvalFrameDefault (python3)\n'
                '        5678 main (python3)\n\n')
            command = '''source "$TEST_ROOT/lib/common.sh"
RUN_DIR="$TEST_RUN"; BENCH=raytrace; VARIANT=baseline
make_flamegraph baseline unused
'''
            for mode, label in [('period', 'period=5000000'), ('freq', 'frequency=999 Hz')]:
                p = subprocess.run(['bash', '-c', command], env=dict(os.environ,
                    TEST_ROOT=str(ROOT), TEST_RUN=str(run), PY_REL=sys.executable,
                    PY_DBG=sys.executable, ENABLE_FLAMEGRAPH='1', PERF_RECORD_MODE=mode,
                    PERF_RECORD_EVENT='cycles', SAMPLE_PERIOD='5000000', SAMPLE_FREQ='999',
                    FLAMEGRAPH_DIR=str(ROOT / 'vendor/FlameGraph')),
                    capture_output=True, text=True)
                self.assertEqual(0, p.returncode, p.stdout + p.stderr)
                text = (run / 'flame/baseline.svg').read_text()
                self.assertIn(label, text)
                if mode == 'period': self.assertNotIn('F=999', text)


if __name__ == '__main__': unittest.main()
