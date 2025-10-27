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

## Extensible Concurrency with `Send` and `Sync`

## 使用 `Send` 和 `Sync` 实现可扩展并发

有趣的是，到目前为止我们在本章中讨论的几乎所有并发功能都是标准库的一部分，而不是语言本身的一部分。你处理并发的选择不仅限于语言或标准库；你可以编写自己的并发功能或使用其他人编写的功能。

然而，在嵌入到语言中而不是标准库中的关键并发概念中，有 `std::marker` 特征 `Send` 和 `Sync`。

### Transferring Ownership Between Threads

### 在线程间转移所有权

`Send` 标记特征表示实现 `Send` 的类型的值的所有权可以在线程间转移。几乎所有 Rust 类型都实现了 `Send`，但有一些例外，包括 `Rc<T>`：它不能实现 `Send`，因为如果你克隆了一个 `Rc<T>` 值并试图将克隆的所有权转移到另一个线程，两个线程可能会同时更新引用计数。因此，`Rc<T>` 被实现用于单线程情况，在这种情况下你不想承担线程安全的性能损耗。

因此，Rust 的类型系统和特征约束确保你永远不会意外地不安全地跨线程发送 `Rc<T>` 值。当我们在示例 16-14 中尝试这样做时，我们得到了错误 `` the trait `Send` is not implemented for `Rc<Mutex<i32>>` ``。当我们切换到确实实现了 `Send` 的 `Arc<T>` 时，代码编译通过了。

完全由 `Send` 类型组成的任何类型也会自动标记为 `Send`。几乎所有基本类型都是 `Send`，除了裸指针，我们将在第 20 章中讨论。

### Accessing from Multiple Threads

### 从多个线程访问

`Sync` 标记特征表示实现 `Sync` 的类型可以安全地被多个线程引用。换句话说，如果 `&T`（对 `T` 的不可变引用）实现了 `Send`，那么任何类型 `T` 都实现了 `Sync`，这意味着引用可以安全地发送到另一个线程。与 `Send` 类似，基本类型都实现了 `Sync`，完全由实现 `Sync` 的类型组成的类型也实现了 `Sync`。

智能指针 `Rc<T>` 也不实现 `Sync`，原因与它不实现 `Send` 相同。`RefCell<T>` 类型（我们在第 15 章中讨论过）和相关的 `Cell<T>` 类型系列不实现 `Sync`。`RefCell<T>` 在运行时进行的借用检查实现不是线程安全的。智能指针 `Mutex<T>` 实现了 `Sync`，可以用于与多个线程共享访问，正如你在["对 `Mutex<T>` 的共享访问"][shared-access]中看到的那样。

### Implementing `Send` and `Sync` Manually Is Unsafe

### 手动实现 `Send` 和 `Sync` 是不安全的

因为完全由其他实现 `Send` 和 `Sync` 特征的类型组成的类型也会自动实现 `Send` 和 `Sync`，所以我们不必手动实现这些特征。作为标记特征，它们甚至没有任何方法需要实现。它们只是用于强制执行与并发相关的不变量。

手动实现这些特征涉及实现不安全 Rust 代码。我们将在第 20 章中讨论使用不安全 Rust 代码；现在，重要的信息是构建不是由 `Send` 和 `Sync` 部分组成的新并发类型需要仔细考虑以维护安全保证。["The Rustonomicon"][nomicon] 有关于这些保证以及如何维护它们的更多信息。

## Summary

## 总结

这不是你在本书中最后一次看到并发：下一章专注于异步编程，第 21 章中的项目将在比这里讨论的较小示例更现实的情况下使用本章中的概念。

如前所述，由于 Rust 处理并发的方式很少是语言的一部分，许多并发解决方案都作为 crate 实现。这些比标准库发展得更快，所以一定要在线搜索当前最先进的 crate 以在多线程情况下使用。

Rust 标准库提供了用于消息传递的通道和智能指针类型，如 `Mutex<T>` 和 `Arc<T>`，它们在并发上下文中使用是安全的。类型系统和借用检查器确保使用这些解决方案的代码不会出现数据竞争或无效引用。一旦你的代码编译通过，你就可以放心它将在多个线程上愉快地运行，而不会出现其他语言中常见的那种难以追踪的错误。并发编程不再是一个令人恐惧的概念：勇敢地去让你的程序并发吧！

[shared-access]: https://doc.rust-lang.org/stable/book/ch16-03-shared-state.html#shared-access-to-mutext
[nomicon]: https://doc.rust-lang.org/stable/nomicon/index.html
