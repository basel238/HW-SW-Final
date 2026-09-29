# Shared GEOM binary64 unit

The selected hardware proposal is an ordered geometry functional unit, primarily for raytrace sphere intersections after the `sphere_shadow` software optimization. The same dot-product operation can serve nbody without changing its `flat_pow` arithmetic. The optional RMAG command is a separate approximate experiment; it is not selected for the exact nbody submission.

## Work split and motivation

Software reduced object construction and repeated Python operations, but the remaining intersection calculation still executes many boxed scalar operations. A native caller can supply numeric operands and receive one result from a multi-operation command. This reduces the number of CPU/device transactions compared with issuing one command for each multiply or add. Moving the loop to C would independently remove interpreter overhead; that software benefit must be measured separately from any hardware benefit.

Raytrace remains responsible for `cp = center - origin`, normalized direction, scene traversal, halfspace intersections, material/shading, recursion, ties and hit eligibility. The hardware computes `v = (cp.x*dx + cp.y*dy) + cp.z*dz`, `q = (cp.x² + cp.y²) + cp.z²`, `disc = r*r - (q - v*v)`, and then `v - sqrt(disc)`. It returns an ordinary no-root status for a finite negative discriminant, avoiding the root operation. Nearest-hit selection must retain `t > -1e-5`; shadow visibility must retain its separate `t > +1e-5` test and early exit. A future adapter must validate complete rendered images, not only distances.

## Architecture and interfaces

The synthesizable logical datapath consists of HardFloat binary64 add/subtract and multiply logic, a shared iterative divide/square-root core, IEEE-to-recoded and recoded-to-IEEE converters, eight 64-bit operand registers, ten 64-bit temporary registers, operand/result multiplexers, and a four-state micro-operation controller. Independent operations each round to nearest, ties to even; gradual underflow is retained. There is no fused multiply-add. The clock target is 50 MHz (20 ns), not a timing-closure result. No synthesis, area/power extraction or hardware performance measurement has been performed.

| Port | Width / direction | Meaning |
|---|---|---|
| clk, rst_n | 1 input each | Clock; active-low reset aborts in-flight work |
| op_we, op_addr, op_wdata | 1, 3, 64 input | One operand write per idle cycle |
| cmd_valid, cmd_ready | 1 input, 1 output | Accept command when both are high |
| cmd_opcode | 8 input | Primitive or macro-operation |
| rsp_valid, rsp_ready | 1 output, 1 input | Result is held until consumed |
| rsp_result, rsp_status | 64, 4 output | Result bits and completion code |
| busy | 1 output | A command/response is outstanding |

The host finishes operand writes before asserting a command. `cmd_ready` is low during a write. Writes while busy are ignored; operand registers remain stable throughout the operation. Only used operand registers need initialization. Reset invalidates previous operands, so the host rewrites every used operand before the next command. Responses remain stable under backpressure. The FSM transitions IDLE → ISSUE → WAIT, repeating ISSUE/WAIT for each primitive, then RESP → IDLE. The ALU waits for actual HardFloat completion; it has no behavioral `real` arithmetic or artificial latency countdown.

| Command | Operands | Micro-operations |
|---|---|---|
| FADD / FSUB / FMUL / FDIV | OP0, OP1 | One selected primitive |
| FSQRT | OP0 | One square root |
| VDOT3 | OP0..2 = a; OP3..5 = b | Three multiplications, then two ordered adds |
| SPHERE | OP0..2 = cp; OP3..5 = direction; OP6 = radius | Eight multiplies and six adds/subtracts to discriminant; on root path one sqrt and one subtract |
| RMAG, optional | OP0 = d²; OP1 = dt | sqrt(d²), multiply by d², divide dt by product |
| NOP | None | Returns zero |

Status 0 means finite success; 1 means no real sphere root; 2 means nonfinite input/intermediate, invalid arithmetic, divide-by-zero or overflow; 15 means unknown command. The host must ignore result bits for statuses 2/15 and execute its original software path or surface the original error. This fallback policy is specified but a deployed CPU/device bridge is not included. Inexact/underflow alone do not cause fallback. Negative zero is not treated as a negative discriminant.

## Software stack and supplied implementation

