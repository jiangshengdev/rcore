#!/bin/bash
# RISC-V Litmus DOT 文件处理脚本

set -e

# 导入通用工具函数
source "$(dirname "${BASH_SOURCE[0]}")/../../common/shell_utils.sh"

# 检查必要的依赖工具是否安装
check_dependencies() {
  local deps=("$@")
  for dep in "${deps[@]}"; do
    if ! command -v "$dep" >/dev/null 2>&1; then
      case "$dep" in
        python3)
          echo "请先安装 python3" >&2
          ;;
        neato)
          echo "请先安装 graphviz（brew install graphviz）" >&2
          ;;
        *)
          echo "请先安装 $dep" >&2
          ;;
      esac
      exit 1
    fi
  done
}

# 初始化工作环境，返回根目录路径
init_environment() {
  local rootdir
  rootdir="$(get_project_root)"
  if [ -z "$rootdir" ]; then
    echo "未找到项目根目录（缺少 docusaurus.config.ts 或 package.json）" >&2
    exit 1
  fi
  cd "$rootdir"
  echo "$rootdir"
}

# 在根目录执行 Python 模块
run_python_module() {
  local module="$1"
  shift
  cd "$(get_project_root)" && python3 -m "$module" "$@"
}

# 检查依赖工具
check_dependencies python3 neato

# 初始化工作环境
rootdir="$(init_environment)"

echo "[INFO] 开始处理 RISC-V Litmus DOT 文件..."

# 运行 riscv_litmus 模块
run_python_module scripts.lib.riscv_litmus.main "$@"

echo "[INFO] RISC-V Litmus DOT 文件处理完成"
