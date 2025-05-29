#!/usr/bin/env python3
"""
memory_viz 测试运行器

运行所有测试（功能测试和单元测试），验证重构后程序的完整性。
"""

import subprocess
import sys
from pathlib import Path


def run_test_script(script_name: str, description: str) -> bool:
    """运行指定的测试脚本"""
    print(f"\n🚀 {description}")
    print("-" * 60)

    script_path = Path(__file__).parent / script_name

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=Path(__file__).parent.parent,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行测试脚本失败: {e}")
        return False


def main():
    """主测试运行函数"""
    print("🧪 memory_viz 完整测试套件")
    print("=" * 60)
    print("验证重构前后程序功能的一致性")

    all_passed = True

    # 运行单元测试
    unit_test_passed = run_test_script(
        "scripts/test_units.py",
        "运行单元测试 - 验证各模块功能"
    )
    all_passed = all_passed and unit_test_passed

    # 运行功能测试
    func_test_passed = run_test_script(
        "scripts/test_functionality.py",
        "运行功能测试 - 验证程序整体输出"
    )
    all_passed = all_passed and func_test_passed

    # 输出最终结果
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！重构是安全的。")
        print("✅ 可以继续进行下一步重构工作")
    else:
        print("⚠️  部分测试失败，请先修复问题再继续重构")
        print("❌ 重构可能引入了功能问题")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
