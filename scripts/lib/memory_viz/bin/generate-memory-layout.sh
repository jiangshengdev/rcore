#!/bin/bash
# 内存布局可视化生成脚本

set -e

# 导入通用工具函数
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# 获取项目目录
SCRIPT_DIR="$(get_script_dir)"
MEMORY_VIZ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检查依赖工具
check_dependencies python3 dot

# 初始化工作环境
rootdir="$(init_environment)"

# 生成 light 主题内存布局
ensure_dir "$MEMORY_VIZ_DIR/output/light"
run_python_module scripts.lib.memory_viz.src.cli.main "$MEMORY_VIZ_DIR/data/mem.txt" --theme light >"$MEMORY_VIZ_DIR/output/light/memory.dot"
dot -Tsvg:cairo "$MEMORY_VIZ_DIR/output/light/memory.dot" -o "$MEMORY_VIZ_DIR/output/light/memory.svg"

# 生成 dark 主题内存布局
ensure_dir "$MEMORY_VIZ_DIR/output/dark"
run_python_module scripts.lib.memory_viz.src.cli.main "$MEMORY_VIZ_DIR/data/mem.txt" --theme dark >"$MEMORY_VIZ_DIR/output/dark/memory.dot"
dot -Tsvg:cairo "$MEMORY_VIZ_DIR/output/dark/memory.dot" -o "$MEMORY_VIZ_DIR/output/dark/memory.svg"

echo "内存布局可视化文件已生成完成"
