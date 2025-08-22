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

# 生成指定主题的内存布局
# 参数: $1 - 主题名称 (light/dark)
#       $2 - 输入文件完整路径
#       $3 - 输出目录路径
#       $4 - 输出文件名（不含扩展名）
generate_memory_layout() {
    local theme="$1"
    local input_file="$2"
    local output_dir="$3"
    local filename="$4"
    
    # 确保输出目录存在
    ensure_dir "$output_dir"
    
    # 生成 DOT 文件
    run_python_module scripts.lib.memory_viz.src.cli.main "$input_file" --theme "$theme" >"${output_dir}/${filename}.dot"
    
    # 转换为 SVG 文件
    dot -Tsvg:cairo "${output_dir}/${filename}.dot" -o "${output_dir}/${filename}.svg"
}

# 扫描并处理所有文档目录下的内存布局文件
echo "正在扫描 docs/ 目录下的内存布局文件..."

# 查找所有 docs/**/_assets/memory/*.txt 文件
find "$rootdir/docs" -name "memory" -type d | while IFS= read -r memory_dir; do
    # 检查 memory 目录下是否有 .txt 文件
    if ls "$memory_dir"/*.txt >/dev/null 2>&1; then
        echo "发现内存布局文件目录: $memory_dir"
        
        # 获取 _assets 目录路径（memory 的父目录）
        assets_dir=$(dirname "$memory_dir")
        
        # 创建 images 目录路径
        images_dir="$assets_dir/images"
        
        # 处理该目录下的每个 .txt 文件
        for txt_file in "$memory_dir"/*.txt; do
            if [[ -f "$txt_file" ]]; then
                # 提取不含扩展名的文件名
                filename=$(basename "$txt_file" .txt)
                echo "  正在处理文件: $filename"
                
                # 生成浅色主题布局
                light_output_dir="$images_dir/light"
                generate_memory_layout "light" "$txt_file" "$light_output_dir" "$filename"
                
                # 生成深色主题布局
                dark_output_dir="$images_dir/dark"
                generate_memory_layout "dark" "$txt_file" "$dark_output_dir" "$filename"
                
                echo "  已完成 $filename 的布局生成"
            fi
        done
    fi
done

echo "内存布局可视化文件已生成完成"
