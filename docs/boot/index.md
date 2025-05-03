---
sidebar_position: 4
---

# 启动流程

系统启动可以看成是从内存某个地址开始执行代码，启动完成后跳转到另一个地址继续运行。而这些地址的意义依赖于内存映射。因此，我们需要了解内存映射。

## 内存映射

QEMU RISC-V virt 虚拟机的内存映射表定义在以下文件：

`qemu-7.0.0/hw/riscv/virt.c`

```c
static const MemMapEntry virt_memmap[] = {
    [VIRT_DEBUG] =       {        0x0,         0x100 },
    [VIRT_MROM] =        {     0x1000,        0xf000 },
    [VIRT_TEST] =        {   0x100000,        0x1000 },
    [VIRT_RTC] =         {   0x101000,        0x1000 },
    [VIRT_CLINT] =       {  0x2000000,       0x10000 },
    [VIRT_ACLINT_SSWI] = {  0x2F00000,        0x4000 },
    [VIRT_PCIE_PIO] =    {  0x3000000,       0x10000 },
    [VIRT_PLIC] =        {  0xc000000, VIRT_PLIC_SIZE(VIRT_CPUS_MAX * 2) },
    [VIRT_APLIC_M] =     {  0xc000000, APLIC_SIZE(VIRT_CPUS_MAX) },
    [VIRT_APLIC_S] =     {  0xd000000, APLIC_SIZE(VIRT_CPUS_MAX) },
    [VIRT_UART0] =       { 0x10000000,         0x100 },
    [VIRT_VIRTIO] =      { 0x10001000,        0x1000 },
    [VIRT_FW_CFG] =      { 0x10100000,          0x18 },
    [VIRT_FLASH] =       { 0x20000000,     0x4000000 },
    [VIRT_IMSIC_M] =     { 0x24000000, VIRT_IMSIC_MAX_SIZE },
    [VIRT_IMSIC_S] =     { 0x28000000, VIRT_IMSIC_MAX_SIZE },
    [VIRT_PCIE_ECAM] =   { 0x30000000,    0x10000000 },
    [VIRT_PCIE_MMIO] =   { 0x40000000,    0x40000000 },
    [VIRT_DRAM] =        { 0x80000000,           0x0 },
};
```

我们重点关注下表中的两个关键设备：

| Enum      | Base       | Size   | Concept                      |
|-----------|------------|--------|------------------------------|
| VIRT_MROM | 0x1000     | 0xf000 | Mask Read-only memory        |
| VIRT_DRAM | 0x80000000 | 0x0    | Dynamic random-access memory |

### MROM（掩模只读存储器）

MROM（Mask ROM）是 QEMU RISC-V virt 虚拟机中的掩模只读存储器，物理地址起始于 0x1000。根据 QEMU
源码（`hw/riscv/boot.c`），MROM 区域存储着系统的 Reset Vector 信息。

### DRAM（动态随机存取存储器）

DRAM（Dynamic RAM）是 QEMU RISC-V virt 虚拟机中的动态随机存取存储器，物理地址起始于 0x80000000。根据 QEMU
源码（`hw/riscv/virt.c`），DRAM 区域用于存放 SBI 固件（如 OpenSBI）。

## 固件动态信息

在详细了解 Reset Vector 中的启动指令之前，还需要先了解固定动态信息数据结构，因为第一条指令就用到固定动态信息的地址。

动态信息基于 OpenSBI，定义在以下文件中：

`qemu-7.0.0/include/hw/riscv/boot_opensbi.h`

```c
/* SPDX-License-Identifier: BSD-2-Clause */
/*
 * Copyright (c) 2019 Western Digital Corporation or its affiliates.
 *
 * Based on include/sbi/{fw_dynamic.h,sbi_scratch.h} from the OpenSBI project.
 */
#ifndef OPENSBI_H
#define OPENSBI_H

/** Expected value of info magic ('OSBI' ascii string in hex) */
#define FW_DYNAMIC_INFO_MAGIC_VALUE     0x4942534f

/** Maximum supported info version */
#define FW_DYNAMIC_INFO_VERSION         0x2

/** Possible next mode values */
#define FW_DYNAMIC_INFO_NEXT_MODE_U     0x0
#define FW_DYNAMIC_INFO_NEXT_MODE_S     0x1
#define FW_DYNAMIC_INFO_NEXT_MODE_M     0x3

enum sbi_scratch_options {
    /** Disable prints during boot */
    SBI_SCRATCH_NO_BOOT_PRINTS = (1 << 0),
    /** Enable runtime debug prints */
    SBI_SCRATCH_DEBUG_PRINTS = (1 << 1),
};

/** Representation dynamic info passed by previous booting stage */
struct fw_dynamic_info {
    /** Info magic */
    target_long magic;
    /** Info version */
    target_long version;
    /** Next booting stage address */
    target_long next_addr;
    /** Next booting stage mode */
    target_long next_mode;
    /** Options for OpenSBI library */
    target_long options;
    /**
     * Preferred boot HART id
     *
     * It is possible that the previous booting stage uses same link
     * address as the FW_DYNAMIC firmware. In this case, the relocation
     * lottery mechanism can potentially overwrite the previous booting
     * stage while other HARTs are still running in the previous booting
     * stage leading to boot-time crash. To avoid this boot-time crash,
     * the previous booting stage can specify last HART that will jump
     * to the FW_DYNAMIC firmware as the preferred boot HART.
     *
     * To avoid specifying a preferred boot HART, the previous booting
     * stage can set it to -1UL which will force the FW_DYNAMIC firmware
     * to use the relocation lottery mechanism.
     */
    target_long boot_hart;
};

#endif
```

