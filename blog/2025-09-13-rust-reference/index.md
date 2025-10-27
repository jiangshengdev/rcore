---
slug: rust-reference
title: Rust Language Reference
authors: [jiangsheng]
tags: [rust]
---

记录学习时查阅的 Rust Language Reference 参考资料要点。

<!-- truncate -->

:::note 翻译说明

本页为 Rust Language Reference 部分内容的中文摘译，仅供学习参考，不具规范效力。

上游英文版本（更新频繁，译文可能未完全同步）：

> https://doc.rust-lang.org/stable/reference/

如用于实现 / 调试 / 合规，请务必核对英文原文；若发现差异或术语不一致，欢迎反馈。

:::

## Inline assembly

## 内联汇编

Rust 通过 `asm!`、`naked_asm!` 和 `global_asm!` 宏提供了内联汇编支持。它可以用于在编译器生成的汇编输出中嵌入手写的汇编代码。

### Operand type

### 操作数类型

Several types of operands are supported:

#### inlateout

#### 延迟输入输出

`inlateout(<reg>) <expr>` / `inlateout(<reg>) <in expr> => <out expr>`

与 `inout` 的唯一区别在于，寄存器分配器可以复用已分配给 `in` 的寄存器（当编译器检测到
`in` 的初始值与 `inlateout`
的初始值相同时可能发生）。必须确保在读取完所有输入操作数后，再向该寄存器写入数据，否则可能覆盖
`in` 的值。
