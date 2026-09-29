// Ordered FP64 GEOM operations. RMAG is approximate versus nbody flat_pow.
package geom_accel_pkg;

  // ------------------------------------------------------------------
  // Opcodes (written to the CMD register, bits [7:0])
  // ------------------------------------------------------------------
  // Fine-grained primitives  (general, NOT workload-specific — matches the
  // Project.pdf "extend ISA ... e.g. multiply-accumulate" guidance):
  typedef enum logic [7:0] {
    OP_NOP    = 8'h00,
    OP_FADD   = 8'h01,  // res = a + b
    OP_FSUB   = 8'h02,  // res = a - b
    OP_FMUL   = 8'h03,  // res = a * b
    OP_FDIV   = 8'h04,  // res = a / b
    OP_FSQRT  = 8'h05,  // res = sqrt(a)
    OP_VDOT3  = 8'h06,  // res = ((a0*b0)+(a1*b1))+(a2*b2)   (ordered, per-op round)
    // Fused macro-ops (one handshake per query -> amortize the HW/SW crossing):
    OP_RMAG   = 8'h10,  // nbody:    s=sqrt(OP0); res = OP1 / (OP0 * s)
    OP_SPHERE = 8'h11   // raytrace: full ray/sphere intersection (see geom_accel.sv)
  } opcode_e;

  // ------------------------------------------------------------------
  // Status / flag codes (STATUS register, bits [3:0])
  // ------------------------------------------------------------------
  typedef enum logic [3:0] {
    ST_OK        = 4'h0,  // finite result produced
    ST_ROOT_NONE = 4'h1,  // SPHERE: discriminant < 0  -> caller uses "no hit"
    ST_NONFINITE = 4'h2,  // NaN/Inf produced or supplied -> CPU fallback
    ST_BADOP     = 4'hF   // unknown opcode
  } status_e;

  // ------------------------------------------------------------------
  // Operand register file layout (8 x FP64), addressed by the host.
  //   VDOT3 : a = {OP0,OP1,OP2}, b = {OP3,OP4,OP5}
  //   RMAG  : d2 = OP0, dt = OP1
  //   SPHERE: cp = {OP0,OP1,OP2}, dir = {OP3,OP4,OP5}, radius = OP6
  // ------------------------------------------------------------------
  localparam int NUM_OPREG = 8;
  localparam int FPW       = 64;  // FP64 datapath width


endpackage : geom_accel_pkg
