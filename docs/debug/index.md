---
sidebar_position: 3
---

# 代码调试

本节以 `ch2` 为例，记录了在 rCore
项目中配置和使用调试工具的过程，包括调试前的准备、环境配置、断点设置、调试服务启动、断开与重连、内存检视等常用流程。希望这些内容能为大家调试和定位问题提供一些参考。

## 调试前准备

首先需要对代码进行一些配置的修改。

:::warning

Rust 在 `dev`（开发）和 `release`（发布）模式下行为差异较大：

- 例如，向 `0x0` 地址写入数据时，`dev` 模式会 Panic，而 `release` 模式不会。
- `dev` 模式生成的程序体积更大，可能导致（但不限于）内核栈空间不足等问题，需参考「[内核栈空间不足](#内核栈空间不足)」小节进行相应修改。

如遇难以解决的问题，可切换回 `release` 模式，此时仍可使用 GDB 调试汇编代码，但调试体验可能不如
`dev` 模式（开发模式，默认包含调试信息）。

:::

### 用户项目修改

修改 `user/src/linker.ld` 文件，链接时需保留 debug 信息：

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

如无需调试用户程序，可跳过本小节。

:::

由于多个用户程序的内存地址可能重叠，为避免断点相互干扰，建议每次只调试一个用户程序。

以调试 `user/src/bin/ch2b_hello_world.rs` 为例，需要修改
`user/Makefile`，将基础测试的目标限定为该程序：

```diff
diff --git a/Makefile b/Makefile
index e523853..95c0e6b 100644
--- a/Makefile
+++ b/Makefile
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

```terminaloutput
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
cd <实验仓库>/os
make build
```

例如：

```shell
cd ~/GitHub/2025s-rcore-jiangshengdev/os
make build
```

以生成带有调试信息的可执行文件。

## 调试系统程序

:::info

[CLion](https://www.jetbrains.com/zh-cn/clion/)（对非商业用途免费）是一款
**适用于 C 和 C++ 的跨平台 IDE**。

安装 [Rust 插件](https://plugins.jetbrains.com/plugin/22407-rust)
后，CLion 亦可支持 Rust 代码的调试，并且其「远程调试」功能目前是 RustRover 所不具备的。

:::

### 配置调试环境

使用 CLion 打开 `<实验仓库>/os` 项目目录。

点击菜单中的「运行 -> 编辑配置...」，打开「运行/调试配置」弹窗。

![debug-config-start.webp](_assets/webp/light/debug-config-start.webp#gh-light-mode-only)
![debug-config-start.webp](_assets/webp/dark/debug-config-start.webp#gh-dark-mode-only)

然后点击左上角的加号，在「添加新配置」菜单中选择「远程调试」。

填入如下参数：

- 名称：`gdbclient`
- 'target remote' 实参：`localhost:1234`
- 符号文件：
  - `$ProjectFileDir$/target/riscv64gc-unknown-none-elf/debug/os` 或
  - `<实验仓库>/os/target/riscv64gc-unknown-none-elf/debug/os`

![debug-config-finish.webp](_assets/webp/light/debug-config-finish.webp#gh-light-mode-only)
![debug-config-finish.webp](_assets/webp/dark/debug-config-finish.webp#gh-dark-mode-only)

### 设置断点

在 `os/src/main.rs` 文件的 `rust_main` 函数中添加行断点。

![break-point.webp](_assets/webp/light/break-point.webp#gh-light-mode-only)
![break-point.webp](_assets/webp/dark/break-point.webp#gh-dark-mode-only)

### 启动调试服务

在项目 `os` 目录下执行如下命令以启动调试服务器端：

```shell
cd <实验仓库>/os
make gdbserver
```

例如：

```shell
cd ~/GitHub/2025s-rcore-jiangshengdev/os
make gdbserver
```

![gdbserver.webp](_assets/webp/light/gdbserver.webp#gh-light-mode-only)
![gdbserver.webp](_assets/webp/dark/gdbserver.webp#gh-dark-mode-only)

### 连接调试客户端

点击 CLion 菜单中的「运行 -> 调试...」，然后在弹出的菜单中选择刚刚配置好的
`gdbclient` 远程调试选项。

![gdbclient.webp](_assets/webp/light/gdbclient.webp#gh-light-mode-only)
![gdbclient.webp](_assets/webp/dark/gdbclient.webp#gh-dark-mode-only)

即可在断点处暂停，至此可以进行 `os` 程序的调试。

### 断开远程连接

执行至 `os/src/batch.rs` 文件中的 `__restore` 函数入口处。

在 CLion 调试工具窗口的 GDB 标签页中执行如下命令，即可断开与调试服务器端的连接：

```gdb
disconnect
```

![clion-disconnect.webp](_assets/webp/light/clion-disconnect.webp#gh-light-mode-only)
![clion-disconnect.webp](_assets/webp/dark/clion-disconnect.webp#gh-dark-mode-only)

此时控制台会显示：「调试器已断开连接」。

![clion-disconnected.webp](_assets/webp/light/clion-disconnected.webp#gh-light-mode-only)
![clion-disconnected.webp](_assets/webp/dark/clion-disconnected.webp#gh-dark-mode-only)

### 重新连接

在终端，启动另一个调试客户端 `gdbclient`：

```shell
cd <实验仓库>/os
make gdbclient
```

例如：

```shell
cd ~/GitHub/2025s-rcore-jiangshengdev/os
make gdbclient
```

可再次连接到上次断开的位置，然后连续使用 `si` 命令（两次左右）则可单步进入到
`__restore` 函数中：

![gdbclient-connect.webp](_assets/webp/light/gdbclient-connect.webp#gh-light-mode-only)
![gdbclient-connect.webp](_assets/webp/dark/gdbclient-connect.webp#gh-dark-mode-only)

然后在 `__restore` 函数中继续使用一次 `si` 命令执行 `mv sp, a0` 这一行代码，将内核栈顶地址赋值给
`sp` 寄存器。

### 内存检视

在 GDB 中执行「检视内存（Examining Memory）」的命令，即可查看内存中的值。

例如，使用如下命令即可检视从当前 `sp` 寄存器值所保存的地址开始的 34 个「巨字（Giant words，8
字节）」的值，并以 16 进制显示：

```gdb
x /34gx $sp
```

![examining-memory.webp](_assets/webp/light/examining-memory.webp#gh-light-mode-only)
![examining-memory.webp](_assets/webp/dark/examining-memory.webp#gh-dark-mode-only)

可以看到这时显示的刚好是内核栈顶的内容。

## 调试用户程序

:::tip

如无需调试用户程序，可跳过本小节。

:::

### 断开远程连接

在 `__restore` 函数结束前，先在 GDB 中执行 `disconnect`，以断开与调试服务器的连接。

![before-user.webp](_assets/webp/light/before-user.webp#gh-light-mode-only)
![before-user.webp](_assets/webp/dark/before-user.webp#gh-dark-mode-only)

此时可以看到 `__restore` 函数末尾有 `sret` 指令，执行后将切换到用户态继续运行。

### 配置调试环境

使用 CLion 打开 `<实验仓库>/user` 项目目录。

点击菜单中的「运行 -> 编辑配置...」，打开「运行/调试配置」弹窗。

然后点击左上角的加号，在「添加新配置」菜单中选择「远程调试」。

填入如下参数：

- 名称：`gdbclient`
- 'target remote' 实参：`localhost:1234`
- 符号文件：
  - `$ProjectFileDir$/target/riscv64gc-unknown-none-elf/debug/ch2b_hello_world` 或
  - `<实验仓库>/user/target/riscv64gc-unknown-none-elf/debug/ch2b_hello_world`

![user-config.webp](_assets/webp/light/user-config.webp#gh-light-mode-only)
![user-config.webp](_assets/webp/dark/user-config.webp#gh-dark-mode-only)

### 设置断点

在 `user/src/bin/ch2b_hello_world.rs` 文件的 `main` 函数中添加行断点。

![user-break-point.webp](_assets/webp/light/user-break-point.webp#gh-light-mode-only)
![user-break-point.webp](_assets/webp/dark/user-break-point.webp#gh-dark-mode-only)

### 连接调试客户端

点击 CLion 菜单中的「运行 -> 调试...」，然后在弹出的菜单中选择刚刚配置好的
`gdbclient` 远程调试选项。

![user-gdbclient.webp](_assets/webp/light/user-gdbclient.webp#gh-light-mode-only)
![user-gdbclient.webp](_assets/webp/dark/user-gdbclient.webp#gh-dark-mode-only)

即可在断点处暂停，至此可以进行 `user` 程序的调试。

## 常见问题

### 无法查看变量

在调试 `user/src/syscall.rs` 文件的 `syscall` 等方法时，可能会遇到变量显示为
`<optimized out>` 的情况。

此时可以尝试添加编译器屏障（compiler fence）来指定内存顺序，避免变量被优化掉。参考如下修改：

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

此时可尝试增大内核栈空间来解决，参考如下修改：

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

### 版本号不一致

在 `ch7` 分支中，Rust 工具链版本与其他分支不一致，导致在 macOS 下无法正常构建。需要将版本号修改为与其他分支保持一致，参考如下修改：

```diff
 rust-toolchain.toml | 2 +-

@@ -1,5 +1,5 @@
 [toolchain]
 profile = "minimal"
 # use the nightly version of the last stable toolchain, see <https://forge.rust-lang.org/>
-channel = "nightly-2024-02-25"
+channel = "nightly-2024-05-02"
 components = ["rust-src", "llvm-tools-preview", "rustfmt", "clippy"]
```

修改的提交细节可查看：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/commit/f3e88d8111f108632c49ae14fa8d2a7657cca58f

### 简易文件系统空间不足

`ch6` 和 `ch7` 分支引入了简易文件系统功能，在调试模式下可能出现空间不足的问题。需要将构建模式改为 debug 并调大文件系统空间，参考如下修改：

```diff
 easy-fs-fuse/src/main.rs |  6 +++---
 os/Makefile              | 10 +++++-----
 os/src/config.rs         |  2 +-

@@ -55,11 +55,11 @@ fn easy_fs_pack() -> std::io::Result<()> {
             .write(true)
             .create(true)
             .open(format!("{}{}", target_path, "fs.img"))?;
-        f.set_len(16 * 2048 * 512).unwrap();
+        f.set_len(160 * 2048 * 512).unwrap();
         f
     })));
