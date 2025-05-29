#!/bin/bash
# 通用Shell工具函数库
# 提供各脚本间共享的实用函数

# 查找项目根目录
# 通过向上遍历目录树寻找包含标记文件的目录
# 返回: 项目根目录路径（通过echo输出），找到时返回0，未找到时返回1
find_project_root() {
    local dir="$PWD"
    # 向上遍历直到文件系统根目录
    while [[ "$dir" != "/" ]]; do
        # 检查是否存在项目标记文件
        if [[ -f "$dir/docusaurus.config.ts" || -f "$dir/package.json" ]]; then
            echo "$dir"
            return 0
        fi
        # 移动到父目录
        dir="$(dirname "$dir")"
    done
    return 1
}

# 获取项目根目录（便捷函数）
# 如果找不到根目录则输出错误信息并退出
# 返回: 项目根目录路径（通过echo输出）
get_project_root() {
    local root
    if ! root="$(find_project_root)"; then
        echo "错误: 未找到项目根目录（缺少 docusaurus.config.ts 或 package.json）" >&2
        exit 1
    fi
    echo "$root"
}

# 创建目录（如果不存在）
# 参数: 目录路径
# 功能: 递归创建目录，如果目录已存在则不报错
ensure_dir() {
    local dir_path="$1"
    if [[ -z "$dir_path" ]]; then
        echo "错误: ensure_dir() 需要目录路径参数" >&2
        return 1
    fi
    mkdir -p "$dir_path"
}

# 为文件创建父目录
# 参数: 文件路径
# 功能: 根据文件路径创建其父目录
ensure_parent_dir() {
    local file_path="$1"
    if [[ -z "$file_path" ]]; then
        echo "错误: ensure_parent_dir() 需要文件路径参数" >&2
        return 1
    fi
    ensure_dir "$(dirname "$file_path")"
}

# 获取当前脚本所在目录的绝对路径
# 返回: 脚本目录的绝对路径（通过echo输出）
get_script_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
}

# 获取调用脚本的目录（用于source的脚本中）
# 返回: 调用脚本目录的绝对路径（通过echo输出）
get_caller_script_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[2]}")" && pwd)"
}
