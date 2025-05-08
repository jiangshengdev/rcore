---
sidebar_position: 3
---

# 代码调试

本节以 `ch2` 为例，记录了在 rCore
项目中配置和使用调试工具的过程，包括调试前的准备、环境配置、断点设置、调试服务启动、断开与重连、内存检视等常用流程。希望这些内容能为大家调试和定位问题提供一些参考。

## 调试前准备

首先需要对代码进行一些配置的修改。

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

## 配置调试环境

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

## 设置断点

在 `os/src/main.rs` 文件的 `rust_main` 函数中添加行断点。

![break-point.png](webp/light/break-point.webp#gh-light-mode-only)
![break-point.png](webp/dark/break-point.webp#gh-dark-mode-only)

## 启动调试服务

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

## 连接调试客户端

点击 CLion 菜单中的「运行 -> 调试...」，然后在弹出的菜单中选择刚刚配置的
`gdbclient` 远程调试项目。

![gdbclient.png](webp/light/gdbclient.webp#gh-light-mode-only)
![gdbclient.png](webp/dark/gdbclient.webp#gh-dark-mode-only)

即可在断点处暂停，至此可以进行 `os` 程序的调试。

## 断开远程连接

在 CLion 调试工具窗口的 GDB 标签页中执行如下命令，可以断开与调试服务器端的连接：

```gdb
disconnect
```

![clion-disconnect.png](webp/light/clion-disconnect.webp#gh-light-mode-only)
![clion-disconnect.png](webp/dark/clion-disconnect.webp#gh-dark-mode-only)

控制台会显示：「调试器已断开连接」。

![clion-disconnected.png](webp/light/clion-disconnected.webp#gh-light-mode-only)
![clion-disconnected.png](webp/dark/clion-disconnected.webp#gh-dark-mode-only)

## 重新连接

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

## 内存检视

在 GDB 中执行与「检视内存（Examining Memory）」相关的命令，即可查看内存中的值。

例如，使用如下命令即可检视当前 `sp` 寄存器指向的内存中 34 个「巨字（Giant words，8
字节）」的值，并以 16 进制显示：

```gdb
x /34gx $sp
```

![examining-memory.png](webp/light/examining-memory.webp#gh-light-mode-only)
![examining-memory.png](webp/dark/examining-memory.webp#gh-dark-mode-only)

可以看到这时显示的刚好是内核栈顶的内容。

---

调试相关的基本流程就整理到这里了。如果有更好的方法或遇到新问题，欢迎补充和交流。
