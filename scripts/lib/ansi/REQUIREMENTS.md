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
   - 添加 MDX frontmatter
   - 输出：Docusaurus 兼容的 MDX 文件

3. **批量处理**
   - 支持单文件转换
   - 支持批量目录转换
   - 文件模式匹配

### 输入输出

- **输入格式**：`.ansi`, `.txt` 等包含 ANSI 转义序列的文件
- **输出格式**：`.mdx` 文件，包含 frontmatter 和格式化的内容
- **默认文件**：`data/input.ansi` → `output/_output.pre.mdx`

## 🛠️ 技术要求

### 依赖工具

- `terminal-to-html` (npm package) - ANSI 转换核心
- Python 3.x - 脚本运行环境

### 命令行接口

```bash
# 单文件转换
python main.py convert input.ansi output.mdx

# 使用默认文件
python main.py convert

# 批量转换
python main.py batch input_dir/ output_dir/

# 环境检查
python main.py convert --check-env

# 详细日志
python main.py convert --verbose
```

### Shell 脚本入口

```bash
bash bin/convert-ansi-to-mdx.sh input.ansi output.mdx
```

## 📄 示例

### 输入文件 (input.ansi)

```
[31mError:[0m Failed to load module
[32mSuccess:[0m Module loaded
[33mWarning:[0m Deprecated API
```

### 输出文件 (output.mdx)

```mdx
---
title: '终端输出'
description: 'ANSI 转换结果'
---

<div className="ansi-output">
  <span style="color: red">Error:</span> Failed to load module
  <span style="color: green">Success:</span> Module loaded
  <span style="color: yellow">Warning:</span> Deprecated API
</div>
```

## 🎨 配置选项

### 转换配置

- **标题设置**：自定义 MDX 文档标题
- **样式选择**：支持不同的 ANSI 样式主题
- **文件扩展名**：支持的输入文件类型
- **行数限制**：大文件处理限制

### 环境配置

- **工具路径**：terminal-to-html 工具位置
- **输出目录**：默认输出路径
- **日志级别**：调试信息详细程度

## 🚫 非功能需求

### 性能要求

- 单个文件转换时间 < 5秒
- 支持大型文件 (>1MB)
- 内存使用合理

### 易用性要求

- 清晰的错误信息
- 进度提示
- 默认配置开箱即用

### 可靠性要求

- 异常处理完善
- 文件安全检查
- 工具依赖验证

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
├── data/
│   └── input.ansi             # 示例输入文件
└── output/                    # 输出目录
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
