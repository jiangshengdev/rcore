# ANSI 转换工具 v2 设计方案

## 📊 现状分析

### 旧版本问题诊断

经过对现有实现的深入分析，发现以下关键问题：

| 指标 | 旧版本现状 | 问题描述 |
|------|------------|----------|
| **文件数量** | 36 个文件 | 过度分解，维护困难 |
| **代码行数** | 2,563 行 | 超出需求 5 倍以上 |
| **模块层次** | 4 层嵌套 | `src/cli/core/utils` 过度抽象 |
| **配置复杂度** | 226 行配置代码 | 单例模式、数据类、线程锁等过度设计 |
| **依赖关系** | 循环导入风险 | 模块间耦合度高 |

### 核心功能分析

实际核心功能非常简单：
1. **调用 `terminal-to-html`** - 20 行代码即可完成
2. **HTML 清理** - 30 行正则表达式处理
3. **MDX 包装** - 10 行字符串模板
4. **文件操作** - 标准库即可满足

**结论：当前 2,563 行代码中，真正必要的不超过 200 行。**

## 🎯 v2 设计目标

### 设计原则

1. **极简主义** - 只保留核心功能，删除所有过度抽象
2. **单一职责** - 每个文件负责明确且独立的功能
3. **Python 优先** - 避免复杂的 Shell 脚本逻辑
4. **零配置** - 使用约定优于配置的原则

### 量化目标

| 指标 | v2 目标 | 改进幅度 |
|------|---------|----------|
| 文件数量 | ≤ 8 个 | 减少 78% |
| 代码行数 | ≤ 350 行 | 减少 86% |
| 模块层次 | 1 层平铺 | 简化 75% |
| 启动时间 | ≤ 100ms | 提升 80% |

## 📁 文件结构设计

```
ansi-v2/                           # 新版本根目录
├── main.py                        # 主程序入口 (~120 行)
├── ansi_converter.py              # ANSI->HTML 转换 (~80 行)
├── mdx_formatter.py               # HTML->MDX 格式化 (~60 行)
├── requirements.txt               # Python 依赖 (0 行，无外部依赖)
├── README.md                      # 使用文档 (~50 行)
├── bin/
│   └── convert.sh                 # Shell 入口 (~15 行)
├── _assets/
│   ├── data/
│   │   └── input.ansi             # 示例输入
│   └── dist/                      # 输出目录
└── tests/                         # 可选：简单测试
    └── test_basic.py              # 基础功能测试 (~30 行)
```

**总计：~355 行代码，8 个文件**

## 🔧 核心模块设计

### 1. main.py - 主程序 (~120 行)

```python
#!/usr/bin/env python3
"""
ANSI 到 MDX 转换器 v2 - 极简版本

简化的命令行工具，专注核心转换功能。
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

from ansi_converter import AnsiConverter
from mdx_formatter import MdxFormatter


def setup_logging(verbose: bool = False):
    """配置日志 - 使用标准库，无复杂配置"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def check_environment() -> bool:
    """检查 terminal-to-html 是否可用"""
    # 简单的环境检查逻辑
    pass


def convert_single_file(input_file: str, output_file: str) -> bool:
    """转换单个文件"""
    # 核心转换逻辑协调
    pass


def convert_batch(input_dir: str, output_dir: str) -> dict:
    """批量转换目录"""
    # 批量处理逻辑
    pass


def main():
    """主函数 - 简化的参数解析"""
    parser = argparse.ArgumentParser(description='ANSI 到 MDX 转换器 v2')
    
    # 简化的命令行接口
    parser.add_argument('command', choices=['convert', 'batch'])
    parser.add_argument('input', nargs='?', default='_assets/data/input.ansi')
    parser.add_argument('output', nargs='?', default='_assets/dist/output.mdx')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--check-env', action='store_true')
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    # 简化的逻辑分发
    if args.check_env:
        return 0 if check_environment() else 1
        
    if args.command == 'convert':
        success = convert_single_file(args.input, args.output)
    elif args.command == 'batch':
        results = convert_batch(args.input, args.output)
        success = results['failed'] == 0
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
```

### 2. ansi_converter.py - ANSI 转换 (~80 行)

```python
"""
ANSI 转换器 - 核心转换逻辑

封装 terminal-to-html 调用和 HTML 预处理。
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AnsiConverter:
    """ANSI 到 HTML 转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.tool_name = 'terminal-to-html'
    
    def check_tool_available(self) -> bool:
        """检查 terminal-to-html 是否可用"""
        try:
            result = subprocess.run(
                [self.tool_name, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def convert_to_html(self, ansi_content: str) -> str:
        """将 ANSI 内容转换为 HTML"""
        try:
            # 调用 terminal-to-html
            process = subprocess.run(
                [self.tool_name, '--no-header'],
                input=ansi_content,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode != 0:
                raise RuntimeError(f"转换失败: {process.stderr}")
            
            return self._clean_html(process.stdout)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("转换超时")
        except FileNotFoundError:
            raise RuntimeError(f"工具未找到: {self.tool_name}")
    
    def _clean_html(self, html_content: str) -> str:
        """清理 HTML 内容"""
        # 移除不必要的标签和属性
        # 标准化换行符
        # 清理空白字符
        return html_content.strip()
    
    def convert_file(self, input_file: Path) -> str:
        """转换文件并返回 HTML 内容"""
        if not input_file.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            ansi_content = f.read()
        
        return self.convert_to_html(ansi_content)
```

