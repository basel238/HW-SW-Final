// GEOM command sequencer using an implemented HardFloat datapath.
// One command outstanding; host operand writes accepted only while idle.
module geom_accel import geom_accel_pkg::*; (
 input logic clk, rst_n,
 input logic op_we, input logic [2:0] op_addr, input logic [63:0] op_wdata,
 input logic cmd_valid, output logic cmd_ready, input logic [7:0] cmd_opcode,
 output logic rsp_valid, input logic rsp_ready,
 output logic [63:0] rsp_result, output logic [3:0] rsp_status,
 output logic busy
);
 typedef enum logic [1:0] {S_IDLE,S_ISSUE,S_WAIT,S_RESP} state_e;
 state_e state;
 logic [63:0] opreg[NUM_OPREG], t[10];
 opcode_e op_q;
 logic [4:0] step;
 logic [63:0] result_q;
 logic [3:0] status_q;
 logic [2:0] d_fop;
 logic [63:0] d_a,d_b,alu_y;
 logic [3:0] d_dst;
 logic d_last,alu_ready,alu_valid,alu_bad;
 localparam logic [2:0] F_ADD=0,F_SUB=1,F_MUL=2,F_DIV=3,F_SQRT=4;
 localparam logic [3:0] DST_RES=15;
 assign cmd_ready=rst_n && state==S_IDLE && !op_we;
 assign rsp_valid=rst_n && state==S_RESP;
 assign rsp_result=result_q;
 assign rsp_status=status_q;
 assign busy=state!=S_IDLE;
 // A command is issued only after its final operand write. Writes while busy
 // are ignored; the complete register set is stable until response retirement.
 always_ff @(posedge clk) if(rst_n && state==S_IDLE && op_we) opreg[op_addr]<=op_wdata;
 fp64_alu u_alu(.clk(clk),.rst_n(rst_n),
   .req_valid(state==S_ISSUE),.req_ready(alu_ready),
   .fop(d_fop),.a(d_a),.b(d_b),
   .rsp_valid(alu_valid),.rsp_ready(state==S_WAIT),.y(alu_y),.nonfinite(alu_bad));
 function automatic logic supported(input logic [7:0] op);
   return op inside {OP_NOP,OP_FADD,OP_FSUB,OP_FMUL,OP_FDIV,OP_FSQRT,OP_VDOT3,OP_RMAG,OP_SPHERE};
 endfunction
 function automatic int operands_used(input logic [7:0] op);
   case(op)
    OP_NOP:return 0; OP_FSQRT:return 1;
    OP_VDOT3:return 6; OP_SPHERE:return 7;
    default:return 2;
   endcase
 endfunction
 logic input_nonfinite;
 always_comb begin
   input_nonfinite=0;
   for(int i=0;i<NUM_OPREG;i++)
     if(i<operands_used(cmd_opcode) && opreg[i][62:52]==11'h7ff) input_nonfinite=1;
 end
  always_comb begin
    // defaults
    d_fop  = F_ADD;  d_a = '0;  d_b = '0;
    d_dst  = 4'd0;  d_last = 1'b0;

    unique case (op_q)
      // ---------------- primitives ----------------
      OP_FADD : begin d_fop=F_ADD;  d_a=opreg[0]; d_b=opreg[1]; d_dst=DST_RES;  d_last=1; end
      OP_FSUB : begin d_fop=F_SUB;  d_a=opreg[0]; d_b=opreg[1]; d_dst=DST_RES;  d_last=1; end
      OP_FMUL : begin d_fop=F_MUL;  d_a=opreg[0]; d_b=opreg[1]; d_dst=DST_RES;  d_last=1; end
      OP_FDIV : begin d_fop=F_DIV;  d_a=opreg[0]; d_b=opreg[1]; d_dst=DST_RES;  d_last=1; end
      OP_FSQRT: begin d_fop=F_SQRT; d_a=opreg[0];               d_dst=DST_RES; d_last=1; end

      // ---------------- VDOT3 : ((P0*P3)+(P1*P4))+(P2*P5) ----------------
      OP_VDOT3: unique case (step)
        5'd0: begin d_fop=F_MUL; d_a=opreg[0]; d_b=opreg[3]; d_dst=4'd0; end
        5'd1: begin d_fop=F_MUL; d_a=opreg[1]; d_b=opreg[4]; d_dst=4'd1; end
        5'd2: begin d_fop=F_MUL; d_a=opreg[2]; d_b=opreg[5]; d_dst=4'd2; end
        5'd3: begin d_fop=F_ADD; d_a=t[0];     d_b=t[1];     d_dst=4'd3; end
        default: begin d_fop=F_ADD; d_a=t[3]; d_b=t[2]; d_dst=DST_RES; d_last=1; end
      endcase

      // ---------------- RMAG : s=sqrt(P0); res = P1/(P0*s) ----------------
      OP_RMAG: unique case (step)
        5'd0: begin d_fop=F_SQRT; d_a=opreg[0];            d_dst=4'd0; end
        5'd1: begin d_fop=F_MUL;  d_a=opreg[0]; d_b=t[0];  d_dst=4'd1;  end
        default: begin d_fop=F_DIV; d_a=opreg[1]; d_b=t[1]; d_dst=DST_RES; d_last=1; end
      endcase

      // ---------------- SPHERE : report ray/sphere formula ----------------
      // v=VDOT3(cp,d); q=VDOT3(cp,cp); disc=r*r-(q-v*v); res=v-sqrt(disc)
      OP_SPHERE: unique case (step)
        5'd0 : begin d_fop=F_MUL; d_a=opreg[0]; d_b=opreg[3]; d_dst=4'd0; end // m0
        5'd1 : begin d_fop=F_MUL; d_a=opreg[1]; d_b=opreg[4]; d_dst=4'd1; end // m1
        5'd2 : begin d_fop=F_MUL; d_a=opreg[2]; d_b=opreg[5]; d_dst=4'd2; end // m2
        5'd3 : begin d_fop=F_ADD; d_a=t[0];     d_b=t[1];     d_dst=4'd3; end // s0
        5'd4 : begin d_fop=F_ADD; d_a=t[3];     d_b=t[2];     d_dst=4'd4; end // v  -> t4
        5'd5 : begin d_fop=F_MUL; d_a=opreg[0]; d_b=opreg[0]; d_dst=4'd0; end // n0
        5'd6 : begin d_fop=F_MUL; d_a=opreg[1]; d_b=opreg[1]; d_dst=4'd1; end // n1
        5'd7 : begin d_fop=F_MUL; d_a=opreg[2]; d_b=opreg[2]; d_dst=4'd2; end // n2
        5'd8 : begin d_fop=F_ADD; d_a=t[0];     d_b=t[1];     d_dst=4'd3; end // p0
        5'd9 : begin d_fop=F_ADD; d_a=t[3];     d_b=t[2];     d_dst=4'd5; end // q  -> t5
        5'd10: begin d_fop=F_MUL; d_a=t[4];     d_b=t[4];     d_dst=4'd6; end // vv -> t6
        5'd11: begin d_fop=F_SUB; d_a=t[5];     d_b=t[6];     d_dst=4'd7; end // q-vv -> t7
        5'd12: begin d_fop=F_MUL; d_a=opreg[6]; d_b=opreg[6]; d_dst=4'd8; end // rr -> t8
        5'd13: begin d_fop=F_SUB; d_a=t[8];     d_b=t[7];     d_dst=4'd9; end // disc -> t9
        5'd14: begin d_fop=F_SQRT;d_a=t[9];                   d_dst=4'd6;end // sqrt(disc)
        default:begin d_fop=F_SUB; d_a=t[4];    d_b=t[6];     d_dst=DST_RES; d_last=1; end // v-sqrt(disc)
      endcase

      default : begin d_dst=DST_RES; d_last=1; end // OP_NOP / unknown
    endcase
  end


 always_ff @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin
   state<=S_IDLE;step<=0;op_q<=OP_NOP;result_q<=0;status_q<=ST_OK;
  end else case(state)
   S_IDLE:if(cmd_valid && cmd_ready) begin
    step<=0;op_q<=opcode_e'(cmd_opcode);result_q<=0;status_q<=ST_OK;
    if(!supported(cmd_opcode)) begin status_q<=ST_BADOP;state<=S_RESP;end
    else if(input_nonfinite) begin status_q<=ST_NONFINITE;state<=S_RESP;end
    else if(cmd_opcode==OP_NOP) state<=S_RESP;
    else state<=S_ISSUE;
   end
   S_ISSUE:if(alu_ready) state<=S_WAIT;
   S_WAIT:if(alu_valid) begin
    // Exceptional intermediates win over the ordinary no-root branch.
    if(alu_bad) begin result_q<=0;status_q<=ST_NONFINITE;state<=S_RESP;end
    else if(op_q==OP_SPHERE && step==13 && alu_y[63] && |alu_y[62:0]) begin
     result_q<=t[4];status_q<=ST_ROOT_NONE;state<=S_RESP;
    end else if(d_last) begin result_q<=alu_y;state<=S_RESP;end
    else begin t[d_dst]<=alu_y;step<=step+1'b1;state<=S_ISSUE;end
   end
   S_RESP:if(rsp_ready) state<=S_IDLE;
   default:state<=S_IDLE;
  endcase
 end
endmodule
