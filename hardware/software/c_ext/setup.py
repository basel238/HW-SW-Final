"""Build CPU control with separate rounding: no FMA or fast-math."""
from setuptools import setup, Extension

ext = Extension(
    "_geomaccel_c",
    sources=["geomaccel_module.c"],
    extra_compile_args=["-O3", "-march=native", "-fno-math-errno", "-ffp-contract=off", "-fno-fast-math"],
)

setup(
    name="geomaccel",
    version="1.0",
    description="Native FP64 GEOM microkernels for nbody + raytrace",
    ext_modules=[ext],
)
