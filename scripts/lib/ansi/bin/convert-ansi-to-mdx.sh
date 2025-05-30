#!/bin/bash
#
# ANSI 到 MDX 转换主脚本
#
# 将 ANSI 格式的终端输出转换为 Docusaurus 兼容的 MDX 文件。
#

# 获取脚本目录并导入通用函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 默认配置
DEFAULT_INPUT_FILE="$ANSI_MODULE_DIR/data/input.ansi"
DEFAULT_OUTPUT_FILE="$ANSI_MODULE_DIR/output/_output.pre.mdx"

# 主转换函数
convert_ansi_to_mdx() {
    local input_file="$1"
    local output_file="$2"
    local title="$3"
    local verbose="$4"
    
    print_info "开始 ANSI 到 MDX 转换"
    print_info "输入文件: $input_file"
    print_info "输出文件: $output_file"
    
    if [[ -n "$title" ]]; then
        print_info "文档标题: $title"
    fi
    
    # 验证输入文件
    if ! validate_ansi_file "$input_file"; then
        return 1
    fi
    
    # 验证输出路径
    if ! validate_output_path "$output_file"; then
        return 1
    fi
    
    # 构建 Python CLI 参数 - 直接使用输入文件
    local python_args=(convert "$input_file" "$output_file")
    
    if [[ -n "$title" ]]; then
        python_args+=(--title "$title")
    fi
    
    if [[ "$verbose" == true ]]; then
        python_args+=(--verbose)
    fi
    
    # 调用 Python CLI 模块进行转换
    print_info "调用 Python 转换模块..."
    if run_python_module "lib/ansi/src/cli/main.py" "${python_args[@]}"; then
        print_success "转换完成: $output_file"
        
        # 显示文件信息
        if [[ -f "$output_file" ]]; then
            local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
            print_info "输出文件大小: $file_size 字节"
        fi
        
        return 0
    else
        print_error "转换失败"
        return 1
    fi
}

# 主函数
main() {
    # 解析命令行参数
    parse_args "$@"
    
    # 从环境变量获取解析结果
    local input_file="$PARSED_INPUT_FILE"
    local output_file="$PARSED_OUTPUT_FILE"
    local title="$PARSED_TITLE"
    local verbose="$PARSED_VERBOSE"
    
    # 设置默认值
    if [[ -z "$input_file" ]]; then
        input_file="$DEFAULT_INPUT_FILE"
        print_info "使用默认输入文件: $input_file"
    fi
    
    if [[ -z "$output_file" ]]; then
        output_file="$DEFAULT_OUTPUT_FILE"
        print_info "使用默认输出文件: $output_file"
    fi
    
    # 转换为绝对路径
    input_file="$(cd "$(dirname "$input_file")" && pwd)/$(basename "$input_file")"
    
    # 确保输出目录存在
    ensure_dir "$(dirname "$output_file")"
    
    # 执行转换
    if convert_ansi_to_mdx "$input_file" "$output_file" "$title" "$verbose"; then
        print_success "ANSI 到 MDX 转换成功完成!"
        
        # 提供使用建议
        echo ""
        print_info "使用建议:"
        echo "  1. 检查生成的 MDX 文件: $output_file"
        echo "  2. 复制到目标目录: cp '$output_file' docs/example/"
        echo "  3. 在 Docusaurus 中引用: import PreMdx from './_output.pre.mdx'"
        
        exit 0
    else
        print_error "转换失败"
        exit 1
    fi
}

# 处理脚本被直接执行的情况
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
