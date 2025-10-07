---
slug: riscv-privileged
title: 'The RISC-V Instruction Set Manual: Volume II: Privileged Architecture'
authors: [jiangsheng]
tags: [riscv]
---

<!-- truncate -->

## Machine-Level ISA, Version 1.13 {#machine}

## 机器级 ISA，版本 1.13

本章描述在机器模式（Machine mode，M-mode）下可用的机器级操作，该模式是 RISC-V 硬件线程（hart）中的最高特权模式。M 模式用于对硬件平台的底层访问，并且在复位时首先进入。M 模式还可用于实现那些直接在硬件中实现过于困难或成本过高的功能。RISC-V 机器级 ISA 包含一个通用核心，其扩展取决于所支持的其他特权级以及硬件实现的其他细节。

### Machine-Level CSRs

### 机器级 CSR

除本节所述的机器级 CSR（控制与状态寄存器）之外，M 模式代码可以访问较低特权级的所有 CSR。

#### Machine Trap-Vector Base-Address (`mtvec`) Register

#### 机器陷入向量基址（`mtvec`）寄存器

`mtvec` 寄存器是一个 MXLEN 位的 **WARL** 可读写寄存器，用于保存陷入向量配置，由向量基址（BASE）和向量模式（MODE）组成。

![mtvec.svg](_assets/svg/light/mtvec.svg#gh-light-mode-only)
![mtvec.svg](_assets/svg/dark/mtvec.svg#gh-dark-mode-only)

**`mtvec` MODE 字段编码。**

`mtvec` 寄存器必须始终实现，但其取值可以是只读的。若 `mtvec` 可写，其可取值集合可随实现而异。BASE 字段的取值必须始终按 4 字节边界对齐，且 MODE 设置可能对 BASE 的取值施加额外的对齐约束。注意，该 CSR 仅包含地址 BASE 的第 XLEN-1 到第 2 位；当作为地址使用时，低两位以零填充，从而得到始终按 4 字节边界对齐的 XLEN 位地址。

<a id="mtvec-mode"></a>

**`mtvec` MODE 字段编码。**

|        值 |      名称      | 描述                               |
|---------:|:------------:|:---------------------------------|
|        0 |  直接（Direct）  | 所有陷入将 `pc` 设为 BASE。              |
|        1 | 向量（Vectored） | 异步中断将 `pc` 设为 BASE+4&#215;cause。 |
| &#8805;2 |     ---      | **保留**                           |

MODE 字段的编码见「[`mtvec` MODE 字段编码](#mtvec-mode)」。当 MODE=Direct 时，进入机器模式的所有陷入都会将 `pc` 设为 BASE 字段中的地址。当 MODE=Vectored 时，进入机器模式的所有同步异常将 `pc` 设为 BASE 字段中的地址，而中断则将 `pc` 设为 BASE 字段中的地址加上中断原因号的四倍。例如，机器态定时器中断（见「 [陷入后机器异常原因（`mcause`）寄存器取值](#mcauses)」）会将 `pc` 设为 BASE+`0x1c`。

实现可针对不同模式采用不同的对齐约束。尤其是，MODE=Vectored 可能比 MODE=Direct 需要更严格的对齐约束。

#### Machine Trap Delegation (`medeleg` and `mideleg`) Registers

#### 机器陷入委派（`medeleg` 与 `mideleg`）寄存器

默认情况下，任意特权级发生的所有陷入都在机器模式处理，但机器态处理程序可以使用 MRET 指令（[从陷入返回指令](#otherpriv)）将陷入重定向回适当的特权级。为提高性能，实现可以在 `medeleg` 与 `mideleg` 中提供独立的可读写位，用以指示某些异常和中断应直接由较低特权级处理。机器异常委派寄存器（`medeleg`）是一个 64 位可读写寄存器。机器中断委派寄存器（`mideleg`）是一个 MXLEN 位可读写寄存器。

在具有 S 模式的硬件线程（hart）上，必须提供 `medeleg` 和 `mideleg` 寄存器；当在 `medeleg` 或 `mideleg` 中设置某一位时，发生于 S 模式或 U 模式的相应陷入将被委派给 S 模式的陷入处理程序。在不支持 S 模式的 hart 上，不应提供 `medeleg` 和 `mideleg` 寄存器。

当某个陷入被委派给 S 模式时，`scause` 寄存器会被写入陷入原因；`sepc` 寄存器会被写入发生陷入的指令的虚拟地址；`stval` 寄存器会被写入与异常相关的特定数据；`mstatus` 的 SPP 字段会被写入陷入发生时的有效特权级；`mstatus` 的 SPIE 字段会被写入陷入发生时 SIE 字段的值；并且 `mstatus` 的 SIE 字段会被清零。`mcause`、`mepc`、`mtval` 寄存器以及 `mstatus` 的 MPP 与 MPIE 字段不会被写入。

实现可以选择仅支持委派陷入的一个子集。可通过对每个位位置写入 1，然后读回 `medeleg` 或 `mideleg`，以确定哪些位会保持为 1，从而发现支持的委派位。

实现不得将 `medeleg` 的任何位固定为只读 1，即任何可被委派的同步陷入必须支持不被委派。类似地，实现不得将对应于机器级中断的 `mideleg` 中的任何位固定为只读 1（但可以对较低级别的中断如此处理）。

陷入不会从更高特权级转换到更低特权级。例如，若 M 态已将非法指令异常委派给 S 态，而 M 态软件随后执行了非法指令，则该陷入仍在 M 态处理，而不会被委派至 S 态。相对地，陷入可以“横向”发生。沿用该示例，若 M 态已将非法指令异常委派给 S 态，而 S 态软件随后执行了非法指令，则该陷入在 S 态处理。

被委派的中断会在委派者的特权级被屏蔽。例如，若通过设置 `mideleg`[5] 将监督定时器中断（STI）委派给 S 态，则在执行于 M 态时不会响应 STI。相对地，若 `mideleg`[5] 为清零，则可在任意模式下响应 STI，且无论当前模式为何，都会将控制权转移到 M 态。

![medeleg.svg](_assets/svg/light/medeleg.svg#gh-light-mode-only)
![medeleg.svg](_assets/svg/dark/medeleg.svg#gh-dark-mode-only)

**机器异常委派（`medeleg`）寄存器。**

`medeleg` 为「[陷入后机器异常原因（`mcause`）寄存器取值](#mcauses)」中列出的每个同步异常都分配了一个位位置，其位索引等于 `mcause` 寄存器返回的值（例如，设置第 8 位允许将用户态的环境调用委派给更低特权级的陷入处理程序）。

当 XLEN=32 时，`medelegh` 是一个 32 位可读写寄存器，别名映射 `medeleg` 的 63:32 位。XLEN=64 时不存在 `medelegh` 寄存器。

![mideleg.svg](_assets/svg/light/mideleg.svg#gh-light-mode-only)
![mideleg.svg](_assets/svg/dark/mideleg.svg#gh-dark-mode-only)

**机器中断委派（`mideleg`）寄存器。**

`mideleg` 保存各个中断的陷入委派位，其位布局与 `mip` 寄存器一致（例如，监督定时器中断挂起 STIP 的委派控制位位于第 5 位）。

对于不可能在较低特权级出现的异常，相应的 `medeleg` 位应为只读 0。特别地，`medeleg`[11] 为只读 0。

由于双重陷入不可委派，`medeleg`[16] 为只读 0。

#### Machine Interrupt (`mip` and `mie`) Registers

#### 机器中断（`mip` 与 `mie`）寄存器

`mip` 寄存器是一个 MXLEN 位可读写寄存器，包含中断挂起信息，而 `mie` 是相应的 MXLEN 位可读写寄存器，包含中断使能位。中断原因号 _i_（由 CSR `mcause` 报告，见「[机器异常原因（`mcause`）寄存器](#mcause)」）与 `mip` 与 `mie` 的第 _i_ 位一一对应。位 15:0 仅分配给标准中断原因，位 16 及以上保留给平台使用。

![mideleg.svg](_assets/svg/light/mideleg.svg#gh-light-mode-only)
![mideleg.svg](_assets/svg/dark/mideleg.svg#gh-dark-mode-only)

**机器中断挂起（`mip`）寄存器。**

![mideleg.svg](_assets/svg/light/mideleg.svg#gh-light-mode-only)
![mideleg.svg](_assets/svg/dark/mideleg.svg#gh-dark-mode-only)

**机器中断使能（`mie`）寄存器**

若满足以下全部条件，中断 _i_ 将陷入到机器模式（使特权级切换为机器模式）：(a) 当前特权级为 M 且 `mstatus` 中的 MIE 位置位，或当前特权级低于机器模式；(b) `mip` 与 `mie` 的第 _i_ 位均为 1；且 (c) 若存在 `mideleg` 寄存器，则 `mideleg` 的第 _i_ 位为 0。

上述导致中断陷入的条件，必须在中断在 `mip` 中变为挂起或不再挂起后的有界时间内完成求值，并且在执行 **x**RET 指令之后，或在对这些中断陷入条件明确依赖的 CSR（包括 `mip`、`mie`、`mstatus` 与 `mideleg`）进行显式写入之后，必须立即重新求值。

发往 M 模式的中断优先于发往较低特权级的任何中断。

`mip` 寄存器中的各独立位可以是可写的，也可以是只读的。当 `mip` 的第 _i_ 位是可写时，可通过向该位写 0 来清除挂起的中断 _i_。如果中断 _i_ 可能变为挂起，但 `mip` 的第 _i_ 位为只读，则实现必须提供其他机制来清除此挂起中断。

若某中断在实现中可能出现挂起，则 `mie` 中对应的位必须是可写的。`mie` 中不可写的位必须为只读 0。

`mip` 与 `mie` 的标准部分（位 15:0）格式分别如「[`mip` 的标准部分（位 15:0）](#mipreg-standard)」与「[`mie` 的标准部分（位 15:0）](#miereg-standard)」所示。

<a id="mipreg-standard"></a>

![mipreg-standard.svg](_assets/svg/light/mipreg-standard.svg#gh-light-mode-only)
![mipreg-standard.svg](_assets/svg/dark/mipreg-standard.svg#gh-dark-mode-only)

**`mip` 的标准部分（位 15:0）。**

<a id="miereg-standard"></a>

![miereg-standard.svg](_assets/svg/light/miereg-standard.svg#gh-light-mode-only)
![miereg-standard.svg](_assets/svg/dark/miereg-standard.svg#gh-dark-mode-only)

**`mie` 的标准部分（位 15:0）。**

`mip`.MEIP 与 `mie`.MEIE 分别是机器级外部中断的中断挂起位与中断使能位。`mip` 中的 MEIP 为只读，由平台特定的中断控制器置位与清零。

`mip`.MTIP 与 `mie`.MTIE 分别是机器定时器中断的中断挂起位与中断使能位。`mip` 中的 MTIP 为只读，通过写内存映射的机器模式定时器比较寄存器进行清除。

`mip`.MSIP 与 `mie`.MSIE 分别是机器级软件中断的中断挂起位与中断使能位。`mip` 中的 MSIP 为只读，其由对内存映射控制寄存器的访问写入，这些寄存器被远端硬件线程用于发出机器级核间中断。硬件线程也可使用相同的内存映射控制寄存器写自身的 MSIP 位。如果系统仅有一个硬件线程，或平台标准改为通过外部中断（MEI）投递机器级核间中断，则 `mip`.MSIP 与 `mie`.MSIE 均可为只读 0。

若未实现监督者模式，则 `mip` 的 SEIP、STIP、SSIP 与 `mie` 的 SEIE、STIE、SSIE 为只读 0。

若实现了监督者模式，则 `mip`.SEIP 与 `mie`.SEIE 分别是监督级外部中断的中断挂起位与中断使能位。`mip` 中的 SEIP 可写，M 模式软件可写此位以指示 S 模式存在一个外部中断挂起。此外，平台级中断控制器也可产生监督级外部中断。监督级外部中断的挂起状态由“软件可写 SEIP 位”与“来自外部中断控制器的信号”的逻辑或决定。当通过 CSR 指令读取 `mip` 时，写入目的寄存器 `rd` 的 SEIP 位值为软件可写位与外部中断控制器信号的逻辑或，但外部中断控制器的信号不用于计算写回至 SEIP 的值。只有软件可写的 SEIP 位参与 CSRRS 或 CSRRC 指令的读-改-写序列。

若实现了监督者模式，则 `mip`.STIP 与 `mie`.STIE 分别是监督级定时器中断的中断挂起位与中断使能位。`mip` 中的 STIP 可写，M 模式软件可以写此位以向 S 模式投递定时器中断。

若实现了监督者模式，则 `mip`.SSIP 与 `mie`.SSIE 分别是监督级软件中断的中断挂起位与中断使能位。`mip` 中的 SSIP 可写，也可由平台特定的中断控制器置为 1。

若实现了 Sscofpmf 扩展，则 `mip`.LCOFIP 与 `mie`.LCOFIE 分别是本地计数器溢出中断的中断挂起位与中断使能位。`mip` 中的 LCOFIP 为可读写，反映由于任一 <code>mhpmevent<strong>n</strong></code>.OF 位置位而产生的本地计数器溢出中断请求的发生。若未实现 Sscofpmf 扩展，则 `mip`.LCOFIP 与 `mie`.LCOFIE 为只读 0。

同时到达且发往 M 模式的多个中断按如下降序优先级处理：MEI、MSI、MTI、SEI、SSI、STI、LCOFI。

`mip` 与 `mie` 的受限视图分别作为监督级的 `sip` 与 `sie` 寄存器出现。若在 `mideleg` 寄存器中设置了相应位以将某个中断委派给 S 模式，则该中断会在 `sip` 寄存器中可见，并可通过 `sie` 寄存器进行屏蔽；否则，`sip` 与 `sie` 中对应位为只读 0。

#### Machine Scratch (`mscratch`) Register

#### 机器态临时寄存器（`mscratch`）寄存器

`mscratch` 寄存器是一个 MXLEN 位可读写寄存器，供机器模式使用。典型用法是保存指向机器态硬件线程（hart）本地上下文空间的指针，并在进入 M 态陷入处理程序时与某个用户寄存器交换。

![mscratch.svg](_assets/svg/light/mscratch.svg#gh-light-mode-only)
![mscratch.svg](_assets/svg/dark/mscratch.svg#gh-dark-mode-only)

**机器模式临时寄存器。**

#### Machine Exception Program Counter (`mepc`) Register

#### 机器异常程序计数器（`mepc`）寄存器

`mepc` 是一个 MXLEN 位可读写寄存器，其格式见「[机器异常程序计数器寄存器](#mepcreg)」。`mepc` 的最低位（`mepc[0]`）始终为 0。对于仅支持 IALIGN=32 的实现，最低两位（`mepc[1:0]`）始终为 0。

如果某实现允许通过更改 CSR `misa`（例如）在 IALIGN=16 与 IALIGN=32 之间切换，则每当 IALIGN=32 时，读取会对位 `mepc[1]` 做屏蔽，使其读为 0。MRET 指令进行的隐式读取同样会发生屏蔽。尽管被屏蔽，在 IALIGN=32 时 `mepc[1]` 仍是可写的。

`mepc` 是 **WARL** 寄存器，必须能够保存所有有效的虚拟地址；不要求能够保存所有可能的无效地址。在写入 `mepc` 之前，实现可以将一个无效地址转换为 `mepc` 能够保存的另一个无效地址。

当陷入进入 M 态时，`mepc` 会被写入发生中断或异常的那条指令的虚拟地址。除此之外，实现不会写入 `mepc`，但软件可显式写入。

<a id="mepcreg"></a>

![mepcreg.svg](_assets/svg/light/mepcreg.svg#gh-light-mode-only)
![mepcreg.svg](_assets/svg/dark/mepcreg.svg#gh-dark-mode-only)

**机器异常程序计数器寄存器。**

#### Machine Cause (`mcause`) Register {#mcause}

#### 机器异常原因（`mcause`）寄存器

`mcause` 寄存器是一个 MXLEN 位可读写寄存器，其格式见「[机器异常原因（`mcause`）寄存器](#mcausereg)」。当陷入进入 M 态时，`mcause` 会被写入一个指示导致此次陷入事件的编码。除此之外，实现不会写入 `mcause`，但软件可显式写入。

若陷入由中断引发，则 `mcause` 寄存器中的中断位（Interrupt bit）会被置位。异常编码（Exception Code）字段包含用于标识最近一次异常或中断的编码。「[陷入后机器异常原因（`mcause`）寄存器取值](#mcauses)」列出了可能的机器级异常编码。异常编码字段为 **WLRL** 字段，因此仅保证能保存受支持的异常编码。

<a id="mcausereg"></a>

![mcausereg.svg](_assets/svg/light/mcausereg.svg#gh-light-mode-only)
![mcausereg.svg](_assets/svg/dark/mcausereg.svg#gh-dark-mode-only)

**机器异常原因（`mcause`）寄存器。**

注意，载入（load）与预留载入（load-reserved）指令会产生载入异常，而存储（store）、条件存储（store-conditional）与 AMO 指令会产生存储/AMO 异常。

如果一条指令可能引发多个同步异常，则应按照「[同步异常优先级（降序）](#exception-priority)」中给出的降序优先级选择要被处理并记录到 `mcause` 的异常。任何自定义同步异常的优先级由实现自行定义。

<a id="mcauses"></a>

**陷入后机器异常原因（`mcause`）寄存器取值。**

| Interrupt | Exception Code | Description   |
|----------:|---------------:|:--------------|
|         1 |              0 | **保留**        |
|         1 |              1 | 监督软件中断        |
|         1 |              2 | **保留**        |
|         1 |              3 | 机器软件中断        |
|         1 |              4 | **保留**        |
|         1 |              5 | 监督定时器中断       |
|         1 |              6 | **保留**        |
|         1 |              7 | 机器定时器中断       |
|         1 |              8 | **保留**        |
|         1 |              9 | 监督外部中断        |
|         1 |             10 | **保留**        |
|         1 |             11 | 机器外部中断        |
|         1 |             12 | **保留**        |
|         1 |             13 | 本地计数器溢出中断     |
|         1 |          14-15 | **保留**        |
|         1 |      &#8805;16 | **指定用于平台使用**  |
|         0 |              0 | 指令地址未对齐       |
|         0 |              1 | 指令访问错误        |
|         0 |              2 | 非法指令          |
|         0 |              3 | 断点            |
|         0 |              4 | 载入地址未对齐       |
|         0 |              5 | 载入访问错误        |
|         0 |              6 | 存储/AMO 地址未对齐  |
|         0 |              7 | 存储/AMO 访问错误   |
|         0 |              8 | 来自 U 模式的环境调用  |
|         0 |              9 | 来自 S 模式的环境调用  |
|         0 |             10 | **保留**        |
|         0 |             11 | 来自 M 模式的环境调用  |
|         0 |             12 | 指令页故障         |
|         0 |             13 | 载入页故障         |
|         0 |             14 | **保留**        |
|         0 |             15 | 存储/AMO 页故障    |
|         0 |             16 | 双重陷入          |
|         0 |             17 | **保留**        |
|         0 |             18 | 软件检查异常        |
|         0 |             19 | 硬件错误          |
|         0 |          20-23 | **保留**        |
|         0 |          24-31 | **指定用于自定义使用** |
|         0 |          32-47 | **保留**        |
|         0 |          48-63 | **指定用于自定义使用** |
|         0 |      &#8805;64 | **保留**        |

<a id="exception-priority"></a>

**同步异常优先级（降序）。**

| Priority |     Exc.Code | Description       |
|:---------|-------------:|:------------------|
| **最高**   |            3 | 指令地址断点            |
|          |              | 在指令地址翻译期间：        |
|          |        12, 1 | 首先遇到的页故障或访问错误     |
|          |              | 针对指令的物理地址：        |
|          |            1 | 指令访问错误            |
|          |            2 | 非法指令              |
|          |            0 | 指令地址未对齐           |
|          |     8, 9, 11 | 环境调用              |
|          |            3 | 环境断点              |
|          |            3 | 载入/存储/AMO 地址断点    |
|          |              | 可选：               |
|          |         4, 6 | 载入/存储/AMO 地址未对齐   |
|          |              | 在对显式内存访问进行地址翻译期间： |
|          | 13, 15, 5, 7 | 首先遇到的页故障或访问错误     |
|          |              | 针对显式内存访问的物理地址：    |
|          |         5, 7 | 载入/存储/AMO 访问错误    |
|          |              | 若未被更高优先级覆盖：       |
| **最低**   |         4, 6 | 载入/存储/AMO 地址未对齐   |

当一个虚拟地址被翻译为物理地址时，地址翻译算法决定可能引发哪一种具体异常。

载入/存储/AMO 地址未对齐异常的优先级相对于载入/存储/AMO 页故障与访问错误异常，可以更高也可以更低。

#### Machine Trap Value (`mtval`) Register

#### 机器陷入值（`mtval`）寄存器

`mtval` 寄存器是一个 MXLEN 位可读写寄存器，其格式见「[机器陷入值（`mtval`）寄存器](#mtvalreg)」。当陷入进入 M 态时，`mtval` 要么被写为 0，要么被写入与异常相关的特定信息，以帮助软件处理此次陷入。除此之外，实现不会写入 `mtval`，但软件可显式写入。硬件平台会规定哪些异常必须向 `mtval` 提供信息、哪些异常可以无条件写为 0、以及哪些异常可根据底层事件选择上述任一行为。如果硬件平台规定没有任何异常会向 `mtval` 写入非零值，则 `mtval` 为只读 0。

当在取指、载入或存储过程中发生断点、地址未对齐、访问错误或页故障异常且 `mtval` 被写入非零值时，`mtval` 将包含导致错误的虚拟地址。

当启用基于页的虚拟内存时，即便是物理内存访问错误异常，`mtval` 也会被写入导致错误的虚拟地址。该设计可降低大多数实现的数据通路成本，尤其是具备硬件页表遍历器的实现。

<a id="mtvalreg"></a>

![mtvalreg.svg](_assets/svg/light/mtvalreg.svg#gh-light-mode-only)
![mtvalreg.svg](_assets/svg/dark/mtvalreg.svg#gh-dark-mode-only)

**机器陷入值（`mtval`）寄存器。**

当一次未对齐的载入或存储导致访问错误或页故障异常且 `mtval` 被写入非零值时，`mtval` 将包含导致错误的那一部分访问的虚拟地址。

当在具有变长指令的硬件线程上发生指令访问错误或页故障异常且 `mtval` 被写入非零值时，`mtval` 将包含导致错误的那部分指令的虚拟地址，而 `mepc` 将指向该指令的起始位置。

`mtval` 寄存器还可以选择性地用于在非法指令异常时返回出错指令的指令位（`mepc` 指向内存中该出错指令）。若在非法指令异常发生时 `mtval` 被写入非零值，则 `mtval` 将包含以下三者中最短者：

- 实际的出错指令
- 出错指令的前 ILEN 位
- 出错指令的前 MXLEN 位

在非法指令异常中装载到 `mtval` 的值是右对齐的，所有未使用的高位清零。

当陷由于“软件检查异常”而产生时，`mtval` 寄存器保存该异常的原因。定义如下编码：

- 0 - 未提供信息。
- 2 - 着陆垫故障（Landing Pad Fault）。由 Zicfilp 扩展定义。
- 3 - 影子栈故障（Shadow Stack Fault）。由 Zicfiss 扩展定义。

对于其他陷入，`mtval` 被置为 0，但未来标准可能会重新定义 `mtval` 在其他陷入下的取值。

如果 `mtval` 不是只读 0，则它是 **WARL** 寄存器，必须能够保存所有有效的虚拟地址以及数值 0；不要求能够保存所有可能的无效地址。在写入 `mtval` 之前，实现可以将一个无效地址转换为 `mtval` 能够保存的另一个无效地址。若实现了返回出错指令位的特性，`mtval` 还必须能保存所有小于 2<sup><strong>N</strong></sup> 的值，其中 _N_ 为 MXLEN 与 ILEN 中较小者。

### Machine-Mode Privileged Instructions

### 机器态特权指令

#### Environment Call and Breakpoint

#### 环境调用与断点

![mm-env-call.svg](_assets/svg/light/mm-env-call.svg#gh-light-mode-only)
![mm-env-call.svg](_assets/svg/dark/mm-env-call.svg#gh-dark-mode-only)

ECALL 指令用于向支撑的执行环境发起请求。当在 U 模式、S 模式或 M 模式下执行时，分别产生“来自 U 模式的环境调用异常”“来自 S 模式的环境调用异常”或“来自 M 模式的环境调用异常”，且不执行其他操作。

EBREAK 指令由调试器使用，用于将控制权转移回调试环境。除非被外部调试环境改写，否则 EBREAK 将引发断点异常，且不执行其他操作。

ECALL 与 EBREAK 会使接收特权级的 `epc` 寄存器被设置为 ECALL 或 EBREAK 指令自身的地址，而非其后一条指令的地址。由于 ECALL 与 EBREAK 会引发同步异常，它们不被视为已退役，且不应使 `minstret` CSR 递增。

#### Trap-Return Instructions {#otherpriv}

#### 从陷入返回指令

用于从陷入返回的指令在 PRIV 次操作码下编码。

![trap-return.svg](_assets/svg/light/trap-return.svg#gh-light-mode-only)
![trap-return.svg](_assets/svg/dark/trap-return.svg#gh-dark-mode-only)

为在处理陷入后返回，每个特权级分别提供了从陷入返回指令：MRET 与 SRET。MRET 始终提供；若支持监督者模式，则必须提供 SRET，否则应引发非法指令异常。当 `mstatus` 中 TSR=1 时，SRET 也应引发非法指令异常，详见「Virtualization Support in `mstatus` Register」。**x**RET 指令可在特权级 _x_ 或更高特权级执行；在更高特权级执行较低特权级的 **x**RET 将弹出相应较低特权级的中断使能与特权级栈。尝试在低于 _x_ 的特权级执行 **x**RET 会引发非法指令异常。除按「Privilege and Global Interrupt-Enable Stack in `mstatus` register」所述操作特权栈之外，**x**RET 还会将 `pc` 设为 <code><strong>x</strong>epc</code> 寄存器中保存的值。

若支持 A 扩展，**x**RET 指令允许清除任何尚未完成的 LR 地址预留，但并非必须清除。若需要，陷入处理程序应在执行 **x**RET 前显式清除该预留（例如使用一次空操作的 SC）。

#### Wait for Interrupt {#wfi}

#### 等待中断（WFI）

等待中断指令（WFI）告知实现：当前硬件线程（hart）可被挂起，直到可能需要服务某个中断。执行 WFI 也可用于告知硬件平台：应优先将合适的中断路由至该硬件线程。WFI 在所有特权级均可用，并可选择性地在 U 模式可用。当 `mstatus` 中 TW=1 时，该指令可能引发非法指令异常，详见「Virtualization Support in `mstatus` Register」。

![wfi.svg](_assets/svg/light/wfi.svg#gh-light-mode-only)
![wfi.svg](_assets/svg/dark/wfi.svg#gh-dark-mode-only)

若在硬件线程挂起期间有一个已使能的中断已挂起或随后变为挂起，则将在下一条指令处进入该中断的陷入处理，即执行从陷入处理程序处恢复，且 `mepc` = `pc`+4。

即便没有任何已使能的中断变为挂起，实现也允许因任何原因恢复执行。因此，将 WFI 实现为一个 NOP（空操作）也是合法实现。

在中断被禁用时也可以执行 WFI。WFI 的行为不得受 `mstatus` 中全局中断位（MIE 与 SIE）以及委派寄存器 `mideleg` 的影响（即：即使某个中断已被委派到更低特权级，只要本地使能且变为挂起，硬件线程也必须恢复）；但应遵循各个单独中断的使能位（例如 MTIE）（即：若某中断已挂起但未单独使能，实现应避免恢复硬件线程）。无论各特权级的全局中断使能为何，WFI 还要求对任一特权级上本地已使能且挂起的中断恢复执行。

如果导致硬件线程恢复执行的事件并未引发中断进入，则执行将在 `pc`+4 处继续，软件必须自行决定后续动作，包括在没有可处理事件时回跳并重试 WFI。

## Supervisor-Level ISA

### Supervisor Instructions

#### Supervisor Memory-Management Fence Instruction

![sfencevma.svg](_assets/svg/light/sfencevma.svg#gh-light-mode-only)
![sfencevma.svg](_assets/svg/dark/sfencevma.svg#gh-dark-mode-only)

监控器内存管理屏障指令 `SFENCE.VMA`
用于将对内存中存储的内存管理数据结构的更新与当前执行进行同步。指令执行会隐式地读取并写入这些数据结构，但这些隐式引用通常不与显式的加载和存储操作排序。执行
`SFENCE.VMA` 能保证：在同一 RISC-V hart 中，任何先前对这些数据结构已可见的存储操作会先于后续对这些数据结构的隐式引用。`rs1`
和 `rs2` 的值决定 `SFENCE.VMA` 所排序的具体操作范围（如下所述）。`SFENCE.VMA`
同时还会使与该 hart 关联的地址转换缓存条目失效（参见第
10.3.2 节）。更多关于此指令行为的细节，参见第 3.1.6.5 节和第 3.7.2 节。

`SFENCE.VMA` 只会对本 hart 的数据结构隐式引用进行排序。

如果只修改单个地址对应的页或超级页，`rs1` 可指定该虚拟地址以只对该映射执行转换屏障。若只修改了
`ASID`（单个地址空间标识符），`rs2` 可指定相应地址空间。`SFENCE.VMA` 根据 `rs1` 和
`rs2` 的值来决定行为：

- 如果 `rs1=x0` 且 `rs2=x0`，则该屏障会对所有地址空间中任意级别页表的所有读写操作进行排序，并使所有地址空间的地址转换缓存条目失效。
- 如果 `rs1=x0` 且 `rs2≠x0`，则该屏障只对由整数寄存器 `rs2`
  指定的地址空间中任意级别页表的所有读写操作进行排序（不包含全局映射
  global 条目的访问），并使该地址空间的所有非全局地址转换缓存条目失效。
- 如果 `rs1≠x0` 且 `rs2=x0`，则该屏障只对所有地址空间中与 `rs1`
  对应虚拟地址相关的页表叶子条目的读写操作进行排序，并使所有地址空间中与该虚拟地址相关的翻译缓存条目失效。
- 如果 `rs1≠x0` 且 `rs2≠x0`，则该屏障只对由整数寄存器 `rs2` 指定的地址空间中、与
  `rs1`
  对应虚拟地址相关的页表叶子条目的读写操作进行排序（不包含全局映射 global
  条目的访问），并使该地址空间中与该虚拟地址相关的非全局翻译缓存条目失效。

若 `rs1` 中的值并非有效虚拟地址，`SFENCE.VMA` 不产生任何效果，也不会引发异常。

当 `rs2≠x0` 时，其高位中的一些保留位目前还未规范使用。在未定义使用前，软件应将其清零，硬件实现可忽略它们。若
`ASIDLEN<ASIDMAX`，则实现会忽略超出 `ASIDLEN` 但小于 `ASIDMAX` 的那部分位。

实现可能对自上次可涵盖该地址的 `SFENCE.VMA` 以来，任何时候都曾经有效的地址使用任何翻译。`SFENCE.VMA`
的排序并不会让对内存管理数据结构的隐式读写与标准 RVWMO 规则相互完全契合。例如，尽管
`SFENCE.VMA`
排序了先前显式访问与后续隐式访问之间的关系，但并不保证先前显式访问在全局内存顺序上必然先于后续显式访问。此外，这些隐式读不一定遵循常规程序次序规则。

实现只能对当前 `satp` 寄存器所指向的页表以及其后续有效 `V=1`
的表项执行隐式读取，并且只能对指令执行产生的隐式访问（而非推测式访问）引发异常。

`sstatus` 寄存器中的 `SUM` 和 `MXR` 位的更改立即生效，无需执行 `SFENCE.VMA`。将
`satp.MODE` 从
`Bare` 改为其它模式或反向也即刻生效，无需 `SFENCE.VMA`。同样地，更改 `satp.ASID`
也会立即生效。

若某个 hart 使用地址转换缓存，则该缓存应被视为此 hart 私有；`ASID` 在各 hart
之间并无一致含义。OS 可以选择在不同 hart 上用相同
`ASID` 代表不同地址空间，或利用其他机制管理 `ASID`。

对于将 `satp.MODE` 固定为零（即一直 `Bare`）的实现，尝试执行 `SFENCE.VMA`
指令可能会触发非法指令异常。
