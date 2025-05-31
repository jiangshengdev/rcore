#!/bin/bash
#
# ANSI 到 MDX 转换入口脚本 - 最小化版本
#
# 将 ANSI 格式的终端输出转换为 Docusaurus 兼容的 MDX 文件。
# 所有核心功能已迁移到 Python CLI，此脚本仅作为兼容性入口点。
#

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

# 设置 Python 路径环境变量
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/scripts:$PYTHONPATH"

# 直接调用 Python CLI，传递所有参数
# Python CLI 现在处理所有功能：参数解析、文件验证、环境检查、转换等
cd "$PROJECT_ROOT/scripts" && python3 "lib/ansi/src/cli/main.py" convert "$@"
