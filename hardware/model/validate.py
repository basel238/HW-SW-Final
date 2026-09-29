#!/usr/bin/env python3
"""Host arithmetic reference checks; this does not execute HDL."""
import json, math, random
from fp64_model import *
rng=random.Random(20260929)
count=20000
for i in range(count):
 a=[rng.uniform(-10,10) for _ in range(3)];b=[rng.uniform(-1,1) for _ in range(3)]
 ref=((a[0]*b[0])+(a[1]*b[1]))+(a[2]*b[2])
 assert f2b(vdot3(a,b))==f2b(ref)
 r=rng.uniform(.1,5);v=ref;q=(a[0]*a[0]+a[1]*a[1])+a[2]*a[2];disc=r*r-(q-v*v)
 st,y=execute(OP_SPHERE,a+b+[r]);assert st==(ST_ROOT_NONE if disc<0 else ST_OK)
 if disc>=0:assert f2b(y)==f2b(v-math.sqrt(disc))
cases=[(255,[],ST_BADOP),(0,[],ST_OK),(1,[math.inf,1],ST_NONFINITE),
 (1,[1e308,1e308],ST_NONFINITE),(4,[1,0],ST_NONFINITE),(5,[-1],ST_NONFINITE),
 (16,[0,.01],ST_NONFINITE),(17,[1e308,0,0,0,1,0,1],ST_NONFINITE),
 (6,[0,0,0,1,1,1],ST_OK),(17,[0,0,1,0,0,1,1],ST_OK)]
for op,values,status in cases:assert execute(op,values)[0]==status
print(json.dumps({'host_reference':'PASS','ordered_dot_cases':count,'sphere_expression_cases':count,'edge_status_cases':len(cases),'rtl_simulated':False},indent=2))
