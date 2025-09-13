---
slug: riscv-unprivileged
title: "RISC-V ISA Manual Volume I: Unprivileged Architecture"
authors: [jiangsheng]
tags: [riscv]
---

记录学习 RISC-V Unprivileged 的一些笔记。

<!-- truncate -->

## RV32I Base Integer Instruction Set, Version 2.1

## RV32I 基础整数指令集，版本 2.1

### Memory Ordering Instructions

### 内存序指令

![mem-order.svg](_assets/svg/light/mem-order.svg#gh-light-mode-only)
![mem-order.svg](_assets/svg/dark/mem-order.svg#gh-dark-mode-only)

FENCE 指令用于对设备 I/O 和内存访问进行排序，这些访问是从其他 RISC-V 硬件线程和外部设备或协处理器的角度观察的。设备输入 (I)、设备输出 (O)、内存读取 \(R) 和内存写入 (W) 的任意组合都可以相对于相同操作的任意组合进行排序。非正式地说，在 FENCE 指令之前的前驱集合中的任何操作之前，其他 RISC-V 硬件线程或外部设备都不能观察到跟随 FENCE 指令的后继集合中的任何操作。「RVWMO 内存一致性模型」提供了 RISC-V 内存一致性模型的精确描述。

FENCE 指令还对硬件线程执行的内存读取和写入进行排序，这些操作是从外部设备执行的内存读取和写入的角度观察的。但是，FENCE 指令不对外部设备使用任何其他信号机制产生的事件观察进行排序。

:::info

设备可能通过某种外部通信机制观察到对内存位置的访问，例如，驱动中断信号到中断控制器的内存映射控制寄存器。这种通信超出了 FENCE 排序机制的范围，因此 FENCE 指令无法保证中断信号的变化何时对中断控制器可见。特定设备可能提供额外的排序保证以减少软件开销，但这些超出了 RISC-V 内存模型的范围。

:::

EEI 将定义可能的 I/O 操作，特别是当载入和储存指令访问哪些内存地址时，这些地址将分别被视为设备输入和设备输出操作并进行相应排序，而不是内存读取和写入。例如，内存映射 I/O 设备通常使用非缓存载入和储存进行访问，这些操作使用 I 和 O 位而不是 R 和 W 位进行排序。指令集扩展也可能描述新的 I/O 指令，这些指令也将使用 FENCE 指令中的 I 和 O 位进行排序。

**Fence mode encoding**

| _fm_ field | Mnemonic suffix | Meaning                                                                                   |
|:----------:|:---------------:|:------------------------------------------------------------------------------------------|
|    0000    |     _none_      | Normal Fence                                                                              |
|    1000    |      .TSO       | With `FENCE RW,RW`: exclude write-to-read ordering; otherwise: _Reserved for future use._ |
|  _other_   |     _other_     | _Reserved for future use._                                                                |

**栅栏模式编码**

FENCE 模式字段 _fm_ 定义了 FENCE 指令的语义。`FENCE` 指令（_fm_=`0000`）将其前驱集合中的所有内存操作排序在其后继集合中的所有内存操作之前。

`FENCE.TSO` 指令编码为 FENCE 指令，其中 _fm_=`1000`、_predecessor_=`RW` 和 _successor_=`RW`。`FENCE.TSO` 将其前驱集合中的所有载入操作排序在其后继集合中的所有内存操作之前，并将其前驱集合中的所有储存操作排序在其后继集合中的所有储存操作之前。这使得 `FENCE.TSO` 前驱集合中的非 AMO 储存操作与其后继集合中的非 AMO 载入操作之间保持无序关系。

:::info

由于 `FENCE RW,RW` 施加了 `FENCE.TSO` 所施加排序的超集，忽略 _fm_ 字段并将 `FENCE.TSO` 实现为 `FENCE RW,RW` 是正确的。

:::

FENCE 指令中的未使用字段——_rs1_ 和 _rd_——被保留用于未来扩展中更细粒度的栅栏指令。为了前向兼容性，基础实现应忽略这些字段，标准软件应将这些字段置零。同样，许多 _fm_ 和前驱/后继集合设置也被保留用于未来使用。基础实现应将所有此类保留配置视为 `FENCE` 指令（_fm_=`0000`），标准软件应仅使用非保留配置。

:::info

我们选择了宽松内存模型，以便从简单的机器实现和可能的未来协处理器或加速器扩展中获得高性能。我们将 I/O 排序与内存读写排序分离，以避免在设备驱动硬件线程内进行不必要的串行化，并支持控制附加协处理器或 I/O 设备的替代非内存路径。简单的实现可能还会忽略 _predecessor_ 和 _successor_ 字段，并始终对所有操作执行保守的 FENCE。

:::

## "Zifencei" Extension for Instruction-Fetch Fence, Version 2.0

本章定义了「Zifencei」扩展，其中包含 `FENCE.I`
指令。该指令为同一硬件线程（hart）上的指令存储器写入操作与指令获取操作之间提供显式同步。目前，`FENCE.I`
是唯一的标准机制，可确保一个关键一致性：任何对 hart
可见的存储操作，必须对其自身的指令获取也可见。

![zifencei-ff.svg](_assets/svg/light/zifencei-ff.svg#gh-light-mode-only)
![zifencei-ff.svg](_assets/svg/dark/zifencei-ff.svg#gh-dark-mode-only)

`FENCE.I` 指令的核心功能是同步指令流和数据流的可见性。RISC-V 架构默认不保证对指令存储器的写入操作在
hart 执行 `FENCE.I`
之前对其自身的指令获取可见。执行 `FENCE.I` 后，该 hart
的后续指令获取将能够看到所有先前对其可见的数据存储。然而，在多处理器系统中，`FENCE.I` 并不保证其他 hart 的指令获取能够观察到本地
hart 的存储。如果需要使对指令存储器的写入对所有
RISC-V hart 全局可见，写入方
hart 必须遵循以下协议：首先执行一条数据流 `FENCE` 指令，以确保写入对其他 hart
可见，然后请求所有远程 hart 执行各自的
`FENCE.I` 指令。

## "A" Extension for Atomic Instructions

### Specifying Ordering of Atomic Instructions

基础 RISC-V ISA 采用宽松的内存模型，通过使用 `FENCE` 指令来施加额外的顺序约束。执行环境将地址空间分为内存域和
I/O 域，`FENCE` 指令可以对这两个地址域之一或二者进行访问排序。

为了更高效地支持释放一致性（Gharachorloo 等，1990），每条原子指令包含两个位：`aq` 和
`rl`，它们可为其他 RISC-V hart
提供额外的内存排序约束。根据原子指令访问的是内存域还是 I/O
域，这两个位会对其中一个域的访问进行排序，对另一个域则无顺序限制；若需要对这两个域都进行排序，可以使用
`FENCE` 指令。

当这两个位都为 0 时，不对原子内存操作施加额外的顺序约束。若只设置 `aq`
位，则该原子内存操作被视为获取（acquire）访问，即在该原子内存操作完成之前，本
hart 不会观察到后续的内存操作。若只设置 `rl` 位，则该原子内存操作被视为释放（release）访问，即本
hart
不会观察到该释放操作在任何早先的内存操作之前完成。若 `aq` 和 `rl`
均被设置，则该原子内存操作具有顺序一致性，不会在任意早先内存操作之前或任意后续内存操作之后被观察到（仅限同一
RISC-V hart，且针对同一地址域）。

### "Zalrsc" Extension for Load-Reserved/Store-Conditional Instructions

![load-reserve-st-conditional.svg](_assets/svg/light/load-reserve-st-conditional.svg#gh-light-mode-only)
![load-reserve-st-conditional.svg](_assets/svg/dark/load-reserve-st-conditional.svg#gh-dark-mode-only)

对单个内存字或双字进行复杂原子内存操作时，需使用 `LR`（加载保留，Load-Reserved）和
`SC`（条件存储，Store-Conditional）指令。`LR.W` 从 `rs1`
中的地址加载一个字，将符号扩展后的值存入 `rd`，并注册保留集 —— 该字节集合包含被寻址字中的所有字节。`SC.W` 有条件地将 `rs2`
中的字写入 `rs1` 中的地址：仅当保留仍然有效且保留集包含被写入的字节时，`SC.W`
才会成功。若 `SC.W` 成功，则将 `rs2`
中的字写入内存，并将 0 写入 `rd`；若失败，则不写入内存，并将非零值写入 `rd`。出于内存保护目的，失败的 `SC.W`
可能被视为存储操作。无论成功与否，执行 `SC.W` 指令都会使当前 hart 持有的所有保留失效。`LR.D` 和 `SC.D` 对双字进行类似操作，仅在
RV64 中可用。对于 RV64，`LR.W` 和 `SC.W` 会对存入 `rd` 的值进行符号扩展。

值为 1 的失败编码表示未指定的失败原因。其他失败编码当前保留。可移植软件应仅假设失败编码为非零值。

对于 `LR` 和 `SC`，「Zalrsc」扩展要求 `rs1` 中的地址必须按操作数大小自然对齐（即双字需
8 字节对齐，字需 4
字节对齐）。如果地址未自然对齐，将产生地址不对齐异常或访问故障异常。对于本可完成但因未对齐而不应被模拟的内存访问，可能产生访问故障异常。

实现可以为每个 `LR` 注册任意大小的保留集，只要该保留集包含被寻址数据字或双字的所有字节。在程序顺序中，`SC` 只能与最近的
`LR` 配对。`SC` 成功需满足：在 `LR` 和 `SC` 之间未观察到其他 hart
对保留集的存储操作，且在程序顺序中 `LR` 和 `SC` 之间没有其他
`SC` 操作；同时需满足：在 `LR` 和 `SC` 之间未观察到非 hart 设备对 `LR`
指令访问字节的写入。注意此 `LR`
可能具有不同的有效地址和数据大小，但将 `SC` 的地址作为保留集的一部分进行了保留。

`SC` 必须失败的情形包括：地址不在程序顺序中最近 `LR` 的保留集内；在 `LR` 和 `SC`
之间观察到其他 hart 对保留集的存储操作；在
`LR` 和 `SC` 之间观察到其他设备对 `LR` 访问字节的写入（若设备写入了保留集但未写入
`LR` 访问的字节，`SC` 可能失败或成功）；在程序顺序中
`LR` 和 `SC` 之间存在其他 `SC`（无论地址如何）。成功 `LR/SC` 序列的原子性要求的精确定义参见第
18.1 节的「Atomicity Axiom」。

在建立保留的 `LR` 指令之前，其他 RISC-V hart 无法观察到 `SC` 指令。

软件不应在 `LR` 指令上设置 `rl` 位（除非同时设置 `aq` 位），也不应在 `SC` 指令上设置
`aq` 位（除非同时设置 `rl` 位）。`LR.rl`
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

`LR/SC` 可用于构建无锁数据结构。清单 2 展示了使用 `LR/SC`
实现比较交换功能的示例。若内联实现，比较交换功能仅需四条指令。
