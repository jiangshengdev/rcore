#!/bin/bash
set -e

# 导入通用Shell工具函数
source "$(dirname "${BASH_SOURCE[0]}")/../common/shell_utils.sh"

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
      if [ -f "$target" ]; then
        echo "跳过已存在: $target"
        continue
      fi
      ensure_parent_dir "$target"
      svgo "$file" -o "$target"
      echo "已压缩: $file -> $target"
    done
  done
done
