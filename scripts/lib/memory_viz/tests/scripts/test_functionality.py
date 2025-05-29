#!/usr/bin/env python3
"""
memory_viz 功能测试脚本

用于验证重构前后程序输出的一致性，确保功能没有损失。
"""

import difflib
import subprocess
import sys
from pathlib import Path

# 测试目录路径
TESTS_DIR = Path(__file__).parent.parent
DATA_DIR = TESTS_DIR / "data"
BASELINE_DIR = TESTS_DIR / "baseline"
TEMP_DIR = TESTS_DIR / "temp"

# 测试用例定义
TEST_CASES = [
    {
        "name": "基础内存可视化_浅色主题_4列",
        "input_file": "sample_memory.gdb",
        "args": ["--theme", "light", "--columns", "4"],
        "baseline_file": "sample_memory_light_4col.dot"
    },
    {
        "name": "寄存器+内存可视化_深色主题_2列",
        "input_file": "sample_register_memory.gdb",
        "args": ["--theme", "dark", "--columns", "2"],
        "baseline_file": "sample_register_memory_dark_2col.dot"
    }
]


def setup_test_env():
    """设置测试环境"""
    TEMP_DIR.mkdir(exist_ok=True)
    print("🔧 测试环境已设置")


def run_memory_viz(input_file: str, args: list) -> str:
    """运行 memory_viz 程序并返回输出"""
    cmd = [
              sys.executable, "-m", "src.cli.main",
              str(DATA_DIR / input_file)
          ] + args

    try:
        result = subprocess.run(
            cmd,
            cwd=TESTS_DIR.parent,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ 程序执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return ""


def compare_outputs(baseline_content: str, current_content: str, test_name: str) -> bool:
    """比较基准输出和当前输出"""
    baseline_lines = baseline_content.strip().splitlines()
    current_lines = current_content.strip().splitlines()

    if baseline_lines == current_lines:
        print(f"✅ {test_name} - 输出完全一致")
        return True
    else:
        print(f"❌ {test_name} - 输出存在差异")
        print("差异详情:")

        # 显示前几行差异
        diff = list(difflib.unified_diff(
            baseline_lines, current_lines,
            fromfile="基准输出", tofile="当前输出",
            lineterm="", n=3
        ))

        for line in diff[:20]:  # 只显示前20行差异
            print(f"  {line}")

        if len(diff) > 20:
            print(f"  ... (还有 {len(diff) - 20} 行差异)")

        return False


def run_tests():
    """运行所有测试用例"""
    print("🧪 开始运行 memory_viz 功能测试")
    print("=" * 50)

    setup_test_env()

    all_passed = True

    for test_case in TEST_CASES:
        print(f"\n🔍 测试: {test_case['name']}")

        # 读取基准输出
        baseline_file = BASELINE_DIR / test_case['baseline_file']
        if not baseline_file.exists():
            print(f"❌ 基准文件不存在: {baseline_file}")
            all_passed = False
            continue

        with open(baseline_file, 'r', encoding='utf-8') as f:
            baseline_content = f.read()

        # 运行当前程序
        current_content = run_memory_viz(
            test_case['input_file'],
            test_case['args']
        )

        if not current_content:
            print(f"❌ 程序无输出")
            all_passed = False
            continue

        # 比较输出
        test_passed = compare_outputs(
            baseline_content,
            current_content,
            test_case['name']
        )

        if not test_passed:
            all_passed = False

            # 保存当前输出用于调试
            debug_file = TEMP_DIR / f"debug_{test_case['baseline_file']}"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(current_content)
            print(f"  💾 当前输出已保存到: {debug_file}")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！重构后功能完全一致。")
        return True
    else:
        print("⚠️  部分测试失败，请检查重构代码。")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
