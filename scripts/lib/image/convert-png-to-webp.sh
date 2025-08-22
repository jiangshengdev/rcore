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
  echo "  将 images 目录中的 PNG 文件转换为 WebP 格式并保存到同级的 webp 目录"
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

# 检查 cwebp 是否安装
command -v cwebp >/dev/null 2>&1 || {
  echo "请先安装 cwebp（brew install webp）" >&2
  exit 1
}

# 获取项目根目录
rootdir="$(get_project_root)"
cd "$rootdir"

# 定义单文件转换函数，并导出供 xargs 调用
convert_one() {
  file="$1"
  imgdir="$2"
  webpdir="$3"
  overwrite="$4"
  rel="${file#"$imgdir"/}"
  target="$webpdir/${rel%.png}.webp"
  
  # 检查文件是否已存在以及是否需要覆盖
  if [[ -f "$target" ]] && [[ "$overwrite" = false ]]; then
    echo "跳过已存在: $target"
    return
  fi
  
  # 如果要覆盖现有文件，提示正在覆盖
  if [[ -f "$target" ]] && [[ "$overwrite" = true ]]; then
    echo "覆盖文件: $target"
  fi
  
  # 确保目标文件的父目录存在
  mkdir -p "$(dirname "$target")"
  cwebp -lossless -z 9 -exact -mt -metadata icc "$file" -o "$target"
  echo "已转换: $file -> $target"
}
export -f convert_one

# 动态获取物理核心数
CPU_NUM=$(sysctl -n hw.physicalcpu 2>/dev/null || echo 2)

# 收集待转换文件列表并并发执行
(
  for root in blog docs; do
    find "$root" -type d -name "images" | while read -r imgdir; do
      webpdir="$(dirname "$imgdir")/webp"
      ensure_dir "$webpdir"
      find "$imgdir" -type f -name "*.png" | while read -r file; do
        rel="${file#"$imgdir"/}"
        target="$webpdir/${rel%.png}.webp"
        # 如果不覆盖模式且文件已存在，则跳过
        if [[ -f "$target" ]] && [[ "$overwrite" = false ]]; then
          continue
        fi
        printf '%s\0%s\0%s\0%s\0' "$file" "$imgdir" "$webpdir" "$overwrite"
      done
    done
  done
) | xargs -0 -P "$CPU_NUM" -n 4 bash -c 'convert_one "$@"' _
