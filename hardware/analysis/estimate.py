#!/usr/bin/env python3
"""Schedule-derived sensitivity, not measured acceleration or timing closure."""
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--clock-mhz',type=float,default=50);p.add_argument('--iter-core-cycles',type=int,default=57);p.add_argument('--host-us',type=float,default=.1)
a=p.parse_args()
# ALU request + response consumption: 2 cycles for a registered simple operation.
# Iterative latency is a configurable assumption pending cycle simulation.
# Add 2 wrapper/controller edges to the assumed core interval.
B=2;I=a.iter_core_cycles+2
cycles={'VDOT3':6+1+5*B+1,'SPHERE_miss':7+1+14*B+1,'SPHERE_root':7+1+14*B+I+B+1,'RMAG':2+1+I+B+I+1}
ray_hw=(172523*cycles['SPHERE_miss']+6934*cycles['SPHERE_root'])/(a.clock_mhz*1000)
nb_hw=200000*cycles['VDOT3']/(a.clock_mhz*1000)
bench={'raytrace':(530.8805,179457,ray_hw),'nbody_vdot_only':(143.3736875,200000,nb_hw)}
result={'kind':'analytical sensitivity, not measured hardware speedup','clock_mhz_target':a.clock_mhz,'iter_core_cycles_assumed':a.iter_core_cycles,'extra_host_us_per_command_assumed':a.host_us,'cycles_including_operand_writes_command_and_retirement':cycles,'benchmarks':{}}
for name,(time,n,device) in bench.items():
 bridge=n*a.host_us/1000;cost=device+bridge
 result['benchmarks'][name]={'software_ms':time,'commands':n,'device_ms':device,'extra_host_ms':bridge,'total_offload_ms':cost,'break_even_removed_fraction':cost/time,'scenarios':[{'removed_fraction_assumed':f,'estimated_ms':time*(1-f)+cost,'estimated_time_reduction_pct':100*(f-cost/time)} for f in [.2,.3,.4,.5,.6]]}
print(json.dumps(result,indent=2))
