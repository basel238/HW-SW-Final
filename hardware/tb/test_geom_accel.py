"""Optional RTL tests. A passing simulation covers cases, not all inputs."""
import sys,random,math
from pathlib import Path
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge,FallingEdge,Timer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model'))
from fp64_model import *
async def edge(d):
 await RisingEdge(d.clk);await Timer(1,units='ns')
async def reset(d):
 d.rst_n.value=0;d.op_we.value=0;d.cmd_valid.value=0;d.rsp_ready.value=0
 d.op_addr.value=0;d.op_wdata.value=0;d.cmd_opcode.value=0
 for _ in range(4):await edge(d)
 await FallingEdge(d.clk);d.rst_n.value=1
 await edge(d)
async def run_op(d,op,values,hold=3):
 for i,x in enumerate(values):
  await FallingEdge(d.clk);d.op_we.value=1;d.op_addr.value=i;d.op_wdata.value=f2b(x)
  await edge(d)
 await FallingEdge(d.clk);d.op_we.value=0
 await edge(d);assert int(d.cmd_ready.value)
 await FallingEdge(d.clk);d.cmd_opcode.value=op;d.cmd_valid.value=1
 await edge(d)
 await FallingEdge(d.clk);d.cmd_valid.value=0
 for _ in range(3000):
  if int(d.rsp_valid.value):break
  await edge(d)
 else:raise AssertionError('response timeout')
 got=(int(d.rsp_status.value),int(d.rsp_result.value))
 for _ in range(hold):
  await edge(d)
  assert int(d.rsp_valid.value) and got==(int(d.rsp_status.value),int(d.rsp_result.value))
 await FallingEdge(d.clk);d.rsp_ready.value=1
 await edge(d)
 await FallingEdge(d.clk);d.rsp_ready.value=0
 return got
@cocotb.test()
async def test_operations_and_status(d):
 cocotb.start_soon(Clock(d.clk,20,units='ns').start());await reset(d)
 rng=random.Random(17)
 cases=[(255,[]),(0,[]),(1,[math.inf,1.]),(1,[1e308,1e308]),(4,[1.,0.]),(5,[-1.]),(16,[0.,.01]),(17,[1e308,0,0,0,1,0,1]),(5,[-0.])]
 for _ in range(30):
  a=rng.uniform(-10,10);b=rng.uniform(.01,10)
  cases.extend((op,[a,b]) for op in [1,2,3,4]);cases.append((5,[abs(a)]))
  cases.append((6,[rng.uniform(-4,4) for _ in range(6)]));cases.append((16,[b,.01]))
  cases.append((17,[rng.uniform(-4,4) for _ in range(6)]+[b]))
 for op,values in cases:
  expected=execute(op,values);status,bits=await run_op(d,op,values)
  assert status==expected[0],(op,values,status,expected)
  if status==ST_OK:assert bits==f2b(expected[1]),(op,values,hex(bits),hex(f2b(expected[1])))
 # Reset also cancels any accepted iterative command and clears response validity.
 await FallingEdge(d.clk);d.op_we.value=1;d.op_addr.value=0;d.op_wdata.value=f2b(2.)
 await edge(d)
 await FallingEdge(d.clk);d.op_we.value=0
 await edge(d)
 await FallingEdge(d.clk);d.cmd_valid.value=1;d.cmd_opcode.value=5
 await edge(d)
 await FallingEdge(d.clk);d.cmd_valid.value=0
 await reset(d)
 for _ in range(70):await edge(d);assert not int(d.rsp_valid.value)
