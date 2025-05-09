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

与 `inout` 的唯一区别在于，寄存器分配器可以复用已分配给 `in` 的寄存器（当编译器检测到
`in` 的初始值与 `inlateout`
的初始值相同时可能发生）。必须确保在读取完所有输入操作数后，再向该寄存器写入数据，否则可能覆盖 `in` 的值。

## Extensible Concurrency with the Sync and Send Traits

### Allowing Access from Multiple Threads with Sync

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
