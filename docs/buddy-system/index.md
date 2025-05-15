---
sidebar_position: 5
---

# 伙伴系统

rCore 使用伙伴系统作为堆内存分配器。

伙伴系统的源代码可以在此处查看：

> https://github.com/rcore-os/buddy_system_allocator

伙伴系统内部使用了侵入式链表来存储内存地址。

## 侵入式链表

为了解其实现，将侵入式链表的代码放置到 `ch1` 分支内，以方便调试。因为 rCore 比较简单，每次运行时，变量的内存地址基本一致。

`linked_list.rs` 文件是直接从伙伴系统复制：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/blob/intrusive-linked-list/os/src/buddy_system/linked_list.rs

`test.rs` 文件为了方便调试，略有修改：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/blob/intrusive-linked-list/os/src/buddy_system/test.rs

### 构建节点的值 

首先进入 2 处的断点：

![values-code.webp](webp/light/values-code.webp#gh-light-mode-only)
![values-code.webp](webp/dark/values-code.webp#gh-dark-mode-only)

此时可以查看 16 个节点数组 `values` 的地址和值，为了方便定位，内存值被赋值为有规律的数字。

这些值后续会被丢弃，重要的他们的地址。测试用例中这些地址在栈中，实际分配内存时，这些地址就在需要分配的内存内部。

values 数组的起始地址为 `0x80218d48`，其值如下图所示：

![values-debug.webp](webp/light/values-debug.webp#gh-light-mode-only)
![values-debug.webp](webp/dark/values-debug.webp#gh-dark-mode-only)

### 新建链表

跳转到下一个断点， `push` 之前。

![list-code.webp](webp/light/list-code.webp#gh-light-mode-only)
![list-code.webp](webp/dark/list-code.webp#gh-dark-mode-only)

可以看到链表 `list` 位于栈上，其地址为 `0x80218e20`，其值为 `0x0`，表示 `head` 首节点当前是空节点。

![list-debug.webp](webp/light/list-debug.webp#gh-light-mode-only)
![list-debug.webp](webp/dark/list-debug.webp#gh-dark-mode-only)

### 插入节点

跳转到下一个断点， `push` 之后。

![push-code.webp](webp/light/push-code.webp#gh-light-mode-only)
![push-code.webp](webp/dark/push-code.webp#gh-dark-mode-only)

查看「内存视图」如下：

![push-debug.webp](webp/light/push-debug.webp#gh-light-mode-only)
![push-debug.webp](webp/dark/push-debug.webp#gh-dark-mode-only)

### 查看内存

同时可以使用 GDB 进行内存检视：

```
(gdb) x /g 0x0000000080218e20
0x80218e20:	0x0000000080218dc0
```

```
(gdb) x /16g 0x0000000080218d48
0x80218d48:	0x0000000000000000	0x0000000080218d48
0x80218d58:	0x0000000080218d50	0x0000000080218d58
0x80218d68:	0x0000000080218d60	0x0000000080218d68
0x80218d78:	0x0000000080218d70	0x0000000080218d78
0x80218d88:	0x0000000080218d80	0x0000000080218d88
0x80218d98:	0x0000000080218d90	0x0000000080218d98
0x80218da8:	0x0000000080218da0	0x0000000080218da8
0x80218db8:	0x0000000080218db0	0x0000000080218db8
```

链表 `list` 所在的地址 `0x80218e20` 上的值被赋值为了 `values` 数组的最后一个元素的地址 `0x80218dc0`，即最后插入的节点的地址。

这最后一个节点作为 `head` 节点，其值为下一个节点的地址 `0x80218db8`。

以此类推，直到最初被插入的节点，其地址为 `0x80218d48`，其值为 `0x0`，表示他是链表的最后一个节点。

下图中每一个矩形表示一个链表节点。左侧的红色背景表示内存地址，右侧的绿色背景表示此地址所在内存的值。

同时除了第一个数组元素的值刚好与空指针一致之外，其他的后续元素的值都被另一个元素的地址覆盖。

![memory.svg](svg/light/memory.svg#gh-light-mode-only)
![memory.svg](svg/dark/memory.svg#gh-dark-mode-only)

### 准备删除

跳转到下一个断点， `pop` 之前。

![next-code.webp](webp/light/next-code.webp#gh-light-mode-only)
![next-code.webp](webp/dark/next-code.webp#gh-dark-mode-only)

注意这里链表 `list` 所在的地址 `0x80218e20` 的值将在接下来发生改变。

![next-debug.webp](webp/light/next-debug.webp#gh-light-mode-only)
![next-debug.webp](webp/dark/next-debug.webp#gh-dark-mode-only)

### 删除节点

跳转到下一个断点， `pop` 之后。

![pop-code.webp](webp/light/pop-code.webp#gh-light-mode-only)
![pop-code.webp](webp/dark/pop-code.webp#gh-dark-mode-only)

链表 `list` 所在的地址 `0x80218e20` 的值被赋值为了 `0x0`，表示 `head` 节点已经为空。

![pop-debug.webp](webp/light/pop-debug.webp#gh-light-mode-only)
![pop-debug.webp](webp/dark/pop-debug.webp#gh-dark-mode-only)

如果使用「步过」按钮一行一行的执行，可以看到 `pop` 与 `push` 不同的是，移除元素时只有链表 `list` 所在地址的值发生了改变。
