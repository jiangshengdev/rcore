---
slug: rust-book
title: The Rust Programming Language
authors: [jiangsheng]
tags: [rust]
---

记录学习时查阅的 The Rust Programming Language 参考资料要点。

<!-- truncate -->

:::note 翻译说明

本页为 The Rust Programming Language 部分内容的中文摘译，仅供学习参考，不具规范效力。

上游英文版本（更新频繁，译文可能未完全同步）：

> https://doc.rust-lang.org/stable/book/

如用于实现 / 调试 / 合规，请务必核对英文原文；若发现差异或术语不一致，欢迎反馈。

:::

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
