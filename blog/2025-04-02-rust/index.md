---
slug: rust
title: Rust
authors: [jiangsheng]
tags: [rust]
---

记录学习 Rust 的一些笔记。

<!-- truncate -->

## Inline assembly

### Operand type

#### inlateout

`inlateout(<reg>) <expr>` / `inlateout(<reg>) <in expr> => <out expr>`
与 `inout` 类似，但寄存器分配器可复用已分配给输入操作数的寄存器。这种情况发生在编译器检测到输入操作数的初始值与
`inlateout`
的初始值相同时。
必须确保在所有输入操作数读取完成后，再向该寄存器写入数据，否则可能导致输入数据被覆盖。
