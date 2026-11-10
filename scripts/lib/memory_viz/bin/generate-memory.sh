#!/bin/bash
# 内存可视化生成脚本
# 这个脚本提供了与原始脚本完全相同的接口，确保向后兼容

set -e

# 导入通用工具函数
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# 获取脚本目录
SCRIPT_DIR="$(get_script_dir)"

# 调用内存布局可视化生成脚本
"$SCRIPT_DIR/generate-memory-layout.sh"

# 调用二叉树可视化生成脚本
"$SCRIPT_DIR/generate-binary-tree.sh"

# 调用伙伴系统可视化生成脚本
"$SCRIPT_DIR/generate-buddy-system.sh"

echo "内存可视化文件已生成完成"
