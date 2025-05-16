#!/bin/bash
set -e

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

# 生成 light 主题
mkdir -p scripts/memory/light
python3 -m scripts.memory.generate_memory_dot scripts/memory/mem.txt --theme light >scripts/memory/light/memory.dot
dot -Tsvg:cairo scripts/memory/light/memory.dot -o scripts/memory/light/memory.svg

# 生成 dark 主题
mkdir -p scripts/memory/dark
python3 -m scripts.memory.generate_memory_dot scripts/memory/mem.txt --theme dark >scripts/memory/dark/memory.dot
dot -Tsvg:cairo scripts/memory/dark/memory.dot -o scripts/memory/dark/memory.svg