-    // 16MiB, at most 4095 files
-    let efs = EasyFileSystem::create(block_file, 16 * 2048, 1);
+    // 160MiB, at most 4095 files
+    let efs = EasyFileSystem::create(block_file, 160 * 2048, 1);
     let root_inode = Arc::new(EasyFileSystem::root_inode(&efs));
     let apps: Vec<_> = read_dir(src_path)
         .unwrap()

@@ -1,6 +1,6 @@
 # Building
 TARGET := riscv64gc-unknown-none-elf
-MODE := release
+MODE := debug
 KERNEL_ELF := target/$(TARGET)/$(MODE)/os
 KERNEL_BIN := $(KERNEL_ELF).bin
 DISASM_TMP := target/$(TARGET)/$(MODE)/asm
@@ -51,7 +51,7 @@ $(KERNEL_BIN): kernel
 fs-img: $(APPS)
 	@make -C ../user build TEST=$(TEST) CHAPTER=$(CHAPTER) BASE=$(BASE)
 	@rm -f $(FS_IMG)
-	@cd ../easy-fs-fuse && cargo run --release -- -s ../user/build/app/ -t ../user/target/riscv64gc-unknown-none-elf/release/
+	@cd ../easy-fs-fuse && cargo run $(MODE_ARG) -- -s ../user/build/app/ -t ../user/target/riscv64gc-unknown-none-elf/$(MODE)/

 kernel:
 	@make -C ../user build TEST=$(TEST) CHAPTER=$(CHAPTER) BASE=$(BASE)
