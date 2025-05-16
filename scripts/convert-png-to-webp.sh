#!/bin/bash
set -e

# 检查 cwebp 是否安装
command -v cwebp >/dev/null 2>&1 || {
  echo "请先安装 cwebp（brew install webp）" >&2
  exit 1
}

# 自动寻找 rcore 根目录（包含 docusaurus.config.ts 或 package.json）
find_root() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/docusaurus.config.ts" || -f "$dir/package.json" ]]; then
      echo "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

rootdir="$(find_root)"
if [ -z "$rootdir" ]; then
  echo "未找到 rcore 根目录（缺少 docusaurus.config.ts 或 package.json）" >&2
  exit 1
fi
cd "$rootdir"

# 定义单文件转换函数，并导出供 xargs 调用
convert_one() {
  file="$1"; imgdir="$2"; webpdir="$3"
  rel="${file#"$imgdir"/}"
  target="$webpdir/${rel%.png}.webp"
  mkdir -p "${target%/*}"
  cwebp -lossless -z 9 -exact -mt "$file" -o "$target"
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
      mkdir -p "$webpdir"
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