### 3. mdx_formatter.py - MDX 格式化 (~60 行)

```python
"""
MDX 格式化器 - HTML 到 MDX 转换

将 HTML 转换为 Docusaurus 兼容的 MDX 格式。
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MdxFormatter:
    """MDX 格式化器"""
    
    def __init__(self):
        """初始化格式化器"""
        pass
    
    def format_to_mdx(self, html_content: str, title: Optional[str] = None) -> str:
        """将 HTML 转换为 MDX 格式"""
        # 转换 class 为 className
        mdx_content = self._convert_class_to_classname(html_content)
        
        # 转义 JSX 特殊字符
        mdx_content = self._escape_jsx_content(mdx_content)
        
        # 包装在容器中
        mdx_content = self._wrap_in_container(mdx_content)
        
        return mdx_content
    
    def _convert_class_to_classname(self, content: str) -> str:
        """转换 HTML class 属性为 JSX className"""
        return re.sub(r'\bclass=(["\'])', r'className=\1', content)
    
    def _escape_jsx_content(self, content: str) -> str:
        """转义 JSX 特殊字符"""
        # 转义大括号
        content = content.replace('{', '&#123;').replace('}', '&#125;')
        return content
    
    def _wrap_in_container(self, content: str) -> str:
        """包装在 ANSI 容器中"""
        return f'<div className="ansi-output">\n{content}\n</div>'
    
    def save_to_file(self, content: str, output_file: Path) -> None:
        """保存 MDX 内容到文件"""
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"MDX 文件已保存: {output_file}")
```

### 4. bin/convert.sh - Shell 入口 (~15 行)

```bash
#!/bin/bash
# ANSI 转换工具 v2 - Shell 入口

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSI_V2_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到 ansi-v2 目录并执行 Python 脚本
cd "$ANSI_V2_DIR"
exec python3 main.py "$@"
```

## 🔄 功能映射对比

| 功能 | 旧版本实现 | v2 版本实现 | 简化程度 |
|------|------------|-------------|----------|
| **配置管理** | 226 行单例+数据类 | 10 行硬编码默认值 | 96% |
| **环境检查** | 150 行工具管理器 | 20 行直接调用 | 87% |
| **文件处理** | 180 行处理器类 | 30 行标准库操作 | 83% |
| **错误处理** | 80 行自定义异常 | 标准 Python 异常 | 100% |
| **日志系统** | 120 行复杂配置 | 5 行 basicConfig | 96% |
| **CLI 解析** | 200 行多级命令 | 50 行简单参数 | 75% |

## ⚡ 性能优化

### 启动优化
- **消除复杂导入链** - 减少模块加载时间
- **延迟初始化** - 按需创建对象
- **简化路径解析** - 直接使用 pathlib

### 内存优化
- **流式处理** - 避免大文件全加载
- **及时释放** - 不保持不必要的引用
- **简化对象模型** - 减少内存占用

## 🧪 测试策略

### 基础测试覆盖
```python
# tests/test_basic.py (~30 行)
def test_ansi_to_html_conversion():
    """测试 ANSI 到 HTML 转换"""
    pass

def test_html_to_mdx_formatting():
    """测试 HTML 到 MDX 格式化"""
    pass

def test_file_operations():
    """测试文件读写操作"""
    pass

def test_batch_processing():
    """测试批量处理"""
    pass
```

### 集成测试
- 端到端转换测试
- 命令行接口测试
- 错误场景测试

## 📈 迁移计划

### 阶段 1：核心实现 (1-2 天)
1. 实现 `main.py` 基础框架
2. 实现 `ansi_converter.py` 核心逻辑
3. 实现 `mdx_formatter.py` 格式化逻辑

### 阶段 2：功能完善 (1 天)
1. 添加 Shell 入口脚本
2. 完善错误处理
3. 添加基础测试

### 阶段 3：验证测试 (0.5 天)
1. 对比测试新旧版本输出
2. 性能基准测试
3. 文档更新

## ✅ 成功指标

### 功能指标
- [ ] 单文件转换正确性 100%
- [ ] 批量转换功能正常
- [ ] 与旧版本输出一致性 ≥ 95%

### 性能指标
- [ ] 启动时间 ≤ 100ms
- [ ] 单文件转换时间 ≤ 1s
- [ ] 内存占用 ≤ 50MB

### 维护性指标
- [ ] 代码行数 ≤ 350 行
- [ ] 文件数量 ≤ 8 个
- [ ] 复杂度评分 ≤ 5/10

## 🎯 预期收益

### 开发效率提升
- **理解成本** - 从 2 小时降至 15 分钟
- **修改成本** - 从 1 天降至 30 分钟  
- **测试成本** - 从 2 小时降至 20 分钟

### 运行性能提升
- **启动速度** - 提升 80%
- **内存占用** - 减少 70%
- **转换速度** - 提升 20%

### 维护成本降低
- **Bug 修复** - 从 1 天降至 1 小时
- **功能添加** - 从 3 天降至 1 天
- **版本升级** - 从 1 周降至 1 天

---

**这个 v2 设计方案是否符合需求？有什么需要调整或补充的地方吗？**
