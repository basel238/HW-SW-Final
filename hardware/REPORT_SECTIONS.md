# raytrace

5. Hardware proposal: ordered sphere-intersection command

The hardware proposal targets the remaining scalar sphere test after the selected sphere_shadow software improvements. The query count is unchanged: 179,457 sphere tests per frame, with 6,934 nonnegative discriminants. A SPHERE command keeps intermediate numbers in hardware registers and sequences the complete ordered expression. This reduces CPU/device command count compared with submitting individual arithmetic operations, while early rejection skips square root for the other 96.14% of queries.

The CPU supplies cp = center − origin, normalized ray direction and radius. Hardware computes v = (cp.x*dx + cp.y*dy) + cp.z*dz; q = (cp.x*cp.x + cp.y*cp.y) + cp.z*cp.z; disc = r*r − (q − v*v); then returns v − sqrt(disc), or ROOT_NONE for a finite negative discriminant. CPU traversal retains nearest-hit t > −1e−5, shadow t > +1e−5, tie order, halfspace handling and early exits. Expression-level agreement does not replace full-image validation of a future integrated adapter.

Architecture and interface. The submitted GEOM unit contains eight 64-bit operand registers, ten 64-bit temporaries, a micro-operation controller, HardFloat add/subtract and multiply logic, and one iterative divide/square-root core. Each operation rounds separately to binary64, round-to-nearest ties-to-even; gradual underflow is retained and FMA is absent. A 50 MHz target is specified, without claiming timing closure. The controller waits for actual arithmetic completion, rather than using behavioral real arithmetic with artificial delays.

Interface | Contract
Operands | op_we + op_addr[2:0] + op_wdata[63:0], idle writes
Command | cmd_opcode[7:0], cmd_valid / cmd_ready
Response | rsp_result[63:0], rsp_status[3:0], rsp_valid / rsp_ready
Control | clk, active-low rst_n; one command outstanding
Status | OK, ROOT_NONE, NONFINITE, BADOP

The host finishes writes before issuing a command. Writes while busy are ignored; a response remains stable until consumed. Reset aborts in-flight work. The CPU retains traversal, original error behavior, and a fallback for exceptional results. The proposed stack is benchmark → native adapter → processor bridge → GEOM. A CPU-native numerical control is included, but no deployed processor bridge or custom instruction is claimed. Moving a loop into C and accelerating it in hardware are separate contributions.

Performance estimate. At two controller cycles per simple operation, 57 assumed core cycles per iterative operation plus two wrapper edges, one cycle per operand write and command/response cycles, a no-root query costs 37 cycles and a root query 98. The 57-cycle input is a conservative planning assumption pending simulation; the controller itself uses completion handshakes. The latest query mix gives 141.258 ms of device work at 50 MHz. An illustrative extra 0.10 microseconds of packing/bridge work per command adds 17.946 ms, for 159.203 ms total offload cost.

Against the current 530.8805 ms/frame software runtime, T_est = 530.8805(1 − f) + 159.20336 ms. Here f is the fraction actually removed by the complete offload boundary, not a debug-profile percentage. At f = 0.30 the estimate is approximately break-even; f = 0.40 gives 477.732 ms (10.01% reduction), and f = 0.50 gives 424.644 ms (20.01%). At f = 0.20 it is 9.99% slower. These are conditional predictions, not achieved hardware results. Equivalent CPU-native and hardware-backed runs are required to isolate a hardware benefit.

Trade-offs and validation. Shared arithmetic and 1,152 bits of operand/temporary storage limit replicated logic; the single outstanding command limits overlap. Add/multiply critical paths may require pipelining, which changes the cycle estimate. No area, power or frequency result is claimed without synthesis and technology data. Saved checks pass 20,000 ordered dot expressions, 20,000 sphere expressions, exceptional-status cases, and RTL semantic elaboration. No RTL simulation or physical experiment was performed. The supplied animations are included as conceptual aids; the authoritative submitted architecture is hardware/diagrams/architecture.svg.

