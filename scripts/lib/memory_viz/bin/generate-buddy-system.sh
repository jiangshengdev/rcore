#!/bin/bash
# 伙伴系统可视化生成脚本

set -e

# 导入通用工具函数
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# 获取脚本目录
SCRIPT_DIR="$(get_script_dir)"

# 检查依赖工具
check_dependencies python3

# 初始化工作环境
rootdir="$(init_environment)"

# 生成伙伴系统可视化
run_python_module scripts.lib.memory_viz.src.visualizers.buddy_system

echo "伙伴系统可视化文件已生成完成"
