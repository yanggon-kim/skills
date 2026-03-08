# XRT RTL Kernel Contract

## Top-Level Port Specification

Every XRT RTL kernel must have these exact port groups. Parameter names and widths are configurable but the naming convention must be followed.

### Required Parameters
```verilog
parameter C_S_AXI_CTRL_ADDR_WIDTH = 7,      // 7 bits = 128 bytes of register space
parameter C_S_AXI_CTRL_DATA_WIDTH = 32,      // Always 32-bit for control
parameter C_M_AXI_MEM_0_ADDR_WIDTH = 64,     // 64-bit addressing for HBM
parameter C_M_AXI_MEM_0_DATA_WIDTH = 512,    // 512-bit data bus (16 x 32-bit elements)
parameter C_M_AXI_MEM_0_ID_WIDTH   = 1       // Minimal ID width
```

### Required System Signals
```verilog
input  wire  ap_clk,      // System clock (300 MHz on U55C)
input  wire  ap_rst_n,    // Active-low reset
output wire  interrupt     // Interrupt to host (active high)
```

### AXI4-Lite Slave Interface (s_axi_ctrl)

Host-to-kernel control. All signals must be prefixed with `s_axi_ctrl_`.

```verilog
// Write address channel
input  wire                                s_axi_ctrl_awvalid,
output wire                                s_axi_ctrl_awready,
input  wire [C_S_AXI_CTRL_ADDR_WIDTH-1:0]  s_axi_ctrl_awaddr,

// Write data channel
input  wire                                s_axi_ctrl_wvalid,
output wire                                s_axi_ctrl_wready,
input  wire [C_S_AXI_CTRL_DATA_WIDTH-1:0]  s_axi_ctrl_wdata,
input  wire [C_S_AXI_CTRL_DATA_WIDTH/8-1:0] s_axi_ctrl_wstrb,

// Write response channel
output wire                                s_axi_ctrl_bvalid,
input  wire                                s_axi_ctrl_bready,
output wire [1:0]                          s_axi_ctrl_bresp,

// Read address channel
input  wire                                s_axi_ctrl_arvalid,
output wire                                s_axi_ctrl_arready,
input  wire [C_S_AXI_CTRL_ADDR_WIDTH-1:0]  s_axi_ctrl_araddr,

// Read data channel
output wire                                s_axi_ctrl_rvalid,
input  wire                                s_axi_ctrl_rready,
output wire [C_S_AXI_CTRL_DATA_WIDTH-1:0]  s_axi_ctrl_rdata,
output wire [1:0]                          s_axi_ctrl_rresp,
```

### AXI4 Master Interface (m_axi_mem_0)

Kernel-to-HBM data path. All signals must be prefixed with `m_axi_mem_0_`.

```verilog
// Write address channel
output wire [C_M_AXI_MEM_0_ID_WIDTH-1:0]    m_axi_mem_0_awid,
output wire [C_M_AXI_MEM_0_ADDR_WIDTH-1:0]  m_axi_mem_0_awaddr,
output wire [7:0]                            m_axi_mem_0_awlen,
output wire [2:0]                            m_axi_mem_0_awsize,
output wire [1:0]                            m_axi_mem_0_awburst,
output wire [1:0]                            m_axi_mem_0_awlock,
output wire [3:0]                            m_axi_mem_0_awcache,
output wire [2:0]                            m_axi_mem_0_awprot,
output wire [3:0]                            m_axi_mem_0_awqos,
output wire [3:0]                            m_axi_mem_0_awregion,
output wire                                  m_axi_mem_0_awvalid,
input  wire                                  m_axi_mem_0_awready,

// Write data channel
output wire [C_M_AXI_MEM_0_DATA_WIDTH-1:0]    m_axi_mem_0_wdata,
output wire [C_M_AXI_MEM_0_DATA_WIDTH/8-1:0]  m_axi_mem_0_wstrb,
output wire                                    m_axi_mem_0_wlast,
output wire                                    m_axi_mem_0_wvalid,
input  wire                                    m_axi_mem_0_wready,

// Write response channel
input  wire [C_M_AXI_MEM_0_ID_WIDTH-1:0]  m_axi_mem_0_bid,
input  wire [1:0]                          m_axi_mem_0_bresp,
input  wire                                m_axi_mem_0_bvalid,
output wire                                m_axi_mem_0_bready,

// Read address channel
output wire [C_M_AXI_MEM_0_ID_WIDTH-1:0]    m_axi_mem_0_arid,
output wire [C_M_AXI_MEM_0_ADDR_WIDTH-1:0]  m_axi_mem_0_araddr,
output wire [7:0]                            m_axi_mem_0_arlen,
output wire [2:0]                            m_axi_mem_0_arsize,
output wire [1:0]                            m_axi_mem_0_arburst,
output wire [1:0]                            m_axi_mem_0_arlock,
output wire [3:0]                            m_axi_mem_0_arcache,
output wire [2:0]                            m_axi_mem_0_arprot,
output wire [3:0]                            m_axi_mem_0_arqos,
output wire [3:0]                            m_axi_mem_0_arregion,
output wire                                  m_axi_mem_0_arvalid,
input  wire                                  m_axi_mem_0_arready,

// Read data channel
input  wire [C_M_AXI_MEM_0_ID_WIDTH-1:0]    m_axi_mem_0_rid,
input  wire [C_M_AXI_MEM_0_DATA_WIDTH-1:0]  m_axi_mem_0_rdata,
input  wire [1:0]                            m_axi_mem_0_rresp,
input  wire                                  m_axi_mem_0_rlast,
input  wire                                  m_axi_mem_0_rvalid,
output wire                                  m_axi_mem_0_rready,
```

