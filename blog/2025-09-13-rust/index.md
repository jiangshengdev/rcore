---
slug: rust
title: Rust
authors: [jiangsheng]
tags: [rust]
---

记录学习时查阅的一些 Rust 语言参考资料要点。

<!-- truncate -->

:::note 翻译说明

本页为 Rust Language Reference 和 The Rust Programming Language 部分内容的中文摘译，仅供学习参考，不具规范效力。

上游英文版本（更新频繁，译文可能未完全同步）：

> https://doc.rust-lang.org/stable/reference/
>
> https://doc.rust-lang.org/stable/book/

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

## Extensible Concurrency with the Sync and Send Traits

## 使用 Sync 和 Send Trait 实现可扩展并发

有趣的是，本章到目前为止讨论的几乎所有并发特性都是标准库的一部分，而不是语言本身的一部分。你处理并发的选择不仅限于语言或标准库；你可以编写自己的并发特性，或者使用其他人编写的特性。

然而，在嵌入到语言而非标准库中的关键并发概念中，有 `std::marker` trait 的 `Send` 和 `Sync`。

### Allowing Access from Multiple Threads with Sync

### 使用 Sync 允许多线程访问

`Sync` 标记 trait 表明，实现该 trait 的类型可以安全地被多个线程引用。换句话说，当且仅当
`&T`（对 `T` 的不可变引用）是 `Send`
时（即该引用可以安全地发送到另一个线程），任何类型 `T` 才是 `Sync` 的。与 `Send`
类似，原始类型都是 `Sync` 的，而完全由 `Sync`
类型组成的复合类型也自动为 `Sync`。

智能指针 `Rc<T>` 不是 `Sync` 的原因与它不是 `Send` 的原因相同。`RefCell<T>` 类型（第
15 章讨论过）及其相关的 `Cell<T>`
类型系列均不是 `Sync` 的。`RefCell<T>` 在运行时进行的借用检查机制不具备线程安全性。而智能指针
`Mutex<T>` 是 `Sync`
的，正如「在多线程间共享 `Mutex<T>`」一节所示，它可以用于跨线程共享访问。
