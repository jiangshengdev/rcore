#!/bin/bash
# 内存可视化生成脚本
# 这个脚本提供了与原始脚本完全相同的接口，确保向后兼容

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_VIZ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检查 python3 是否安装
command -v python3 >/dev/null 2>&1 || {
  echo "请先安装 python3" >&2
  exit 1
}

# 检查 dot 是否安装
command -v dot >/dev/null 2>&1 || {
  echo "请先安装 graphviz（brew install graphviz）" >&2
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

# 生成可视化文件到指定目录
# 生成 light 主题
mkdir -p "$MEMORY_VIZ_DIR/output/light"
cd "$rootdir" && python3 -m scripts.lib.memory_viz.src.cli.main "$MEMORY_VIZ_DIR/data/mem.txt" --theme light > "$MEMORY_VIZ_DIR/output/light/memory.dot"
cd "$rootdir" && dot -Tsvg:cairo "$MEMORY_VIZ_DIR/output/light/memory.dot" -o "$MEMORY_VIZ_DIR/output/light/memory.svg"

# 生成 dark 主题
mkdir -p "$MEMORY_VIZ_DIR/output/dark"
cd "$rootdir" && python3 -m scripts.lib.memory_viz.src.cli.main "$MEMORY_VIZ_DIR/data/mem.txt" --theme dark > "$MEMORY_VIZ_DIR/output/dark/memory.dot"
cd "$rootdir" && dot -Tsvg:cairo "$MEMORY_VIZ_DIR/output/dark/memory.dot" -o "$MEMORY_VIZ_DIR/output/dark/memory.svg"

# 生成二叉树可视化
cd "$rootdir" && python3 -m scripts.lib.memory_viz.src.visualizers.binary_tree

# 生成伙伴系统可视化
cd "$rootdir" && python3 -m scripts.lib.memory_viz.src.visualizers.buddy_system

echo "内存可视化文件已生成完成"
