---
sidebar_position: 1
---

# 实验环境配置

与 rCore-Tutorial-Guide-2025S 文档中的 **第零章：实验环境配置** 重复部分不单独列出

> https://learningos.cn/rCore-Tutorial-Guide-2025S/0setup-devel-env.html

## OS 环境配置

介绍 macOS 下的环境配置方案

:::note

请确保使用 Apple M1 或 M2 等芯片

请确保使用 macOS Sequoia 15.4.1 版本系统

:::

## Rust 开发环境配置

看 Rust 马上开始

> https://www.rust-lang.org/zh-CN/learn/get-started

## Qemu 模拟器安装

我们需要使用 Qemu 7.0.0 版本进行实验，为此，从源码手动编译安装 Qemu 模拟器：

:::warning

不要下载 7.2.17 版本

:::

看 Building QEMU for macOS

> https://wiki.qemu.org/Hosts/Mac#Building_QEMU_for_macOS

下载 QEMU

> https://download.qemu.org/qemu-7.0.0.tar.xz

解压到下载文件夹

```shell
# 安装编译所需的依赖包
brew install ninja
brew install pkgconf
brew install glib
brew install meson
brew install pixman

# 编译安装并配置 RISC-V 支持
cd qemu-7.0.0
./configure --target-list=riscv64-softmmu
make -j$(nproc)

# 复制并重命名
cd build
cp qemu-system-riscv64-unsigned qemu-system-riscv64
```

编辑 `~/.zshrc` 文件（如果使用的是默认的 zsh 终端），在文件的末尾加入几行：

```shell
# 注意 $HOME 是 macOS 自动设置的表示你家目录的环境变量，你也可以根据实际位置灵活调整
export PATH="$HOME/Downloads/qemu-7.0.0/build/:$PATH"
```

直接重启一个新的终端。

确认 Qemu 的版本：

```shell
qemu-system-riscv64 --version
```

## 试运行 rCore-Tutorial

看 rCore-Tutorial-Guide-2025S 文档

> https://learningos.cn/rCore-Tutorial-Guide-2025S/0setup-devel-env.html#rcore-tutorial

如果你的环境配置正确，你应当会看到如下输出：

```
[rustsbi] RustSBI version 0.3.0-alpha.4, adapting to RISC-V SBI v1.0.0
.______       __    __      _______.___________.  _______..______   __
|   _  \     |  |  |  |    /       |           | /       ||   _  \ |  |
|  |_)  |    |  |  |  |   |   (----`---|  |----`|   (----`|  |_)  ||  |
|      /     |  |  |  |    \   \       |  |      \   \    |   _  < |  |
|  |\  \----.|  `--'  |.----)   |      |  |  .----)   |   |  |_)  ||  |
| _| `._____| \______/ |_______/       |__|  |_______/    |______/ |__|
[rustsbi] Implementation     : RustSBI-QEMU Version 0.2.0-alpha.2
[rustsbi] Platform Name      : riscv-virtio,qemu
[rustsbi] Platform SMP       : 1
[rustsbi] Platform Memory    : 0x80000000..0x88000000
[rustsbi] Boot HART          : 0
[rustsbi] Device Tree Region : 0x87000000..0x87000ef2
[rustsbi] Firmware Address   : 0x80000000
[rustsbi] Supervisor Address : 0x80200000
[rustsbi] pmp01: 0x00000000..0x80000000 (-wr)
[rustsbi] pmp02: 0x80000000..0x80200000 (---)
[rustsbi] pmp03: 0x80200000..0x88000000 (xwr)
[rustsbi] pmp04: 0x88000000..0x00000000 (-wr)
[kernel] Hello, world!
[DEBUG] [kernel] .rodata [0x80202000, 0x80203000)
[ INFO] [kernel] .data [0x80203000, 0x80204000)
[ WARN] [kernel] boot_stack top=bottom=0x80214000, lower_bound=0x80204000
[ERROR] [kernel] .bss [0x80214000, 0x80215000)
```

恭喜你完成了实验环境的配置，可以开始 **GDB 调试支持** 部分了！

## GDB 调试支持\*

:::tip

使用 GDB debug 并不是必须的，你可以暂时跳过本小节。

:::

你可以选择使用 Homebrew 进行安装

```shell
brew install riscv64-elf-gdb
```

并自行重命名可执行文件

---

或者下载 CLion .dmg (Apple Silicon) 并安装

> https://www.jetbrains.com/zh-cn/clion/

然后对 CLion.app 右键并显示包内容，可以看到内部存在 gdb 文件

```shell
# 复制并重命名
cd ~/Applications/CLion.app/Contents/bin/gdb/mac/aarch64/bin/
cp gdb riscv64-unknown-elf-gdb
```

编辑 `~/.zshrc` 文件（如果使用的是默认的 zsh 终端），在文件的末尾加入几行：

```shell
export PATH="$HOME/Applications/CLion.app/Contents/bin/gdb/mac/aarch64/bin/:$PATH"
```

直接重启一个新的终端。

确认 GDB 的版本：

```
riscv64-unknown-elf-gdb
GNU gdb (GDB; JetBrains IDE bundle; build 39) 15.2
Copyright (C) 2024 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "aarch64-apple-darwin23.6.0".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word".
(gdb) quit
```

可以按下 `control+D` 即 `⌃D`，来退出 GDB。

## 安装 GDB dashboard\*\*

:::tip

使用 GDB dashboard 并不是必须的，你可以暂时跳过本小节。

:::

```shell
brew install wget
wget -P ~ https://github.com/cyrus-and/gdb-dashboard/raw/master/.gdbinit
```

```shell
cd ~/GitHub/rCore-Tutorial-Code-2025S/os
make gdbserver
```

![gdbserver.png](image/gdbserver.png)

通常 rCore 会自动关闭 Qemu 。如果在某些情况下需要强制结束，可以先按下 `control+A` 即 `⌃A`，再按下 `X` 来退出 Qemu。

```shell
cd ~/GitHub/rCore-Tutorial-Code-2025S/os
make gdbclient
```

![gdbclient.png](image/gdbclient.png)

可以按下 `control+D` 即 `⌃D` 2 次，来退出 GDB。