其属性定义如下表：

| Name      | Concept                     |
|-----------|-----------------------------|
| magic     | Info magic                  |
| version   | Info version                |
| next_addr | Next booting stage address  |
| next_mode | Next booting stage mode     |
| options   | Options for OpenSBI library |
| boot_hart | Preferred boot HART id      |

## 启动指令

virt 通用虚拟平台启动后，会先执行 Reset Vector 中的指令，其定义如下：

`qemu-7.0.0/hw/riscv/boot.c`

```c
void riscv_setup_rom_reset_vec(MachineState *machine, RISCVHartArrayState *harts,
                               hwaddr start_addr,
                               hwaddr rom_base, hwaddr rom_size,
                               uint64_t kernel_entry,
                               uint32_t fdt_load_addr, void *fdt)
{
    int i;
    uint32_t start_addr_hi32 = 0x00000000;

    if (!riscv_is_32bit(harts)) {
        start_addr_hi32 = start_addr >> 32;
    }
    /* reset vector */
    uint32_t reset_vec[10] = {
        0x00000297,                  /* 1:  auipc  t0, %pcrel_hi(fw_dyn) */
        0x02828613,                  /*     addi   a2, t0, %pcrel_lo(1b) */
        0xf1402573,                  /*     csrr   a0, mhartid  */
        0,
        0,
        0x00028067,                  /*     jr     t0 */
        start_addr,                  /* start: .dword */
        start_addr_hi32,
        fdt_load_addr,               /* fdt_laddr: .dword */
        0x00000000,
                                     /* fw_dyn: */
    };
    if (riscv_is_32bit(harts)) {
        reset_vec[3] = 0x0202a583;   /*     lw     a1, 32(t0) */
        reset_vec[4] = 0x0182a283;   /*     lw     t0, 24(t0) */
    } else {
        reset_vec[3] = 0x0202b583;   /*     ld     a1, 32(t0) */
        reset_vec[4] = 0x0182b283;   /*     ld     t0, 24(t0) */
    }

    /* copy in the reset vector in little_endian byte order */
    for (i = 0; i < ARRAY_SIZE(reset_vec); i++) {
        reset_vec[i] = cpu_to_le32(reset_vec[i]);
    }
    rom_add_blob_fixed_as("mrom.reset", reset_vec, sizeof(reset_vec),
                          rom_base, &address_space_memory);
    riscv_rom_copy_firmware_info(machine, rom_base, rom_size, sizeof(reset_vec),
                                 kernel_entry);

    return;
}
```

参考前面环境准备中的启动 `gdbserver` 与 `gdbclient`，在系统启动后暂停并查看当前 PC 寄存器指向的指令内容：

```
x/6i $pc
```

可以打印出将要执行的6条指令。

```riscv
   0x1000:	auipc	t0,0x0
   0x1004:	addi	a2,t0,40
   0x1008:	csrr	a0,mhartid
   0x100c:	ld	a1,32(t0)
   0x1010:	ld	t0,24(t0)
   0x1014:	jr	t0
```

执行前2条指令：

```riscv
   0x1000:	auipc	t0,0x0
   0x1004:	addi	a2,t0,40
```

会将 `a2` 寄存器赋值为 `0x0000000000001028`，其表示 `fw_dyn` 的地址。使用内存检视命令：

```
x/6gx $a2
```

可以打印出固件动态信息的值：

```
0x1028:	0x000000004942534f	0x0000000000000002
0x1038:	0x0000000000000000	0x0000000000000001
0x1048:	0x0000000000000000	0x0000000000000000
```

其中：

- `0x000000004942534f` magic 表示这是固件动态信息的开始
- `0x0000000000000002` version 表示其版本号为 `0x2`，符合最大支持信息版本要求
- `0x0000000000000000` next_addr 的值略显奇怪，并不是所熟知的 `0x0000000080000000` 或 `0x0000000080200000`
- `0x0000000000000001` next_mode 表示下一个可能的模式为 S 态
- `0x0000000000000000` options 未配置选项
- `0x0000000000000000` boot_hart 表示 Preferred boot HART id 为 0 号

由于这块的信息主要是提供给 SBI 使用，在学习 SBI 之前，还不能了解为什么如此设置值，在此时就先略过。

第三条指令：

```riscv
   0x1008:	csrr	a0,mhartid
```

将硬件线程 ID 写入了 `a0` 寄存器，其值为 `0x0`。

接下来的指令：

```riscv
   0x100c:	ld	a1,32(t0)
   0x1010:	ld	t0,24(t0)
```

会将

- `a1` 寄存器赋值为 `0x0000000087000000`，表示设备树的地址
- `t0` 寄存器赋值为 `0x0000000080000000`，表示 SBI 的起始地址

最后的指令：

```riscv
   0x1014:	jr	t0
```

跳转至 SBI 的起始地址继续执行，至此，系统启动完成，接下来执行的就是 SBI 的部分了。
