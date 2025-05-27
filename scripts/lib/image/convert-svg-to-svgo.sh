#!/bin/bash
set -e

# 检查 svgo 是否安装
command -v svgo >/dev/null 2>&1 || {
  echo "请先安装 svgo（npm install -g svgo）" >&2
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
    # 在 image 同级新建 svg 文件夹
    svgdir="$(dirname "$imgdir")/svg"
    mkdir -p "$svgdir"
    find "$imgdir" -type f -name "*.svg" | while read -r file; do
      relpath="${file#"$imgdir"/}"
      target="$svgdir/$relpath"
      if [ -f "$target" ]; then
        echo "跳过已存在: $target"
        continue
      fi
      mkdir -p "$(dirname "$target")"
      svgo "$file" -o "$target"
      echo "已压缩: $file -> $target"
    done
  done
done
