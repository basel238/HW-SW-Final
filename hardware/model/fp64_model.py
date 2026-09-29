"""Ordered binary64 reference, not an RTL simulation or whole-render proof.
NONFINITE also covers domain/zero-division/overflow; its result bits are ignored.
RMAG is approximate compared with the selected nbody flat_pow kernel.
"""
import math, struct
ST_OK,ST_ROOT_NONE,ST_NONFINITE,ST_BADOP=0,1,2,15
OP_NOP=0
OP_FADD,OP_FSUB,OP_FMUL,OP_FDIV,OP_FSQRT,OP_VDOT3=1,2,3,4,5,6
OP_RMAG,OP_SPHERE=16,17
COUNTS={0:0,1:2,2:2,3:2,4:2,5:1,6:6,16:2,17:7}
def f2b(x):return struct.unpack('<Q',struct.pack('<d',x))[0]
def b2f(x):return struct.unpack('<d',struct.pack('<Q',x))[0]
def checked(x):
    if not math.isfinite(x):raise ArithmeticError('nonfinite intermediate')
    return x
def fadd(a,b):return checked(a+b)
def fsub(a,b):return checked(a-b)
def fmul(a,b):return checked(a*b)
def fdiv(a,b):return checked(a/b)
def fsqrt(a):return checked(math.sqrt(a))
def vdot3(a,b):
    m0=fmul(a[0],b[0]);m1=fmul(a[1],b[1]);m2=fmul(a[2],b[2])
    return fadd(fadd(m0,m1),m2)
def rmag(d2,dt):
    try:return ST_OK,fdiv(dt,fmul(d2,fsqrt(d2)))
    except (ArithmeticError,ValueError):return ST_NONFINITE,0.0
def sphere(cp,d,r):
    try:
        v=vdot3(cp,d);q=vdot3(cp,cp);vv=fmul(v,v)
        z=fsub(q,vv);rr=fmul(r,r);disc=fsub(rr,z)
        if disc<0:return ST_ROOT_NONE,v
        return ST_OK,fsub(v,fsqrt(disc))
    except (ArithmeticError,ValueError):return ST_NONFINITE,0.0
def execute(opcode,opreg):
    if opcode not in COUNTS:return ST_BADOP,0.0
    if any(not math.isfinite(x) for x in opreg[:COUNTS[opcode]]):return ST_NONFINITE,0.0
    try:
        if opcode==0:return ST_OK,0.0
        if opcode in (1,2,3,4):return ST_OK,{1:fadd,2:fsub,3:fmul,4:fdiv}[opcode](*opreg[:2])
        if opcode==5:return ST_OK,fsqrt(opreg[0])
        if opcode==6:return ST_OK,vdot3(opreg[:3],opreg[3:6])
        if opcode==16:return rmag(*opreg[:2])
        return sphere(opreg[:3],opreg[3:6],opreg[6])
    except (ArithmeticError,ValueError):return ST_NONFINITE,0.0
