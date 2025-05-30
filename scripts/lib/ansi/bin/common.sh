#!/bin/bash
#
# 通用 Shell 工具函数
#
# 为 ANSI 转 MDX 脚本提供通用的 Shell 工具函数。
#

# 脚本目录路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
ANSI_MODULE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 颜色输出函数
print_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# 检查必要工具是否可用
check_tool() {
    local tool_name="$1"
    if ! command -v "$tool_name" &> /dev/null; then
        print_error "必需工具 '$tool_name' 未找到，请安装后重试"
        return 1
    fi
    return 0
}

# 检查文件是否存在
check_file() {
    local file_path="$1"
    if [[ ! -f "$file_path" ]]; then
        print_error "文件不存在: $file_path"
        return 1
    fi
    return 0
}

# 创建目录（如果不存在）
ensure_dir() {
    local dir_path="$1"
    if [[ ! -d "$dir_path" ]]; then
        mkdir -p "$dir_path"
        print_info "创建目录: $dir_path"
    fi
}

# 验证输入文件格式
validate_ansi_file() {
    local file_path="$1"
    
    # 检查文件是否存在
    if ! check_file "$file_path"; then
        return 1
    fi
    
    # 检查文件扩展名
    if [[ ! "$file_path" =~ \.(ansi|txt)$ ]]; then
        print_warning "输入文件扩展名不是 .ansi 或 .txt: $file_path"
    fi
    
    # 检查文件是否包含 ANSI 转义序列
    if ! grep -q $'\033\[' "$file_path"; then
        print_warning "文件似乎不包含 ANSI 转义序列: $file_path"
    fi
    
    return 0
}

# 验证输出文件路径
validate_output_path() {
    local output_path="$1"
    
    # 检查输出目录是否可写
    local output_dir="$(dirname "$output_path")"
    if [[ ! -d "$output_dir" ]]; then
        ensure_dir "$output_dir"
    fi
    
    if [[ ! -w "$output_dir" ]]; then
        print_error "输出目录不可写: $output_dir"
        return 1
    fi
    
    # 检查输出文件扩展名
    if [[ ! "$output_path" =~ \.mdx$ ]]; then
        print_warning "输出文件扩展名不是 .mdx: $output_path"
    fi
    
    return 0
}

# 运行 Python 模块
run_python_module() {
    local module_path="$1"
    shift
    local args=("$@")
    
    # 设置 Python 路径
    export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/scripts:$PYTHONPATH"
    
    # 检查 Python 是否可用
    if ! check_tool "python3"; then
        return 1
    fi
    
    # 运行 Python 模块
    cd "$PROJECT_ROOT/scripts" || return 1
    python3 "$module_path" "${args[@]}"
}

# 清理临时文件
cleanup_temp_files() {
    local temp_dir="$1"
    if [[ -d "$temp_dir" ]] && [[ "$temp_dir" =~ /tmp/ ]]; then
        rm -rf "$temp_dir"
        print_info "清理临时目录: $temp_dir"
    fi
}

# 显示帮助信息
show_usage() {
    local script_name="$1"
    echo "用法: $script_name [选项] <输入文件> [输出文件]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -t, --title <标题>      设置 MDX 文档标题"
    echo "  -v, --verbose           显示详细输出"
    echo "  -o, --output <文件>     指定输出文件路径"
    echo ""
    echo "示例:"
    echo "  $script_name input.ansi"
    echo "  $script_name input.ansi output.mdx"
    echo "  $script_name --title \"虚拟内存示例\" input.ansi output.mdx"
    echo "  $script_name --verbose input.ansi"
}

# 解析命令行参数
parse_args() {
    # 使用全局变量而非 nameref
    input_file=""
    output_file=""
    title=""
    verbose=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage "$(basename "$0")"
                exit 0
                ;;
            -t|--title)
                title="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            --)
                shift
                break
                ;;
            -*)
                print_error "未知选项: $1"
                show_usage "$(basename "$0")"
                exit 1
                ;;
            *)
                if [[ -z "$input_file" ]]; then
                    input_file="$1"
                elif [[ -z "$output_file" ]]; then
                    output_file="$1"
                else
                    print_error "过多的位置参数: $1"
                    show_usage "$(basename "$0")"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 导出全局变量供脚本使用
    export PARSED_INPUT_FILE="$input_file"
    export PARSED_OUTPUT_FILE="$output_file"
    export PARSED_TITLE="$title"
    export PARSED_VERBOSE="$verbose"
}
