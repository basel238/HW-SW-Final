# Latest measured results and evidence

The submission selects raytrace `sphere_shadow` (scalar sphere intersection and shadow-ray reuse) and nbody `flat_pow`. Both pass the 7% runtime-reduction target with their saved exactness gates. The reduced raytrace configuration is **slower than historical `full`**; it is selected for the requested implementation scope, not because it measured faster.

## Runtime comparison

| Benchmark / configuration | Baseline median | Optimized median | Runtime reduction | Speedup |
|---|---:|---:|---:|---:|
| Raytrace, latest `sphere_shadow` | 795.618 ms/frame | 530.881 ms/frame | 33.274% | 1.499× |
| Nbody, latest `flat_pow` | 227.196 ms/20,000 steps | 143.374 ms/20,000 steps | 36.894% | 1.585× |
| Raytrace, historical `full` | 791.215 ms/frame | 452.696 ms/frame | 42.785% | 1.748× |

These are release-Python clean timing medians from 11 independent processes per arm. Each raytrace process measures four 100×100 frames; each nbody process measures 16 consecutive 20,000-step units. Divide the process duration by its recorded loop count. Report time reduction as `100 × (1 − Topt/Tbase)`; throughput gain is a different quantity.

The latest raytrace standard deviations are 6.389 ms baseline and 2.645 ms optimized. Nbody standard deviations are 1.990 ms and 1.441 ms. Independent-arm bootstrap intervals for the median-based runtime reduction are 32.81–33.91% (raytrace) and 35.92–37.45% (nbody), based on 20,000 resamples. These intervals describe sampled within-session variation only. The runs are sequential, not interleaved; the intervals do not measure drift or prove absence of bias.

Raytrace `sphere_shadow` is 17.271% slower than historical `full` in absolute optimized medians. Their baselines differ by only +0.557%; comparing each optimized/baseline ratio gives a 16.622% increase in relative runtime, or 9.510 percentage points less runtime reduction. This is evidence for the direction and scale of the trade-off, not a direct same-session ablation. The historical run was on September 20; the selected run was on September 29. No older raw raytrace directories are included in the final bundle; their extracted statistics and relevant profile evidence are retained in `latest_results_analysis.json`.

## Raytrace: what the new measurements explain

The computation still performs 179,457 sphere queries per frame and makes the same rendering decisions. Fewer Python objects, calls and repeated ray normalizations implement that work.

| cProfile count per frame | Upstream | `sphere_shadow` | Historical `full` |
|---|---:|---:|---:|
| All recorded function calls, including startup | 3,092,298 | 1,171,138 | 881,684 |
| Sphere intersection | 179,457 | 179,457 | 179,457 |
| Vector dot | 509,873 | 78,787 | 78,785 |
| Point subtraction | 277,865 | 26,236 | 26,236 |
| Vector constructor | 452,955 | 129,154 | 105,497 |
| Ray constructor | 98,172 | 26,000 | 26,000 |
| Vector normalization | 109,887 | 37,715 | 37,715 |
| Sphere square roots | 6,934 | 6,934 | 6,934 |
| All square roots, including normalization and one import call | 116,822 | 44,650 | 44,650 |

The scalar sphere path removes the temporary displacement Vector and dot-method machinery while preserving the expression order. Shadow-ray reuse avoids reconstructing and normalizing the same ray separately for each object tested. The dot/constructor/normalization count changes are direct evidence for these mechanisms. cProfile timing itself is affected by tracing; it is not used for the runtime-reduction result.

Why `full` was faster requires more than listing its additional guard, camera, nearest-hit and checkerboard changes. Its render wrapper also cached the stock-scene classification. The selected two-change configuration leaves that wrapper upstream and performs scene validation on each shadow visibility call:

| Validation helper count per frame | `sphere_shadow` | Historical `full` |
|---|---:|---:|
| `stock_scene` | 10,666 | 26,000 |
| `all` | 10,666 | 1 |
| Validation generator resumptions | 95,994 | 9 |
| `id` | 10,666 | 26,002 |

`full` calls the helper more often but nearly always takes its cached path. The new configuration repeatedly scans the eight scene objects. Its `stock_scene` cProfile inclusive time is 0.081379 seconds versus 0.017424 seconds in the older full profile; these are attribution observations, not clean-time costs. This difference is part of the measured configuration trade-off. The current data cannot isolate each omitted change's individual contribution.

