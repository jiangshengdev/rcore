"""
memory_viz 配置管理模块

集中管理所有配置常量，包括：
- 正则表达式模式
- 显示格式常量  
- DOT 布局参数
- 可视化常量

通过集中配置来提高代码的可维护性。

注意：此模块正在重构过程中，配置项将逐步从其他模块迁移至此处
"""

# 命令行参数默认配置
DEFAULT_THEME = 'light'  # 默认主题：浅色模式
DEFAULT_COLUMNS = 4  # 默认内存布局列数
THEME_CHOICES = ['light', 'dark']  # 可选主题列表

# DOT 布局参数 (从 generator.py 迁移)
RANKDIR = "TB"  # 子图布局方向：自顶向下
SPLINES = "ortho"  # 边的样式：使用正交线条
FONT = "SF Mono,monospace"  # 字体名称：等宽字体
FONT_SIZE = 12  # 字体大小
CELL_PADDING = 4  # 表格单元格内边距
NODE_MARGIN = 0.125  # 节点边距

# 正则表达式模式 (从 parser.py 迁移)
# 匹配 GDB 内存输出行中的地址和值，如：0x83a5b000:	0x0000000000000000	0x0000000000000000
MEMORY_PATTERN = r"0x([0-9a-fA-F]+):\s*(.*)"

# 匹配字符串中的十六进制地址，如：(gdb) x /512g 0x83A5B000 或其他包含地址的字符串
ADDRESS_PATTERN = r"0x([0-9a-fA-F]+)"

# 匹配 GDB 内存查看命令及其参数，如：(gdb) x /8g 0x83A5B000
GROUP_CMD_PATTERN = r"\(gdb\) x /(g|\d+g) (0x[0-9a-fA-F]+)"

# 匹配 GDB 寄存器查看命令，如：(gdb) i r
REGISTER_CMD_PATTERN = r'\(gdb\)\s+i\s+r\s*(.*)$'

# 匹配寄存器值输出行，如：satp           0x8000000000083a5b	-9223372036854236581
REGISTER_VALUE_PATTERN = r'^[a-zA-Z_][a-zA-Z0-9_]*\s+0x[0-9a-fA-F]+'

# 匹配寄存器行解析，用于提取寄存器名称和值
REGISTER_LINE_PATTERN = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s+(0x[0-9a-fA-F]+)'

# 空值处理常量 (从 generator.py 和 filter.py 迁移)
NULL_VAL = "0x0000000000000000"  # 完整的空指针值
DISPLAY_NULL_VAL = "0x0"  # 空指针的简化显示值
PADDED_NULL_DISPLAY = "0x00000000"  # 空指针的填充显示值
DEFAULT_NULL_VALUES = ["0x0000000000000000", "0x0"]  # 默认空值列表

# 位移和掩码常量 (从 main.py 和 parser.py 迁移)
PAGE_SHIFT = 12  # 页地址右移位数：计算物理页号
PTE_PPN_SHIFT = 10  # 页表项右移位数：提取物理页号
MEMORY_STEP = 8  # 内存地址步长：64位系统中每个地址单元字节数
SATP_PPN_MASK = 0xFFFFFFFFFFF  # SATP寄存器PPN掩码：取低44位

# 寄存器名称常量
SATP_REGISTER_NAME = "satp"  # SATP寄存器名称

# 预编译正则表达式对象 (提升性能)
import re

MEMORY_PATTERN_COMPILED = re.compile(MEMORY_PATTERN)
ADDRESS_PATTERN_COMPILED = re.compile(ADDRESS_PATTERN)
GROUP_CMD_PATTERN_COMPILED = re.compile(GROUP_CMD_PATTERN)
REGISTER_CMD_PATTERN_COMPILED = re.compile(REGISTER_CMD_PATTERN)
REGISTER_VALUE_PATTERN_COMPILED = re.compile(REGISTER_VALUE_PATTERN)
REGISTER_LINE_PATTERN_COMPILED = re.compile(REGISTER_LINE_PATTERN)
