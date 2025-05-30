---
sidebar_position: 6
---

# 虚拟内存

本节调试的代码 Tag 为 `virtual-memory`：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/tree/virtual-memory

## 简单分页

### 系统内核页表

先分析系统内核态的页表构造。

在 `src/mm/memory_set.rs:277` 处断点暂停。

![new-kernel-code.webp](webp/light/new-kernel-code.webp#gh-light-mode-only)
![new-kernel-code.webp](webp/dark/new-kernel-code.webp#gh-dark-mode-only)

可以看到已经完成了跳板和 `.text` 段的页表项构造。

其中跳板为非恒等映射，而 `.text` 段则为恒等映射。

![new-kernel-print.webp](webp/light/new-kernel-print.webp#gh-light-mode-only)
![new-kernel-print.webp](webp/dark/new-kernel-print.webp#gh-dark-mode-only)

查看变量，可以看到系统内存集合内页表的根物理页号 `root_ppn` 其值为 `0x83A5B`。

帧跟踪器记录了 5 个物理页号，分别为：`0x83A5B`、`0x83A5C`、`0x83A5D`、`0x83A5E` 和 `0x83A5F`。

![new-kernel-debug.webp](webp/light/new-kernel-debug.webp#gh-light-mode-only)
![new-kernel-debug.webp](webp/dark/new-kernel-debug.webp#gh-dark-mode-only)

使用 GDB 检视这 5 个物理页号所对应的物理地址区间的内存段中内存的值。

```
(gdb) x /512g 0x83A5B000
(gdb) x /512g 0x83A5C000
(gdb) x /512g 0x83A5D000
(gdb) x /512g 0x83A5E000
(gdb) x /512g 0x83A5F000
```

由于输出较多，此处不进行展示，仅将非 `0x0` 值在下方绘制。

图中，每一个灰色边框的组即为一个寄存器或者为页表项数组。

其中每一个页表项数组含有 512 个数组元素。其存储在以其物理页号转换为的物理地址内存段中，占用 4 KiB 空间。

每一个元素红色背景的部分为物理地址或寄存器名称；蓝色背景的部分为其所在页表项数组中的下标。

绿色背景的部分，上半部分为其存储的值，即下一个物理页号向左偏移 10 位后加上其他标志位；下半部分为其值解析出的物理页号。

虽然此时 `satp` 寄存器还未赋值，但当页表构建完成后，会修改 `satp` 的值。为方便查看，下图就先绘制出后续的值。

![memory.svg](svg/light/memory.svg#gh-light-mode-only)
![memory.svg](svg/dark/memory.svg#gh-dark-mode-only)

可以看到 `satp` 寄存器指向了 `0x83a5b` 这个物理页号。

#### 跳板映射

以跳板映射 `VPN:0x7ffffff -> PPN:0x0080201` 为例，虚拟页号 `0x7ffffff` 分割为 3 段后为 `[511, 511, 511]`。

`0x83a5b` 这个物理页号，其数组下标为 511 的元素地址为 `0x83a5bff8`。其值解析后可得下一个物理页号为 `0x83a5c`。

`0x83a5c` 这个物理页号，其数组下标为 511 的元素地址为 `0x83a5cff8`。其值解析后可得下一个物理页号为 `0x83a5d`。

`0x83a5d` 这个物理页号，其数组下标为 511 的元素地址为 `0x83a5dff8`。其值解析后可得真实的物理页号为 `0x80201`。

#### 恒等映射

以恒等映射 `VPN:0x0080200 -> PPN:0x0080200` 为例，虚拟页号 `0x0080200` 分割为 3 段后为 `[2, 1, 0]`。

`0x83a5b` 这个物理页号，其数组下标为 2 的元素地址为 `0x83a5b010`。其值解析后可得下一个物理页号为 `0x83a5e`。

`0x83a5e` 这个物理页号，其数组下标为 1 的元素地址为 `0x83a5e008`。其值解析后可得下一个物理页号为 `0x83a5f`。

`0x83a5f` 这个物理页号，其数组下标为 0 的元素地址为 `0x83a5f000`。其值解析后可得真实的物理页号为 `0x80200`。