## Release perf counters

The following consistently uses `perf/stat_*.txt`, matching each saved comparison's `counters.txt`. The CSV counter files come from a separate repeated invocation and therefore have slightly different estimates. Do not combine a numerator from one with a denominator from the other.

| Event per unit of work | Ray baseline | Ray optimized | Change | Nbody baseline | Nbody optimized | Change |
|---|---:|---:|---:|---:|---:|---:|
| Instructions | 5.055 billion | 3.281 billion | −35.105% | 1.692 billion | 1.101 billion | −34.912% |
| Cycles | 1.924 billion | 1.283 billion | −33.306% | 549.829 million | 347.974 million | −36.712% |
| Branches | 648.765 million | 419.115 million | −35.398% | 193.593 million | 125.500 million | −35.173% |
| L1 data loads | 1.643 billion | 1.049 billion | −36.138% | 535.846 million | 351.722 million | −34.361% |
| L1 data misses | 44.382 million | 33.018 million | −25.604% | 0.212 million | 0.233 million | +10.033% |
| IPC | 2.627 | 2.556 | −2.70% | 3.077 | 3.164 | +2.84% |

The strong common signal is fewer instructions and fewer cycles for the same useful workload. Raytrace improves despite a slightly lower IPC, so improved IPC is not its explanation. Nbody combines substantially less work with a small IPC increase. The mechanisms are consistent with removing interpreter-mediated operations, repeated indexing and object work; the counters do not establish that every saved cycle belonged to a particular helper.

Counter events are multiplexed: cycles run roughly 50% of the collection period, instructions/branches roughly 60%, and L1/TLB events roughly 40%. Ratios are estimates. In raytrace, the L1 miss rate rises from about 2.70% to 3.15% while misses per frame fall: the access denominator falls faster. Nbody's miss count rises slightly while runtime falls substantially; that is incompatible with a claim that improved cache misses caused the speedup. LLC-load events are unsupported. Topdown outputs include negative fractions and are rejected. Do not quote a precise memory-bound percentage, zero DRAM stalls, or a measured arithmetic-accelerator ceiling from these outputs.

## Flame graphs and native attribution

| Native cycle profile observation | Ray baseline | Ray optimized | Nbody baseline | Nbody optimized |
|---|---:|---:|---:|---:|
| Samples | 1,068 | 648 | 1,175 | 725 |
| `_PyEval_EvalFrameDefault` self samples | 318 | 179 | 526 | 285 |
| Its fraction of the profile | 29.78% | 27.62% | 44.77% | 39.31% |

Raytrace profiles each cover one frame; nbody profiles each cover five units. They use `python3-dbg` and cycle-period sampling, with period 5,000,000 cycles. They include startup/import work. Reported lost samples are zero, but this alone does not prove perfect unwinding or source-level attribution.

The new flame graphs remain tall and structurally similar because the program still uses the same recursive ray-tracing control flow and CPython C call machinery. Removing many calls reduces how much work is executed; it need not eliminate the deepest surviving call stack. A flame graph's vertical axis is stack depth, not elapsed time. Each graph scales its total sample weight to its width, so two equally wide pictures can correspond to substantially different total work.

For example, raytrace's weighted mean captured native depth is 68.07 frames baseline and 66.81 optimized, and both have up to 15 simultaneously captured `_PyEval_EvalFrameDefault` frames. The eval self count nevertheless falls from 318 to 179. Those debug-build observations support the structural explanation; they are not fractions of the release clean runtime. Repeated interpreter frames do not imply a fixed instruction cost for every Python call.

The retained differential graphs were generated with `difffolded.pl -n`: totals are normalized before subtraction. Red indicates a larger *relative sample share*, blue a smaller share. Red does not by itself mean an operation became slower in absolute time. The standard and inverted graphs answer different stack-navigation questions, while the associated folded files and perf reports preserve the counts.

Raw historical SVGs are preserved byte-for-byte. Some carry an inherited frequency subtitle (`999`) despite the actual recorded period mode and have a text-encoding artifact in the title. The manifest, `phases.tsv`, record logs and this explanation define the measurement method. Presentation figures should use the correct period label rather than reproduce that misleading subtitle.

