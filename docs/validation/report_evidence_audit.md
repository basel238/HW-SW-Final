# Final report evidence audit — 29 September 2026

Reviewed the newly generated `report_raytrace.txt` and `report_nbody.txt` against the retained analysis, actual upstream and optimized sources, recorded profiles, and submitted hardware estimate/validation files. This was a factual read-only audit; no report or source edits were made.

## Verdict

No substantive unsupported software-performance claim found. The reports correctly distinguish measured software improvement, historical alternatives, native-software controls and conditional hardware estimates. Two small wording/path corrections were sent to the parent for integration:

1. Raytrace line 223 says “Debug cProfile times do not supply it.” cProfile uses release Python. Suggested replacement: “Debug-profile shares and cProfile timings do not supply it.”
2. The final deliverables tables abbreviate source JSON filenames. Their complete repository-relative paths are `docs/reports/raytrace_source.json` and `docs/reports/nbody_source.json`.

## Confirmed facts

- Latest raytrace: 795.61825 → 530.8805 ms/frame, 33.274469% reduction; latest nbody: 227.19575 → 143.3736875 ms/unit, 36.894204% reduction.
- Historical `full` comparison is accurately labeled an independent-session comparison and a faster unselected alternative. Raw regression 17.270797%; baseline-normalized regression 16.621703%.
- Raytrace count identities hold: 72,172 fewer Ray constructions/normalizations; 323,801 fewer Vector constructions = 144,344 from shadow reuse + 179,457 from scalar sphere displacement; 431,086 fewer dots = 72,172 + 2×179,457; 251,629 fewer Point subtractions = 72,172 +179,457.
- Historical full saves another 23,657 Vector constructions: 19,800 camera-scale temporaries plus 3,857 checkerboard temporaries. The report also acknowledges the separate stock-scene validation/caching difference.
- Three additional reflection bounces is consistent with upstream `recursionDepth > 3` termination.
- Nbody's upstream timer includes energy evaluation before and after each advance; momentum offset precedes the timer. Sixteen units accumulate state, rather than resetting it.
- Nbody per-step source component counts are consistent: upstream150 reads/75 writes, grouped114/57; flat30 reads and30 writes per advance call. The unchanged numeric-result expression count is270 per timestep.
- Exact multiplication grouping, pair update order, position-update order and original power expression are preserved in flat_pow. The report acknowledges delayed-writeback exception semantics.
- Recomputed inclusive union of stacks containing `PyObject_GetItem` or `PyObject_SetItem`:206 baseline,2 optimized. Eval and float/pow sample counts agree with analysis.
- Reports separate self from inclusive attribution, debug profiles from release timing, sampled mechanisms from release Amdahl fractions, and actual fixed-cycle sampling from the legacy F999 caption.
- Hardware estimate agrees with `hardware/analysis/estimate.json`: SPHERE37/98 cycles,141.25766ms device,159.20336ms total assumed offload; VDOT18 cycles,72ms device,92ms total,64.16798% break-even removed fraction. Assumptions and lack of hardware measurements are stated.
- Host validation artifact records20,000 dot cases,20,000 sphere expressions,10 status cases and `rtl_simulated:false`, matching report coverage.
- Historical grouped3.40% and preceding flat_pow37.53% were independently found in original comparison summaries; they are presented as historical figures, not new selected runs.
- Full run commands and interleaved A/B command argument positions are valid. All six `results/latest_*` links resolve.

## Raw evidence integrity

Every entry in `analysis/latest_results_selection_inventory.json` was checked against the copied final bundle:

- **175 selected original files**
- **94,012,138 bytes**
- **175/175 size and SHA-256 matches**
- **No missing or changed files**

This verifies preservation of selected evidence; it does not assert that all remaining repository files are historical measurement artifacts.

Final resolution: both wording/path corrections were applied to the report sources and both TXT/PDF pairs were rebuilt. The affected pages were rendered again for layout review.
