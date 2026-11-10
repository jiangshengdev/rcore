#!/bin/bash
# Bytefield SVG 生成脚本

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
          echo "错误: 未找到 python3，请先安装 Python 3" >&2
          ;;
        bytefield-svg)
          echo "错误: 未找到 bytefield-svg，请先安装" >&2
          echo "安装方法: npm install -g bytefield-svg" >&2
          echo "或访问: https://github.com/Deep-Symmetry/bytefield-svg" >&2
          ;;
        inkscape)
          echo "错误: 未找到 Inkscape，请先安装 Inkscape" >&2
          echo "macOS: brew install inkscape" >&2
          echo "Ubuntu: sudo apt install inkscape" >&2
          ;;
        *)
          echo "错误: 未找到 $dep，请先安装" >&2
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
    echo "错误: 未找到项目根目录（缺少 docusaurus.config.ts 或 package.json）" >&2
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

main() {
  # 检查依赖
  check_dependencies python3 bytefield-svg inkscape

  # 初始化环境
  local rootdir
  rootdir=$(init_environment)

  echo "正在生成 Bytefield SVG 文件..."

  # 调用 Python 主模块
  run_python_module "scripts.lib.bytefield.main" "$@"

  echo "Bytefield SVG 文件生成完成"
}

# 如果直接执行此脚本，则调用 main 函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
