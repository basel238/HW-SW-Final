# GEOM hardware proposal

Start with `docs/HARDWARE_DESIGN.md` and `diagrams/architecture.svg`. This is the adapted hardware proposal from the supplied archive, with actual HardFloat datapath/control. It is separate from the measured exact Python optimizations.

From the submission root:

```bash
python3 -B hardware/model/validate.py
python3 -B hardware/analysis/estimate.py
python3 -B hardware/check_syntax.py
```

The last command requires `pyslang==11.0.0`; it elaborates, but does not simulate or synthesize. Optional RTL simulation instructions are in `tb/README.md`. No installation or network activity is hidden in any command.

Optional CPU control:

```bash
(cd hardware/software/c_ext && python3 setup.py build_ext --inplace)
PYTHONPATH=hardware/software/c_ext python3 -B hardware/software/check_cpu_control.py
```

This uses host C arithmetic, not accelerator hardware. The nbody native demo is approximate and is never selected by `run_all.sh`. Final exact kernels remain raytrace `sphere_shadow` and nbody `flat_pow`. See saved validation files for checks actually executed. Performance estimates are conditional; no measured hardware speedup is claimed.
