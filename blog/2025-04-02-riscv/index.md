---
slug: riscv
title: RISC-V
authors: [jiangsheng]
tags: [riscv]
---

记录学习 RISC-V 的一些笔记。

<!-- truncate -->

## Machine-Level ISA

### Machine-Mode Privileged Instructions

#### Wait for Interrupt

**等待中断指令 (WFI)** 通知硬件实现：当前 hart 可暂停运行，直到可能需要处理中断。执行 WFI 还可建议硬件平台将合适的中断优先分配到此
hart。WFI 在所有特权模式下可用，并可选择性地支持用户模式 (U-mode)。如第 3.1.6.6 节所述，当 `mstatus` 寄存器的 `TW=1`
时，此指令可能触发非法指令异常。

## "Zifencei" Extension for Instruction-Fetch Fence

本章定义了 **"Zifencei"** 扩展，该扩展包含 `FENCE.I` 指令。此指令为 **同一硬件线程 (hart)** 上的指令存储器写入操作与指令获取操作提供显式同步。当前，
`FENCE.I` 是唯一的标准机制，可确保以下关键一致性：**任何对 hart 可见的存储操作，必须对其自身的指令获取可见** 。

`FENCE.I` 指令的核心功能是 **同步指令流与数据流的可见性** 。RISC-V 架构默认不保证对指令存储器的写入操作在 hart 执行
`FENCE.I` 前对其自身的指令获取可见。执行 `FENCE.I` 后，该 hart 的后续指令获取将观察到所有先前已对其可见的数据存储。然而，在
**多处理器系统** 中，`FENCE.I` 不保证其他 hart 的指令获取能观测到本地 hart 的存储。若需使指令存储器的写入对所有 RISC-V
hart 全局可见，写入方 hart 必须遵循以下协议：首先执行一条 **数据流 `FENCE` 指令** 以确保写入对其他 hart 可见，随后请求所有远程
hart 执行各自的 `FENCE.I` 指令。
