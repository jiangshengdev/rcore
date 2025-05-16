---
sidebar_position: 5
---

# 伙伴系统

rCore 使用伙伴系统（Buddy System）作为堆内存分配器，用于高效管理和分配内存。

伙伴系统的源代码可以在此处查看：

> https://github.com/rcore-os/buddy_system_allocator

在实现中，伙伴系统内部使用了侵入式链表（intrusive linked
list）来存储和管理空闲内存块的地址，以提升操作效率和空间利用率。

## 侵入式链表

为了便于调试和理解实现细节，将侵入式链表的相关代码放置在 `ch1` 分支中。由于 rCore
的结构较为简单，每次运行时变量的内存地址基本保持一致，便于观察和分析。

其中，`linked_list.rs` 文件直接从伙伴系统项目中复制：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/blob/intrusive-linked-list/os/src/buddy_system/linked_list.rs

而 `test.rs` 文件则为方便调试做了一些修改：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/blob/intrusive-linked-list/os/src/buddy_system/test.rs

### 构建节点的值

下图展示的是【2. 新建 list 并保存它的地址以便调试】之前的断点状态：

![values-code.webp](webp/light/values-code.webp#gh-light-mode-only)
![values-code.webp](webp/dark/values-code.webp#gh-dark-mode-only)

此时可以查看由 16 个元素组成的数组 `values` 的地址和值。为了便于调试和定位，每个元素的值都被赋予了有规律的数字。

这些数值本身并不重要，关键在于它们的内存地址。测试用例中，这些地址位于栈上；而在实际内存分配时，这些地址会对应到分配区域的内部。

`values` 数组的起始地址为 `0x80218d48`，下图显示了各个元素的值（即每个元素的初始内容）：

![values-debug.webp](webp/light/values-debug.webp#gh-light-mode-only)
![values-debug.webp](webp/dark/values-debug.webp#gh-dark-mode-only)

### 新建链表

此时程序已执行完链表和节点的初始化，但尚未执行任何 `push` 操作。断点位于【5. 依次
push】之前。

![list-code.webp](webp/light/list-code.webp#gh-light-mode-only)
![list-code.webp](webp/dark/list-code.webp#gh-dark-mode-only)

可以看到链表 `list` 位于栈上，其地址为 `0x80218e20`。此时
`head` 字段的值为 `0x0`，表示链表为空，没有任何节点被插入。

```
(gdb) p &list
$1 = (*mut os::buddy_system::linked_list::LinkedList) 0x80218e20
(gdb) p &list.head
$2 = (*mut *mut usize) 0x80218e20
(gdb) p list
$3 = os::buddy_system::linked_list::LinkedList = {head = 0x0}
(gdb) p list.head
$4 = (*mut usize) 0x0
```

:::tip

由于 `LinkedList` 结构体仅包含 `head` 一个字段，因此
`&list` 与 `&list.head` 的地址相同，二者都为 `0x80218e20`。

:::

![list-debug.webp](webp/light/list-debug.webp#gh-light-mode-only)
![list-debug.webp](webp/dark/list-debug.webp#gh-dark-mode-only)

### 插入节点

跳转到【6. head 应指向最后 push 的节点】的断点，此时所有节点已依次插入链表，`head`
字段指向最后插入的节点。

![push-code.webp](webp/light/push-code.webp#gh-light-mode-only)
![push-code.webp](webp/dark/push-code.webp#gh-dark-mode-only)

此时可以通过「内存视图」观察链表结构的变化：

![push-debug.webp](webp/light/push-debug.webp#gh-light-mode-only)
![push-debug.webp](webp/dark/push-debug.webp#gh-dark-mode-only)

### 查看内存

此时可以使用 GDB 检查链表和节点的内存布局。例如：

```
(gdb) x /g 0x0000000080218e20
0x80218e20:	0x0000000080218dc0
```

这里 `0x80218e20` 是链表 `list` 结构体的地址，存储的值 `0x80218dc0` 是
`head` 字段存储的指针，指向链表的首节点（最近插入的节点）的地址。

继续查看数组中各个元素的内容：

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

每一行左侧是节点的地址，右侧是该地址存储的值（即下一个节点的地址或
`0x0`，表示链表尾部）。这样可以直观地看到链表的连接关系和节点内容。

链表 `list` 所在的地址为 `0x80218e20`，该地址存储的值是 `values` 数组最后一个元素的地址
`0x80218dc0`，也就是最近插入链表的节点地址。

这个最近插入的节点成为链表的首节点，其存储的值（`next`
指针）为下一个节点的地址 `0x80218db8`。

依次类推，每个节点的地址依次为
`0x80218dc0`、`0x80218db8`、...、`0x80218d48`，每个节点的值为下一个节点的地址。最早插入的节点（地址为
`0x80218d48`）的值为 `0x0`，表示它是链表的最后一个节点。

下图中，每一个矩形表示一个链表节点。左侧的红色背景表示该节点的内存地址，右侧的绿色背景表示该地址处存储的值（即下一个节点的地址或
`0x0`）。

需要注意的是，除了第一个数组元素的值刚好与空指针一致（`0x0`），其余元素的值都被后续节点的地址覆盖。

![memory.svg](svg/light/memory.svg#gh-light-mode-only)
![memory.svg](svg/dark/memory.svg#gh-dark-mode-only)

### 准备删除

跳转到【9. pop 也应以同样顺序逐个拿出】之前的断点。

![next-code.webp](webp/light/next-code.webp#gh-light-mode-only)
![next-code.webp](webp/dark/next-code.webp#gh-dark-mode-only)

此时链表 `list` 所在的地址 `0x80218e20` 的值即将发生变化。

![next-debug.webp](webp/light/next-debug.webp#gh-light-mode-only)
![next-debug.webp](webp/dark/next-debug.webp#gh-dark-mode-only)

### 删除节点

跳转到【9. pop 也应以同样顺序逐个拿出】之后的断点。

![pop-code.webp](webp/light/pop-code.webp#gh-light-mode-only)
![pop-code.webp](webp/dark/pop-code.webp#gh-dark-mode-only)

此时链表 `list` 所在的地址 `0x80218e20` 的值被赋值为
`0x0`，表示 `head` 字段被设为 `null`，即链表已为空。

![pop-debug.webp](webp/light/pop-debug.webp#gh-light-mode-only)
![pop-debug.webp](webp/dark/pop-debug.webp#gh-dark-mode-only)

如果使用「步过」按钮逐行执行，可以看到 `pop` 与 `push` 不同，移除元素时只有链表
`list` 所在地址的值发生了改变。
