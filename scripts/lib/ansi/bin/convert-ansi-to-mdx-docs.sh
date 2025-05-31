#!/bin/bash
#
# ANSI 到 MDX 转换脚本 - docs 文件夹递归处理版本
#
# 递归扫描 docs 文件夹，找到所有 .ansi 文件并转换为 MDX 格式。
# 对于 _assets 等下划线开头的文件夹，直接使用原文件名保存 MDX 文件。
#

# 获取脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"

# 设置 Python 路径环境变量
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/scripts:$PYTHONPATH"

# 检查 docs 目录是否存在
if [ ! -d "$DOCS_DIR" ]; then
    echo "错误: docs 目录不存在: $DOCS_DIR"
    exit 1
fi

echo "🔍 开始扫描 docs 文件夹中的 ANSI 文件..."
echo "📁 扫描目录: $DOCS_DIR"

# 统计变量
total_files=0
converted_files=0
failed_files=0

# 递归查找所有 .ansi 文件
while IFS= read -r -d '' ansi_file; do
    total_files=$((total_files + 1))
    
    # 获取文件的相对路径（相对于 docs 目录）
    rel_path="${ansi_file#$DOCS_DIR/}"
    
    # 获取文件名（不含扩展名）
    filename=$(basename "$ansi_file" .ansi)
    
    # 获取文件所在目录
    file_dir=$(dirname "$ansi_file")
    
    # 生成输出文件路径（同目录下，.ansi 改为 .mdx）
    output_file="$file_dir/$filename.mdx"
    
    echo ""
    echo "📄 处理文件 [$total_files]: $rel_path"
    echo "   输入: $ansi_file"
    echo "   输出: $output_file"
    
    # 调用 Python CLI 进行转换（不传递标题，因为这些文件用于代码高亮显示）
    cd "$PROJECT_ROOT"
    if python3 -m scripts.lib.ansi.src.cli.main convert "$ansi_file" "$output_file"; then
        converted_files=$((converted_files + 1))
        echo "   ✅ 转换成功"
    else
        failed_files=$((failed_files + 1))
        echo "   ❌ 转换失败"
    fi
    
done < <(find "$DOCS_DIR" -name "*.ansi" -type f -print0)

echo ""
echo "================================"
echo "🎯 转换完成统计:"
echo "   总计文件: $total_files"
echo "   成功转换: $converted_files"
echo "   转换失败: $failed_files"

if [ $failed_files -eq 0 ]; then
    echo "   🎉 所有文件转换成功！"
    exit 0
else
    echo "   ⚠️  部分文件转换失败"
    exit 1
fi
