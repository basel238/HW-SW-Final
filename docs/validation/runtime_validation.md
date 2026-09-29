# Standalone runtime validation

- 69 correctness and integration tests passed (63.126 s), including varied ray scenes, exact floating-point checks, safe patch restoration, nbody fallback/state handling, kernel selection through all phases, paired timing, and no Git/perf execution during clean timing.
- Additional final-workload gates passed: raytrace `sphere_shadow`, four 100×100 frames bit-identical; nbody `flat_pow`, 16×20,000 steps, energy and all 30 state components bit-identical. These were local correctness checks, not replacement timing results.
- All selected Python runtime sources parsed and all 15 shell scripts passed `bash -n`.
- Both upstream kernels are byte-identical to the official cached pyperformance 1.14.0 wheel. The read-only verifier checks pinned SHA-256 and function source origin. All upstream, wrapper, and optimized Python sources remain byte-identical to the original repo.
- Official FlameGraph revision 41fee1f99f9276008b7cd112fca19dc3ea84ac32 is included under `vendor/FlameGraph`, with intact CDDL notices, license, source hashes, and original README. All three Perl scripts pass syntax checks and an actual miniature perf-to-SVG test.
- Future native SVG subtitles identify cycle sampling period (rather than the unused frequency setting). Historical saved graphs remain unchanged.
- Script defaults: `sphere_shadow` for raytrace, `flat_pow` for nbody; `run_all.sh` runs both original and optimized variants with the full configured profiling workflow. Historical candidate kernels remain explicitly selectable for ablation. Non-course stand-in sources are excluded; `USE_UPSTREAM=0` is rejected.
- Official pyperformance harness is an original-benchmark cross-check (phase 6). Optimized comparisons use wrappers around genuine kernel functions. No report should claim the optimized wrapper ran as an official pyperformance benchmark.
- Runtime dependencies: standard-library Python for wrappers; Linux perf and debug Python for symbol-rich sampling; Perl for included FlameGraph; pinned `pyperformance==1.14.0`, `pyperf==2.10.0` for official harness. Optional py-spy is a cross-check only.
- Default local environment paths are `.venv` and `vendor/FlameGraph`; `VENV_DIR` / `FLAMEGRAPH_DIR` can use the existing shared-machine setup. `setup/04_make_venv.sh` prepares harness dependencies; `setup/02_get_flamegraph.sh` now verifies the included toolkit. `setup/01_install_deps.sh` and `setup/03_tune_vm.sh` are optional provisioning scripts, not invoked automatically by run_all; the latter changes system settings and is unnecessary on an already prepared course VM.

## Scope

No original repository files were edited and no Git commands were executed. Saved data and source identity are preserved. Linux perf measurements were not rerun on the Mac. Report builds and hardware checks are recorded separately. The new report builder reads the reviewed report sources and does not execute benchmarks.

