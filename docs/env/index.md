---
sidebar_position: 2
---

# 环境准备

本节记录了在 macOS（Apple M1/M2 芯片，Sequoia 15.4.1 及以上）下配置 rCore
实验开发环境的详细过程，包括 Rust、QEMU、GDB
及相关工具的安装与验证。希望这些步骤能帮助大家顺利完成环境搭建。

与 rCore-Tutorial-Guide-2025S 文档中的 **第零章：实验环境配置** 重复部分不单独列出。

> https://learningos.cn/rCore-Tutorial-Guide-2025S/0setup-devel-env.html

## macOS 环境准备

:::note

请确保使用 Apple M1 或 M2 等芯片。

请确保使用 macOS Sequoia 15.4.1 版本系统。

其他芯片型号或系统版本尚未经过充分测试，配置过程中可能会遇到未预料的问题，建议优先使用推荐的硬件与系统环境。

:::

## Rust 开发环境

请参考 Rust 官方入门文档：

> https://www.rust-lang.org/zh-CN/learn/get-started

## 安装 QEMU 模拟器

实验需要使用 QEMU 7.0.0 版本。目前 Homebrew 已不再提供 QEMU 7.0.0
及更低版本的安装包，因此需通过源码手动编译并安装 QEMU
模拟器。

参考 Building QEMU for macOS。

> https://wiki.qemu.org/Hosts/Mac#Building_QEMU_for_macOS

### 下载 QEMU 源码包

你可以使用 `wget` 命令直接将 QEMU 7.0.0 源码包下载到指定目录（如 `~/Develop`）：

```shell
brew install wget  # 如果尚未安装 wget
mkdir -p ~/Develop
cd ~/Develop
wget https://download.qemu.org/qemu-7.0.0.tar.xz
```

> https://download.qemu.org/qemu-7.0.0.tar.xz

或者你也可以直接使用浏览器下载上述链接的源码包。

:::warning

请勿下载 7.2.17、8.2.10、9.2.3、10.0.0 等较新版本，否则可能需要对实验代码进行适配和修改，建议严格按照指定版本安装。

:::

### 解压 QEMU 源码包

下载完成后，使用如下命令解压源码包：

```shell
cd ~/Develop
tar -xf qemu-7.0.0.tar.xz
```

你也可以使用「归档实用工具」等图形界面工具，将源码包解压到你指定的文件夹（如
`~/Develop`）。

### 编译安装 QEMU

安装 QEMU 编译所需依赖，配置、编译并安装 QEMU：

```shell
# 安装编译所需的依赖包
brew install ninja
brew install pkgconf
brew install glib
brew install meson
brew install pixman
```

```shell
# 配置、编译并安装 QEMU
cd ~/Develop/qemu-7.0.0
./configure --target-list=riscv64-softmmu
make -j$(sysctl -n hw.ncpu)
```

:::info

Homebrew 是 macOS（或 Linux）缺失的软件包的管理器。

使用 Homebrew 安装 Apple（或您的 Linux 系统）没有预装但 **你需要的东西**。更多信息可以查看：

https://brew.sh/zh-cn/

:::

### 重命名可执行文件

编译完成后，需将生成的可执行文件重命名以便后续脚本调用：

```shell
# 复制并重命名
cd ~/Develop/qemu-7.0.0/build
cp qemu-system-riscv64-unsigned qemu-system-riscv64
```

:::tip

QEMU 7.0.0 在不同系统下生成的可执行文件名可能不同。请在 `build` 目录下用 `ls`
命令确认实际生成的文件名。

如果没有 `qemu-system-riscv64-unsigned`，请根据实际文件名进行重命名或软链接操作。

:::

### 配置环境变量

编辑 `~/.zshrc` 文件（如果使用的是默认的 zsh 终端），将 QEMU 路径加入环境变量
`PATH`：

