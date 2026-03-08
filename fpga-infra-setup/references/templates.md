# Infrastructure File Templates

These are proven templates from a successful Alveo U55C build. Adapt them to the user's specific RTL design.

## Table of Contents
1. [Makefile](#makefile)
2. [sources.txt](#sourcestxt)
3. [vitis.ini](#vitisini)
4. [run.sh](#runsh)
5. [gen_xo.tcl](#gen_xotcl)
6. [package_kernel.tcl](#package_kerneltcl)
7. [parse_vcs_list.tcl](#parse_vcs_listtcl)
8. [AXI4-Lite Control Slave](#axi4-lite-control-slave)
9. [AXI4 Master Compute Core (FSM pattern)](#axi4-master-compute-core)
10. [Top-Level Wrapper](#top-level-wrapper)
11. [Host Application](#host-application)

---

## Makefile

```makefile
# RTL-to-FPGA build for Alveo U55C
# Pipeline: sources.txt -> XO (Vivado) -> XCLBIN (v++) -> host (g++)

PLATFORM ?= xilinx_u55c_gen3x16_xdma_3_202210_1
TARGET   ?= hw

VIVADO ?= /tools/Xilinx/Vivado/2024.1/bin/vivado
VPP    ?= /tools/Xilinx/Vitis/2024.1/bin/v++

KERNEL_NAME := <KERNEL_NAME>
BUILD_DIR   := build_$(TARGET)

XO_FILE     := $(BUILD_DIR)/$(KERNEL_NAME).xo
XCLBIN_FILE := $(BUILD_DIR)/$(KERNEL_NAME).xclbin

SRC_DIR  := $(CURDIR)
SCRIPT_DIR := $(SRC_DIR)/scripts

# Max parallel Vivado jobs
MAX_JOBS ?= 8
NCPUS := $(shell nproc 2>/dev/null || echo 4)
JOBS  := $(shell echo $$(( $(NCPUS) > $(MAX_JOBS) ? $(MAX_JOBS) : $(NCPUS) )))

# v++ flags
VPP_FLAGS := --link --target $(TARGET) --platform $(PLATFORM)
VPP_FLAGS += --save-temps --no_ip_cache
VPP_FLAGS += --vivado.synth.jobs $(JOBS) --vivado.impl.jobs $(JOBS)
VPP_FLAGS += --config $(SRC_DIR)/vitis.ini
VPP_FLAGS += --report_level 2
VPP_FLAGS += --optimize 3
VPP_FLAGS += --connectivity.sp $(KERNEL_NAME)_1.m_axi_mem_0:HBM[0:31]

# XRT include/lib paths
XRT_INC ?= /opt/xilinx/xrt/include
XRT_LIB ?= /opt/xilinx/xrt/lib

.PHONY: all xo xclbin host clean

all: xclbin host

# Step 1: Package RTL into .xo
xo: $(XO_FILE)
$(XO_FILE): sources.txt <RTL_DEPS> \
            scripts/gen_xo.tcl scripts/package_kernel.tcl scripts/parse_vcs_list.tcl
	mkdir -p $(BUILD_DIR)
	cd $(BUILD_DIR) && $(VIVADO) -mode batch -source $(SCRIPT_DIR)/gen_xo.tcl \
		-tclargs $(CURDIR)/$(XO_FILE) $(KERNEL_NAME) $(CURDIR)/sources.txt $(CURDIR)/$(BUILD_DIR)

# Step 2: Link .xo into .xclbin (this is the long FPGA build step)
xclbin: $(XCLBIN_FILE)
$(XCLBIN_FILE): $(XO_FILE)
	mkdir -p $(BUILD_DIR)
	cd $(BUILD_DIR) && $(VPP) $(VPP_FLAGS) -o $(CURDIR)/$(XCLBIN_FILE) $(CURDIR)/$(XO_FILE)

# Step 3: Compile host application
host: host/<TEST_BINARY>
host/<TEST_BINARY>: host/host.cpp
	g++ -std=c++17 -O2 -o $@ $< -I$(XRT_INC) -L$(XRT_LIB) -lxrt_coreutil -lpthread

clean:
	rm -rf $(BUILD_DIR) host/<TEST_BINARY>
```

Replace `<KERNEL_NAME>`, `<RTL_DEPS>`, `<TEST_BINARY>` with actual names.

---

## sources.txt

```
+incdir+./rtl
./rtl/<ctrl_module>.sv
./rtl/<core_module>.sv
./rtl/<top_wrapper>.v
```

List order matters for some tools. Put include directories first, then dependencies before modules that instantiate them, and the top-level wrapper last.

If user RTL files are in a different directory, use absolute paths or paths relative to the sources.txt location. The `package_kernel.tcl` template resolves relative paths from the directory containing `sources.txt`.

---

## vitis.ini

```ini
[vivado]
prop=run.impl_1.STEPS.OPT_DESIGN.IS_ENABLED=true
```

This enables the optimization design step during implementation, which can help with timing closure.

---

## run.sh

```bash
#!/bin/bash
# One-shot: source environment, build everything, run test.
set -e

echo "=== Setting up environment ==="

# XRT runtime
source /opt/xilinx/xrt/setup.sh
export PATH=$PATH:/usr/bin:/usr/local/bin:/bin

# Vivado + Vitis
source /tools/Xilinx/Vivado/2024.1/settings64.sh
source /tools/Xilinx/Vitis/2024.1/settings64.sh

echo "Vivado: $(which vivado)"
echo "v++:    $(which v++)"

# Build host (fast, ~seconds)
echo ""
echo "=== Building host application ==="
make host

# Build FPGA (slow, ~1-2 hours)
echo ""
echo "=== Building XO (IP packaging) ==="
make xo

echo ""
echo "=== Building XCLBIN (synthesis + implementation) ==="
make xclbin

# Run test
echo ""
echo "=== Running FPGA test ==="
./host/<TEST_BINARY> build_hw/<KERNEL_NAME>.xclbin
```

---

## gen_xo.tcl

```tcl
# Generate .xo (Xilinx Object) from RTL sources.

if { $::argc != 4 } {
    puts "ERROR: Program \"$::argv0\" requires 4 arguments!\n"
    puts "Usage: $::argv0 <xoname> <krnl_name> <vcs_file> <build_dir>\n"
    exit
}

set xoname    [lindex $::argv 0]
set krnl_name [lindex $::argv 1]
set vcs_file  [lindex $::argv 2]
set build_dir [lindex $::argv 3]

set script_dir [ file dirname [ file normalize [ info script ] ] ]

puts "Using xoname=$xoname"
puts "Using krnl_name=$krnl_name"
puts "Using vcs_file=$vcs_file"
puts "Using build_dir=$build_dir"
puts "Using script_dir=$script_dir"

if {[file exists "${xoname}"]} {
    file delete -force "${xoname}"
}

# Package the kernel
set argv [list ${krnl_name} ${vcs_file} ${build_dir}]
set argc 3
source ${script_dir}/package_kernel.tcl

package_xo -xo_path ${xoname} -kernel_name ${krnl_name} -ip_directory "${build_dir}/xo/packaged_kernel"
```

This file is stable — no customization needed for different designs.

---

## package_kernel.tcl

This is the most complex template. It must be customized for each design's register map. The structure below shows the pattern; adapt the register definitions section.

```tcl
# Package RTL into Vivado IP for XRT kernel.

if { $::argc != 3 } {
    puts "ERROR: Program \"$::argv0\" requires 3 arguments!\n"
    puts "Usage: $::argv0 <krnl_name> <vcs_file> <build_dir>\n"
    exit
}

set krnl_name [lindex $::argv 0]
set vcs_file  [lindex $::argv 1]
set build_dir [lindex $::argv 2]

set script_dir [ file dirname [ file normalize [ info script ] ] ]

set path_to_packaged "${build_dir}/xo/packaged_kernel"
set path_to_tmp_project "${build_dir}/xo/project"

source "${script_dir}/parse_vcs_list.tcl"
set vlist [parse_vcs_list "${vcs_file}"]

set vsources_list  [lindex $vlist 0]
set vincludes_list [lindex $vlist 1]
set vdefines_list  [lindex $vlist 2]

# Resolve relative paths from the directory containing sources.txt
set vcs_dir [file dirname [file normalize "${vcs_file}"]]

set resolved_sources [list]
foreach src $vsources_list {
    if {[file pathtype $src] eq "relative"} {
        lappend resolved_sources [file normalize [file join $vcs_dir $src]]
    } else {
        lappend resolved_sources $src
    }
}
set vsources_list $resolved_sources

set resolved_includes [list]
foreach inc $vincludes_list {
    if {[file pathtype $inc] eq "relative"} {
        lappend resolved_includes [file normalize [file join $vcs_dir $inc]]
    } else {
        lappend resolved_includes $inc
    }
}
set vincludes_list $resolved_includes

create_project -force kernel_pack $path_to_tmp_project

add_files -norecurse ${vsources_list}

set_property include_dirs ${vincludes_list} [current_fileset]
set_property verilog_define ${vdefines_list} [current_fileset]

set obj [get_filesets sources_1]
set_property -verbose -name "top" -value ${krnl_name} -objects $obj

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
ipx::package_project -root_dir $path_to_packaged -vendor xilinx.com -library RTLKernel -taxonomy /KernelIP -import_files -set_current false
ipx::unload_core $path_to_packaged/component.xml
ipx::edit_ip_in_project -upgrade true -name tmp_edit_project -directory $path_to_packaged $path_to_packaged/component.xml

set core [ipx::current_core]

set_property core_revision 2 $core
foreach up [ipx::get_user_parameters] {
    ipx::remove_user_parameter [get_property NAME $up] $core
}

# Associate bus interfaces with clock
ipx::associate_bus_interfaces -busif s_axi_ctrl -clock ap_clk $core
ipx::associate_bus_interfaces -busif m_axi_mem_0 -clock ap_clk $core

# =========================================================
# Register map — CUSTOMIZE THIS SECTION FOR YOUR DESIGN
# =========================================================
set mem_map    [::ipx::add_memory_map -quiet "s_axi_ctrl" $core]
set addr_block [::ipx::add_address_block -quiet "reg0" $mem_map]

# --- CTRL register (0x00) — ALWAYS INCLUDE AS-IS ---
set reg [::ipx::add_register "CTRL" $addr_block]
set_property description    "Control signals"    $reg
set_property address_offset 0x000 $reg
set_property size           32    $reg

set field [ipx::add_field AP_START $reg]
set_property ACCESS {read-write} $field
set_property BIT_OFFSET {0} $field
set_property BIT_WIDTH {1} $field
set_property DESCRIPTION {Control signal Register for 'ap_start'.} $field
set_property MODIFIED_WRITE_VALUE {modify} $field

set field [ipx::add_field AP_DONE $reg]
set_property ACCESS {read-only} $field
set_property BIT_OFFSET {1} $field
set_property BIT_WIDTH {1} $field
set_property DESCRIPTION {Control signal Register for 'ap_done'.} $field
set_property READ_ACTION {modify} $field

set field [ipx::add_field AP_IDLE $reg]
set_property ACCESS {read-only} $field
set_property BIT_OFFSET {2} $field
set_property BIT_WIDTH {1} $field
set_property DESCRIPTION {Control signal Register for 'ap_idle'.} $field
set_property READ_ACTION {modify} $field

set field [ipx::add_field AP_READY $reg]
set_property ACCESS {read-only} $field
set_property BIT_OFFSET {3} $field
set_property BIT_WIDTH {1} $field
set_property DESCRIPTION {Control signal Register for 'ap_ready'.} $field
set_property READ_ACTION {modify} $field

set field [ipx::add_field RESERVED_1 $reg]
set_property ACCESS {read-only} $field
set_property BIT_OFFSET {4} $field
set_property BIT_WIDTH {4} $field
set_property DESCRIPTION {Reserved.  0s on read.} $field
set_property READ_ACTION {modify} $field

set field [ipx::add_field RESERVED_2 $reg]
set_property ACCESS {read-only} $field
set_property BIT_OFFSET {8} $field
set_property BIT_WIDTH {24} $field
set_property DESCRIPTION {Reserved.  0s on read.} $field
set_property READ_ACTION {modify} $field

# --- GIER (0x04) — ALWAYS INCLUDE AS-IS ---
set reg [::ipx::add_register "GIER" $addr_block]
set_property description    "Global Interrupt Enable Register"    $reg
set_property address_offset 0x004 $reg
set_property size           32    $reg

# --- IP_IER (0x08) — ALWAYS INCLUDE AS-IS ---
set reg [::ipx::add_register "IP_IER" $addr_block]
set_property description    "IP Interrupt Enable Register"    $reg
set_property address_offset 0x008 $reg
set_property size           32    $reg

# --- IP_ISR (0x0C) — ALWAYS INCLUDE AS-IS ---
set reg [::ipx::add_register "IP_ISR" $addr_block]
set_property description    "IP Interrupt Status Register"    $reg
set_property address_offset 0x00C $reg
set_property size           32    $reg

# --- CUSTOM REGISTERS START HERE (0x10+) ---
# For each 64-bit address parameter:
#   set reg [::ipx::add_register -quiet "PARAM_NAME" $addr_block]
#   set_property address_offset 0x0XX $reg
#   set_property size           [expr {8*8}]   $reg
#
# For each 32-bit scalar parameter:
#   set reg [::ipx::add_register -quiet "PARAM_NAME" $addr_block]
#   set_property address_offset 0x0XX $reg
#   set_property size           32    $reg

# --- MEM_0 (memory bank association) — ALWAYS INCLUDE ---
# Place this AFTER all custom registers
set reg [::ipx::add_register -quiet "MEM_0" $addr_block]
set_property address_offset 0x0XX $reg  ;# adjust offset
set_property size           [expr {8*8}]   $reg
set regparam [::ipx::add_register_parameter ASSOCIATED_BUSIF $reg]
set_property value m_axi_mem_0 $regparam

set_property slave_memory_map_ref "s_axi_ctrl" [::ipx::get_bus_interfaces -of $core "s_axi_ctrl"]

set_property xpm_libraries {XPM_CDC XPM_MEMORY XPM_FIFO} $core
set_property sdx_kernel true $core
set_property sdx_kernel_type rtl $core
set_property supported_families { } $core
set_property auto_family_support_level level_2 $core

ipx::create_xgui_files $core
ipx::update_checksums $core
ipx::check_integrity -kernel $core
ipx::save_core $core
close_project -delete
```

---

## parse_vcs_list.tcl

```tcl
# Reusable TCL procedure to parse Verilog filelist files.

proc parse_vcs_list {flist_path} {
    set f [split [string trim [read [open $flist_path r]]] "\n"]
    set flist [list ]
    set dir_list [list ]
    set def_list [list ]
    foreach x $f {
        if {![string match "" $x]} {
            if {[string match "#*" $x]} {
                # comment line
            } elseif {[string match "+incdir+*" $x]} {
                set trimchars "+incdir+"
                set temp [string trimleft $x $trimchars]
                set expanded [subst $temp]
                lappend dir_list $expanded
            } elseif {[string match "+define+*" $x]} {
                set trimchars "+define+"
                set temp [string trimleft $x $trimchars]
                set expanded [subst $temp]
                lappend def_list $expanded
            } else {
                set expanded [subst $x]
                lappend flist $expanded
            }
        }
    }
    return [list $flist $dir_list $def_list]
}
```

This file is stable — no customization needed.

---

## AXI4-Lite Control Slave

See the working example at `00_workspace/99_fpge_example/rtl/vadd_ctrl.sv` for the complete implementation. Key structural elements:

- Write FSM: WSTATE_ADDR → WSTATE_DATA → WSTATE_RESP (3-state)
- Read FSM: RSTATE_ADDR → RSTATE_DATA → RSTATE_RESP (3-state, the DATA state is critical for registering mux output)
- Write strobe mask: expand `wstrb[i]` to `wmask[8*i +: 8]` for byte-level write enable
- `ap_start` cleared by `ap_ready` (not by software)
- ISR uses toggle-on-write semantics: `isr <= isr ^ wdata[1:0]`
- All custom registers use read-modify-write pattern: `reg <= (wdata & wmask) | (reg & ~wmask)`

---

## AXI4 Master Compute Core

The compute core FSM pattern for single-beat AXI4 transactions:

```
S_IDLE → S_READ_INPUT_0 → S_WAIT_READ_0 → S_READ_INPUT_1 → S_WAIT_READ_1 → ... → S_WRITE_OUTPUT → S_WAIT_WRITE → S_WAIT_BRESP → (loop or S_DONE)
```

Key AXI4 fixed signal assignments for single-beat, 512-bit transfers:
```verilog
assign m_axi_awlen    = 8'd0;       // 1 beat
assign m_axi_awsize   = 3'b110;     // 64 bytes (512 bits)
assign m_axi_awburst  = 2'b01;      // INCR
assign m_axi_awlock   = 2'b00;
assign m_axi_awcache  = 4'b0011;    // bufferable
assign m_axi_awprot   = 3'b000;
assign m_axi_awqos    = 4'b0000;
assign m_axi_awregion = 4'b0000;
assign m_axi_wstrb    = {(AXI_DATA_WIDTH/8){1'b1}};  // all bytes valid
assign m_axi_wlast    = 1'b1;       // always last (single beat)
// Same pattern for AR channel
```

AXI handshake pattern for reads:
```verilog
S_READ: begin
    m_axi_araddr  <= base_addr + offset;
    m_axi_arvalid <= 1'b1;
    state         <= S_WAIT_READ;
end

S_WAIT_READ: begin
    if (m_axi_arvalid && m_axi_arready) begin
        m_axi_arvalid <= 1'b0;
        m_axi_rready  <= 1'b1;
    end
    if (m_axi_rvalid && m_axi_rready) begin
        latched_data <= m_axi_rdata;
        m_axi_rready <= 1'b0;
        state        <= NEXT_STATE;
    end
end
```

AXI handshake pattern for writes (handles AW/W channel ordering):
```verilog
S_WRITE: begin
    m_axi_awaddr  <= base_addr + offset;
    m_axi_awvalid <= 1'b1;
    m_axi_wdata   <= computed_data;
    m_axi_wvalid  <= 1'b1;
    state         <= S_WAIT_WRITE;
end

S_WAIT_WRITE: begin
    if (m_axi_awvalid && m_axi_awready)
        m_axi_awvalid <= 1'b0;
    if (m_axi_wvalid && m_axi_wready)
        m_axi_wvalid <= 1'b0;
    if (~m_axi_awvalid && ~m_axi_wvalid) begin
        m_axi_bready <= 1'b1;
        state        <= S_WAIT_BRESP;
    end
end

S_WAIT_BRESP: begin
    if (m_axi_bvalid && m_axi_bready) begin
        m_axi_bready <= 1'b0;
        offset       <= offset + BEAT_BYTES;
        state        <= NEXT_STATE;
    end
end
```

---

## Top-Level Wrapper

Must be `.v` (Verilog). Instantiates the control slave and compute core, wiring control signals between them. See `00_workspace/99_fpge_example/rtl/vadd_kernel.v` for the complete port list and wiring pattern.

Key internal wires:
```verilog
wire        ap_start, ap_done, ap_idle, ap_ready;
wire [63:0] addr_param_0, addr_param_1, addr_param_2;
wire [31:0] scalar_param;
```

---

## Host Application

```cpp
#include <iostream>
#include <cstring>
#include <cstdlib>
#include <chrono>
#include <thread>

#include "experimental/xrt_device.h"
#include "experimental/xrt_bo.h"
#include "experimental/xrt_ip.h"

// Register offsets — must match control slave RTL
constexpr uint32_t REG_CTRL = 0x00;
// ... custom registers at 0x10+

// AP control bits
constexpr uint32_t AP_START = 0x1;
constexpr uint32_t AP_DONE  = 0x2;
constexpr uint32_t AP_IDLE  = 0x4;

int main(int argc, char* argv[]) {
    std::string xclbin_path = "build_hw/<KERNEL_NAME>.xclbin";
    // Parse arguments...

    try {
        // Open device and load bitstream
        auto device = xrt::device(0);
        auto uuid = device.load_xclbin(xclbin_path);
        auto ip = xrt::ip(device, uuid, "<KERNEL_NAME>");

        // Allocate device buffers on HBM (memory group 0)
        size_t buf_size = num_elements * sizeof(int32_t);
        auto bo_in  = xrt::bo(device, buf_size, 0);
        auto bo_out = xrt::bo(device, buf_size, 0);

        // Map, initialize, sync to device
        auto* ptr_in  = bo_in.map<int32_t*>();
        auto* ptr_out = bo_out.map<int32_t*>();
        // ... fill input data ...
        bo_in.sync(XCL_BO_SYNC_BO_TO_DEVICE);

        // Write registers
        uint64_t addr_in  = bo_in.address();
        uint64_t addr_out = bo_out.address();
        ip.write_register(REG_ADDR_IN_LO,  (uint32_t)(addr_in  & 0xFFFFFFFF));
        ip.write_register(REG_ADDR_IN_HI,  (uint32_t)(addr_in  >> 32));
        ip.write_register(REG_ADDR_OUT_LO, (uint32_t)(addr_out & 0xFFFFFFFF));
        ip.write_register(REG_ADDR_OUT_HI, (uint32_t)(addr_out >> 32));
        ip.write_register(REG_LENGTH, (uint32_t)num_elements);

        // Start kernel
        ip.write_register(REG_CTRL, AP_START);

        // Poll for completion (10 second timeout)
        auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(10);
        bool done = false;
        while (std::chrono::steady_clock::now() < deadline) {
            if (ip.read_register(REG_CTRL) & AP_DONE) { done = true; break; }
            std::this_thread::sleep_for(std::chrono::microseconds(100));
        }
        if (!done) { std::cerr << "ERROR: Kernel timed out!" << std::endl; return 1; }

        // Sync results back and verify
        bo_out.sync(XCL_BO_SYNC_BO_FROM_DEVICE);
        // ... compare ptr_out against expected values ...

    } catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << std::endl;
        return 1;
    }
}
```

Compile with:
```bash
g++ -std=c++17 -O2 -o host/<binary> host/host.cpp -I/opt/xilinx/xrt/include -L/opt/xilinx/xrt/lib -lxrt_coreutil -lpthread
```