Nbody provides particularly direct native evidence of reduced container access: the number of samples whose stack includes `PyObject_GetItem` is 83→0 and `PyObject_SetItem` 123→2. These are inclusive counts and should not be added indiscriminately across arbitrary symbols. Conversely, stacks containing `PyFloat_FromDouble` remain 71→73, float deallocation 41→42, and libm pow self samples 20→19. Thus the flattening removes repeated indexing and loop/dispatch work but leaves boxed arithmetic and the exact power operation. Its 44.77% baseline eval share must not be presented as the optimized share, which is 39.31%.

Nbody's total cProfile calls rise because the optimized wrapper imports more helper code. The arithmetic loop itself remains a single `advance_flat_pow` call. Do not interpret whole-process cProfile call totals as nbody hot-loop work or use them to contradict the runtime result.

## Remaining bottlenecks and hardware implications

The new raytrace results support the same broad explanation as `full`: Python dispatch, calls, type/object handling and temporary allocation remain substantial alongside arithmetic. They do not justify assigning every bytecode or call a fixed instruction count, treating a debug symbol's share as a release Amdahl fraction, or asserting that native C speedup proves custom-hardware speedup.

The geometric workload is unchanged from `full`: 179,457 sphere queries, 6,934 nonnegative discriminants requiring square root (3.864%), 15,265 nearest-intersection operations and 10,666 shadow visibility checks. Therefore a geometry hardware proposal can retain those workload counts and semantic obligations. Its baseline runtime must change to 530.881 ms/frame if it is modeled as an addition to the selected optimized software. The offloaded release-time fraction, transfer cost, handling of early exits and host overhead still require explicit assumptions or a controlled native reference; debug self percentages are not a substitute. Dividing sphere queries by seven is not a measured hardware crossing count because shadow traversal can stop early.

## Correctness, tools and provenance

- Raytrace's selected saved verification covers all candidate kernels at 24×24, 100×100 and 37×23, with restoration checks. It explicitly adds four consecutive 100×100 `sphere_shadow` frames, all bit-identical. The 100×100 canvas SHA prefix is `11f2c36b02044f11`.
- Nbody's selected gate covers 16 consecutive 20,000-step units. `flat_pow` energy and all 30 position/velocity components are bit-identical; final reference energy is `-0.1690801979358367`. Square-root variants pass a tolerance test but are not the selected exact kernel.
- The clean timing and counting phases use release Python 3.10.12; symbol-rich sampling uses its debug build. Saved `perf` version is 5.15.209. Standard FlameGraph folded and SVG artifacts are present, together with perf data, scripts, self/children/caller reports and cProfile files. py-spy is explicitly disabled in these sessions; a filename ending `_python.svg` is not proof of a py-spy profile.
- The baseline official pyperformance phase succeeds for both benchmarks, using suite 1.14.0 and pyperf 2.10.0. Latest raytrace official baseline mean is 801±7 ms, consistent with the separate clean baseline. The optimized wrapper lies outside that official harness; its speedup is the matched clean custom measurement, not an official pyperformance comparison.
- All latest raytrace source hashes match the reviewed repository. Nbody's variant, wrapper, upstream source, configuration and common library hashes match; the shared pipeline changed later for the raytrace default. That does not rerun nbody, and the saved nbody manifest remains the measured provenance.
- The manifests record upstream SHA-256 values but mark extraction-version provenance `UNVERIFIED`. Their official baseline logs identify the pyperformance version actually run. Byte identity against the supplied upstream source must be verified separately if claiming a particular source distribution.

## Retained evidence

`latest_results_selection_inventory.json` enumerates 175 original files (94,012,138 bytes), with SHA-256 hashes. The largest is 9,932,672 bytes; no selected artifact exceeds GitHub's 100 MiB ordinary-file limit. Only the latest matched raw runs are selected; older full numbers survive as extracted comparison evidence. Session records retain their original VM paths for provenance, so those strings are not expected to resolve on another machine.

Run `python3 analysis/recompute_results.py` from the final bundle to recompute medians, counters and eval sample totals from its retained evidence. This script needs only Python's standard library and does not edit any measurement file.