The HDL and vendored HardFloat sources are complete logical datapath/control sources, with license and provenance. `model/fp64_model.py` defines ordered operations and status semantics. `tb/` contains an optional cocotb testbench. `software/c_ext/` is a CPU-only control, compiled with FP contraction and fast-math disabled. It does not issue GEOM instructions and is not selected by the benchmark scripts. Its nbody routine is explicitly named `advance_nbody_approx`; it uses the optional square-root formulation. Its sphere helper is a numeric demonstration and still converts scene sequences per call. Persistent scene storage and the processor bridge are integration work, not claimed implemented functionality.

The intended stack is benchmark → native adapter → operand/command/response bridge → GEOM RTL. A single Python/native call may contain many hardware commands: one per tested sphere, or 200,000 VDOT3 commands per 20,000-step nbody unit. No DMA engine, CPU ISA encoding, kernel driver, resident-scene memory or whole-timestep controller is claimed. The command interface could be attached to a coprocessor or a mapped register block; that integration must be costed for its target system.

## Schedule-derived estimate

`analysis/estimate.py` counts actual ordered micro-operations. Each simple add/subtract/multiply uses two controller edges (issue, capture). An iterative operation uses the core's variable completion interval plus two wrapper/controller edges. The default sensitivity assumes 57 core cycles for a normal divide/square root; this is a conservative planning input, not a simulated exact latency. One clock per operand write, one command-accept cycle and one response-retirement cycle are included. The resulting budgets are 18 cycles per VDOT3, 37 per no-root SPHERE, 98 per root SPHERE and 124 per optional RMAG. Cycle simulation and timing closure would refine these budgets.

For the latest raytrace workload there are 179,457 sphere queries and 6,934 roots. At 50 MHz the device budget is 141.258 ms/frame. An illustrative extra host cost of 0.10 microseconds per command adds 17.946 ms, for 159.203 ms total offload cost. This extra term covers packing/bridge work beyond the register cycles already counted; it is an assumption to measure. Against the selected 530.8805 ms software runtime:

`T_est = 530.8805 * (1 - f) + 159.20336 ms`,

where `f` is the fraction actually removed by the complete offload boundary. At assumed f=0.20 it slows down by 9.99%; f=0.30 is approximately break-even; f=0.40 gives 477.732 ms (10.01% reduction); f=0.50 gives 424.644 ms (20.01% reduction). These are conditional estimates, not achieved results. Debug interpreter profile shares cannot establish f. Compare exact optimized Python, equivalent CPU-native software, and native plus hardware to separate contributions. Increasing bridge cost or missing the target frequency can remove the benefit.

For exact nbody, offloading only VDOT3 while retaining host `pow` gives 72 ms device work plus an assumed 20 ms host overhead per unit. The 92 ms cost requires removal of over 64.17% of the current 143.3736875 ms runtime merely to break even, which current evidence does not establish for dot products. Therefore shared instruction applicability is demonstrated, but a hardware speedup for exact nbody is not claimed. RMAG changes the numerical formulation and remains optional approximate.

## Area, power and limitations

Sharing one iterative divide/sqrt core, one multiplier and one adder limits replicated arithmetic and control area; operand/temporary storage is 1,152 bits before result/control registers. No numeric gate count, mm² or watts is asserted without a technology, synthesis and activity data. Unpipelined combinational add/mul can limit achievable clock; adding pipeline stages changes all schedules. The single outstanding command avoids queues and reorder logic but limits throughput and overlap. Retaining CPU traversal and error fallback simplifies correctness, at the cost of bridge traffic. Higher frequency, pipelining or batches could help, but they are future designs requiring new estimates.

## Validation status and figures

Saved `validation/host_reference.json` checks 20,000 ordered dots, 20,000 sphere expressions and exceptional statuses in the Python reference. `validation/rtl_elaboration.txt` records semantic RTL elaboration with zero errors; its one warning is a duplicate wire declaration in vendored HardFloat. The optional testbench exercises finite/random operations, unknown commands, nonfinite/domain inputs and held responses. No RTL simulation has been run for this submission; numerical hardware equivalence and cycle budgets are therefore not represented as proven. Complete benchmark software gates remain in the main workflow.

`diagrams/architecture.svg` and `architecture.mmd` describe the submitted design. The three supplied HTML animations are included as conceptual teaching aids with a prominent status banner. Their historical counters and wait-state illustration are not an executable simulation of the final completion-driven RTL.
