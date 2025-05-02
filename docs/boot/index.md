---
sidebar_position: 4
---

# 启动流程

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
