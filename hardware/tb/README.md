# Optional RTL simulation

Simulation was not required or performed for the submitted evidence. The saved semantic elaboration is not a simulation result.

This testbench targets cocotb 1.9.2 and Verilator with SystemVerilog support. Once these are installed in a suitable environment:

```bash
cd hardware/tb
make
```

It checks random finite primitives/macros, bad opcodes, nonfinite/domain/overflow status, negative zero, held response under backpressure and reset cancellation. Numeric comparisons use `model/fp64_model.py`. This testbench has not been executed here; simulator-specific compatibility may require adjustment. No full benchmark or physical timing claim follows from these tests.
