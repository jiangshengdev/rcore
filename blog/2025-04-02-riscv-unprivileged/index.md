---
slug: riscv-unprivileged
title: RISC-V Unprivileged
authors: [jiangsheng]
tags: [riscv]
---

记录学习 RISC-V Unprivileged 的一些笔记。

<!-- truncate -->

## "Zifencei" Extension for Instruction-Fetch Fence

本章定义了「Zifencei」扩展，其中包含 `FENCE.I`
指令。该指令为同一硬件线程（hart）上的指令存储器写入操作与指令获取操作之间提供显式同步。目前，
`FENCE.I` 是唯一的标准机制，可确保一个关键一致性：任何对 hart 可见的存储操作，必须对其自身的指令获取也可见。

![FENCE.I.svg](image/light/FENCE.I.svg#gh-light-mode-only)
![FENCE.I.svg](image/dark/FENCE.I.svg#gh-dark-mode-only)

`FENCE.I` 指令的核心功能是同步指令流和数据流的可见性。RISC-V 架构默认不保证对指令存储器的写入操作在 hart 执行 `FENCE.I`
之前对其自身的指令获取可见。执行 `FENCE.I` 后，该 hart 的后续指令获取将能够看到所有先前对其可见的数据存储。然而，在多处理器系统中，
`FENCE.I` 并不保证其他 hart 的指令获取能够观察到本地 hart 的存储。如果需要使对指令存储器的写入对所有 RISC-V hart 全局可见，写入方
hart 必须遵循以下协议：首先执行一条数据流 `FENCE` 指令，以确保写入对其他 hart 可见，然后请求所有远程 hart 执行各自的
`FENCE.I` 指令。

## "A" Extension for Atomic Instructions

### Specifying Ordering of Atomic Instructions

基础 RISC-V ISA 采用宽松的内存模型，通过使用 `FENCE` 指令来施加额外的顺序约束。执行环境将地址空间分为内存域和 I/O 域，
`FENCE` 指令可以对这两个地址域之一或二者进行访问排序。

为了更高效地支持释放一致性（Gharachorloo 等，1990），每条原子指令包含两个位：`aq` 和 `rl`，它们可为其他 RISC-V hart
提供额外的内存排序约束。根据原子指令访问的是内存域还是 I/O
域，这两个位会对其中一个域的访问进行排序，对另一个域则无顺序限制；若需要对这两个域都进行排序，可以使用
`FENCE` 指令。

当这两个位都为 0 时，不对原子内存操作施加额外的顺序约束。若只设置 `aq`
位，则该原子内存操作被视为获取（acquire）访问，即在该原子内存操作完成之前，本
hart 不会观察到后续的内存操作。若只设置 `rl` 位，则该原子内存操作被视为释放（release）访问，即本 hart
不会观察到该释放操作在任何早先的内存操作之前完成。若 `aq` 和 `rl`
均被设置，则该原子内存操作具有顺序一致性，不会在任意早先内存操作之前或任意后续内存操作之后被观察到（仅限同一
RISC-V hart，且针对同一地址域）。

### "Zalrsc" Extension for Load-Reserved/Store-Conditional Instructions

![Load-Reserved_Store-Conditional.svg](image/light/Load-Reserved_Store-Conditional.svg#gh-light-mode-only)
![Load-Reserved_Store-Conditional.svg](image/dark/Load-Reserved_Store-Conditional.svg#gh-dark-mode-only)

对单个内存字或双字进行复杂原子内存操作时，需使用 `LR`（加载保留，Load-Reserved）和 `SC`
（条件存储，Store-Conditional）指令。`LR.W` 从 `rs1`
中的地址加载一个字，将符号扩展后的值存入 `rd`，并注册保留集 —— 该字节集合包含被寻址字中的所有字节。`SC.W` 有条件地将 `rs2`
中的字写入 `rs1` 中的地址：仅当保留仍然有效且保留集包含被写入的字节时，`SC.W` 才会成功。若 `SC.W` 成功，则将 `rs2`
中的字写入内存，并将 0 写入 `rd`；若失败，则不写入内存，并将非零值写入 `rd`。出于内存保护目的，失败的 `SC.W`
可能被视为存储操作。无论成功与否，执行 `SC.W` 指令都会使当前 hart 持有的所有保留失效。`LR.D` 和 `SC.D` 对双字进行类似操作，仅在
RV64 中可用。对于 RV64，`LR.W` 和 `SC.W` 会对存入 `rd` 的值进行符号扩展。

值为 1 的失败编码表示未指定的失败原因。其他失败编码当前保留。可移植软件应仅假设失败编码为非零值。

对于 `LR` 和 `SC`，「Zalrsc」扩展要求 `rs1` 中的地址必须按操作数大小自然对齐（即双字需 8 字节对齐，字需 4
字节对齐）。如果地址未自然对齐，将产生地址不对齐异常或访问故障异常。对于本可完成但因未对齐而不应被模拟的内存访问，可能产生访问故障异常。

实现可以为每个 `LR` 注册任意大小的保留集，只要该保留集包含被寻址数据字或双字的所有字节。在程序顺序中，`SC` 只能与最近的
`LR` 配对。`SC` 成功需满足：在 `LR` 和 `SC` 之间未观察到其他 hart 对保留集的存储操作，且在程序顺序中 `LR` 和 `SC` 之间没有其他
`SC` 操作；同时需满足：在 `LR` 和 `SC` 之间未观察到非 hart 设备对 `LR` 指令访问字节的写入。注意此 `LR`
可能具有不同的有效地址和数据大小，但将`SC` 的地址作为保留集的一部分进行了保留。

`SC` 必须失败的情形包括：地址不在程序顺序中最近 `LR` 的保留集内；在 `LR` 和 `SC` 之间观察到其他 hart 对保留集的存储操作；在
`LR` 和 `SC` 之间观察到其他设备对 `LR` 访问字节的写入（若设备写入了保留集但未写入 `LR` 访问的字节，`SC` 可能失败或成功）；在程序顺序中
`LR` 和 `SC` 之间存在其他 `SC`（无论地址如何）。成功 `LR/SC` 序列的原子性要求的精确定义参见第 18.1 节的「Atomicity Axiom」。

在建立保留的 `LR` 指令之前，其他 RISC-V hart 无法观察到 `SC` 指令。

软件不应在 `LR` 指令上设置 `rl` 位（除非同时设置 `aq` 位），也不应在 `SC` 指令上设置 `aq` 位（除非同时设置 `rl` 位）。`LR.rl`
和 `SC.aq` 指令不保证提供比两 bit 均清零时更强的顺序性，但可能导致性能下降。

**清单 2. 使用 LR/SC 实现比较交换功能的示例代码**

```riscv
        # a0 保存内存位置的地址
        # a1 保存期望值
        # a2 保存目标值
        # a0 保存返回值，成功为 0，失败为非零
    cas:
        lr.w t0, (a0)        # 加载原始值
        bne t0, a1, fail     # 不匹配则失败
        sc.w t0, a2, (a0)    # 尝试更新
        bnez t0, cas         # 条件存储失败则重试
        li a0, 0             # 设置返回成功
        jr ra                # 返回
    fail:
        li a0, 1             # 设置返回失败
        jr ra                # 返回
```

`LR/SC` 可用于构建无锁数据结构。清单 2 展示了使用 `LR/SC` 实现比较交换功能的示例。若内联实现，比较交换功能仅需四条指令。

## Supervisor-Level ISA

### Supervisor Instructions

#### Supervisor Memory-Management Fence Instruction

![SFENCE.VMA.svg](image/light/SFENCE.VMA.svg#gh-light-mode-only)
![SFENCE.VMA.svg](image/dark/SFENCE.VMA.svg#gh-dark-mode-only)

监控器内存管理屏障指令 `SFENCE.VMA`
用于将对内存中存储的内存管理数据结构的更新与当前执行进行同步。指令执行会隐式地读取并写入这些数据结构，但这些隐式引用通常不与显式的加载和存储操作排序。执行
`SFENCE.VMA` 能保证：在同一 RISC-V hart 中，任何先前对这些数据结构已可见的存储操作会先于后续对这些数据结构的隐式引用。`rs1`
和 `rs2` 的值决定 `SFENCE.VMA` 所排序的具体操作范围（如下所述）。`SFENCE.VMA` 同时还会使与该 hart 关联的地址转换缓存条目失效（参见第
10.3.2 节）。更多关于此指令行为的细节，参见第 3.1.6.5 节和第 3.7.2 节。

`SFENCE.VMA` 只会对本 hart 的数据结构隐式引用进行排序。

如果只修改单个地址对应的页或超级页，`rs1` 可指定该虚拟地址以只对该映射执行转换屏障。若只修改了 `ASID`（单个地址空间标识符），
`rs2` 可指定相应地址空间。`SFENCE.VMA` 根据 `rs1` 和 `rs2` 的值来决定行为：

- 如果 `rs1=x0` 且 `rs2=x0`，则该屏障会对所有地址空间中任意级别页表的所有读写操作进行排序，并使所有地址空间的地址转换缓存条目失效。
- 如果 `rs1=x0` 且 `rs2≠x0`，则该屏障只对由整数寄存器 `rs2` 指定的地址空间中任意级别页表的所有读写操作进行排序（不包含全局映射
  global 条目的访问），并使该地址空间的所有非全局地址转换缓存条目失效。
- 如果 `rs1≠x0` 且 `rs2=x0`，则该屏障只对所有地址空间中与 `rs1`
  对应虚拟地址相关的页表叶子条目的读写操作进行排序，并使所有地址空间中与该虚拟地址相关的翻译缓存条目失效。
- 如果 `rs1≠x0` 且 `rs2≠x0`，则该屏障只对由整数寄存器 `rs2` 指定的地址空间中、与 `rs1`
  对应虚拟地址相关的页表叶子条目的读写操作进行排序（不包含全局映射 global
  条目的访问），并使该地址空间中与该虚拟地址相关的非全局翻译缓存条目失效。

若 `rs1` 中的值并非有效虚拟地址，`SFENCE.VMA` 不产生任何效果，也不会引发异常。

当 `rs2≠x0` 时，其高位中的一些保留位目前还未规范使用。在未定义使用前，软件应将其清零，硬件实现可忽略它们。若
`ASIDLEN<ASIDMAX`，则实现会忽略超出 `ASIDLEN` 但小于 `ASIDMAX` 的那部分位。

实现可能对自上次可涵盖该地址的 `SFENCE.VMA` 以来，任何时候都曾经有效的地址使用任何翻译。`SFENCE.VMA`
的排序并不会让对内存管理数据结构的隐式读写与标准 RVWMO 规则相互完全契合。例如，尽管 `SFENCE.VMA`
排序了先前显式访问与后续隐式访问之间的关系，但并不保证先前显式访问在全局内存顺序上必然先于后续显式访问。此外，这些隐式读不一定遵循常规程序次序规则。

实现只能对当前 `satp` 寄存器所指向的页表以及其后续有效 `V=1` 的表项执行隐式读取，并且只能对指令执行产生的隐式访问（而非推测式访问）引发异常。

`sstatus` 寄存器中的 `SUM` 和 `MXR` 位的更改立即生效，无需执行 `SFENCE.VMA`。将 `satp.MODE` 从
`Bare` 改为其它模式或反向也即刻生效，无需 `SFENCE.VMA`。同样地，更改 `satp.ASID` 也会立即生效。

若某个 hart 使用地址转换缓存，则该缓存应被视为此 hart 私有；`ASID` 在各 hart 之间并无一致含义。OS 可以选择在不同 hart 上用相同
`ASID` 代表不同地址空间，或利用其他机制管理 `ASID`。

对于将 `satp.MODE` 固定为零（即一直 `Bare`）的实现，尝试执行 `SFENCE.VMA` 指令可能会触发非法指令异常。
