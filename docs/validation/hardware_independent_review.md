# Independent review of the adapted hardware submission

Scope: read-only inspection of `outputs/HW-SW-Final/hardware/`, plus independent host reference validation and semantic RTL elaboration. No hardware files were changed, no Git command was executed, and no RTL simulation was performed.

## Conclusion

No blocking datapath, handshake, numerical-contract, or estimate-consistency defect was found in this bounded review. The revised proposal corrects the central issues in the supplied archive: a real HardFloat main datapath replaces behavioral `real` arithmetic; CPU-native demonstrations are labelled correctly; approximate RMAG is excluded from the exact nbody path; and hardware runtime claims are conditional, schedule-derived estimates.

This review does not prove RTL numerical correctness, timing closure, cycle counts for all iterative inputs, or end-to-end benchmark integration. The submission explicitly acknowledges these limits and should retain that language.

## Checks and evidence

1. **Actual datapath.** `fp64_binary.sv` instantiates IEEE/recoded converters, `addRecFN`, and `mulRecFN`. `fp64_alu.sv` instantiates `divSqrtRecFN_small` and waits for its actual `outValid`. Add/subtract/multiply use separate rounding, and no FMA is instantiated. There are no artificial wait counters or SystemVerilog `real` arithmetic in the selected main RTL.

2. **Command and operand handshake.** The host finishes writes before asserting a command. `cmd_ready` is suppressed during an operand write. Operand writes are ignored while the sequencer is busy, so operands cannot change beneath an active micro-operation. The controller only advances after the ALU response. Command outputs remain registered and stable in RESP until `rsp_ready`. Reset aborts both the command controller and iterative arithmetic. Temporary values are written before use in each implemented macro sequence.

3. **Statuses.** Unknown opcodes produce BADOP. Used nonfinite operands are rejected at acceptance. ALU invalid/divide-by-zero/overflow or nonfinite results produce NONFINITE before the sphere no-root check. Finite negative discriminants produce ROOT_NONE; negative zero does not. The documented CPU fallback is an integration contract, not a claimed deployed driver.

4. **Numerical scope.** VDOT3 preserves three rounded multiplies and ordered adds. SPHERE preserves the scalar expression dependency order; the host supplies center-minus-origin and retains traversal, eligibility and shading. The numerical demonstration is not a full-render integration test. Exact nbody may use VDOT3 while retaining original host power arithmetic. RMAG and `advance_nbody_approx` are explicitly approximate, are not selected by the measured scripts, and should remain separate.

5. **Schedule consistency.** For a simple primitive, the issue edge captures the ALU result and the following wait edge consumes it: two controller cycles. The reported transaction budgets include operand writes, command acceptance and response retirement: VDOT3 = 6+1+5×2+1 = 18; sphere miss = 7+1+14×2+1 = 37. Root and RMAG estimates add the explicitly assumed 57-cycle iterative core interval plus wrapper/controller edges. Thus the simple-path counting matches the sequencer structure. Iterative latency remains a sensitivity input pending cycle simulation; it is not an observed latency.

6. **ROI arithmetic.** Re-running `analysis/estimate.py` reproduced the submitted results: raytrace device budget 141.25766 ms plus assumed extra host cost 17.9457 ms; total 159.20336 ms and break-even removed fraction 29.98855% against 530.8805 ms. Exact nbody VDOT-only costs 92 ms under the selected assumptions and needs more than 64.17% runtime removed merely to break even. The report appropriately does not claim exact nbody hardware speedup.

7. **Host CPU control.** The native module remains CPU C software, with contraction and fast-math disabled in its build. Its name, README, and validation distinguish CPU-native arithmetic from RTL execution. Per-call scene conversion and lack of deployed bridge are disclosed. Host control checks do not establish whole-benchmark equivalence or hardware speedup.

8. **Elaboration independently reproduced.** `hardware/check_syntax.py`, using the existing local pyslang 11.0.0 installation, returned success with zero errors and one duplicate-wire warning from unmodified HardFloat. The diagnostic is semantic elaboration, not simulation or synthesis. Independent output is saved as `hardware_independent_elaboration.log` beside this review.

9. **Reference validation independently reproduced.** `hardware/model/validate.py` passed 20,000 dot cases, 20,000 sphere-expression cases and 10 exceptional-status cases. These checks execute host Python only; the output truthfully declares `rtl_simulated: false`.

10. **Optional cocotb testbench.** The testbench drives operands/commands on falling edges, samples after rising edges, checks responses under backpressure, covers finite arithmetic/status cases, and resets an accepted iterative command. Its timeout is bounded. Makefile source paths and package ordering are consistent with `files.f`. The documented unexecuted status is important: simulator compatibility, further adversarial input coverage and exact transaction-cycle tests remain unverified.

## Non-blocking follow-ups

- If simulation is later performed, add transaction-cycle measurements, busy-time operand-write attempts, all opcode reset positions, and subnormal/boundary inputs. These are future confidence improvements, not presently claimed test results.
- Native scene batching and a processor bridge must be implemented and costed before claiming measured hardware acceleration. The proposal currently defines their responsibilities clearly.
- A target of 50 MHz and 57 iterative core cycles must remain labelled assumptions until timing/cycle evidence exists.
- The three HTML animations must retain their conceptual-status banners; their historical counters and artificial wait illustration do not match the completion-driven final RTL.
