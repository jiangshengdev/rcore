---
slug: rust-reference
title: The Rust Language Reference
authors: [jiangsheng]
tags: [rust]
---

记录学习时查阅的 The Rust Language Reference 参考资料要点。

<!-- truncate -->

:::note 翻译说明

本页为 The Rust Language Reference 部分内容的中文摘译，仅供学习参考，不具规范效力。

上游英文版本（更新频繁，译文可能未完全同步）：

> https://doc.rust-lang.org/stable/reference/

如用于实现 / 调试 / 合规，请务必核对英文原文；若发现差异或术语不一致，欢迎反馈。

:::

## Inline assembly

## 内联汇编

内联汇编的支持通过 [`asm!`]、[`naked_asm!`] 和 [`global_asm!`] 宏提供。它可以用于在编译器生成的汇编输出中嵌入手写的汇编代码。

[`asm!`]: https://doc.rust-lang.org/stable/core/arch/macro.asm.html
[`naked_asm!`]: https://doc.rust-lang.org/stable/core/arch/macro.naked_asm.html
[`global_asm!`]: https://doc.rust-lang.org/stable/core/arch/macro.global_asm.html

内联汇编在以下架构上是稳定的：

- x86 和 x86-64
- ARM
- AArch64 和 Arm64EC
- RISC-V
- LoongArch
- s390x

如果在不支持的目标平台上使用汇编宏，编译器将发出错误。

### Operand type

### 操作数类型

支持几种类型的操作数：

- `in(<reg>) <expr>`

  - `<reg>` 可以引用寄存器类或显式寄存器。分配的寄存器名称被替换到 asm 模板字符串中。
  - 分配的寄存器将在汇编代码开始时包含 `<expr>` 的值。
  - 分配的寄存器必须在汇编代码结束时包含相同的值（除非 `lateout` 被分配到同一寄存器）。

- `out(<reg>) <expr>`

  - `<reg>` 可以引用寄存器类或显式寄存器。分配的寄存器名称被替换到 asm 模板字符串中。
  - 分配的寄存器将在汇编代码开始时包含未定义值。
  - `<expr>` 必须是一个（可能未初始化的）位置表达式，分配的寄存器的内容在汇编代码结束时写入其中。
  - 可以指定下划线（`_`）而不是表达式，这将导致寄存器的内容在汇编代码结束时被丢弃（有效地充当覆盖）。

- `lateout(<reg>) <expr>`

  - 与 `out` 相同，但寄存器分配器可以重用分配给 `in` 的寄存器。
  - 您应该只在读取所有输入后才写入寄存器，否则可能会覆盖输入。

- `inout(<reg>) <expr>`

  - `<reg>` 可以引用寄存器类或显式寄存器。分配的寄存器名称被替换到 asm 模板字符串中。
  - 分配的寄存器将在汇编代码开始时包含 `<expr>` 的值。
  - `<expr>` 必须是一个可变的已初始化位置表达式，分配的寄存器的内容在汇编代码结束时写入其中。

- `inout(<reg>) <in expr> => <out expr>`

  - 与 `inout` 相同，但寄存器的初始值取自 `<in expr>` 的值。
  - `<out expr>` 必须是一个（可能未初始化的）位置表达式，分配的寄存器的内容在汇编代码结束时写入其中。
  - 可以为 `<out expr>` 指定下划线（`_`）而不是表达式，这将导致寄存器的内容在汇编代码结束时被丢弃（有效地充当覆盖）。
  - `<in expr>` 和 `<out expr>` 可以具有不同的类型。

- `inlateout(<reg>) <expr>` / `inlateout(<reg>) <in expr> => <out expr>`

  - 与 `inout` 相同，但寄存器分配器可以重用分配给 `in` 的寄存器（如果编译器知道 `in` 具有与 `inlateout` 相同的初始值，则可能发生这种情况）。
  - 您应该只在读取所有输入后才写入寄存器，否则可能会覆盖输入。

- `sym <path>`

  - `<path>` 必须引用 `fn` 或 `static`。
  - 引用该项的修饰后的符号名被替换到 asm 模板字符串中。
  - 替换的字符串不包括任何修饰符（例如 GOT、PLT、重定位等）。
  - `<path>` 允许指向 `#[thread_local]` 静态变量，在这种情况下，汇编代码可以将符号与重定位（例如 `@plt`、`@TPOFF`）结合以从线程局部数据中读取。

- `const <expr>`

  - `<expr>` 必须是整数常量表达式。此表达式遵循与内联 `const` 块相同的规则。
  - 表达式的类型可以是任何整数类型，但默认为 `i32`，就像整数字面量一样。
  - 表达式的值被格式化为字符串并直接替换到 asm 模板字符串中。

- `label <block>`

  - 块的地址被替换到 asm 模板字符串中。汇编代码可以跳转到替换的地址。
  - 对于区分直接跳转和间接跳转的目标平台（例如启用了 `cf-protection` 的 x86-64），汇编代码不得间接跳转到替换的地址。
  - 在块执行后，`asm!` 表达式返回。
  - 块的类型必须是单元类型或 `!`（never）。
  - 块开始一个新的安全上下文；`label` 块内的不安全操作必须包装在内部 `unsafe` 块中，即使整个 `asm!` 表达式已经包装在 `unsafe` 中。

操作数表达式从左到右求值，就像函数调用参数一样。在 `asm!` 执行后，输出按从左到右的顺序写入。如果两个输出指向同一位置，这很重要：该位置将包含最右边输出的值。

因为 `naked_asm!` 定义了整个函数体，并且编译器无法发出任何额外的代码来处理操作数，所以它只能使用 `sym` 和 `const` 操作数。

因为 `global_asm!` 存在于函数之外，所以它只能使用 `sym` 和 `const` 操作数。
