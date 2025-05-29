#!/bin/bash
# 内存可视化脚本通用辅助函数

# 检查必要的依赖工具是否安装
check_dependencies() {
    local deps=("$@")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            case "$dep" in
                python3)
                    echo "请先安装 python3" >&2
                    ;;
                dot)
                    echo "请先安装 graphviz（brew install graphviz）" >&2
                    ;;
                *)
                    echo "请先安装 $dep" >&2
                    ;;
            esac
            exit 1
        fi
    done
}

# 自动寻找 rcore 根目录（包含 docusaurus.config.ts 或 package.json）
find_rcore_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/docusaurus.config.ts" || -f "$dir/package.json" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# 初始化工作环境，返回根目录路径
init_environment() {
    local rootdir
    rootdir="$(find_rcore_root)"
    if [ -z "$rootdir" ]; then
        echo "未找到 rcore 根目录（缺少 docusaurus.config.ts 或 package.json）" >&2
        exit 1
    fi
    cd "$rootdir"
    echo "$rootdir"
}

# 在根目录执行 Python 模块
run_python_module() {
    local module="$1"
    shift
    cd "$(find_rcore_root)" && python3 -m "$module" "$@"
}
