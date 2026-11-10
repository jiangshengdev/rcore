#!/bin/bash
# WaveDrom SVG 生成脚本

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
        wavedrom-cli)
          echo "请先安装 wavedrom-cli (npm install -g @wavedrom/cli)" >&2
          ;;
        node)
          echo "请先安装 Node.js" >&2
          ;;
        inkscape)
          echo "请先安装 Inkscape (brew install inkscape)" >&2
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

main() {
  # 检查依赖
  check_dependencies python3 wavedrom-cli node inkscape

  # 初始化环境
  local rootdir
  rootdir=$(init_environment)

  echo "正在生成 WaveDrom SVG 文件..."

  # 调用 Python 主模块
  run_python_module "scripts.lib.wavedrom.main" "$@"

  echo "WaveDrom SVG 文件生成完成"
}

# 如果直接执行此脚本，则调用 main 函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
