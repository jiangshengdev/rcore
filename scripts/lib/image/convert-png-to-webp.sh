#!/bin/bash
set -e

# 导入通用Shell工具函数
source "$(dirname "${BASH_SOURCE[0]}")/../common/shell_utils.sh"

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
  rel="${file#"$imgdir"/}"
  target="$webpdir/${rel%.png}.webp"
  ensure_parent_dir "$target"
  cwebp -lossless -z 9 -exact -mt -metadata icc "$file" -o "$target"
  echo "已转换: $file -> $target"
}
export -f convert_one

# 动态获取物理核心数
CPU_NUM=$(sysctl -n hw.physicalcpu 2>/dev/null || echo 2)

# 收集待转换文件列表并并发执行
(
  for root in blog docs; do
    find "$root" -type d -name "image" | while read -r imgdir; do
      webpdir="$(dirname "$imgdir")/webp"
      ensure_dir "$webpdir"
      find "$imgdir" -type f -name "*.png" | while read -r file; do
        rel="${file#"$imgdir"/}"
        target="$webpdir/${rel%.png}.webp"
        if [[ -f "$target" ]]; then
          echo "跳过已存在: $target" >&2
        else
          printf '%s\0%s\0%s\0' "$file" "$imgdir" "$webpdir"
        fi
      done
    done
  done
) | xargs -0 -P "$CPU_NUM" -n 3 bash -c 'convert_one "$@"' _
