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
