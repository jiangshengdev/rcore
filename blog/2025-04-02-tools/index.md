---
slug: tools
title: Tools
authors: [jiangsheng]
tags: [rust]
---

记录开发调试时用到的一些工具。

<!-- truncate -->

## 打印信息

### 打印外部符号

```shell
rust-nm -g -C -v target/riscv64gc-unknown-none-elf/debug/os | grep -v '::'
```

可能的输出：

```terminaloutput
0000000080200000 A BASE_ADDRESS
0000000080200000 T _start
0000000080200000 T skernel
0000000080200000 T stext
0000000080201030 T rust_main
0000000080206000 T etext
0000000080206000 T srodata
0000000080208000 R erodata
0000000080208000 R sdata
0000000080209000 B boot_stack_lower_bound
0000000080209000 D edata
0000000080219000 B boot_stack_top
0000000080219000 B sbss
000000008021a000 B ebss
000000008021a000 B ekernel
```

### 打印段布局

```shell
rust-size -A -x target/riscv64gc-unknown-none-elf/debug/os
```

可能的输出：

```terminaloutput
target/riscv64gc-unknown-none-elf/debug/os  :
section                  size         addr
.text                  0x520c   0x80200000
.rodata                0x10e0   0x80206000
.data                   0x1d0   0x80208000
.bss                  0x10010   0x80209000
.debug_abbrev          0x3314            0
.debug_info           0x32f83            0
.debug_aranges         0x3280            0
.debug_str            0x429c2            0
.comment                 0x48            0
.riscv.attributes        0x3e            0
.debug_frame           0x21e0            0
.debug_line           0x278c3            0
.debug_ranges         0x1f1b0            0
.debug_loc              0x190            0
Total                 0xdb20e
```