## Register Map Specification

The AXI4-Lite register space must follow the XRT kernel register map convention. The first 0x10 bytes are reserved for the standard AP control and interrupt registers. Custom kernel arguments start at offset 0x10.

### Standard Registers (0x00-0x0C)

| Offset | Name    | Description |
|--------|---------|-------------|
| 0x00   | AP_CTRL | bit[0]=ap_start (RW), bit[1]=ap_done (RO), bit[2]=ap_idle (RO), bit[3]=ap_ready (RO) |
| 0x04   | GIER    | Global Interrupt Enable (bit[0]) |
| 0x08   | IP_IER  | IP Interrupt Enable (bit[0]=done, bit[1]=ready) |
| 0x0C   | IP_ISR  | IP Interrupt Status (toggle-on-write to clear) |

### Custom Registers (0x10+)

Lay out buffer addresses and parameters starting at 0x10. Each 64-bit address takes two consecutive 32-bit registers (LO at offset, HI at offset+4).

Example layout for a 3-buffer design:
| Offset | Name     | Width | Description |
|--------|----------|-------|-------------|
| 0x10   | ADDR_A_LO | 32  | Buffer A address low 32 bits |
| 0x14   | ADDR_A_HI | 32  | Buffer A address high 32 bits |
| 0x18   | ADDR_B_LO | 32  | Buffer B address low 32 bits |
| 0x1C   | ADDR_B_HI | 32  | Buffer B address high 32 bits |
| 0x20   | ADDR_C_LO | 32  | Buffer C address low 32 bits |
| 0x24   | ADDR_C_HI | 32  | Buffer C address high 32 bits |
| 0x28   | LENGTH    | 32  | Number of elements |

### Memory Bank Association Register

After all custom registers, add a MEM_0 register with an `ASSOCIATED_BUSIF` parameter. This tells XRT which AXI master interface maps to which memory bank.

```
0x30   MEM_0     64-bit    ASSOCIATED_BUSIF = m_axi_mem_0
```

## IP Packaging Requirements

### package_kernel.tcl Must:
1. Associate `s_axi_ctrl` and `m_axi_mem_0` bus interfaces with `ap_clk`
2. Set `sdx_kernel = true` and `sdx_kernel_type = rtl`
3. Set `auto_family_support_level = level_2`
4. Set `xpm_libraries = {XPM_CDC XPM_MEMORY XPM_FIFO}`
5. Define the complete register map with fields matching the RTL control slave
6. Set `slave_memory_map_ref` for the control interface
7. Run `ipx::check_integrity -kernel` and verify it passes

### v++ Linking Flags
```
--link --target hw --platform xilinx_u55c_gen3x16_xdma_3_202210_1
--save-temps --no_ip_cache
--connectivity.sp <kernel_name>_1.m_axi_mem_0:HBM[0:31]
--optimize 3
--report_level 2
```

## AP Control Handshake Protocol

```
Host writes ap_start=1 → Core sees ap_start, deasserts ap_idle, begins work
Core finishes → Asserts ap_done=1, ap_ready=1, ap_idle=1 (all in same cycle)
Core transitions to IDLE → ap_done STAYS HIGH until next ap_start
Host polls and sees ap_done=1 → Reads results
Host writes ap_start=1 for next run → Core clears ap_done, begins new work
```

The critical requirement is that `ap_done` must persist (not be a single-cycle pulse). The host polls over PCIe which has microsecond-scale latency, so a single-cycle pulse will be missed.
