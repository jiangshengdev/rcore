---
slug: riscv-privileged
title: RISC-V Privileged
authors: [jiangsheng]
tags: [riscv]
---

记录学习 RISC-V Privileged 的一些笔记。

## Machine-Level ISA

### Machine-Mode Privileged Instructions

#### Wait for Interrupt

`WFI`（等待中断指令，Wait for Interrupt）通知硬件实现当前硬件线程（hart）可以暂停运行，直到可能需要处理中断。执行 `WFI`
还可用于建议硬件平台优先将合适的中断分配到该
hart。`WFI` 在所有特权模式下可用，并可选择性地支持用户模式（U-mode）。如第 3.1.6.6 节所述，当 `mstatus` 寄存器的 `TW=1`
时，执行该指令可能会触发非法指令异常。

![WFI.svg](image/light/WFI.svg#gh-light-mode-only)
![WFI.svg](image/dark/WFI.svg#gh-dark-mode-only)
