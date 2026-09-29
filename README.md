# HW/SW Co-Design — final submission

The submission measures the original pyperformance **raytrace** and **nbody** benchmarks, preserves their source, and supplies exact optimized variants, reports, execution scripts and the latest recorded evidence.

| Selected optimization | Baseline median | Optimized median | Runtime reduction |
|---|---:|---:|---:|
| Raytrace: `sphere_shadow` | 795.618 ms/frame | 530.881 ms/frame | **33.274%** |
| Nbody: `flat_pow` | 227.196 ms/20,000 steps | 143.374 ms/20,000 steps | **36.894%** |

Both exceed the project's 7% target. Raytrace now selects **scalar sphere intersections and shadow-ray reuse only**. Historical `full` was faster, at 452.696 ms/frame, but is not the selected submission configuration. The reports explain this scope decision and the independent-session comparison.

## Read first

- Required reports: [`report_raytrace.txt`](report_raytrace.txt), [`report_nbody.txt`](report_nbody.txt). PDF reading copies: [`docs/reports/report_raytrace.pdf`](docs/reports/report_raytrace.pdf), [`docs/reports/report_nbody.pdf`](docs/reports/report_nbody.pdf).
- Required scripts: [`script_raytrace.sh`](script_raytrace.sh), [`script_nbody.sh`](script_nbody.sh). [`run_all.sh`](run_all.sh) runs baseline and selected optimized variants of both benchmarks.
- Publication commands for the requested empty repository: [`PUBLISH.md`](PUBLISH.md).
- AI interaction record: [`prompt.txt`](prompt.txt).
- Submission mapping and remaining presentation: [`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md).
- Evidence locations and interpretation: [`docs/RESULTS_GUIDE.md`](docs/RESULTS_GUIDE.md).
- Hardware proposal: [`hardware/docs/HARDWARE_DESIGN.md`](hardware/docs/HARDWARE_DESIGN.md), [`architecture.svg`](hardware/diagrams/architecture.svg), and interactive HTML explanations under [`hardware/diagrams/`](hardware/diagrams/).

## Run on the course Ubuntu VM

Use the existing course machine configuration. The full workflow needs working Linux `perf`, release `python3`, `python3-dbg`, Perl and the usual shell tools. The scripts do not automatically change system settings. Do not run `setup/03_tune_vm.sh` or change shared-machine permissions/governors; use the course-approved perf access if preflight reports a permission failure.

From the repository root, create the local harness environment only if it is missing, then run:

```bash
./setup/04_make_venv.sh
./tools/verify_upstream.sh
./run_all.sh
```

`run_all.sh` performs preflight and selects `sphere_shadow` for raytrace and `flat_pow` for nbody. It creates a new timestamped session and preserves the authored reports. Review any phase marked unavailable in `phases.tsv`; a completed script does not make an unavailable hardware event valid.

To reproduce the submitted batch sizes separately:

```bash
./script_raytrace.sh --variant both --kernel sphere_shadow --loops 4
./script_nbody.sh --variant both --kernel flat_pow --loops 16
```

For clean runtime only, add `--time-only`. The complete workflow separately performs correctness verification, unprofiled timing, `perf stat`, `perf record`/flame graphs, cProfile, and an official pyperformance baseline cross-check. Optimized timing is a matched wrapper measurement; it is not represented as an official optimized pyperformance entry.

## Validate or inspect without rerunning the VM experiment

```bash
python3 -B -m unittest discover -s tests -v
python3 -B analysis/recompute_results.py
```

The submission validation passes **69 tests**; the summary and full logs are in [`docs/validation/`](docs/validation/). Saved exactness checks compare raytrace pixels and nbody energy plus all 30 position/velocity components. `flat_sqrt` and the optional native/hardware RMAG path use a different numerical contract and are not selected by the exact benchmark workflow.

`results/` contains only the latest matched raw run per benchmark, including clean timing, native profiles, folded stacks, SVGs and comparison artifacts. Historical `full` figures are retained as extracted comparison evidence in `analysis/`, not as another raw result set.

## Sources and hardware status

The two `upstream/` files are byte-identical to the **pyperformance 1.14.0 wheel**, documented in [`upstream/PROVENANCE.txt`](upstream/PROVENANCE.txt). Harness requirements pin pyperformance 1.14.0 and pyperf 2.10.0. The included FlameGraph subset is pinned to revision `41fee1f99f9276008b7cd112fca19dc3ea84ac32`; see its [`provenance`](vendor/FlameGraph/PROVENANCE.txt) and [`third-party notices`](THIRD_PARTY_NOTICES.md).

The hardware directory contains the adapted GEOM proposal, actual HardFloat datapath/control, host references, software-interface material, conditional estimates and the supplied animations. Raytrace is its primary acceleration target. Hardware speedup, area, power and achieved frequency have **not** been measured; host numerical checks and HDL elaboration are distinguished from RTL simulation and deployment. See [`hardware/README.md`](hardware/README.md) for separate hardware checks.
