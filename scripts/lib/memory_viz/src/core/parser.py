"""
GDB 输出解析模块
解析 GDB 内存输出为结构化数据
"""
from typing import List, Dict, Tuple, Any, Optional

from .config import (
    MEMORY_PATTERN_COMPILED, GROUP_CMD_PATTERN_COMPILED, REGISTER_CMD_PATTERN_COMPILED,
    REGISTER_VALUE_PATTERN_COMPILED, REGISTER_LINE_PATTERN_COMPILED, ADDRESS_PATTERN_COMPILED,
    PAGE_SHIFT, DISPLAY_NULL_VAL, MEMORY_STEP, SATP_PPN_MASK, SATP_REGISTER_NAME
)


# 预编译的正则表达式已从 config.py 导入


def parse_gdb_output(lines: List[str]) -> Tuple[Dict[str, str], List[str]]:
    """将 GDB 内存输出解析为地址到值的映射，以及按访问顺序排列的地址列表"""
    memory: Dict[str, str] = {}
    addresses: List[str] = []
    for line in lines:
        match = MEMORY_PATTERN_COMPILED.match(line)
        if not match:
            continue
        addr_int = int(match.group(1), 16)
        addr = f"0x{addr_int:x}"
        values = match.group(2).split()
        for v in values:
            addresses.append(addr)
            memory[addr] = f"0x{int(v, 16):x}"
            # 地址递增一个内存单元
            addr_int += MEMORY_STEP
            addr = f"0x{addr_int:x}"
    return memory, addresses


def parse_gdb_groups(lines: List[str]) -> List[Dict[str, Any]]:
    """将 GDB 内存查看命令和其输出按命令分组，返回每组的命令文本与对应输出行"""
    groups: List[Dict[str, Any]] = []
    curr_group: Optional[Dict[str, Any]] = None
    for line in lines:
        m = GROUP_CMD_PATTERN_COMPILED.match(line)
        if m:
            if curr_group is not None:
                groups.append(curr_group)
            curr_group = {'cmd': line, 'lines': []}
        else:
            if curr_group is not None:
                curr_group['lines'].append(line)
    if curr_group is not None:
        groups.append(curr_group)
    return groups


def is_register_command(line: str) -> bool:
    """检测是否为寄存器命令行"""
    return bool(REGISTER_CMD_PATTERN_COMPILED.match(line.strip()))


def is_register_value_line(line: str) -> bool:
    """检测是否为寄存器值输出行"""
    # 匹配格式：寄存器名 + 空格 + 十六进制值 + 可选的十进制值
    return bool(REGISTER_VALUE_PATTERN_COMPILED.match(line.strip()))


def parse_register_line(line: str) -> Tuple[str, str]:
    """解析单行寄存器输出为 (名称, 值) 对"""
    # 示例输入：satp           0x8000000000083a5b	-9223372036854236581
    match = REGISTER_LINE_PATTERN_COMPILED.match(line.strip())
    if match:
        name = match.group(1)
        value = match.group(2)
        return name, value
    raise ValueError(f"无法解析寄存器行: {line}")


def parse_register_to_memory_format(lines: List[str]) -> Tuple[Dict[str, str], List[str]]:
    """将寄存器输出转换为内存格式，复用现有的内存处理逻辑"""
    memory: Dict[str, str] = {}
    addresses: List[str] = []

    for line in lines:
        if is_register_value_line(line):
            name, value = parse_register_line(line)
            # 使用寄存器名作为"地址"
            memory[name] = value
            addresses.append(name)

    return memory, addresses


def contains_register_output(lines: List[str]) -> bool:
    """检测输入中是否包含寄存器命令"""
    return any(is_register_command(line) for line in lines)


def extract_register_page_number_core(register_name: str, register_value: str) -> int:
    """从寄存器值中提取物理页号的核心逻辑
    
    Args:
        register_name: 寄存器名称，如 "satp"
        register_value: 寄存器值，如 "0x8000000000083a5b"
        
    Returns:
        物理页号（整数），如果无效则返回-1
    """
    try:
        if not register_value or register_value == DISPLAY_NULL_VAL:
            return -1

        # 移除 "0x" 前缀并转为整数
        if register_value.startswith("0x"):
            reg_int = int(register_value[2:], 16)
        else:
            reg_int = int(register_value, 16)

        # 根据寄存器类型进行不同处理
        if register_name.lower() == SATP_REGISTER_NAME:
            # satp寄存器：低44位是PPN，高位忽略
            page_num = reg_int & SATP_PPN_MASK  # 取低44位
            return page_num
        else:
            # 其他寄存器：按普通地址处理，使用页面移位
            return reg_int >> PAGE_SHIFT

    except (ValueError, TypeError):
        return -1


def extract_register_page_number(register_name: str, register_value: str) -> int:
    """从寄存器值中提取物理页号（整数形式）"""
    return extract_register_page_number_core(register_name, register_value)


def extract_register_page_number_display(register_name: str, register_value: str) -> str:
    """从寄存器值中提取物理页号并格式化为显示字符串
    
    Args:
        register_name: 寄存器名称，如 "satp"
        register_value: 寄存器值，如 "0x8000000000083a5b"
        
    Returns:
        格式化的物理页号字符串，如 "0x83a5b" 或空字符串（如果无效）
    """
    page_num = extract_register_page_number_core(register_name, register_value)
    if page_num == -1:
        return ""
    return f"0x{page_num:x}"


def extract_address_from_string(text: str) -> Optional[int]:
    """从字符串中提取第一个十六进制地址
    
    Args:
        text: 包含地址的字符串，如 "(gdb) x /512g 0x83A5B000"
        
    Returns:
        地址的整数值，如果未找到则返回None
    """
    match = ADDRESS_PATTERN_COMPILED.search(text)
    if match:
        return int(match.group(1), 16)
    return None


def extract_page_number_from_address(address: int) -> int:
    """从地址计算物理页号
    
    Args:
        address: 地址的整数值
        
    Returns:
        物理页号（整数）
    """
    return address >> PAGE_SHIFT


def extract_page_number_from_string(text: str) -> Optional[int]:
    """从字符串中提取地址并计算物理页号
    
    Args:
        text: 包含地址的字符串，如 "(gdb) x /512g 0x83A5B000"
        
    Returns:
        物理页号（整数），如果未找到地址则返回None
    """
    address = extract_address_from_string(text)
    if address is not None:
        return extract_page_number_from_address(address)
    return None


def format_page_number_label(text: str) -> str:
    """从字符串中提取地址并格式化为页号标签
    
    Args:
        text: 包含地址的字符串，如 "(gdb) x /512g 0x83A5B000"
        
    Returns:
        格式化的页号标签，如 "Physical Page: 0x83a5b"，如果解析失败返回原字符串
    """
    page_num = extract_page_number_from_string(text)
    if page_num is not None:
        return f"Physical Page: 0x{page_num:x}"
    return text
