#!/usr/bin/env python3
"""
memory_viz 单元测试脚本

用于测试各个模块的具体功能，确保重构后各组件正常工作。
"""

import sys
import unittest
from pathlib import Path

# 添加源码路径到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core import parser
from core.colors import get_theme_colors
from core.filter import filter_zero_rows


class TestMemoryParser(unittest.TestCase):
    """内存解析器测试"""

    def setUp(self):
        """设置测试环境"""
        # 测试用 GDB 输出样本
        self.sample_gdb_output = [
            "(gdb) x /8g 0x83A5B000",
            "0x83a5b000:\t0x0000000000000000\t0x0000000000000000",
            "0x83a5b010:\t0x20e97801\t0x20e98801",
            "0x83a5b020:\t0x20e99801\t0x20e9a801"
        ]

    def test_parse_gdb_output(self):
        """测试 GDB 输出解析功能"""
        memory, addresses = parser.parse_gdb_output(self.sample_gdb_output)

        # 验证解析结果数量
        self.assertEqual(len(addresses), 6)

        # 验证第一个条目
        first_addr = addresses[0]
        self.assertEqual(first_addr, "0x83a5b000")
        self.assertEqual(memory[first_addr], "0x0")

        # 验证非零值条目
        self.assertEqual(memory["0x83a5b010"], "0x20e97801")
        self.assertEqual(memory["0x83a5b018"], "0x20e98801")

    def test_parse_gdb_groups(self):
        """测试 GDB 分组解析功能"""
        groups = parser.parse_gdb_groups(self.sample_gdb_output)

        # 验证分组数量
        self.assertEqual(len(groups), 1)

        # 验证分组内容
        group = groups[0]
        self.assertEqual(group['cmd'], "(gdb) x /8g 0x83A5B000")
        self.assertEqual(len(group['lines']), 3)


class TestColorSystem(unittest.TestCase):
    """颜色系统测试"""

    def test_light_theme(self):
        """测试浅色主题"""
        colors = get_theme_colors("light")

        # 验证主要颜色设置
        self.assertIn("text_color", colors)
        self.assertIn("system_red", colors)

    def test_dark_theme(self):
        """测试深色主题"""
        colors = get_theme_colors("dark")

        # 验证主要颜色设置
        self.assertIn("text_color", colors)
        self.assertIn("system_red", colors)

    def test_invalid_theme(self):
        """测试无效主题处理"""
        # 应该抛出 ValueError 异常
        with self.assertRaises(ValueError):
            get_theme_colors("invalid_theme")


class TestMemoryFilter(unittest.TestCase):
    """内存过滤器测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建测试用内存条目
        self.test_addresses = ["0x1000", "0x1008", "0x1010", "0x1018"]
        self.test_memory = {
            "0x1000": "0x0",
            "0x1008": "0x12345678",
            "0x1010": "0x0",
            "0x1018": "0xdeadbeef"
        }

    def test_filter_zero_rows(self):
        """测试零值过滤功能"""
        # 创建一个4个地址的测试用例，按2列布局会分成2行
        # 第一行: ["0x1000", "0x1008"] - 包含非零值
        # 第二行: ["0x1010", "0x1018"] - 包含非零值
        # 由于每行都包含非零值，所以都应该保留
        filtered = filter_zero_rows(self.test_addresses, self.test_memory, 2)

        # 应该保留所有地址，因为每行都有非零值
        self.assertEqual(len(filtered), 4)

        # 测试全零行过滤
        zero_addresses = ["0x2000", "0x2008", "0x2010", "0x2018"]
        zero_memory = {
            "0x2000": "0x0",
            "0x2008": "0x0",  # 第一行全零
            "0x2010": "0x12345678",
            "0x2018": "0x0"  # 第二行有非零值
        }

        filtered_zero = filter_zero_rows(zero_addresses, zero_memory, 2)
        # 第一行应该被保留（包含索引0），第二行应该被保留（有非零值）
        self.assertEqual(len(filtered_zero), 4)


def run_unit_tests():
    """运行所有单元测试"""
    print("🧪 开始运行 memory_viz 单元测试")
    print("=" * 50)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试用例
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryParser))
    suite.addTests(loader.loadTestsFromTestCase(TestColorSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryFilter))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 所有单元测试通过！")
        return True
    else:
        print(f"⚠️  {len(result.failures)} 个测试失败，{len(result.errors)} 个测试错误")
        return False


if __name__ == "__main__":
    success = run_unit_tests()
    sys.exit(0 if success else 1)
