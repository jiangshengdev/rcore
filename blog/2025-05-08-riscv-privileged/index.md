---
slug: riscv-privileged
title: 'The RISC-V Instruction Set Manual: Volume II: Privileged Architecture'
authors: [jiangsheng]
tags: [riscv]
---

<!-- truncate -->

## Machine-Level ISA, Version 1.13

## 机器级 ISA，版本 1.13

### Machine-Mode Privileged Instructions

### 机器态特权指令

#### Wait for Interrupt

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