```shell
# 注意 $HOME 是 macOS 自动设置的，表示你家目录的环境变量，你也可以根据实际位置灵活调整。
export PATH="$HOME/Develop/qemu-7.0.0/build/:$PATH"
```

如果你将 QEMU 下载解压在其他目录，请相应修改路径。

重启一个新的终端，或执行 `source ~/.zshrc` 使配置立即生效。

### 验证安装

完成编译和安装后，可以通过以下命令验证 QEMU 是否安装成功：

```shell
qemu-system-riscv64 --version
```

应当会看到如下输出：

```
QEMU emulator version 7.0.0
Copyright (c) 2003-2022 Fabrice Bellard and the QEMU Project developers
```

## 运行 rCore 实验

参考 rCore-Tutorial-Guide-2025S 文档。

> https://learningos.cn/rCore-Tutorial-Guide-2025S/0setup-devel-env.html#rcore-tutorial

如果你的环境配置正确，你应当会看到如下输出：

![run.webp](_assets/webp/light/run.webp#gh-light-mode-only)
![run.webp](_assets/webp/dark/run.webp#gh-dark-mode-only)

## 检查器依赖

ci-user 检查器依赖 `timeout` 工具（用于限制命令执行时间），可通过以下命令安装核心工具集：

```shell
brew install coreutils
```

## GDB 调试工具

:::tip

使用 GDB debug 并不是必须的，你可以暂时跳过本小节。

:::

### 安装 GDB

你可以使用 Homebrew 进行安装：

```shell
brew install riscv64-elf-gdb
```

### 重命名 GDB

安装后可执行文件与实验脚本中的名称不一致，还需要重命名。请根据实际文件名进行重命名或软链接操作：

```shell
# 复制并重命名
cd /opt/homebrew/bin/
cp riscv64-elf-gdb riscv64-unknown-elf-gdb
```

### 验证 GDB 版本

安装并重命名完成后，可以通过以下命令验证 GDB 是否安装成功：

```shell
riscv64-unknown-elf-gdb
```

如果安装成功，执行上述命令后应看到类似如下的版本和版权信息输出（仅供参考，实际内容可能略有不同）：

```
GNU gdb (GDB) 16.3
Copyright (C) 2024 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "--host=aarch64-apple-darwin24.4.0 --target=riscv64-elf".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word".
>>> quit
```

可以按下 `control + D`（即 `⌃ D`）来退出 GDB。

## 安装 GDB dashboard

:::tip

使用 GDB dashboard 并不是必须的，你可以暂时跳过本小节。

:::

### 下载配置文件

```shell
brew install wget
wget -P ~ https://github.com/cyrus-and/gdb-dashboard/raw/master/.gdbinit
```

### 启动 gdbserver

进入 rCore-Tutorial 代码目录并启动 `gdbserver`：

```shell
cd ~/GitHub/rCore-Tutorial-Code-2025S/os
make gdbserver
```

执行结果如下：

![gdbserver.webp](_assets/webp/light/gdbserver.webp#gh-light-mode-only)
![gdbserver.webp](_assets/webp/dark/gdbserver.webp#gh-dark-mode-only)

待后续调试完成后，通常 rCore 会自动关闭 QEMU。如果需要强制结束 QEMU，可以先按下
`control + A`（即 `⌃ A`），再按下 `X`。

### 启动 gdbclient

打开另外一个终端，启动 `gdbclient`：

```shell
cd ~/GitHub/rCore-Tutorial-Code-2025S/os
make gdbclient
```

执行结果如下：

![gdbclient.webp](_assets/webp/light/gdbclient.webp#gh-light-mode-only)
![gdbclient.webp](_assets/webp/dark/gdbclient.webp#gh-dark-mode-only)

可以按下 `control + D`（即 `⌃ D`）两次来退出 GDB。

第一次按下会提示 `Quit anyway?`，再次按下来确认退出。

---

到这里，rCore 实验环境的配置过程就全部记录完了。如果后续遇到问题，欢迎随时参考本页内容或相关文档，也欢迎交流补充。
