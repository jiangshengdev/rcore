# ANSI 转换工具需求分析

## 📋 项目背景

将包含 ANSI 转义序列的终端输出文件转换为 Docusaurus 兼容的 MDX 格式，用于文档网站展示。

## 🎯 核心需求

### 主要功能

1. **ANSI → HTML 转换**

   - 输入：包含 ANSI 转义序列的文本文件
   - 使用 `terminal-to-html` 工具进行转换
   - 输出：带样式的 HTML 内容

2. **HTML → MDX 转换**

   - 输入：HTML 内容
   - 清理和格式化 HTML
   - 输出：纯 HTML 的 MDX 文件（无 frontmatter）

3. **批量处理**
   - 支持单文件转换
   - 支持批量目录转换
   - 文件模式匹配

### 输入输出

- **输入格式**：`.ansi`, `.txt` 等包含 ANSI 转义序列的文件
- **输出格式**：`.mdx` 文件，包含格式化的 HTML 内容
- **默认文件**：`_assets/data/input.ansi` → `_assets/dist/output.mdx`

## 🛠️ 技术要求

### 设计原则

- **Python 优先**：所有核心逻辑都在 Python 中实现
- **Shell 最小化**：Shell 脚本仅作为参数传递的简单入口
- **单一职责**：每个 Python 模块负责明确的功能
- **易于维护**：代码结构清晰，依赖关系简单

### 依赖工具

- `terminal-to-html` (npm package) - ANSI 转换核心，通过 Python 调用
- Python 3.x - 脚本运行环境（主要实现语言）
- `subprocess` - Python 标准库，用于调用外部工具
- `argparse` - Python 标准库，用于命令行参数解析
- `logging` - Python 标准库，用于日志记录和错误输出

### 命令行接口

```bash
# 单文件转换
python main.py convert _assets/data/input.ansi _assets/dist/output.mdx

# 使用默认文件
python main.py convert

# 批量转换
python main.py batch _assets/data/ _assets/dist/

# 环境检查
python main.py convert --check-env

# 详细日志
python main.py convert --verbose
```

### Shell 脚本入口

```bash
# 简单的入口脚本，所有逻辑在 Python 中实现
bash bin/convert-ansi-to-mdx.sh _assets/data/input.ansi _assets/dist/output.mdx
```

**注意**：Shell 脚本仅作为简单的参数传递入口，所有核心逻辑、错误处理、环境检查、文件操作都在 Python 中实现。

## 📄 示例

### 输入文件 (input.ansi)

```
[31mError:[0m Failed to load module
[32mSuccess:[0m Module loaded
[33mWarning:[0m Deprecated API
```

### 输出文件 (output.mdx)

```mdx
<div className="ansi-output">
  <span style="color: red">Error:</span> Failed to load module
  <span style="color: green">Success:</span> Module loaded
  <span style="color: yellow">Warning:</span> Deprecated API
</div>
```

## 🎨 配置选项

### 转换配置

- **文件扩展名**：仅支持 `.ansi` 纯文本文件（不支持配置）
- **样式主题**：使用固定的默认主题（不支持主题切换）

### 环境配置

- **输出目录**：默认输出路径
- **日志级别**：调试信息详细程度（使用 Python 标准库 logging）

## 🛠️ Python 模块设计

### 核心模块

1. **main.py** - 主程序入口
   - 命令行参数解析（argparse）
   - 环境检查和依赖验证
   - 单文件/批量处理逻辑协调
   - 错误处理和用户反馈

2. **ansi_converter.py** - ANSI 转换核心
   - 调用 `terminal-to-html` 工具（subprocess）
   - HTML 内容预处理和清理

3. **mdx_formatter.py** - MDX 格式化
   - HTML 到 MDX 的结构转换
   - CSS 类名和样式处理

### 职责分离

- **文件操作**：全部在 Python 中处理
- **路径解析**：使用 Python `pathlib`
- **错误处理**：Python 异常系统
- **进度显示**：Python 内置进度提示
- **环境检查**：Python subprocess 调用

## 📁 期望的文件结构

```
scripts/lib/ansi-v2/           # 新版本目录
├── main.py                    # 主程序 (~150行)
├── ansi_converter.py          # 核心转换逻辑 (~100行)
├── mdx_formatter.py           # MDX格式化 (~80行)
├── requirements.txt           # Python依赖
├── README.md                  # 使用说明
├── bin/
│   └── convert.sh             # Shell入口脚本
├── _assets/
│   ├── data/
│   │   └── input.ansi         # 示例输入文件
│   └── dist/                  # 输出目录
└── src/                       # 源代码目录（可选）
```

**总计：约330行代码，8个文件**

## ✅ 验收标准

### 基本功能

- [ ] 单文件转换正常工作
- [ ] 批量转换正常工作
- [ ] 默认文件转换正常工作
- [ ] Shell脚本入口正常工作

### 错误处理

- [ ] 文件不存在时给出清晰错误
- [ ] 工具未安装时给出安装指导
- [ ] 转换失败时给出具体原因

### 用户体验

- [ ] 命令行帮助信息完整
- [ ] 进度提示清晰
- [ ] 日志输出有用

## 🔄 与现有版本的区别

### 现有版本问题

- ❌ 过度工程化：15个文件，2500+行代码
- ❌ 功能重复：多个模块做相同的事
- ❌ 复杂配置：不必要的抽象层

### 新版本目标

- ✅ 简洁实用：<10个文件，<500行代码
- ✅ 职责清晰：每个文件负责明确功能
- ✅ 易于维护：直观的代码结构

---

**这个需求文档是否准确反映了项目的真实需要？有什么需要补充或修改的吗？**
