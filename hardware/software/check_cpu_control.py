#!/usr/bin/env python3
"""CPU C versus ordered Python numeric controls. Not an RTL or image test."""
import json, math, random, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model'))
from fp64_model import sphere,rmag,vdot3,f2b,ST_OK
import _geomaccel_c as native
r=random.Random(20260929)
for _ in range(2000):
 centers=[r.uniform(-3,3) for _ in range(21)];radii=[r.uniform(.1,2) for _ in range(7)]
 o=[r.uniform(-2,2) for _ in range(3)];d=[r.uniform(-1,1) for _ in range(3)];n=math.sqrt(sum(x*x for x in d));d=[x/n for x in d]
 expected=(math.inf,-1)
 for j in range(7):
  cp=[centers[3*j+k]-o[k] for k in range(3)]
  status,dist=sphere(cp,d,radii[j])
  if status==ST_OK and dist> -1e-5 and dist<expected[0]:expected=(dist,j)
 actual=native.intersect_scene(centers,radii,*o,*d,-1e-5)
 assert f2b(actual[0])==f2b(expected[0]) and actual[1]==expected[1],(actual,expected)
pos=[float(i//3*2)+(i%3)*.25 for i in range(15)];vel=[.01*(i%4) for i in range(15)];mass=[1.,.1,.2,.3,.4]
pn=pos.copy();vn=vel.copy();native.advance_nbody_approx(pn,vn,mass,.01,100)
for _ in range(100):
 for i in range(5):
  for j in range(i+1,5):
   delta=[pos[3*i+k]-pos[3*j+k] for k in range(3)]
   status,mag=rmag(vdot3(delta,delta),.01);assert status==ST_OK
   mi=mass[i]*mag;mj=mass[j]*mag
   for k in range(3):vel[3*i+k]-=delta[k]*mj;vel[3*j+k]+=delta[k]*mi
 for k in range(15):pos[k]+=.01*vel[k]
assert [f2b(x) for x in pn+vn]==[f2b(x) for x in pos+vel]
print(json.dumps({'backend':'cpu-native','sphere_batch_cases':2000,'approximate_nbody_steps':100,'state_bits_vs_sqrt_model':'PASS','rtl_executed':False,'whole_upstream_benchmark_validated':False},indent=2))
