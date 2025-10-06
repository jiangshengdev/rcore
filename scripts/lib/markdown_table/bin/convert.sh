#!/bin/bash
# Markdown table <br> expander entry

set -e

# import common helpers
source "$(dirname "${BASH_SOURCE[0]}")/../../common/shell_utils.sh"

check_dependencies() {
  local deps=(python3)
  for dep in "${deps[@]}"; do
    if ! command -v "$dep" >/dev/null 2>&1; then
      echo "请先安装 $dep" >&2
      exit 1
    fi
  done
}

run_python_module() {
  cd "$(get_project_root)" && python3 -m scripts.lib.markdown_table.main "$@"
}

main() {
  check_dependencies
  run_python_module "$@"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
