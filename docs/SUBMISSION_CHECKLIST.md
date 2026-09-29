# Submission checklist

This maps the project's “What You Need to Submit” and hardware requirements to the final repository. Paths are relative to its root. The required text files remain the submission artifacts; PDFs are additional reading copies.

| Requirement | Submitted location / status |
|---|---|
| Raytrace benchmark report, mandated filename | `report_raytrace.txt`; PDF at `docs/reports/report_raytrace.pdf` |
| Nbody benchmark report, mandated filename | `report_nbody.txt`; PDF at `docs/reports/report_nbody.pdf` |
| Overview of benchmark, libraries and data structures | Each report's overview; original kernels in `upstream/`, wrappers in `bench/` |
| Initial performance analysis, flame graphs and profiler data | Each report's analysis; selected `results/*/perf/`, `flame/`, `raw/`; `analysis/latest_results_analysis.json` |
| Explained software optimizations and correctness | Each report; `variants/`, `tests/`, saved `logs/verify.log` |
| Performance comparison against original workload | Latest session comparison directories, clean timing CSVs, and report tables; raytrace 33.274%, nbody 36.894% runtime reduction |
| Required execution scripts | `script_raytrace.sh`, `script_nbody.sh`; shared `lib/`, `config/`, `setup/`, `tools/` included |
| Dependency setup, execution, profiling and comparison | Local environment setup in `setup/04_make_venv.sh`; full phase workflow in benchmark scripts; `run_all.sh` defaults to both baselines and `sphere_shadow` / `flat_pow` |
| Supporting code, logs and configuration | Latest raw evidence in `results/`; `analysis/`, `experiments/`, tests, verified upstream sources and pinned FlameGraph tools |
| AI prompts or instructions | `prompt.txt`; prior interaction material retained under `docs/provenance/` |
| Hardware proposal and supporting design files | `hardware/`, hardware sections in both reports |
| Presentation and live discussion | **Separate requirement remains: prepare a 20–25 minute presentation and be ready for 5–10 minutes of Q&A. A presentation deck is not delivered in this bundle.** |

## Hardware requirement mapping

| Requirement from project point 7 | Location / qualification |
|---|---|
| Verilog/SystemVerilog main datapath and control | `hardware/rtl/`, `hardware/vendor/HardFloat-1/`, compilation list `hardware/files.f` |
| Inputs, outputs, bit widths, interfaces and frequency | `hardware/docs/HARDWARE_DESIGN.md`; 64-bit operands, command/response handshake and 50 MHz target stated explicitly |
| Internal architecture and operation | Same design document, RTL and `hardware/diagrams/architecture.svg` |
| Hardware/software interface and integration | Same design document plus `hardware/software/`; proposed processor bridge is not claimed as deployed |
| Acceleration justification and estimated performance | Report hardware sections, `hardware/analysis/estimate.py` and `estimate.json`; assumptions and break-even limits are explicit |
| Block diagram and system integration | `hardware/diagrams/architecture.svg`; additional conceptual HTML animations in the same directory |
| Performance, area, power and frequency trade-offs | Hardware design and report sections; no synthesis-derived area/power or timing-closure claim |
| Validation scope | Saved host reference, native control and semantic elaboration checks in `hardware/validation/`; **no RTL simulation or physical hardware measurement claimed** |

The proposal prioritizes raytrace. Shared dot-product support is discussed for exact nbody, but no nbody hardware speedup is asserted. Approximate RMAG remains separate from the exact software result. The brief does not require synthesis, fabrication or physical testing; that does not turn analytical estimates into measurements.

## Final interpretation checks

- Software correctness: selected raytrace batch is pixel-bit-identical; selected nbody batch preserves energy and all 30 state components. The submission test suite passes **69 tests**. See `docs/validation/runtime_validation.md`, `runtime_tests.log`, `runtime_raytrace_exact.log` and `runtime_nbody_exact.log`.
- Source identity: `upstream/PROVENANCE.txt`, `SHA256SUMS` and `tools/verify_upstream.sh` identify and verify unmodified pyperformance 1.14.0 kernels.
- Tool identity: `requirements.txt` pins the official harness versions; `vendor/FlameGraph/PROVENANCE.txt` pins the included plotting tools. Historical runs did not record the FlameGraph revision; no retroactive version claim is made.
- Runtime evidence: use unprofiled release-Python results. Debug flame shares, cProfile durations, PMU estimates and conditional hardware estimates carry their own limits.
- Scope choice: raytrace `sphere_shadow` is intentionally selected although the earlier `full` configuration was faster. Historical `full` is a comparison, not a failed optimization.
- Evidence retention: only the latest raw matched runs are included. A historical session header can mention omitted raytrace data; `docs/RESULTS_GUIDE.md` explains this preserved provenance.
- Remaining delivery action: push this reviewed folder to the requested repository and prepare the separate presentation. No Git history is fabricated to imply work that did not occur in that repository.
