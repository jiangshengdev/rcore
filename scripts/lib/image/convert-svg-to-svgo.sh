#!/bin/bash
set -e

# 导入通用Shell工具函数
source "$(dirname "${BASH_SOURCE[0]}")/../common/shell_utils.sh"

# 默认不覆盖已存在文件
overwrite=false

# 显示使用帮助
show_usage() {
  echo "用法: $0 [选项]"
  echo "选项:"
  echo "  -f, --force     覆盖已存在的文件"
  echo "  -h, --help      显示此帮助信息"
  echo ""
  echo "说明:"
  echo "  将 images 目录中的 SVG 文件使用 svgo 压缩后保存到同级的 svg 目录"
  echo "  默认跳过已存在的文件，使用 -f 参数可强制覆盖"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    -f|--force)
      overwrite=true
      shift
      ;;
    -h|--help)
      show_usage
      exit 0
      ;;
    *)
      echo "未知参数: $1" >&2
      show_usage >&2
      exit 1
      ;;
  esac
done

# 检查 svgo 是否安装
command -v svgo >/dev/null 2>&1 || {
  echo "请先安装 svgo（npm install -g svgo）" >&2
  exit 1
}

# 获取项目根目录
rootdir="$(get_project_root)"
cd "$rootdir"

# 只递归 blog 和 docs 目录
for root in blog docs; do
  find "$root" -type d -name "images" | while read -r imgdir; do
    # 在 images 同级新建 svg 文件夹
    svgdir="$(dirname "$imgdir")/svg"
    ensure_dir "$svgdir"
    find "$imgdir" -type f -name "*.svg" | while read -r file; do
      relpath="${file#"$imgdir"/}"
      target="$svgdir/$relpath"
      
      # 检查文件是否已存在以及是否需要覆盖
      if [ -f "$target" ] && [ "$overwrite" = false ]; then
        echo "跳过已存在: $target"
        continue
      fi
      
      # 如果要覆盖现有文件，提示正在覆盖
      if [ -f "$target" ] && [ "$overwrite" = true ]; then
        echo "覆盖文件: $target"
      fi
      
      ensure_parent_dir "$target"
      svgo "$file" -o "$target"
      echo "已压缩: $file -> $target"
    done
  done
done
