#!/bin/bash
# 最小化批量转换脚本 - 递归处理 docs 文件夹下所有 ANSI 文件

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"

# 递归查找并转换所有 .ansi 文件
find "$DOCS_DIR" -name "*.ansi" -type f | while read ansi_file; do
  output_file="${ansi_file%.ansi}.mdx"
  python3 "$SCRIPT_DIR/main.py" "$ansi_file" "$output_file"
done
