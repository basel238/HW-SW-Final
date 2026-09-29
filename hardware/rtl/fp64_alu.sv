// Real binary64 hardware: HardFloat add/sub, multiplier, iterative div/sqrt.
// Each primitive rounds independently, RNE, gradual underflow, no FMA.
`include "HardFloat_consts.vi"
module fp64_alu(
 input logic clk,rst_n,req_valid, output logic req_ready,
 input logic [2:0] fop,input logic [63:0] a,b,
 output logic rsp_valid,input logic rsp_ready,
 output logic [63:0] y,output logic nonfinite
);
 typedef enum logic [1:0] {A_IDLE,A_ITER,A_RESP} alu_state_e;
 alu_state_e state;
 wire [63:0] simple_result,iter_result;
 wire [4:0] simple_flags,iter_flags;
 wire [64:0] rec_a,rec_b,rec_result;
 wire iter_ready,iter_valid,sqrt_unused;
 wire iter_request=req_valid && req_ready && (fop==3 || fop==4);
 fp64_binary simple(.multiply(fop==2),.subtract(fop==1),.a(a),.b(b),
   .result(simple_result),.exception_flags(simple_flags));
 fNToRecFN #(.expWidth(11),.sigWidth(53)) da(.in(a),.out(rec_a));
 fNToRecFN #(.expWidth(11),.sigWidth(53)) db(.in(b),.out(rec_b));
 divSqrtRecFN_small #(.expWidth(11),.sigWidth(53),.options(0)) iter(
  .nReset(rst_n),.clock(clk),.control(`flControl_tininessAfterRounding),
  .inReady(iter_ready),.inValid(iter_request),.sqrtOp(fop==4),
  .a(rec_a),.b(rec_b),.roundingMode(`round_near_even),
  .outValid(iter_valid),.sqrtOpOut(sqrt_unused),.out(rec_result),.exceptionFlags(iter_flags));
 recFNToFN #(.expWidth(11),.sigWidth(53)) enc(.in(rec_result),.out(iter_result));
 assign req_ready=rst_n && state==A_IDLE && iter_ready;
 assign rsp_valid=rst_n && state==A_RESP;
 always_ff @(posedge clk or negedge rst_n) begin
  if(!rst_n) begin state<=A_IDLE;y<=0;nonfinite<=0;end
  else case(state)
   A_IDLE:if(req_valid && req_ready) begin
    if(fop==3 || fop==4) state<=A_ITER;
    else begin
     y<=simple_result;
     nonfinite<=simple_result[62:52]==11'h7ff || |simple_flags[4:2];
     state<=A_RESP;
    end
   end
   A_ITER:if(iter_valid) begin
    y<=iter_result;nonfinite<=iter_result[62:52]==11'h7ff || |iter_flags[4:2];
    state<=A_RESP;
   end
   A_RESP:if(rsp_ready) state<=A_IDLE;
   default:state<=A_IDLE;
  endcase
 end
endmodule
