---
sidebar_position: 5
---

# 伙伴系统

A buddy system allocator in pure Rust.

> https://github.com/rcore-os/buddy_system_allocator

# 侵入式链表

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/blob/intrusive-linked-list/os/src/buddy_system/linked_list.rs

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/blob/intrusive-linked-list/os/src/buddy_system/test.rs

![values-code.webp](webp/light/values-code.webp#gh-light-mode-only)
![values-code.webp](webp/dark/values-code.webp#gh-dark-mode-only)

![values-debug.webp](webp/light/values-debug.webp#gh-light-mode-only)
![values-debug.webp](webp/dark/values-debug.webp#gh-dark-mode-only)

![list-code.webp](webp/light/list-code.webp#gh-light-mode-only)
![list-code.webp](webp/dark/list-code.webp#gh-dark-mode-only)

![list-debug.webp](webp/light/list-debug.webp#gh-light-mode-only)
![list-debug.webp](webp/dark/list-debug.webp#gh-dark-mode-only)

![push-code.webp](webp/light/push-code.webp#gh-light-mode-only)
![push-code.webp](webp/dark/push-code.webp#gh-dark-mode-only)

![push-debug.webp](webp/light/push-debug.webp#gh-light-mode-only)
![push-debug.webp](webp/dark/push-debug.webp#gh-dark-mode-only)

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

![next-code.webp](webp/light/next-code.webp#gh-light-mode-only)
![next-code.webp](webp/dark/next-code.webp#gh-dark-mode-only)

![next-debug.webp](webp/light/next-debug.webp#gh-light-mode-only)
![next-debug.webp](webp/dark/next-debug.webp#gh-dark-mode-only)

![pop-code.webp](webp/light/pop-code.webp#gh-light-mode-only)
![pop-code.webp](webp/dark/pop-code.webp#gh-dark-mode-only)

![pop-debug.webp](webp/light/pop-debug.webp#gh-light-mode-only)
![pop-debug.webp](webp/dark/pop-debug.webp#gh-dark-mode-only)
