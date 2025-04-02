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

与 `inout` 的唯一区别在于，寄存器分配器可以复用已分配给 `in` 的寄存器（当编译器检测到 `in` 的初始值与 `inlateout`
的初始值相同时可能发生）。
必须确保在读取完所有输入操作数后，再向该寄存器写入数据，否则可能覆盖 `in` 的值。