@@ -88,9 +88,9 @@ debug: build

 gdbserver: build
 	@qemu-system-riscv64 -M 128m -machine virt -nographic -bios $(BOOTLOADER) -device loader,file=$(KERNEL_BIN),addr=$(KERNEL_ENTRY_PA) \
-	-drive file=$(FS_IMG),if=none,format=raw,id=x0 \
-        -device virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0 \
-	-s -S
+		-drive file=$(FS_IMG),if=none,format=raw,id=x0 \
+		-device virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0 \
+		-s -S

 gdbclient:
 	@riscv64-unknown-elf-gdb -ex 'file $(KERNEL_ELF)' -ex 'set arch riscv:rv64' -ex 'target remote localhost:1234'

@@ -5,7 +5,7 @@
 /// user app's stack size
 pub const USER_STACK_SIZE: usize = 4096 * 2;
 /// kernel stack size
-pub const KERNEL_STACK_SIZE: usize = 4096 * 2;
+pub const KERNEL_STACK_SIZE: usize = 4096 * 4;
 /// kernel heap size
 pub const KERNEL_HEAP_SIZE: usize = 0x200_0000;
```

:::warning

`ch6` 分支的 `os/Makefile` 文件中的 `gdbserver` 参数配置不完整，缺少块设备相关配置，请参考 `ch7` 分支的完整配置进行补全。

:::

修改的提交细节可查看：

> https://github.com/LearningOS/2025s-rcore-jiangshengdev/commit/7312670c810f80a8d85b9536a8a9fc9e4f3cb5dd

---

调试相关的基本流程就整理到这里了。如果有更好的方法或遇到新问题，欢迎补充和交流。

## 参考资料

- [GDB 官方文档](https://sourceware.org/gdb/documentation/)
- [GDB 检视内存官方文档](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Memory.html#Memory)
- [CLion 调试官方文档](https://www.jetbrains.com/help/clion/debugging-code.html)
- [CLion 远程调试官方文档](https://www.jetbrains.com/help/clion/remote-debug.html)
