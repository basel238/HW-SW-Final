SIM ?= verilator
TOPLEVEL_LANG = verilog
TOPLEVEL = geom_accel
MODULE = test_geom_accel
ROOT := $(abspath ../..)
VERILOG_SOURCES := $(addprefix $(ROOT)/,$(shell sed '/^+/d' ../files.f))
COMPILE_ARGS += --Wno-fatal -I$(ROOT)/hardware/vendor/HardFloat-1/source -I$(ROOT)/hardware/vendor/HardFloat-1/source/8086-SSE
include $(shell cocotb-config --makefiles)/Makefile.sim
