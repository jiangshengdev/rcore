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

# 只递归 blog 和 docs 目录
for root in blog docs; do
  find "$root" -type d -name "image" | while read -r imgdir; do
    # 在 image 同级新建 webp 文件夹
    webpdir="$(dirname "$imgdir")/webp"
    mkdir -p "$webpdir"
    find "$imgdir" -type f -name "*.png" | while read -r file; do
      relpath="${file#"$imgdir"/}"
      target="$webpdir/${relpath%.png}.webp"
      if [ -f "$target" ]; then
        echo "跳过已存在: $target"
        continue
      fi
      mkdir -p "$(dirname "$target")"
      cwebp -lossless -z 9 -exact -mt "$file" -o "$target"
      echo "已转换: $file -> $target"
    done
  done
done
