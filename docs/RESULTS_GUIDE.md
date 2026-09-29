# Results guide

The bundle retains the latest complete matched result set for each benchmark. Runtime conclusions come from each pair's unprofiled timing phase, normalized by the amount of work recorded in that same run.

## Selected evidence

| Item | Path under `results/` |
|---|---|
| Raytrace upstream baseline | `raytrace_baseline_20260929-193534_678/` |
| Raytrace `sphere_shadow` | `raytrace_optimized_20260929-195030_678/` |
| Raytrace comparison | `session_raytrace_20260929-193534_678/comparison_raytrace/` |
| Nbody upstream baseline | `nbody_baseline_20260920-080806_16940/` |
| Nbody `flat_pow` | `nbody_optimized_20260920-081744_16940/` |
| Nbody comparison | `session_all_20260920-074308_674/comparison_nbody/` |

The original `session_all_20260920-074308_674/session.tsv` mentions the earlier `full` raytrace session. Its raw raytrace runs and comparison are deliberately omitted because the bundle keeps only the latest raytrace evidence. Preserve that header as an original record; it does not select the final raytrace kernel. Historical full statistics and selected profile extracts survive in `analysis/latest_results_analysis.json`.

Manifests and session TSVs retain original `/root/HW-SW-V2/...` paths. These record where the VM ran the experiment; use the relative directory names above in this checkout. New executions write new timestamped sessions and do not silently update the authored reports.

## Which files answer which question?

| Artifact | Interpretation |
|---|---|
| `timing/clean_*.csv` and summaries | Release-Python, no profiler. Primary runtime evidence: 11 independent processes per arm; four raytrace frames or 16 nbody units per process. |
| `logs/verify.log` | Saved correctness gates, including four 100×100 raytrace frames and 16×20,000 nbody steps. |
| `perf/stat_*.txt` | Release-Python counter estimates from separate counting runs. Report tables consistently use these text outputs. |
| `perf/stat_*.csv` | Another repeated counting invocation, not a machine-formatted copy of the same text measurements. Small differences are expected; do not mix the two. |
| `perf/*.data`, `*_script.txt`, `report_*.txt` | Native sampling data, expanded stacks and perf reports; debug Python for symbol attribution. |
| `flame/*.folded`, `*.svg`, `*_icicle.svg`, `*_top30_stacks.txt` | Same native stack evidence in several views. Width is sample share; vertical depth is call depth. `_python.svg` does not establish a separate Python profiler; py-spy was disabled. |
| Comparison `diff_flame*.svg` | `difffolded.pl -n` normalizes total weights. Red means larger relative share, not necessarily greater absolute runtime. |
| `raw/cprofile_*.pstats` and text | Python call counts and tracing attribution. Do not use these durations as benchmark speedup. |
| Baseline `raw/pyperf_*.json` and stats | Successful official pyperformance baseline cross-check. The optimized wrapper comparison remains a separate matched timing experiment. |
| `manifest.txt` and `phases.tsv` | Source hashes, tool settings, selected kernel, completion and unavailable-phase records. |

Files named `DO_NOT_QUOTE` contain durations collected while profiling and are retained only for traceability.

## Findings and limits

Raytrace's selected median falls from **795.618 to 530.881 ms/frame (33.274%)**; nbody falls from **227.196 to 143.374 ms per 20,000 steps (36.894%)**. Historical raytrace `full` was 452.696 ms/frame against its own 791.215 ms baseline. The reduced configuration is 17.271% slower in absolute medians, or 16.622% after normalization to the two baselines. The sessions were nine days apart; this is not a same-session ablation.

The new raytrace still removes work: recorded calls decrease 62.13%, instructions/frame 35.11% and cycles/frame 33.31%, while sphere-query count stays 179,457. Nbody removes repeated container access and interpretation work while retaining the original power arithmetic. Similar flame shapes are expected because CPython and recursive rendering remain; equal image widths do not imply equal total work. The reduced raytrace also repeats stock-scene validation that `full` cached, so the measured difference cannot be assigned solely to its omitted named optimizations.

Native cycle profiles use `python3-dbg`; clean timing and counter phases use release Python. Debug helper shares are not release-runtime fractions or precise Amdahl limits. Hardware events are multiplexed at roughly 40–60% running time. The saved topdown reports contain invalid negative fractions and are rejected; LLC-load counters are unsupported. Do not infer a precise DRAM-bound fraction from them.

The actual native sampling mode is **cycles, fixed period 5,000,000**, with DWARF unwinding. Original SVGs are preserved unchanged, including an inherited `F=999`/frequency subtitle and occasional title encoding artifacts. That subtitle is misleading for these captures; the manifest and record log define the actual method. Presentation figures use corrected labels.

## Provenance and reproducibility

The saved raytrace manifest hashes matched the source repository at review. Nbody's measured variant, wrapper and upstream sources matched too; its shared pipeline later changed when raytrace's default changed. Packaging also makes workflow-only adjustments. Consequently, raw manifests remain records of the measured versions, not claims that every final script is byte-identical to every older run.

Historical manifests say upstream extraction provenance was `UNVERIFIED`. The final bundle closes that source-origin gap separately: `upstream/PROVENANCE.txt` records byte-for-byte agreement with the pyperformance 1.14.0 wheel and the wheel/source SHA-256 values. Official baseline logs also identify suite 1.14.0 and pyperf 2.10.0. `tools/verify_upstream.sh` checks the supplied hashes and confirms that baseline functions load from the verified files.

The included official FlameGraph subset is pinned to revision `41fee1f99f9276008b7cd112fca19dc3ea84ac32`, with hashes and license. Historical result manifests did not save the toolkit revision, so the pin establishes future reproducibility without retroactively asserting an identical historical version.

```bash
python3 -B analysis/recompute_results.py
python3 -B -m unittest discover -s tests -v
```

The first command recomputes principal timing, counters and eval sample totals from retained files without changing them. The second runs the **69-test** submission suite. Its saved output and fresh exactness logs are in `docs/validation/runtime_tests.log`, `runtime_raytrace_exact.log` and `runtime_nbody_exact.log`, with summary `runtime_validation.md`. `analysis/latest_results_selection_inventory.json` enumerates original selected files with sizes and hashes; no selected original file exceeds 100 MiB.

Hardware material is a separate design and validation track. Its estimates use explicit offload fractions and transaction assumptions, not these debug shares. Host C is a native-software control, not deployed accelerator performance. See `hardware/README.md` and `hardware/validation/` for what was actually checked.
