#!/bin/bash
# 伙伴系统可视化生成脚本

set -e

# 获取脚本目录并加载通用辅助函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 检查依赖工具
check_dependencies python3

# 初始化工作环境
rootdir="$(init_environment)"

# 生成伙伴系统可视化
run_python_module scripts.lib.memory_viz.src.visualizers.buddy_system

echo "伙伴系统可视化文件已生成完成"
