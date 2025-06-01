#!/bin/bash
#
# 通用 Shell 工具函数 - 最小化版本
#
# 为 ANSI 转 MDX 脚本提供基础的环境设置和路径管理。
# 大部分功能已迁移到 Python 模块中。
#

# 获取基本路径信息
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
ANSI_MODULE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置 Python 环境路径
setup_python_environment() {
  export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/scripts:$PYTHONPATH"
}

# 基础颜色输出函数（保留用于简单的 Shell 脚本输出）
print_info() {
  echo -e "\033[34m[INFO]\033[0m $1"
}

print_error() {
  echo -e "\033[31m[ERROR]\033[0m $1"
}

# 运行 Python CLI（简化版本）
run_python_cli() {
  setup_python_environment
  cd "$PROJECT_ROOT/scripts" && python3 "lib/ansi/src/cli/main.py" "$@"
}
