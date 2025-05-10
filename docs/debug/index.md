---
sidebar_position: 3
---

# 代码调试

本节以 `ch2` 为例，记录了在 rCore
项目中配置和使用调试工具的过程，包括调试前的准备、环境配置、断点设置、调试服务启动、断开与重连、内存检视等常用流程。希望这些内容能为大家调试和定位问题提供一些参考。

## 调试前准备

首先需要对代码进行一些配置的修改。

:::danger

Rust 在 `dev`（调试）和 `release`（发布）模式下行为差异较大：

- 例如，向 `0x0` 地址写入数据时，`dev` 模式会 Panic，而 `release` 模式不会。
- `dev`
  模式生成的程序体积更大，可能导致（但不限于）内核栈空间不足等问题，需参考 [内核栈空间不足](#内核栈空间不足)
  进行相应修改。

如遇到难以解决的问题，可切换回 `release` 模式，此时仍可用 GDB 调试汇编代码，但调试体验可能不如
`dev` 模式。

:::

### 用户项目修改

修改 `user/src/linker.ld` 文件，链接时需要保留 debug 信息：

```diff
 src/linker.ld | 1 -

@@ -28,6 +28,5 @@ SECTIONS
     }
     /DISCARD/ : {
         *(.eh_frame)
-        *(.debug*)
     }
 }
```

修改 `user/build.py` 文件，配置默认 debug 模式：

```diff
 build.py      | 2 +-

@@ -8,7 +8,7 @@ app_id = 0
 apps = os.listdir("build/app")
 apps.sort()
 chapter = os.getenv("CHAPTER")
-mode = os.getenv("MODE", default = "release")
+mode = os.getenv("MODE", default = "debug")
 if mode == "release" :
 	mode_arg = "--release"
 else :
```

修改 `user/Makefile` 文件，配置默认 debug 模式：

```diff
 Makefile      | 2 +-

@@ -1,5 +1,5 @@
 TARGET := riscv64gc-unknown-none-elf
-MODE := release
+MODE := debug
 APP_DIR := src/bin
 TARGET_DIR := target/$(TARGET)/$(MODE)
 BUILD_DIR := build
```

修改的提交细节可查看：

> https://github.com/jiangshengdev/rCore-Tutorial-Test-2025S/commit/247d9c295f0b93e97ccca073bef226bc86b32b76

### 系统项目修改

修改 `os/Makefile` 文件，配置默认 debug 模式：

```diff
 os/Makefile | 2 +-

@@ -1,6 +1,6 @@
 # Building
 TARGET := riscv64gc-unknown-none-elf
-MODE := release
+MODE := debug
 KERNEL_ELF := target/$(TARGET)/$(MODE)/os
 KERNEL_BIN := $(KERNEL_ELF).bin
 DISASM_TMP := target/$(TARGET)/$(MODE)/asm
```

修改的提交细节可查看：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/commit/0b72ba0cf8f6679f893c4b32bebd084186ca835a

### 选择用户程序

:::tip

如无需调试用户程序，可跳过本节。

:::

由于多个用户程序的内存地址可能重叠，为避免断点相互干扰，建议每次只调试一个用户程序。

以调试 `user/src/bin/ch2b_hello_world.rs` 为例，需要修改
`user/Makefile`，将基础测试仅运行该程序：

```diff
diff --git forkSrcPrefix/Makefile forkDstPrefix/Makefile
index e52385322d38503e03f6daafb1f97864da261f63..95c0e6bbf9ca0e5b57012ca7662d84d689058c91 100644
--- forkSrcPrefix/Makefile
+++ forkDstPrefix/Makefile
@@ -27,7 +27,7 @@ else
 	ifeq ($(BASE), 0) # Normal tests only
 		APPS := $(foreach T, $(TESTS), $(wildcard $(APP_DIR)/ch$(T)_*.rs))
 	else ifeq ($(BASE), 1) # Basic tests only
-		APPS := $(foreach T, $(TESTS), $(wildcard $(APP_DIR)/ch$(T)b_*.rs))
+		APPS := $(foreach T, $(TESTS), $(wildcard $(APP_DIR)/ch2b_hello_world.rs))
 	else # Basic and normal
 		APPS := $(foreach T, $(TESTS), $(wildcard $(APP_DIR)/ch$(T)*.rs))
 	endif
```

修改后，在 `os` 目录下执行 `make run`，即可验证只运行了 `ch2b_hello_world.rs`：

```
[kernel] Hello, world!
[kernel] num_app = 1
[kernel] app_0 [0x80212018, 0x8021e208)
[kernel] Loading app_0
Hello, world from user mode program!
All applications completed!
```

### 生成可执行文件

修改完成后，需要执行：

```shell
cd <你的实验项目目录>/os
make build
```

比如：

```shell
cd ~/GitHub/2025s-rcore-jiangshengdev/os
make build
```

以生成带有调试信息的可执行文件。

## 调试系统程序

### 配置调试环境

使用 CLion 打开 `<你的实验项目目录>/os` 项目目录。

点击菜单中的「运行 -> 编辑配置...」，打开「运行/调试配置」弹窗。

![debug-config-start.png](webp/light/debug-config-start.webp#gh-light-mode-only)
![debug-config-start.png](webp/dark/debug-config-start.webp#gh-dark-mode-only)

然后点击左上角的加号，在「添加新配置」菜单中选择「远程调试」。

填入如下参数：

- 名称：`gdbclient`
- 'target remote' 实参：`localhost:1234`
- 符号文件：
  - `$ProjectFileDir$/target/riscv64gc-unknown-none-elf/debug/os`
  - `<你的实验项目目录>/os/target/riscv64gc-unknown-none-elf/debug/os`

![debug-config-finish.png](webp/light/debug-config-finish.webp#gh-light-mode-only)
![debug-config-finish.png](webp/dark/debug-config-finish.webp#gh-dark-mode-only)

### 设置断点

在 `os/src/main.rs` 文件的 `rust_main` 函数中添加行断点。

![break-point.png](webp/light/break-point.webp#gh-light-mode-only)
![break-point.png](webp/dark/break-point.webp#gh-dark-mode-only)

### 启动调试服务

在项目 `os` 目录下执行如下命令以启动调试服务器端：

```shell
cd <你的实验项目目录>/os
make gdbserver
```

比如：

```shell
cd ~/GitHub/2025s-rcore-jiangshengdev/os
make gdbserver
```

![gdbserver.png](webp/light/gdbserver.webp#gh-light-mode-only)
![gdbserver.png](webp/dark/gdbserver.webp#gh-dark-mode-only)

### 连接调试客户端

点击 CLion 菜单中的「运行 -> 调试...」，然后在弹出的菜单中选择刚刚配置的
`gdbclient` 远程调试项目。

![gdbclient.png](webp/light/gdbclient.webp#gh-light-mode-only)
![gdbclient.png](webp/dark/gdbclient.webp#gh-dark-mode-only)

即可在断点处暂停，至此可以进行 `os` 程序的调试。

### 断开远程连接

在 CLion 调试工具窗口的 GDB 标签页中执行如下命令，可以断开与调试服务器端的连接：

```gdb
disconnect
```

![clion-disconnect.png](webp/light/clion-disconnect.webp#gh-light-mode-only)
![clion-disconnect.png](webp/dark/clion-disconnect.webp#gh-dark-mode-only)

控制台会显示：「调试器已断开连接」。

![clion-disconnected.png](webp/light/clion-disconnected.webp#gh-light-mode-only)
![clion-disconnected.png](webp/dark/clion-disconnected.webp#gh-dark-mode-only)

### 重新连接

在终端，启动另外一个调试客户端 `gdbclient`：

```shell
cd <你的实验项目目录>/os
make gdbclient
```

比如：

```shell
cd ~/GitHub/2025s-rcore-jiangshengdev/os
make gdbclient
```

可以再次连接到上次断开的位置，然后连续使用 `si` 命令（两次左右）可以单步进入到
`__restore` 函数中：

![gdbclient-connect.png](webp/light/gdbclient-connect.webp#gh-light-mode-only)
![gdbclient-connect.png](webp/dark/gdbclient-connect.webp#gh-dark-mode-only)

然后在 `__restore` 函数中继续使用一次 `si` 命令执行 `mv sp, a0` 这一行代码，将内核栈顶地址赋值给
`sp` 寄存器。

### 内存检视

在 GDB 中执行与「检视内存（Examining Memory）」相关的命令，即可查看内存中的值。

例如，使用如下命令即可检视当前 `sp` 寄存器指向的内存中 34 个「巨字（Giant words，8
字节）」的值，并以 16 进制显示：

```gdb
x /34gx $sp
```

![examining-memory.png](webp/light/examining-memory.webp#gh-light-mode-only)
![examining-memory.png](webp/dark/examining-memory.webp#gh-dark-mode-only)

可以看到这时显示的刚好是内核栈顶的内容。

## 调试用户程序

:::tip

如无需调试用户程序，可跳过本节。

:::

### 断开远程连接

在 `__restore` 函数结束前，先在 GDB 中执行 `disconnect`，以断开与调试服务器的连接。

![before-user.webp](webp/light/before-user.webp#gh-light-mode-only)
![before-user.webp](webp/dark/before-user.webp#gh-dark-mode-only)

此时可以看到 `__restore` 函数末尾有 `sret` 指令，执行后将切换到用户态继续运行。

### 配置调试环境

使用 CLion 打开 `<你的实验项目目录>/user` 项目目录。

点击菜单中的「运行 -> 编辑配置...」，打开「运行/调试配置」弹窗。

然后点击左上角的加号，在「添加新配置」菜单中选择「远程调试」。

填入如下参数：

- 名称：`gdbclient`
- 'target remote' 实参：`localhost:1234`
- 符号文件：
  - `$ProjectFileDir$/target/riscv64gc-unknown-none-elf/debug/ch2b_hello_world`
  - `<你的实验项目目录>/user/target/riscv64gc-unknown-none-elf/debug/ch2b_hello_world`

![user-config.webp](webp/light/user-config.webp#gh-light-mode-only)
![user-config.webp](webp/dark/user-config.webp#gh-dark-mode-only)

### 设置断点

在 `user/src/bin/ch2b_hello_world.rs` 文件的 `main` 函数中添加行断点。

![user-break-point.webp](webp/light/user-break-point.webp#gh-light-mode-only)
![user-break-point.webp](webp/dark/user-break-point.webp#gh-dark-mode-only)

### 连接调试客户端

点击 CLion 菜单中的「运行 -> 调试...」，然后在弹出的菜单中选择刚刚配置的
`gdbclient` 远程调试项目。

![user-gdbclient.webp](webp/light/user-gdbclient.webp#gh-light-mode-only)
![user-gdbclient.webp](webp/dark/user-gdbclient.webp#gh-dark-mode-only)

即可在断点处暂停，至此可以进行 `user` 程序的调试。

## 常见问题

### 无法查看变量

在调试 `user/src/syscall.rs` 文件的 `syscall` 方法时，可能会遇到变量显示为
`<optimized out>` 的情况。

此时可以通过添加编译器屏障（compiler fence）来指定内存顺序，避免变量被优化掉。参考如下修改：

```diff
 src/syscall.rs | 6 ++++++

@@ -1,4 +1,6 @@
 use crate::SignalAction;
+use core::sync::atomic::compiler_fence;
+use core::sync::atomic::Ordering;

 use super::{Stat, TimeVal};

@@ -47,6 +49,7 @@ pub const SYSCALL_CONDVAR_WAIT: usize = 473;

 pub fn syscall(id: usize, args: [usize; 3]) -> isize {
     let mut ret: isize;
+    compiler_fence(Ordering::SeqCst);
     unsafe {
         core::arch::asm!(
             "ecall",
@@ -56,11 +59,13 @@ pub fn syscall(id: usize, args: [usize; 3]) -> isize {
             in("x17") id
         );
     }
+    compiler_fence(Ordering::SeqCst);
     ret
 }

 pub fn syscall6(id: usize, args: [usize; 6]) -> isize {
     let mut ret: isize;
+    compiler_fence(Ordering::SeqCst);
     unsafe {
         core::arch::asm!("ecall",
             inlateout("x10") args[0] => ret,
@@ -72,6 +77,7 @@ pub fn syscall6(id: usize, args: [usize; 6]) -> isize {
             in("x17") id
         );
     }
+    compiler_fence(Ordering::SeqCst);
     ret
 }
```

修改的提交细节可查看：

> https://github.com/jiangshengdev/rCore-Tutorial-Test-2025S/commit/44d2f17ebc9c21a88903af234d89a8b2506d7522

### 内核栈空间不足

在 `ch5` 中，默认的内核栈空间较小，可能会导致程序卡住或无法正常运行。

此时可以通过增大内核栈空间来解决，参考如下修改：

```diff
 os/src/config.rs            |   2 +-

@@ -5,7 +5,7 @@
 /// user app's stack size
 pub const USER_STACK_SIZE: usize = 4096 * 2;
 /// kernel stack size
-pub const KERNEL_STACK_SIZE: usize = 4096 * 2;
+pub const KERNEL_STACK_SIZE: usize = 4096 * 4;
 /// kernel heap size
 pub const KERNEL_HEAP_SIZE: usize = 0x200_0000;
```

修改的提交细节可查看：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/commit/fa9263c77cb1e9979ac6173ce28b369ce973530e

---

调试相关的基本流程就整理到这里了。如果有更好的方法或遇到新问题，欢迎补充和交流。