The earlier packet-based design informed the choice of a smaller command interface. The retained proposal uses actual HardFloat logic and an explicit transaction budget. The reported software result remains the measured sphere_shadow improvement; additional hardware speedup remains a conditional design estimate.

# nbody

5. Hardware proposal: shared ordered dot-product support

The shared GEOM unit can compute the pairwise squared distance d² = (dx*dx + dy*dy) + dz*dz with its VDOT3 command. To preserve the exact final nbody contract, the CPU retains dt * d²**(−1.5), mass factors, ordered velocity updates, position updates and energy evaluation. The final measured kernel remains flat_pow. Moving a whole timestep loop to native C could reduce interpreter and boxed-number overhead, but that would be a separate software control, not evidence of custom hardware acceleration.

Architecture and interface. The submitted GEOM unit contains eight 64-bit operand registers, ten 64-bit temporaries, a micro-operation controller, HardFloat add/subtract and multiply logic, and one iterative divide/square-root core. Each operation rounds separately to binary64, round-to-nearest ties-to-even; gradual underflow is retained and FMA is absent. A 50 MHz target is specified, without claiming timing closure. The controller waits for actual arithmetic completion, rather than using behavioral real arithmetic with artificial delays.

Interface | Contract
Operands | op_we + op_addr[2:0] + op_wdata[63:0], idle writes
Command | cmd_opcode[7:0], cmd_valid / cmd_ready
Response | rsp_result[63:0], rsp_status[3:0], rsp_valid / rsp_ready
Control | clk, active-low rst_n; one command outstanding
Status | OK, ROOT_NONE, NONFINITE, BADOP

The host finishes writes before issuing a command. Writes while busy are ignored; a response remains stable until consumed. Reset aborts in-flight work. The CPU retains traversal, original error behavior, and a fallback for exceptional results. The proposed stack is benchmark → native adapter → processor bridge → GEOM. A CPU-native numerical control is included, but no deployed processor bridge or custom instruction is claimed. Moving a loop into C and accelerating it in hardware are separate contributions.

Exactness. VDOT3 uses three separately rounded multiplications followed by two ordered additions, matching the selected distance expression. The optional RMAG command instead computes dt / (d² * sqrt(d²)); it corresponds to flat_sqrt and can alter the accumulated trajectory. RMAG is included as an explicitly approximate capability, not a replacement for the bit-identical submitted kernel. Neither energy tolerance alone nor expression tests establish exact final state equivalence.

Schedule and feasibility. A VDOT3 command needs six operand writes, one command cycle, ten micro-operation cycles, and one response-retirement cycle: 18 cycles in the conservative transaction budget. There are ten pairs per step and 20,000 steps per unit, hence 200,000 hardware commands even if the Python/native boundary is crossed only once. At 50 MHz that is 72 ms of device work. An illustrative additional 0.10 microseconds per command adds 20 ms, so total offload cost is 92 ms.

Compared with the measured 143.3736875 ms/unit flat_pow runtime, T_est = 143.3736875(1 − f) + 92 ms. Breaking even requires removal of more than 64.17% of runtime. The profiles do not establish such a removable share for the dot product alone. Therefore the shared operation is logically applicable to exact nbody, but this design does not claim a nbody hardware speedup. Raytrace is the primary acceleration target; the project proposal need not force one unit to improve both workloads.

Trade-offs and validation. One shared adder, multiplier and iterative divide/square-root unit saves duplication but serializes work. A whole-system resident-state engine or a lower-cost processor instruction could amortize communication further, at the cost of a different design and a new estimate. The submitted design is deliberately bounded. Host reference checks and RTL semantic elaboration pass; no RTL simulation, synthesis, area/power extraction or physical timing is claimed. The numerical default and the software speedup measurements are unchanged by this proposal.

